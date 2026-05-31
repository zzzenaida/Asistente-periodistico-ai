# Asistente Periodistico AI

Aplicacion en Streamlit para adaptar noticias a X, LinkedIn y TikTok con Gemini.

## Uso de API key

La app publicada en Streamlit Cloud puede usar una `GEMINI_API_KEY` privada configurada en los Secrets del despliegue. Esa clave no aparece en GitHub y no debe subirse nunca al repositorio.

Si la cuota de esa clave se agota, la propia interfaz permite que cada usuario introduzca su API key personal de Gemini para esa sesion.

En una prueba local, como `localhost`, la app no tiene acceso a los Secrets privados de Streamlit Cloud. Para probarla en local hay que definir `GEMINI_API_KEY` en un archivo `.env` o pegar una clave personal en el panel de la interfaz.

## Como conseguir una API key personal

1. Entra en https://aistudio.google.com/app/apikey.
2. Inicia sesion con tu cuenta de Google.
3. Pulsa en **Create API key**.
4. Copia la clave y pegala en el panel de configuracion de la app.

La clave personal introducida en la app se guarda solo durante la sesion del navegador. No se sube a GitHub ni se escribe en el repositorio.

## Configuracion en Streamlit Cloud

En la app publicada, configura la clave privada en:

```toml
GEMINI_API_KEY = "TU_CLAVE_DE_GEMINI"
```

Debe añadirse en **Settings > Secrets** de Streamlit Cloud, no en el codigo.

## Instalacion local

1. Crea un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Crea un archivo `.env` local con tu clave:

```env
GEMINI_API_KEY=TU_CLAVE_DE_GEMINI
```

4. Lanza la app:

```bash
streamlit run app.py
```

## Seguridad

- No publiques `.env`.
- No subas `.streamlit/secrets.toml`.
- Si una clave se filtra, revocala y crea otra.
- Si la app publica recibe mucho uso, la cuota de Gemini puede agotarse. En ese caso, cada usuario puede introducir su propia clave en la interfaz.
