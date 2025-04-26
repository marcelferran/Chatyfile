# CSV Chat App

Esta es una aplicación Streamlit que te permite subir un archivo CSV y chatear con tus datos usando el modelo Gemini 2.0 Flash.

## Archivos

- `app.py`: El archivo principal de la aplicación que orquesta los diferentes componentes.
- `engine.py`: Maneja la interacción con la API y el modelo de Gemini.
- `utils.py`: Contiene funciones de utilidad, como el procesamiento de la respuesta del modelo.
- `layout.py`: Define los elementos de la interfaz de usuario y el diseño de Streamlit.
- `config.py`: Almacena variables de configuración y maneja la obtención de la clave API.
- `requirements.txt`: Lista los paquetes de Python necesarios.
- `readme.md`: Este archivo.

## Configuración

1.  **Clona el repositorio** (o crea estos archivos manualmente).
2.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    **Nota:** La librería `tabulate` es necesaria para mostrar vistas previas de los datos.
3.  **Obtén una clave de API de Gemini:**
    - Ve a [Google AI Studio](https://makersuite.google.com/).
    - Crea una clave API.
4.  **Configura tu clave de API:**
    - **Opción 1 (Variable de Entorno):** Configura la variable de entorno `GEMINI_API_KEY` con tu clave API.
      ```bash
      export GEMINI_API_KEY='TU_CLAVE_API'
      ```
      (Reemplaza `TU_CLAVE_API` con tu clave real)
    - **Opción 2 (Secretos de Streamlit Cloud):** Si vas a desplegar en Streamlit Cloud, crea una carpeta `.streamlit` y dentro de ella, un archivo `secrets.toml`. Añade tu clave API así:
      ```toml
      GEMINI_API_KEY="TU_CLAVE_API"
      ```
      (Reemplaza `TU_CLAVE_API` con tu clave real)

## Ejecutar la Aplicación

1.  Abre tu terminal en el directorio donde están guardados los archivos.
2.  Ejecuta la aplicación Streamlit:
    ```bash
    streamlit run app.py
    ```
3.  Tu navegador web se abrirá con la aplicación.

## Uso

1.  Sube tu archivo CSV usando el cargador de archivos.
2.  Una vez que el archivo esté cargado, se mostrará una vista previa.
3.  Usa el cuadro de entrada del chat en la parte inferior para hacer preguntas sobre tus datos.
4.  La IA responderá con texto, tablas o gráficos básicos basados en los datos.

## Extensión

- Puedes modificar `layout.py` para cambiar la apariencia de la aplicación.
- Mejora `utils.py` para manejar formatos de respuesta más complejos o generar diferentes tipos de gráficos (por ejemplo, usando Altair o Plotly).
- Refina las instrucciones en `app.py` (o muévelas a un archivo separado) para guiar las respuestas de la IA de manera más efectiva.
