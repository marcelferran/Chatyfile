import streamlit as st
from config import configure_genai
from layout import apply_custom_styles, show_header, show_footer
from utils import cargar_csv
from engine import ChatEngine

# Configurar API Gemini
configure_genai()

# Aplicar estilos visuales
apply_custom_styles()

# Mostrar encabezado
show_header()

# Sidebar para cargar CSV
st.sidebar.header("📂 Cargar archivo CSV")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])

# Área de interacción principal
if uploaded_file:
    df = cargar_csv(uploaded_file)
    if df is not None:
        chat_engine = ChatEngine(df)

        st.subheader("🤖 Asistente de DataFrame")

        chat_placeholder = st.container()
        input_container = st.container()

        # Inicializar estado de sesión si no existe
        if "history" not in st.session_state:
            st.session_state.history = []

        if "user_input" not in st.session_state:
            st.session_state.user_input = ""

        # Mostrar historial de mensajes
        with chat_placeholder:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.history:
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Input de nueva pregunta
        with input_container:
            user_input = st.text_input("Escribe tu pregunta aquí...", key="user_input")

            if st.button("Enviar"):
                if user_input.strip() != "":
                    response = chat_engine.process_question(user_input)
                    st.session_state.history.append({"role": "user", "content": user_input})
                    st.session_state.history.append({"role": "assistant", "content": response})
                    st.session_state.user_input = ""  # Limpiar el campo automáticamente
                    st.experimental_rerun()  # Refrescar sin errores

    else:
        st.error("❌ Error al cargar el archivo. Asegúrate de que sea un CSV válido.")
else:
    st.info("📄 Por favor carga un archivo CSV para comenzar.")

# Mostrar pie de página
show_footer()
