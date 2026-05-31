# Asistente Periodístico AI

Aplicación web en Streamlit para transformar una noticia original en contenidos adaptados a X, LinkedIn y TikTok con ayuda de Gemini, manteniendo rigor informativo, claridad y ausencia de clickbait.

## Créditos

Aplicación creada por Lena Costas Moldes y Zenaida Pontes Jordá  
Proyecto de la asignatura Periodismo Automatizado Inteligente  
Facultad de Ciencias de la Comunicación - Universidade de Santiago de Compostela  
Curso 2025-2026 | [ia.xornalismo.gal](http://ia.xornalismo.gal/)

## Para qué sirve

El objetivo de la app es ayudar a adaptar una misma pieza periodística a distintos formatos sociales sin inventar datos ni alterar el sentido de la noticia.

La aplicación permite:

- introducir una noticia pegando texto completo;
- extraer texto desde una URL;
- subir un archivo PDF o DOCX;
- generar una adaptación para X/Twitter;
- generar una adaptación profesional para LinkedIn;
- generar un guion audiovisual breve para TikTok;
- revisar y copiar los resultados generados.

## Cómo se usa la app online

1. Abre la aplicación desplegada en Streamlit Cloud.
2. En el apartado **1. Ingresa la noticia original**, elige una de estas opciones:
	- **Pegar texto**: pega el contenido completo de la noticia.
	- **URL**: pega el enlace de una noticia para intentar extraer su texto.
	- **Subir archivo**: carga un PDF o DOCX con la noticia.
3. Pulsa el botón correspondiente para procesar el contenido.
4. Cuando la noticia esté procesada, ve al apartado **2. Generar adaptaciones**.
5. Pulsa el botón de la plataforma que quieras generar:
	- **Generar para X (Twitter)**;
	- **Generar para LinkedIn**;
	- **Generar guion para TikTok**.
6. Consulta el resultado en el apartado **3. Resultados**.

La app no sustituye la revisión periodística. Los textos generados deben revisarse antes de publicarse, especialmente si la noticia contiene cifras, nombres propios, declaraciones o información sensible.

## Cómo funciona por dentro

La app sigue este flujo:

1. Recibe una noticia mediante texto, URL, PDF o DOCX.
2. Extrae el texto útil de la fuente introducida.
3. Envía ese texto a Gemini con un prompt específico para cada plataforma.
4. Devuelve una propuesta adaptada al formato elegido.
5. Limpia marcas de formato innecesarias, como asteriscos de Markdown o bloques de código.

Cada plataforma tiene una orientación distinta:

- **X/Twitter**: síntesis clara, directa y pensada para lectura rápida.
- **LinkedIn**: tono profesional, analítico e informativo.
- **TikTok**: guion breve con indicaciones visuales y locución.

## API key de Gemini

La app necesita una clave de Gemini para generar contenidos.

En la app publicada en Streamlit Cloud, la clave debe configurarse como Secret privado:

```toml
GEMINI_API_KEY = "TU_CLAVE_DE_GEMINI"
```

Esa clave no aparece en GitHub y no debe escribirse nunca en el código.

Si la cuota de la clave principal se agota, la interfaz permite que cada usuario introduzca su propia API key de Gemini durante esa sesión. Esa clave personal no se sube a GitHub ni se guarda en el repositorio.

En una prueba local, como `localhost`, la app no tiene acceso a los Secrets privados de Streamlit Cloud. Para probarla en local hay que definir `GEMINI_API_KEY` en un archivo `.env` o pegar una clave personal en el panel de la interfaz.

## Cómo conseguir una API key personal

1. Entra en [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Inicia sesión con una cuenta de Google.
3. Pulsa **Create API key**.
4. Copia la clave generada.
5. Pégala en el panel **API key de Gemini** de la app, si necesitas usar una clave personal.

## Instalación local

Para ejecutar la aplicación en un ordenador propio:

1. Clona el repositorio.

```bash
git clone https://github.com/zzzenaida/Asistente-periodistico-ai.git
cd Asistente-periodistico-ai
```

2. Crea y activa un entorno virtual.

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instala las dependencias.

```bash
pip install -r requirements.txt
```

4. Crea un archivo `.env` con la clave de Gemini.

```env
GEMINI_API_KEY=TU_CLAVE_DE_GEMINI
```

5. Lanza la app.

```bash
streamlit run app.py
```

## Despliegue en Streamlit Cloud

Para publicar la app online:

1. Entra en [Streamlit Community Cloud](https://share.streamlit.io/).
2. Crea una nueva app desde GitHub.
3. Selecciona el repositorio.
4. Configura estos valores:

```text
Branch: main
Main file path: app.py
```

5. En **Secrets**, añade:

```toml
GEMINI_API_KEY = "TU_CLAVE_DE_GEMINI"
```

6. Pulsa **Deploy**.

## Seguridad

- No publiques archivos `.env`.
- No subas `.streamlit/secrets.toml` a GitHub.
- No pegues claves reales en el README, en capturas públicas ni en commits.
- Si una clave se filtra, revócala en Google AI Studio y crea una nueva.
- Si la app pública recibe mucho uso, la cuota de Gemini puede agotarse. En ese caso, cada usuario puede introducir temporalmente su propia clave en la interfaz.

## Limitaciones

- Algunas webs pueden bloquear la extracción automática desde URL.
- Los PDF escaneados como imagen pueden no devolver texto legible.
- Gemini puede cometer errores; los resultados deben revisarse antes de su publicación.
- La app genera borradores de adaptación, no piezas periodísticas verificadas por sí mismas.
