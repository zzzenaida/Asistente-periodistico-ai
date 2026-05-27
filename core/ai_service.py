import google.generativeai as genai
import os
from core.prompts import SYSTEM_PROMPT, PROMPT_X, PROMPT_LINKEDIN, PROMPT_TIKTOK

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no encontrada.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

def _generate_content(news_text: str, specific_prompt: str) -> str:
    try:
        model = get_gemini_client()
        response = model.generate_content(specific_prompt.format(news_text=news_text))
        return response.text
    except Exception as e:
        return f"Error en la API de Gemini: {str(e)}"

def generate_x_post(news_text: str) -> str:
    return _generate_content(news_text, PROMPT_X)

def generate_linkedin_post(news_text: str) -> str:
    return _generate_content(news_text, PROMPT_LINKEDIN)

def generate_tiktok_script(news_text: str) -> str:
    return _generate_content(news_text, PROMPT_TIKTOK)
