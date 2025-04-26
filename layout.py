import streamlit as st
import pandas as pd
from utils import display_chat_elements # Import the display function

def setup_page_config():
    """Sets up the basic Streamlit page configuration and injects custom CSS."""
    st.set_page_config(page_title="Chat con tu CSV", layout="wide")

    # Inject custom CSS for styling
    # Using the CSS block provided by the user.
    # If styling still doesn't apply, the CSS class names below
    # might not match the ones in your specific Streamlit environment.
    # Use browser developer tools (F12) to inspect elements and
    # replace the class names in this CSS block if needed.

    st.markdown("""
        <style>
        /* General body and app container styling */
        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; /* Modern font */
            background-color: #f0f2f6; /* Light gray background */
            color: #333; /* Default text color */
        }

        .stApp {
            background-color: #f0f2f6; /* Ensure app background is light gray */
        }

        /* Header styling */
        .stApp > header {
             background-color: transparent; /* Make header background transparent */
             color: #0077b5; /* LinkedIn Blue for header text */
             padding: 1rem;
        }

        /* Main content container styling */
        /* This targets the primary block container where most content resides */
        .css-1cypcdb { /* EXAMPLE CLASS NAME - FIND THE REAL ONE WITH F12 IF NEEDED */
            max-width: 800px; /* Limit width for centering */
            margin-left: auto;
            margin-right: auto;
            background-color: #ffffff; /* White background for the content area */
            padding: 2rem;
            border-radius: 12px; /* More rounded corners */
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1); /* Softer shadow */
            margin-top: 2rem; /* Add some space from the top */
            margin-bottom: 2rem; /* Add some space at the bottom */
        }

        /* Specific styling for the file uploader button */
        /* Targeting the button-like part of the file uploader */
        .css-19rxjxo.ef3psqc11 > div > button { /* EXAMPLE SELECTOR - FIND THE REAL ONE WITH F12 IF NEEDED */
            background-color: #0077b5; /* LinkedIn Blue */
            color: white;
            border-radius: 8px; /* Rounded corners */
            padding: 0.75rem 1.5rem; /* More padding */
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.1s ease;
            border: none; /* Remove default border */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .css-19rxjxo.ef3psqc11 > div > button:hover {
            background-color: #005582; /* Darker blue on hover */
            transform: translateY(-2px); /* Slight lift effect */
        }

         /* Styling for general Streamlit buttons */
        .stButton>button {
            background-color: #0077b5; /* LinkedIn Blue */
            color: white;
            border-radius: 8px; /* Rounded corners */
            padding: 0.75rem 1.5rem; /* More padding */
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.1s ease;
            border: none; /* Remove default border */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .stButton>button:hover {
            background-color: #005582; /* Darker blue on hover */
            transform: translateY(-2px); /* Slight lift effect */
        }


        /* Styling for chat messages */
        /* The data-testid selector is more stable, but check if .stChatMessage itself is correct */
        .stChatMessage { /* Check if this base class is correct */
            background-color: #e9ecef; /* Light gray for messages */
            border-radius: 10px; /* Rounded corners */
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); /* Subtle shadow */
        }

        .stChatMessage[data-testid="stChatMessage"][data-message-role="user"] {
             background-color: #cfe2ff; /* Light blue for user messages */
             text-align: right; /* Align user text to the right */
             border-bottom-right-radius: 2px; /* Tail effect */
        }

         .stChatMessage[data-testid="stChatMessage"][data-message-role="assistant"] {
             background-color: #e9ecef; /* Light gray for assistant messages */
             text-align: left; /* Align assistant text to the left */
             border-bottom-left-radius: 2px; /* Tail effect */
        }


        .stChatMessage>.stMarkdown {
            color: #333; /* Text color within messages */
        }

        /* Styling for tables within messages */
        .stChatMessage .dataframe {
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
            font-size: 0.9rem;
            border-radius: 8px; /* Rounded corners for table */
            overflow: hidden; /* Ensures corners are rounded */
        }

        .stChatMessage .dataframe th, .stChatMessage .dataframe td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }

        .stChatMessage .dataframe th {
            background-color: #0077b5; /* LinkedIn Blue */
            color: white;
            font-weight: bold;
        }

        .stChatMessage .dataframe tr:nth-child(even){background-color: #f2f2f2;}

        /* Styling for chat input */
        /* *** REPLACE '.css-1cypcdb .stTextInput > div > div > input' BELOW with the actual selector for the chat input *** */
        .css-1cypcdb .stTextInput > div > div > input { /* EXAMPLE SELECTOR - FIND THE REAL ONE WITH F12 IF NEEDED */
             border-radius: 8px; /* Rounded corners */
             border: 1px solid #ced4da;
             padding: 0.75rem 1rem;
             box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
             transition: border-color 0.2s ease;
        }

        .css-1cypcdb .stTextInput > div > div > input:focus {
             border-color: #0077b5; /* LinkedIn Blue on focus */
             outline: none; /* Remove default outline */
             box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05), 0 0 0 0.2rem rgba(0, 119, 181, 0.25);
        }

        /* Adjust chat input container padding */
        /* *** REPLACE '.css-1cypcdb .css-1gh52kc' BELOW with the actual selector for the chat input container if needed *** */
        .css-1cypcdb .css-1gh52kc { /* EXAMPLE SELECTOR - FIND THE REAL ONE WITH F12 IF NEEDED */
            padding-bottom: 1rem; /* Add padding below the input */
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

