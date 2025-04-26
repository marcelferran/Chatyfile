# Chatyfile

Esta es una aplicación Streamlit que te permite subir un archivo CSV y chatear con tus datos usando el modelo Gemini 2.0 Flash, con un layout personalizado.

## Archivos

- `app.py`: El archivo principal de la aplicación que orquesta los diferentes componentes y maneja la lógica del chat.
- `engine.py`: Contiene la clase `ChatEngine` para interactuar con el modelo Gemini y procesar preguntas.
- `utils.py`: Contiene funciones de utilidad para parsear las respuestas del modelo y ayudar a la visualización.
- `layout.py`: Define las funciones para configurar la página, aplicar estilos CSS personalizados y mostrar el encabezado y pie de página.
- `config.py`: Almacena variables de configuración y maneja la obtención de la clave API.
- `requirements.txt`: Lista los paquetes de Python necesarios.
- `readme.md`: Este archivo.

## Configuración

1.  **Clona el repositorio** (o crea estos archivos manualmente).
2.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
    **Nota:** Asegúrate de que todas las librerías listadas estén instaladas.
3.  **Obtén una clave de API de Gemini:**
    - Ve a [Google AI Studio](https://makersuite.google.com/).
    - Crea una clave API.
4.  **Configura tu clave de API:**
    - **Opción 1 (Variable de Entorno):** Configura la variable de entorno `GEMINI_API_KEY` con tu clave API.
      ```bash
      export GEMINI_API_KEY='TU_CLAVE_API'
      ```
      (Reemplaza `TU_CLAVE_API` con tu clave real)
    - **Option 2 (Streamlit Cloud Secrets):** If deploying to Streamlit Cloud, create a `.streamlit` folder and inside it, a `secrets.toml` file. Add your API key like this:
      ```toml
      GEMINI_API_KEY="TU_CLAVE_API"
      ```
      (Replace `TU_CLAVE_API` with your actual key)
5.  **Asegúrate de tener un archivo `logo.jpeg`** en el mismo directorio que `app.py` si deseas que se muestre el logo en el encabezado.

## Ejecutar la Aplicación

1.  Abre tu terminal en el directorio donde están guardados los archivos.
2.  Ejecuta la aplicación Streamlit:
    ```bash
    streamlit run app.py
    ```
3.  Tu navegador web se abrirá con la aplicación.

## Uso

1.  Sube tu archivo CSV usando el cargador de archivos en la barra lateral.
2.  Una vez que el archivo esté cargado, un mensaje de bienvenida aparecerá en el chat.
3.  Usa el cuadro de entrada de texto en la parte inferior para hacer preguntas sobre tus datos.
4.  La IA responderá con texto, tablas o gráficos básicos basados en los datos.

## Extensión

- Puedes modificar el CSS en `layout.py` para ajustar aún más la apariencia.
- Mejora `utils.py` para manejar formatos de respuesta más complejos o generar diferentes tipos de gráficos (por ejemplo, usando Altair o Plotly en lugar de los gráficos básicos de Streamlit).
- Refina las instrucciones en `engine.py` para guiar las respuestas de la IA de manera más efectiva.
