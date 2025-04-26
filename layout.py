import streamlit as st
import pandas as pd
from utils import display_chat_elements # Import the display function

def setup_page_config():
    """Sets up the basic Streamlit page configuration."""
    st.set_page_config(page_title="Chat con tu CSV", layout="wide")

def display_header():
    """Displays the application header and description."""
    st.title("📊 Chat con tu Archivo CSV")
    st.markdown("""
        Sube un archivo CSV y haz preguntas sobre tus datos.
        Puedo responder preguntas, mostrar tablas y generar gráficos básicos.
    """)

def file_uploader_section():
    """Handles the CSV file upload and returns the dataframe."""
    uploaded_file = st.file_uploader("Sube tu archivo CSV aquí", type="csv")
    dataframe = None
    if uploaded_file is not None:
        try:
            dataframe = pd.read_csv(uploaded_file)
            st.success("Archivo CSV cargado exitosamente.")
            st.subheader("Vista previa de los datos:")
            st.dataframe(dataframe.head())
            # Store dataframe in session state
            st.session_state['dataframe'] = dataframe
        except Exception as e:
            st.error(f"Error al leer el archivo CSV: {e}")
            st.session_state['dataframe'] = None # Clear invalid dataframe
    else:
        # Clear dataframe from session state if no file is uploaded
        if 'dataframe' in st.session_state:
            del st.session_state['dataframe']

    return dataframe

def display_chat_history():
    """Displays the chat history from the session state."""
    st.subheader("Chat con tus datos")
    # Ensure chat_history exists in session state
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    for message in st.session_state['chat_history']:
        role = "user" if message['role'] == 'user' else "assistant"
        with st.chat_message(role):
            # Use the utility function to display content
            # Pass the current dataframe from session state for chart generation
            current_df = st.session_state.get('dataframe', None)
            display_chat_elements(message['content'], current_df)

def get_user_input():
    """Gets user input from the chat input box."""
    return st.chat_input("Haz una pregunta sobre tus datos...")

def display_sidebar_notes():
    """Displays notes in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.markdown("Este es el código base. Cuando tengas tu archivo de layout, podemos integrarlo aquí.")
    st.sidebar.markdown("El layout puede controlar la disposición de los elementos (barra lateral, columnas, etc.).")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cómo ejecutar la aplicación:")
    st.sidebar.markdown("1. Guarda los archivos (`app.py`, `engine.py`, `utils.py`, `layout.py`, `config.py`, `requirements.txt`, `readme.md`).")
    st.sidebar.markdown("2. Asegúrate de tener las dependencias instaladas (`pip install -r requirements.txt`).")
    st.sidebar.markdown("3. Configura tu clave de API de Gemini (`GEMINI_API_KEY`) como variable de entorno o en `st.secrets.toml`.")
    st.sidebar.markdown("4. Ejecuta la aplicación desde tu terminal: `streamlit run app.py`")
    st.sidebar.markdown("5. Abre la URL que aparece en tu terminal.")

