import io
import json
import re
from urllib.parse import urlparse

import PyPDF2
import requests
from bs4 import BeautifulSoup
from docx import Document

try:
    import trafilatura
except ImportError:
    trafilatura = None


MIN_ARTICLE_CHARS = 600
MIN_ARTICLE_WORDS = 90


def _normalise_text(text: str) -> str:
    text = (text or "").replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalise_inline(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _is_usable_article_text(text: str) -> bool:
    cleaned = _normalise_text(text)
    return len(cleaned) >= MIN_ARTICLE_CHARS and len(cleaned.split()) >= MIN_ARTICLE_WORDS


def _join_unique(parts: list[str]) -> str:
    seen = set()
    cleaned_parts = []
    for part in parts:
        cleaned = _normalise_text(part)
        fingerprint = cleaned.lower()
        if cleaned and fingerprint not in seen:
            cleaned_parts.append(cleaned)
            seen.add(fingerprint)
    return _normalise_text("\n\n".join(cleaned_parts))


def _iter_json_ld_items(data):
    if isinstance(data, list):
        for item in data:
            yield from _iter_json_ld_items(item)
    elif isinstance(data, dict):
        yield data
        graph = data.get("@graph")
        if graph:
            yield from _iter_json_ld_items(graph)


def _json_value_to_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("name") or value.get("headline") or ""
    if isinstance(value, list):
        return ", ".join(filter(None, (_json_value_to_text(item) for item in value)))
    return ""


def _meta_content(soup: BeautifulSoup, *selectors: str) -> str:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            content = node.get("content") or node.get_text(" ", strip=True)
            if content:
                return content
    return ""


def _extract_title_and_description(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else ""
    if not title:
        title = _meta_content(
            soup,
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            "title",
        )
    description = _meta_content(
        soup,
        'meta[name="description"]',
        'meta[property="og:description"]',
        'meta[name="twitter:description"]',
    )
    return _join_unique([title, description])


def _extract_from_json_ld(soup: BeautifulSoup) -> str:
    article_types = {"article", "newsarticle", "reportagenewsarticle", "blogposting"}
    candidates = []

    for script in soup.select('script[type="application/ld+json"]'):
        raw_json = script.string or script.get_text(strip=True)
        if not raw_json:
            continue
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            continue

        for item in _iter_json_ld_items(data):
            raw_type = item.get("@type", "")
            types = raw_type if isinstance(raw_type, list) else [raw_type]
            normalised_types = {str(item_type).lower() for item_type in types}
            if not normalised_types.intersection(article_types):
                continue

            headline = _json_value_to_text(item.get("headline") or item.get("name"))
            description = _json_value_to_text(item.get("description"))
            author = _json_value_to_text(item.get("author"))
            date_published = _json_value_to_text(item.get("datePublished"))
            body = _json_value_to_text(item.get("articleBody") or item.get("text"))
            text = _join_unique([headline, description, author, date_published, body])
            if text:
                candidates.append(text)

    if not candidates:
        return ""
    return max(candidates, key=len)


def _remove_non_content_nodes(soup: BeautifulSoup) -> None:
    for node in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "button",
        "svg",
        "iframe",
    ]):
        node.decompose()

    noisy_tokens = re.compile(
        r"cookie|consent|newsletter|subscribe|social|share|related|recommended|"
        r"advert|promo|breadcrumb|menu|nav|footer|header|sidebar|comment",
        re.IGNORECASE,
    )
    for node in soup.find_all(True):
        class_id = " ".join(node.get("class", [])) + " " + str(node.get("id", ""))
        if noisy_tokens.search(class_id):
            node.decompose()


def _link_density(node) -> float:
    text_length = len(_normalise_inline(node.get_text(" ", strip=True)))
    if text_length == 0:
        return 1.0
    link_text_length = sum(len(_normalise_inline(link.get_text(" ", strip=True))) for link in node.find_all("a"))
    return link_text_length / text_length


def _candidate_score(node) -> float:
    text = _normalise_inline(node.get_text(" ", strip=True))
    paragraphs = node.find_all("p")
    paragraph_text = " ".join(_normalise_inline(p.get_text(" ", strip=True)) for p in paragraphs)
    paragraph_length = len(paragraph_text)
    if len(text) < 200 or paragraph_length < 100:
        return 0

    score = paragraph_length
    score += len(paragraphs) * 80
    score += text.count(".") * 8
    score += text.count(",") * 4
    score -= _link_density(node) * len(text) * 1.5

    node_name = getattr(node, "name", "")
    if node_name == "article":
        score += 500
    if node_name == "main" or node.get("role") == "main":
        score += 300
    return score


def _extract_from_html_structure(soup: BeautifulSoup) -> str:
    _remove_non_content_nodes(soup)
    selectors = [
        "article",
        "main",
        '[role="main"]',
        '[itemtype*="NewsArticle"]',
        '[itemtype*="Article"]',
        '[class*="article"]',
        '[class*="story"]',
        '[class*="post"]',
        '[class*="entry"]',
        '[class*="content"]',
    ]

    candidates = []
    seen_ids = set()
    for selector in selectors:
        for node in soup.select(selector):
            node_id = id(node)
            if node_id not in seen_ids:
                candidates.append(node)
                seen_ids.add(node_id)

    if not candidates:
        candidates = soup.find_all(["article", "main", "section", "div"])

    scored_candidates = [(node, _candidate_score(node)) for node in candidates]
    scored_candidates = [candidate for candidate in scored_candidates if candidate[1] > 0]
    if not scored_candidates:
        return ""

    best_node = max(scored_candidates, key=lambda candidate: candidate[1])[0]
    title = soup.find("h1")
    title_text = title.get_text(" ", strip=True) if title else ""
    paragraph_parts = [p.get_text(" ", strip=True) for p in best_node.find_all("p")]
    if not paragraph_parts:
        paragraph_parts = [best_node.get_text(" ", strip=True)]
    return _join_unique([title_text, *paragraph_parts])


def _extract_with_trafilatura(html: str, url: str) -> str:
    if trafilatura is None:
        return ""
    extracted = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
        output_format="txt",
    )
    return _normalise_text(extracted or "")


def _ensure_url_has_scheme(url: str) -> str:
    url = (url or "").strip()
    parsed = urlparse(url)
    if parsed.scheme:
        return url
    return f"https://{url}"

def extract_from_url(url: str) -> str:
    """Extrae el texto principal de una URL periodística con varios métodos genéricos."""
    try:
        url = _ensure_url_has_scheme(url)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.7",
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "html" not in content_type.lower() and response.text.lstrip()[:1] != "<":
            return "Error al extraer URL: la URL no parece contener una página HTML legible."

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        title_and_description = _extract_title_and_description(soup)

        extracted_text = _extract_with_trafilatura(html, url)
        extracted_text = _join_unique([title_and_description, extracted_text])
        if _is_usable_article_text(extracted_text):
            return extracted_text

        extracted_text = _extract_from_json_ld(soup)
        extracted_text = _join_unique([title_and_description, extracted_text])
        if _is_usable_article_text(extracted_text):
            return extracted_text

        extracted_text = _extract_from_html_structure(soup)
        if _is_usable_article_text(extracted_text):
            return extracted_text

        return (
            "Error al extraer URL: no se encontró suficiente texto periodístico en la página. "
            "Puede deberse a bloqueo del medio, paywall, contenido cargado por JavaScript o una estructura no legible. "
            "Prueba a pegar manualmente el cuerpo de la noticia."
        )
    except Exception as e:
        return f"Error al extraer URL: {str(e)}"

def extract_from_pdf(file_bytes: bytes) -> str:
    """Extrae el texto de un archivo PDF."""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error al leer PDF: {str(e)}"

def extract_from_docx(file_bytes: bytes) -> str:
    """Extrae el texto de un archivo DOCX."""
    try:
        doc_file = io.BytesIO(file_bytes)
        doc = Document(doc_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error al leer DOCX: {str(e)}"
