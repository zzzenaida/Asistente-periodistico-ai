import google.generativeai as genai
import os
from core.prompts import SYSTEM_PROMPT, PROMPT_X, PROMPT_LINKEDIN, PROMPT_TIKTOK

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
    return f"No se pudo generar el contenido con Gemini. Detalle técnico: {message}"

def get_gemini_client(api_key: str = ""):
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no encontrada.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="models/gemini-flash-latest",
        system_instruction=SYSTEM_PROMPT
    )

def _generate_content(news_text: str, specific_prompt: str, api_key: str = "") -> str:
    try:
        model = get_gemini_client(api_key)
        response = model.generate_content(specific_prompt.format(news_text=news_text))
        return _clean_model_output(response.text)
    except Exception as e:
        return _friendly_api_error(e)

def generate_x_post(news_text: str, api_key: str = "") -> str:
    return _generate_content(news_text, PROMPT_X, api_key)

def generate_linkedin_post(news_text: str, api_key: str = "") -> str:
    return _generate_content(news_text, PROMPT_LINKEDIN, api_key)

def generate_tiktok_script(news_text: str, api_key: str = "") -> str:
    return _generate_content(news_text, PROMPT_TIKTOK, api_key)
