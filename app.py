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

# Área principal
if uploaded_file:
    df = cargar_csv(uploaded_file)
    if df is not None:
        chat_engine = ChatEngine(df)

        st.subheader("🤖 Asistente de DataFrame")

        chat_placeholder = st.container()
        input_container = st.container()

        # Inicializar historial en session_state
        if "history" not in st.session_state:
            st.session_state.history = []

        if "pending_user_input" not in st.session_state:
            st.session_state.pending_user_input = None

        # Mostrar historial anterior
        with chat_placeholder:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.history:
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message">{message["content"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Formulario para nueva pregunta
        with input_container:
            with st.form(key="input_form", clear_on_submit=True):
                user_input = st.text_input("Escribe tu pregunta aquí...")
                submitted = st.form_submit_button("Enviar")

                if submitted and user_input.strip() != "":
                    # Guardar pregunta pendiente en session_state
                    st.session_state.pending_user_input = user_input

        # Procesar fuera del form
        if st.session_state.pending_user_input:
            pregunta = st.session_state.pending_user_input
            respuesta = chat_engine.process_question(pregunta)

            # Guardar en historial
            st.session_state.history.append({"role": "user", "content": pregunta})
            st.session_state.history.append({"role": "assistant", "content": respuesta})

            # Limpiar input pendiente
            st.session_state.pending_user_input = None

            # Recargar para mostrar nueva respuesta
            st.experimental_rerun()

    else:
        st.error("❌ Error al cargar el archivo. Asegúrate de que sea un CSV válido.")
else:
    st.info("📄 Por favor carga un archivo CSV para comenzar.")

# Mostrar pie de página
show_footer()
