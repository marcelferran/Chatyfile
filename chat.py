import streamlit as st
from config import load_config
from chat_engine import GeminiChat
from utils import load_file, execute_code
from layout import render_header, render_sidebar, render_footer, render_data_summary

# === CONFIGURACIÓN INICIAL ===
load_config()
render_header()

# === CARGAR ARCHIVO DESDE SIDEBAR ===
uploaded_file = render_sidebar()

# === VALIDAR API KEY ===
if "GEMINI_API_KEY" not in st.session_state:
    api_key = st.text_input("🔑 Introduce tu GEMINI_API_KEY", type="password")
    if api_key:
        st.session_state["GEMINI_API_KEY"] = api_key
    else:
        st.warning("Por favor, introduce tu clave API para continuar.")
        st.stop()
else:
    api_key = st.session_state["GEMINI_API_KEY"]

# === PROCESAR ARCHIVO SUBIDO ===
if uploaded_file:
    df = load_file(uploaded_file)
    render_data_summary(df)

    # Crear instancia del chat si no existe
    if "chat" not in st.session_state or st.session_state.chat is None:
        st.session_state.chat = GeminiChat(api_key, df.columns)

    # Mostrar historial
    for msg in st.session_state.chat.history:
        st.write(msg)

    # Formulario de preguntas
    with st.form("pregunta_form", clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="input_pregunta")
        enviar = st.form_submit_button("Enviar")

    if enviar and pregunta:
        if pregunta.lower() == "salir":
            st.session_state.chat.reset_chat()
            st.session_state.chat = None
            st.rerun()
        else:
            code = st.session_state.chat.send_question(pregunta, df.columns)
            output, fig = execute_code(code, df)
            if output:
                st.code(output)
            if fig:
                st.pyplot(fig)

# === PIE DE PÁGINA ===
render_footer()
