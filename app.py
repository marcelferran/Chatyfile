import pandas as pd
import streamlit as st
from config import configure_genai
from utils import mostrar_resumen_df
from chat_engine import iniciar_chat, mostrar_historial, procesar_pregunta, borrar_historial
from layout import apply_custom_styles, show_header, show_footer, show_welcome_message, sidebar_file_uploader

# Configuración de la página
st.set_page_config(
    page_title="Chatyfile",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos y mostrar elementos de diseño
apply_custom_styles()
show_header()
show_welcome_message()
uploaded_file = sidebar_file_uploader()
show_footer()

# Configurar la API de Google Generative AI usando la clave desde secrets
try:
    api_key = st.secrets["GOOGLE_API_KEY"]  # Ajusta el nombre de la clave si es diferente
    configure_genai(api_key)
except KeyError:
    st.error("No se encontró la clave API en st.secrets. Por favor, configura 'GOOGLE_API_KEY' en los secrets de Streamlit.")
    st.stop()

# Inicializar estado de la sesión
if "chat" not in st.session_state:
    st.session_state.chat = None
if "history" not in st.session_state:
    st.session_state.history = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    mostrar_resumen_df(df)

    # Iniciar el chat si no ha sido iniciado
    if st.session_state.chat is None:
        iniciar_chat(df)

    # Mostrar el historial de la conversación
    mostrar_historial()

    # Formulario para enviar preguntas
    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar", disabled=False)

    if submitted and pregunta:
        if pregunta.lower() == "salir":
            st.session_state.history.append({"role": "system", "content": "👋 Adios."})
            st.session_state.chat = None
            st.rerun()
        else:
            procesar_pregunta(pregunta, df)
            st.rerun()

    # Mostrar el botón para borrar el historial
    st.write("")  # Espacio para mejor presentación
    borrar_historial()  # Esto crea el botón "Borrar chat"

else:
    st.warning("Por favor, sube un archivo para continuar.")
