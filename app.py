import streamlit as st
import pandas as pd
from engine import ChatEngine
from layout import apply_custom_styles, show_header, show_footer

# Configuración de la página
st.set_page_config(page_title="Chatyfile", page_icon="📄", layout="wide")

# Aplicar estilos
apply_custom_styles()

# Mostrar encabezado
show_header()

# Inicializar variables de sesión
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None
if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = ""

# Sidebar para cargar CSV
st.sidebar.header("📂 Cargar archivo CSV")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.chat_engine = ChatEngine(df)
    st.session_state.history = []  # Reiniciar historial
    st.success(f"✅ Archivo '{uploaded_file.name}' cargado correctamente.")

# Mostrar pie de página
def main_chat_area():
    chat_placeholder = st.container()

    with chat_placeholder:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
            elif message["role"] == "assistant":
                if message["type"] == "text":
                    st.markdown(f'<div class="chat-message assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
                elif message["type"] == "dataframe":
                    st.dataframe(message["content"])
                elif message["type"] == "plot":
                    st.image(message["content"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Si ya cargó el CSV
if st.session_state.chat_engine is not None:
    main_chat_area()

    # Input siempre abajo
    with st.form(key="user_input_form"):
        user_input = st.text_input("Escribe tu pregunta aquí:", value="", key="input_text")
        submitted = st.form_submit_button("Enviar")

    if submitted and user_input.strip() != "":
        # Guardar input pendiente
        st.session_state.pending_user_input = user_input
        st.experimental_rerun()

    if st.session_state.pending_user_input:
        pregunta = st.session_state.pending_user_input
        with st.spinner('⏳ Pensando la respuesta...'):
            respuesta = st.session_state.chat_engine.process_question(pregunta)

        st.session_state.history.append({"role": "user", "content": pregunta})
        st.session_state.history.append({"role": "assistant", "type": respuesta["type"], "content": respuesta["content"]})

        # Limpiar el input pendiente
        st.session_state.pending_user_input = ""

        # Volver a renderizar para mostrar inmediatamente
        st.experimental_rerun()

else:
    st.info("📂 Por favor carga un archivo CSV para comenzar.")

show_footer()
