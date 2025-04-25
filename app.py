import streamlit as st
from utils import cargar_csv
from engine import ChatEngine
from config import configure_genai
from layout import apply_custom_styles, show_header, show_footer


# Configurar API
configure_genai()

# Aplicar estilos
apply_custom_styles()

# Mostrar encabezado
show_header()

# Sidebar para cargar CSV
st.sidebar.header("📂 Cargar archivo CSV")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])

# Área del chat
if uploaded_file:
    df = cargar_csv(uploaded_file)
    if df is not None:
        chat_engine = ChatEngine(df)

        st.subheader("🤖 Asistente de DataFrame")

        chat_placeholder = st.container()
        input_container = st.container()

        if "history" not in st.session_state:
            st.session_state.history = []

        with chat_placeholder:
            for message in st.session_state.history:
                st.write(message)

        with input_container:
            user_input = st.text_input("Escribe tu pregunta aquí...")

            if st.button("Enviar"):
                if user_input.strip() != "":
                    response = chat_engine.process_question(user_input)
                    st.session_state.history.append(f"🤔 Tú: {user_input}")
                    st.session_state.history.append(f"💬 Asistente:\n{response}")
                    st.experimental_rerun()

    else:
        st.error("❌ Error al cargar el archivo. Asegúrate que sea un CSV válido.")
else:
    st.info("📄 Por favor carga un archivo CSV para comenzar.")

# Mostrar pie de página
show_footer()
