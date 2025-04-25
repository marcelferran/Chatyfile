import streamlit as st
import pandas as pd
from engine import ChatEngine
from layout import apply_custom_styles, show_header, show_footer

# Configurar la página
st.set_page_config(page_title="Chatyfile", page_icon="📄", layout="wide")

# Aplicar estilos
apply_custom_styles()

# Mostrar encabezado
show_header()

# Inicializar sesión
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None

# Sidebar para cargar CSV
st.sidebar.header("📂 Cargar archivo CSV")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.chat_engine = ChatEngine(df)
    st.success(f"✅ Archivo '{uploaded_file.name}' cargado correctamente.")

if st.session_state.chat_engine is None:
    st.info("📂 Por favor carga un archivo CSV para comenzar.")
else:
    # Historial
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

    # Input
    with st.form(key="input_form", clear_on_submit=True):
        user_input = st.text_input("Escribe tu pregunta aquí...")
        submitted = st.form_submit_button("Enviar")

        if submitted and user_input.strip() != "":
            with st.spinner('⏳ Pensando la respuesta...'):
                respuesta = st.session_state.chat_engine.process_question(user_input)

            st.session_state.history.append({"role": "user", "content": user_input})
            st.session_state.history.append({"role": "assistant", "type": respuesta["type"], "content": respuesta["content"]})

# Footer
show_footer()
