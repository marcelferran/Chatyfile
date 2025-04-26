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

# Sidebar para cargar CSV
st.sidebar.header("📂 Cargar archivo CSV")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])

# Si cargamos un CSV
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state.chat_engine = ChatEngine(df)
    st.session_state.history = []  # Reiniciar historial
    st.success(f"✅ Archivo '{uploaded_file.name}' cargado correctamente.")

# Función para mostrar el historial del chat
def mostrar_historial():
    chat_placeholder = st.container()
    with chat_placeholder:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for mensaje in st.session_state.history:
            if mensaje["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">{mensaje["content"]}</div>', unsafe_allow_html=True)
            elif mensaje["role"] == "assistant":
                if mensaje["type"] == "text":
                    st.markdown(f'<div class="chat-message assistant-message">{mensaje["content"]}</div>', unsafe_allow_html=True)
                elif mensaje["type"] == "dataframe":
                    st.dataframe(mensaje["content"])
                elif mensaje["type"] == "plot":
                    st.image(mensaje["content"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# Si ya cargamos un archivo
if st.session_state.chat_engine is not None:
    mostrar_historial()

    # Input para nueva pregunta
    with st.form(key="input_form", clear_on_submit=True):
        user_input = st.text_input("Escribe tu pregunta aquí...")
        submitted = st.form_submit_button("Enviar")

    if submitted and user_input.strip() != "":
        with st.spinner('⏳ Pensando la respuesta...'):
            respuesta = st.session_state.chat_engine.process_question(user_input)

        # Agregar al historial
        st.session_state.history.append({"role": "user", "content": user_input})
        st.session_state.history.append({"role": "assistant", "type": respuesta["type"], "content": respuesta["content"]})

        # Volver a mostrar historial actualizado
        mostrar_historial()
else:
    st.info("📂 Por favor carga un archivo CSV para comenzar.")

# Mostrar pie de página
show_footer()
