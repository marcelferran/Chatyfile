import streamlit as st
import pandas as pd
from utils import display_chat_elements # Import the display function

def setup_page_config():
    """Sets up the basic Streamlit page configuration."""
    st.set_page_config(page_title="Chat con tu CSV", layout="wide")

    # Inject custom CSS for styling
    # Note: Centering the main content area precisely can be tricky with Streamlit's default structure.
    # This CSS targets the main block container and attempts to apply styling.
    # The background color and link color (for accents like the file uploader) are set here.
    st.markdown("""
        <style>
        /* General body styling */
        body {
            background-color: #f0f2f6; /* Light gray background */
            color: #333; /* Default text color */
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        }

        /* Main content container styling */
        .stApp > header {
             background-color: transparent; /* Make header background transparent */
        }

        .stApp {
            background-color: #f0f2f6; /* Ensure app background is light gray */
        }

        .stApp > div:first-child {
            /* This targets the main block container where content is added */
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Attempt to center the main content and limit its width */
        /* This requires targeting Streamlit's internal classes, which can be fragile */
        .st-emotion-cache-1cypcdb { /* Example class for the main block container - may change with Streamlit updates */
            max-width: 800px; /* Limit width */
            margin-left: auto;
            margin-right: auto;
            background-color: #ffffff; /* White background for the content area */
            padding: 2rem;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Styling for the file uploader button */
        .st-emotion-cache-19rxjxo.ef3psqc11 { /* Example class for the file uploader button - may change */
            background-color: #0077b5; /* LinkedIn Blue */
            color: white;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .st-emotion-cache-19rxjxo.ef3psqc11:hover {
            background-color: #005582; /* Darker blue on hover */
        }

        /* Styling for Streamlit buttons in general for a modern look */
        .stButton>button {
            background-color: #0077b5; /* LinkedIn Blue */
            color: white;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s ease;
            border: none; /* Remove default border */
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .stButton>button:hover {
            background-color: #005582; /* Darker blue on hover */
        }

        /* Styling for chat messages */
        .stChatMessage {
            background-color: #e9ecef; /* Light gray for messages */
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .stChatMessage>.stMarkdown {
            color: #333; /* Text color within messages */
        }

        /* Styling for tables */
        .dataframe {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
            font-size: 0.9rem;
        }

        .dataframe th, .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        .dataframe th {
            background-color: #0077b5; /* LinkedIn Blue */
            color: white;
        }

        .dataframe tr:nth-child(even){background-color: #f2f2f2;}

        /* Styling for chat input */
        .st-emotion-cache-1cypcdb .stTextInput > div > div > input {
             border-radius: 0.5rem;
             border: 1px solid #ced4da;
             padding: 0.75rem 1rem;
        }


        </style>
        """, unsafe_allow_html=True)


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
