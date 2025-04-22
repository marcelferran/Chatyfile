import streamlit as st
import pandas as pd
from config import get_api_key, configure_genai
from layout import apply_custom_styles, show_header, show_footer, show_welcome_message, sidebar_file_uploader
from chat_engine import iniciar_chat, mostrar_historial, procesar_pregunta
from utils import mostrar_resumen_df

st.set_page_config(
    page_title="Chatyfile",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()
show_header()
show_welcome_message()
uploaded_file = sidebar_file_uploader()
show_footer()

api_key = get_api_key()
if not api_key:
    st.warning("Por favor, introduce tu clave API para continuar.")
    st.stop()

configure_genai(api_key)

if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    mostrar_resumen_df(df)

    if st.session_state.chat is None:
        iniciar_chat(df)

    mostrar_historial()

    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar", disabled=False)

    if submitted and pregunta:
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Adios.")
            st.session_state.chat = None
            st.rerun()
        else:
            procesar_pregunta(pregunta, df)
            st.rerun()
else:
    st.warning("Por favor, sube un archivo para continuar.")
