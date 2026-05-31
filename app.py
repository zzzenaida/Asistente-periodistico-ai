import streamlit as st
import os
from dotenv import load_dotenv
from core.extractors import extract_from_url, extract_from_pdf, extract_from_docx
from core.ai_service import generate_x_post, generate_linkedin_post, generate_tiktok_script

# Cargar variables de entorno
load_dotenv()

st.set_page_config(page_title="Asistente Periodístico AI", page_icon="🗞️", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --color-white:          #FFFFFF;
        --color-off-white:      #FDF7F9;
        --color-surface:        #FFF0F5;
        --color-surface-alt:    #FFE4EE;

        --color-pink-100:       #FFD6E7;
        --color-pink-200:       #FFB3CF;
        --color-pink-300:       #FF85B3;
        --color-pink-400:       #F5588C;
        --color-pink-500:       #E03575;
        --color-pink-600:       #C0215D;

        --color-text-primary:   #2D0A1A;
        --color-text-secondary: #8C3F5E;
        --color-text-muted:     #C08098;
        --color-text-on-pink:   #FFFFFF;

        --color-border-light:   #FFD6E7;
        --color-border-medium:  #FFB3CF;
        --color-border-focus:   #F5588C;

        --font-family:          -apple-system, "SF Pro Display", "SF Pro Text",
                               BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
        --font-size-xs:         11px;
        --font-size-sm:         13px;
        --font-size-base:       15px;
        --font-size-md:         17px;
        --font-size-lg:         20px;
        --font-size-xl:         24px;
        --font-size-2xl:        28px;
        --font-size-3xl:        34px;

        --font-weight-regular:  500;
        --font-weight-medium:   600;
        --font-weight-semibold: 700;
        --font-weight-bold:     800;

        --line-height-tight:    1.2;
        --line-height-normal:   1.5;
        --line-height-loose:    1.7;
        --letter-spacing-tight: -0.02em;
        --letter-spacing-normal: 0em;
        --letter-spacing-wide:  0.02em;

        --space-2:   2px;
        --space-4:   4px;
        --space-6:   6px;
        --space-8:   8px;
        --space-12:  12px;
        --space-16:  16px;
        --space-20:  20px;
        --space-24:  24px;
        --space-32:  32px;
        --space-40:  40px;
        --space-48:  48px;
        --space-64:  64px;

        --radius-xs:    4px;
        --radius-sm:    8px;
        --radius-md:    12px;
        --radius-lg:    16px;
        --radius-xl:    20px;
        --radius-full:  9999px;

        --shadow-sm:    0 1px 3px rgba(240, 60, 120, 0.08),
                        0 1px 2px rgba(240, 60, 120, 0.04);
        --shadow-md:    0 4px 12px rgba(240, 60, 120, 0.12),
                        0 2px 6px rgba(240, 60, 120, 0.06);
        --shadow-lg:    0 8px 24px rgba(240, 60, 120, 0.16),
                        0 4px 12px rgba(240, 60, 120, 0.08);
        --shadow-focus: 0 0 0 3px rgba(245, 88, 140, 0.25);

        --transition-fast:   100ms ease;
        --transition-normal: 200ms ease;
        --transition-slow:   350ms ease;

        --ink: #1e2a2a;
        --accent: #1f4b45;
        --accent-soft: #b7c9c3;
        --accent-2: #7a3b2e;
        --accent-3: #2f5f91;
        --surface: #ffffff;
        --surface-muted: #f7f5f2;
    }

    body {
        font-family: var(--font-family);
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-medium);
        line-height: var(--line-height-normal);
        color: var(--color-text-primary);
        background-color: var(--color-off-white);
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        background-color: var(--color-off-white);
        color: var(--color-text-primary);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-family);
        letter-spacing: var(--letter-spacing-tight);
        color: var(--color-text-primary);
    }

    .stMarkdown, .stText, .stTextInput, .stTextArea, .stTabs {
        font-family: var(--font-family);
    }

    .stButton > button {
        height: 44px;
        padding: 0 var(--space-20);
        border-radius: var(--radius-md);
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-semibold);
        background-color: var(--color-pink-400);
        color: var(--color-text-on-pink);
        border: none;
        box-shadow: var(--shadow-sm);
        transition: background-color var(--transition-fast),
                    transform var(--transition-fast),
                    box-shadow var(--transition-fast),
                    opacity var(--transition-fast);
    }

    .stButton > button:hover {
        background-color: var(--color-pink-500);
        box-shadow: var(--shadow-md);
    }

    .stButton > button:active {
        background-color: var(--color-pink-600);
        transform: scale(0.97);
    }

    .stButton > button:focus-visible {
        outline: none;
        box-shadow: var(--shadow-focus);
    }

    .stTabs [data-baseweb="tab"] {
        height: 32px;
        padding: 0 var(--space-16);
        border-radius: var(--radius-full);
        font-size: var(--font-size-sm);
        background-color: var(--color-surface);
        color: var(--color-text-secondary);
        border: 1px solid var(--color-border-light);
        transition: background-color var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
    }

    .stTabs [data-baseweb="tab"]:hover {
        border-color: var(--color-border-medium);
        background-color: var(--color-surface-alt);
    }

    .stTabs [aria-selected="true"] {
        color: var(--color-text-on-pink);
        background-color: var(--color-pink-400);
        border-color: var(--color-pink-400);
    }

    .stTabs [aria-selected="true"]::after {
        background-color: transparent;
    }

    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextInput"] input {
        background-color: var(--color-surface);
        border: 1px solid var(--color-border-light);
        border-radius: var(--radius-sm);
        color: var(--color-text-primary);
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-regular);
    }

    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stTextInput"] input:focus {
        border-color: var(--color-border-focus);
        box-shadow: var(--shadow-focus);
    }

    div[data-testid="stTextArea"] textarea::placeholder,
    div[data-testid="stTextInput"] input::placeholder {
        color: var(--color-text-muted);
    }

    div[data-testid="stFileUploader"] {
        background: var(--color-surface);
        border: 1px solid var(--color-border-light);
        border-radius: var(--radius-md);
        padding: var(--space-8) var(--space-12);
        box-shadow: var(--shadow-sm);
    }

    div[data-testid="stAlert"] {
        border-left: 4px solid var(--color-pink-400);
        background-color: var(--color-surface);
        box-shadow: var(--shadow-sm);
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-4);
        padding: var(--space-2) var(--space-8);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: var(--font-weight-semibold);
        letter-spacing: var(--letter-spacing-wide);
    }

    .badge-success {
        background: #E6F9F0;
        color: #1A7F4B;
    }

    .card-social {
        background: var(--color-white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--color-border-light);
        box-shadow: var(--shadow-sm);
        padding: var(--space-16);
        display: flex;
        flex-direction: column;
        gap: var(--space-12);
        margin-bottom: var(--space-12);
    }

    .card-social-header {
        display: flex;
        align-items: center;
        gap: var(--space-12);
    }

    .card-social-name {
        font-size: var(--font-size-md);
        font-weight: var(--font-weight-semibold);
        letter-spacing: var(--letter-spacing-tight);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🗞️ Asistente periodístico")
st.write("Adapta tus noticias a X, LinkedIn y TikTok con rigor informativo. **Cero clickbait, cero invenciones.**")

def _is_valid_key(value: str) -> bool:
    return bool(value and value.strip() and value.strip() != "tu_clave_de_google_aqui")

def _get_streamlit_secret_key() -> str:
    try:
        return str(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        return ""

def _get_app_api_key() -> str:
    secret_key = _get_streamlit_secret_key()
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if _is_valid_key(secret_key):
        return secret_key.strip()
    if _is_valid_key(env_key):
        return env_key.strip()
    return ""

def _mask_key(value: str) -> str:
    value = (value or "").strip()
    if len(value) < 10:
        return "clave añadida"
    return f"{value[:4]}...{value[-4:]}"

def _looks_like_api_issue(text: str) -> bool:
    lowered = (text or "").lower()
    return "cuota de gemini" in lowered or "api key de gemini" in lowered or "no se pudo generar" in lowered

def _looks_like_ready_news(text: str) -> bool:
    return isinstance(text, str) and len(text.strip().split()) >= 40

def _generate_safely(generator, news_text: str, api_key: str) -> str:
    if not _is_valid_key(api_key):
        return (
            "No se pudo generar el contenido porque no hay una API key de Gemini disponible. "
            "Añade tu propia clave en el panel de configuración de la app."
        )
    if not _looks_like_ready_news(news_text):
        return (
            "No se pudo generar el contenido porque el texto de la noticia está vacío o es demasiado breve. "
            "Pega el cuerpo completo de la noticia o prueba otra fuente."
        )
    try:
        result = generator(news_text, api_key)
    except Exception as error:
        return f"No se pudo generar el contenido con Gemini. Detalle técnico: {error}"
    if not isinstance(result, str) or not result.strip():
        return "No se pudo generar el contenido porque Gemini no devolvió texto. Prueba de nuevo o usa otra API key."
    return result

if "user_gemini_api_key" not in st.session_state:
    st.session_state.user_gemini_api_key = ""

app_api_key = _get_app_api_key()
user_api_key = st.session_state.user_gemini_api_key
api_key_to_use = user_api_key if _is_valid_key(user_api_key) else app_api_key

with st.expander("🔐 API key de Gemini", expanded=not _is_valid_key(api_key_to_use)):
    if _is_valid_key(app_api_key):
        st.info("La app está usando automáticamente su API key privada. No tienes que introducir ninguna clave salvo que la cuota se agote o quieras usar la tuya.")
    else:
        st.warning("Esta ejecución no tiene una GEMINI_API_KEY privada configurada. En localhost es normal: los Secrets de Streamlit Cloud no viajan con el repositorio. Para probar aquí, añade una clave personal; en la app publicada bastará con configurar la clave en Secrets.")

    st.markdown(
        """
Si necesitas usar tu propia clave:
1. Entra en [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Inicia sesión con tu cuenta de Google.
3. Pulsa en **Create API key**.
4. Copia la clave y pégala aquí.

La clave personal se guarda solo durante esta sesión del navegador. No se sube a GitHub ni se escribe en el repositorio.
        """
    )
    api_key_input = st.text_input("Tu GEMINI_API_KEY", type="password", placeholder="Pega aquí tu API key de Gemini")
    col_key_save, col_key_clear = st.columns(2)
    with col_key_save:
        if st.button("Usar mi clave", use_container_width=True):
            if _is_valid_key(api_key_input):
                st.session_state.user_gemini_api_key = api_key_input.strip()
                st.success("Clave personal guardada para esta sesión.")
                st.rerun()
            else:
                st.error("La clave está vacía o no es válida.")
    with col_key_clear:
        if st.button("Quitar mi clave", use_container_width=True):
            st.session_state.user_gemini_api_key = ""
            st.rerun()

    if _is_valid_key(st.session_state.user_gemini_api_key):
        st.caption(f"Usando clave personal: {_mask_key(st.session_state.user_gemini_api_key)}")
    elif _is_valid_key(app_api_key):
        st.caption("Usando clave privada de la app.")

if not _is_valid_key(api_key_to_use):
    st.warning("⚠️ No hay una API key de Gemini disponible en esta ejecución. Añade una clave personal para probar en local o configura GEMINI_API_KEY en los Secrets del despliegue.")

# 1. Zona de Ingesta (Pestañas)
st.subheader("1. Ingresa la noticia original")
tab_texto, tab_url, tab_archivo = st.tabs(["📝 Pegar texto", "🔗 URL", "📁 Subir archivo"])

if "noticia_procesada" not in st.session_state:
    st.session_state.noticia_procesada = ""

with tab_texto:
    texto_ingresado = st.text_area("Pega el contenido completo de la noticia aquí:", height=200)
    if st.button("Procesar texto"):
        if texto_ingresado.strip():
            st.session_state.noticia_procesada = texto_ingresado
            st.success("Texto procesado correctamente.")
        else:
            st.error("El texto está vacío.")

with tab_url:
    url_ingresada = st.text_input("Ingresa la URL de la noticia:")
    if st.button("Extraer de URL"):
        if url_ingresada.strip():
            with st.spinner("Extrayendo contenido de la web..."):
                texto_extraido = extract_from_url(url_ingresada)
                if "Error" not in texto_extraido[:7]:
                    st.session_state.noticia_procesada = texto_extraido
                    st.success("Texto extraído de la URL correctamente.")
                    st.caption(f"Texto preparado: {len(texto_extraido.split())} palabras aproximadamente.")
                    with st.expander("Ver texto extraído"):
                        st.write(st.session_state.noticia_procesada)
                else:
                    st.error(texto_extraido)
                    st.info("💡 Consejo: Algunos sitios bloquean la extracción automatizada (Paywalls, bloqueos anti-bot). Intenta pegar el texto manualmente.")
        else:
            st.error("La URL está vacía.")

with tab_archivo:
    archivo_subido = st.file_uploader("Sube un archivo PDF o DOCX", type=["pdf", "docx"])
    if st.button("Extraer de archivo"):
        if archivo_subido is not None:
            with st.spinner("Extrayendo contenido del archivo..."):
                if archivo_subido.name.endswith('.pdf'):
                    texto_extraido = extract_from_pdf(archivo_subido.read())
                elif archivo_subido.name.endswith('.docx'):
                    texto_extraido = extract_from_docx(archivo_subido.read())
                
                if "Error" not in texto_extraido[:7]:
                    st.session_state.noticia_procesada = texto_extraido
                    st.success("Texto extraído del archivo correctamente.")
                    with st.expander("Ver texto extraído"):
                        st.write(st.session_state.noticia_procesada)
                else:
                    st.error(texto_extraido)
        else:
            st.error("Por favor, sube un archivo.")

# 2. Zona de Generación
if st.session_state.noticia_procesada:
    st.divider()
    st.subheader("2. Generar adaptaciones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🐦 Generar para X (Twitter)", use_container_width=True):
            with st.spinner("Redactando hilo periodístico..."):
                resultado_x = _generate_safely(generate_x_post, st.session_state.noticia_procesada, api_key_to_use)
                st.session_state.resultado_x = resultado_x
                if _looks_like_api_issue(resultado_x):
                    st.warning(resultado_x)

    with col2:
        if st.button("💼 Generar para LinkedIn", use_container_width=True):
            with st.spinner("Redactando post profesional..."):
                resultado_linkedin = _generate_safely(generate_linkedin_post, st.session_state.noticia_procesada, api_key_to_use)
                st.session_state.resultado_linkedin = resultado_linkedin
                if _looks_like_api_issue(resultado_linkedin):
                    st.warning(resultado_linkedin)

    with col3:
        if st.button("📱 Generar guion para TikTok", use_container_width=True):
            with st.spinner("Redactando guion audiovisual..."):
                resultado_tiktok = _generate_safely(generate_tiktok_script, st.session_state.noticia_procesada, api_key_to_use)
                st.session_state.resultado_tiktok = resultado_tiktok
                if _looks_like_api_issue(resultado_tiktok):
                    st.warning(resultado_tiktok)

    # 3. Zona de Resultados
    if "resultado_x" in st.session_state or "resultado_linkedin" in st.session_state or "resultado_tiktok" in st.session_state:
        st.divider()
        st.subheader("3. Resultados")
        tab_res_x, tab_res_linkedin, tab_res_tiktok = st.tabs(["🐦 X (Twitter)", "💼 LinkedIn", "📱 TikTok"])
        
        with tab_res_x:
            if "resultado_x" in st.session_state:
                st.markdown(
                    """
                    <div class="card-social">
                        <div class="card-social-header">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="#000000" xmlns="http://www.w3.org/2000/svg"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.746l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                            <div class="card-social-name">X / Twitter</div>
                            <span class="badge badge-success" style="margin-left:auto;">Generado</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.text_area("Resultado X:", st.session_state.resultado_x, height=300)
            else:
                st.info("Presiona 'Generar para X' arriba.")
                
        with tab_res_linkedin:
            if "resultado_linkedin" in st.session_state:
                st.markdown(
                    """
                    <div class="card-social">
                        <div class="card-social-header">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="#0A66C2" xmlns="http://www.w3.org/2000/svg"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                            <div class="card-social-name">LinkedIn</div>
                            <span class="badge badge-success" style="margin-left:auto;">Generado</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.text_area("Resultado LinkedIn:", st.session_state.resultado_linkedin, height=300)
            else:
                st.info("Presiona 'Generar para LinkedIn' arriba.")
                
        with tab_res_tiktok:
            if "resultado_tiktok" in st.session_state:
                st.markdown(
                    """
                    <div class="card-social">
                        <div class="card-social-header">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="#010101" xmlns="http://www.w3.org/2000/svg"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.69a8.18 8.18 0 0 0 4.78 1.52V6.76a4.85 4.85 0 0 1-1.01-.07z"/></svg>
                            <div class="card-social-name">TikTok</div>
                            <span class="badge badge-success" style="margin-left:auto;">Generado</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.text_area("Resultado TikTok:", st.session_state.resultado_tiktok, height=300)
            else:
                st.info("Presiona 'Generar Guion de TikTok' arriba.")

st.divider()
st.markdown(
    """
    <div style="font-size: 0.9rem; color: #555; line-height: 1.5;">
        <strong>Aplicación creada por Lena Costas Moldes y Zenaida Pontes Jordá</strong><br>
        Proyecto de la asignatura Periodismo Automatizado Inteligente<br>
        Facultad de Ciencias de la Comunicación - Universidade de Santiago de Compostela<br>
        Curso 2025-2026 | <a href="http://ia.xornalismo.gal/" target="_blank">ia.xornalismo.gal</a>
    </div>
    """,
    unsafe_allow_html=True,
)
