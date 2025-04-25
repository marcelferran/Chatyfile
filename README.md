Chatyfile

Chatyfile es un asistente inteligente que te ayuda a interactuar con archivos CSV usando lenguaje natural.
Basado en Gemini 2.0 Flash de Google y construido con Streamlit, permite hacer preguntas sobre tus datos, obtener respuestas, filtrar información y generar gráficos automáticamente.

Características
*Carga de archivos CSV de manera sencilla.

*Asistente de datos usando Gemini 2.0 Flash.

*Generación automática de tablas y gráficos (usando pandas y matplotlib).

*Indicador de procesamiento ("Pensando la respuesta...").

*Historial de chat con scroll y diseño moderno.

*Interfaz responsiva y estética en tonos azul, gris y blanco.

*Sin uso de librerías externas como Plotly o Seaborn.

Tecnologías utilizadas
*Python 3.9+

*Streamlit 1.38.0+

*Google Generative AI (google-generativeai)

*Pandas

*Matplotlib

Instalación local
Clonar el repositorio:
git clone https://github.com/tu_usuario/chatyfile.git
cd chatyfile

Instalar las dependencias
pip install -r requirements.txt

Configurar la API KEY de Google Generative AI:
Crear un archivo .streamlit/secrets.toml en la raíz del proyecto con el siguiente contenido:
GOOGLE_API_KEY = "tu_clave_api"
Nota: Puedes obtener tu API Key gratuita en Google AI Studio: https://makersuite.google.com/app/apikey

Ejecutar la aplicación
streamlit run app.py

Despliegue en Streamlit Cloud
Crear un nuevo repositorio en GitHub y subir todos los archivos (app.py, engine.py, layout.py, utils.py, config.py, requirements.txt, etc).
Conectar la cuenta en Streamlit Cloud: https://streamlit.io/cloud
Desplegar la aplicación seleccionando el repositorio.

Configurar los Secrets en Streamlit Cloud
Settings > Secrets:
GOOGLE_API_KEY = "tu_clave_api"
Ejecutar y utilizar la aplicación en la nube.

Cómo usar Chatyfile
Subir un archivo CSV.
Realizar preguntas en lenguaje natural, ejemplos:
  "¿Cuántos proveedores de Urea hay?"
  "Muestra las primeras 5 filas"
  "Haz un gráfico de pastel con el porcentaje de ventas del top 5 de proveedores"
Visualizar las respuestas como texto, tablas interactivas o gráficos.

Desarrollado por
Marcel Ferran Castro Ponce de Leon
https://www.linkedin.com/in/marcelcastroponcedeleon/
https://github.com/marcelferran
WiseJourney Branding

Licencia
Este proyecto está protegido por derechos de autor © 2025 Chatyfile.
Todos los derechos reservados. Uso interno o educativo permitido bajo solicitud.
