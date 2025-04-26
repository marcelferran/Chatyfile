import streamlit as st
import pandas as pd
# Import components from your layout file
from layout import setup_page_config, apply_custom_styles, show_header, show_footer
# Import our engine and utils
from engine import ChatEngine
from utils import parse_gemini_response, display_message_content # Import utility functions

# --- Application Setup ---
setup_page_config() # Set page config using layout function
apply_custom_styles() # Apply custom CSS styles

# --- Header ---
show_header() # Display header using layout function

# --- Initialize Session State ---
if "history" not in st.session_state:
    st.session_state.history = []
if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None
# Initialize chat object from engine if not exists
if 'chat' not in st.session_state or st.session_state['chat'] is None:
     # ChatEngine will handle the initialization of the Gemini chat object internally
     # We don't need a separate 'chat' key in session_state here anymore,
     # as it's managed by the ChatEngine instance.
     pass # ChatEngine will be created upon file upload

# --- Sidebar for CSV Upload ---
st.sidebar.header("📂 Cargar archivo CSV")
uploaded_file = st.sidebar.file_uploader("Selecciona un archivo CSV", type=["csv"])

# Handle file upload
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        # Initialize ChatEngine with the dataframe
        st.session_state.chat_engine = ChatEngine(df)
        st.session_state.history = []  # Reset history on new file upload
        st.success(f"✅ Archivo '{uploaded_file.name}' cargado correctamente.")
        # Add a welcome message from the assistant
        if not st.session_state.history:
             st.session_state.history.append({
                 "role": "assistant",
                 "type": "text",
                 "content": "¡Hola! He cargado tu archivo CSV. ¿En qué puedo ayudarte hoy?"
             })
    except Exception as e:
        st.error(f"Error al leer el archivo CSV: {e}")
        st.session_state.chat_engine = None # Clear engine if file reading fails
        st.session_state.history = [] # Clear history on error


# --- Function to display chat history ---
def mostrar_historial():
    """Displays the chat history using custom CSS classes."""
    # Use a container to hold the chat messages for scrolling
    chat_placeholder = st.container()
    with chat_placeholder:
        # Use the custom chat-container div
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for mensaje in st.session_state.history:
            role = mensaje["role"]
            content_type = mensaje.get("type", "text") # Default to text if type is missing
            content = mensaje["content"]

            # Use custom chat-message divs based on role
            message_class = "user-message" if role == "user" else "assistant-message"

            # Display content based on type
            if content_type == "text":
                 st.markdown(f'<div class="chat-message {message_class}">{content}</div>', unsafe_allow_html=True)
            elif content_type == "dataframe":
                 # Display dataframe outside the custom message div for better rendering
                 st.dataframe(content)
            elif content_type == "plot":
                 # Assuming 'content' for plot is image data or path
                 # You might need to adjust this based on how your engine generates plots
                 try:
                     st.image(content, use_container_width=True)
                 except Exception as e:
                     st.warning(f"No se pudo mostrar el gráfico: {e}")
                     st.markdown(f'<div class="chat-message assistant-message">No se pudo mostrar el gráfico.</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True) # Close chat-container div


# --- Main Content Area ---
# If a file is loaded, display chat history and input form
if st.session_state.chat_engine is not None:
    mostrar_historial()

    # Input for new question using a form at the bottom
    # Use a container for the input form to apply styling if needed
    # The 'input-container' class from layout.py is intended for this
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    with st.form(key="input_form", clear_on_submit=True):
        user_input = st.text_input("Escribe tu pregunta aquí...")
        submitted = st.form_submit_button("Enviar")
    st.markdown('</div>', unsafe_allow_html=True) # Close input-container div


    if submitted and user_input.strip() != "":
        # Add user query to history immediately
        st.session_state.history.append({"role": "user", "content": user_input})

        with st.spinner('⏳ Pensando la respuesta...'):
            # Process the question using the ChatEngine
            # The engine will use Gemini and return structured response
            respuesta_estructurada = st.session_state.chat_engine.process_question(user_input)

        # Add assistant response to history
        # respuesta_estructurada is expected to be a list of {"type": ..., "content": ...}
        st.session_state.history.append({"role": "assistant", "content": respuesta_estructurada}) # Store as a list of elements

        # Rerun the app to display the updated history
        st.rerun() # Use st.rerun() to refresh and show new messages

else:
    # Display message if no file is loaded
    st.info("📂 Por favor carga un archivo CSV para comenzar.")

# --- Footer ---
show_footer() # Display footer using layout function

