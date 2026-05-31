import google.generativeai as genai
import os
from core.prompts import SYSTEM_PROMPT, PROMPT_X, PROMPT_LINKEDIN, PROMPT_TIKTOK

MAX_NEWS_TEXT_CHARS = 30000
MIN_NEWS_TEXT_WORDS = 40

def _clean_model_output(text: str) -> str:
    cleaned = text or ""
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.replace("`", "")
    cleaned = cleaned.replace("[VISUAL/TEXTO EN PANTALLA]", "VISUAL/TEXTO EN PANTALLA:")
    cleaned = cleaned.replace("[LOCUCIÓN]", "LOCUCIÓN:")
    cleaned = cleaned.replace("[LOCUCION]", "LOCUCIÓN:")
    cleaned = cleaned.replace("\n* ", "\n- ")
    return cleaned.strip()

def _friendly_api_error(error: Exception) -> str:
    message = str(error)
    lower_message = message.lower()
    if "429" in lower_message or "quota" in lower_message or "resource exhausted" in lower_message:
        return (
            "No se pudo generar el contenido porque la cuota de Gemini parece agotada temporalmente. "
            "Prueba de nuevo más tarde o introduce tu propia API key de Gemini en el panel de configuración de la app."
        )
    if "api_key" in lower_message or "gemini_api_key" in lower_message:
        return (
            "No se pudo generar el contenido porque no hay una API key de Gemini configurada. "
            "Añade tu propia clave en el panel de configuración de la app."
        )
    if "invalid" in lower_message and "key" in lower_message:
        return (
            "No se pudo generar el contenido porque la API key de Gemini no parece válida. "
            "Revisa la clave o introduce una nueva en el panel de configuración de la app."
        )
    if "blocked" in lower_message or "safety" in lower_message or "finish_reason" in lower_message:
        return (
            "Gemini no devolvió texto para esta solicitud. Puede deberse a filtros de seguridad, "
            "a un texto de entrada problemático o a una respuesta vacía del modelo. Revisa la noticia y prueba de nuevo."
        )
    return f"No se pudo generar el contenido con Gemini. Detalle técnico: {message}"


def _prepare_news_text(news_text: str) -> str:
    if not isinstance(news_text, str):
        raise TypeError("La noticia procesada debe ser texto.")
    cleaned = "\n".join(line.strip() for line in news_text.splitlines())
    cleaned = "\n".join(line for line in cleaned.splitlines() if line)
    cleaned = cleaned.strip()
    if len(cleaned.split()) < MIN_NEWS_TEXT_WORDS:
        raise ValueError("El texto de la noticia es demasiado breve para generar una adaptación fiable.")
    if len(cleaned) > MAX_NEWS_TEXT_CHARS:
        cutoff = cleaned.rfind("\n\n", 0, MAX_NEWS_TEXT_CHARS)
        if cutoff < MAX_NEWS_TEXT_CHARS * 0.6:
            cutoff = MAX_NEWS_TEXT_CHARS
        cleaned = cleaned[:cutoff].strip()
    return cleaned


def _response_text(response) -> str:
    try:
        text = response.text
    except Exception:
        text_parts = []
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                part_text = getattr(part, "text", "")
                if part_text:
                    text_parts.append(part_text)
        text = "\n".join(text_parts)

    cleaned = _clean_model_output(text)
    if not cleaned:
        raise ValueError("Gemini devolvió una respuesta vacía.")
    return cleaned

def get_gemini_client(api_key: str = ""):
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not api_key or not api_key.strip():
        raise ValueError("GEMINI_API_KEY no encontrada.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="models/gemini-flash-latest",
        system_instruction=SYSTEM_PROMPT
    )

def _generate_content(news_text: str, specific_prompt: str, api_key: str = "") -> str:
    try:
        news_text = _prepare_news_text(news_text)
        model = get_gemini_client(api_key)
        response = model.generate_content(specific_prompt.format(news_text=news_text))
        return _response_text(response)
    except Exception as e:
        return _friendly_api_error(e)

def generate_x_post(news_text: str, api_key: str = "") -> str:
    return _generate_content(news_text, PROMPT_X, api_key)

def generate_linkedin_post(news_text: str, api_key: str = "") -> str:
    return _generate_content(news_text, PROMPT_LINKEDIN, api_key)

def generate_tiktok_script(news_text: str, api_key: str = "") -> str:
    return _generate_content(news_text, PROMPT_TIKTOK, api_key)
