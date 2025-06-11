#app.py

import pandas as pd
import numpy as np
import streamlit as st
from config import configure_genai
from utils import mostrar_resumen_df
from chat_engine import iniciar_chat, mostrar_historial, procesar_pregunta
from layout import apply_custom_styles, show_header, show_welcome_message, sidebar_file_uploader, show_footer

# Configuración de la página
st.set_page_config(
    page_title="Chatyfile",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Aplicar estilos y mostrar elementos de diseño
apply_custom_styles()
show_header()

# Contenedor principal para el contenido
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    show_welcome_message()
    uploaded_file = sidebar_file_uploader()

    # Configurar la API de Google Generative AI usando la clave desde secrets
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        configure_genai()
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
        # Mostrar resumen con estilo
        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
        mostrar_resumen_df(df)
        st.markdown('</div>', unsafe_allow_html=True)

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
                
    else:
        st.warning("Por favor, sube un archivo para continuar.")
    st.markdown('</div>', unsafe_allow_html=True)

show_footer()
