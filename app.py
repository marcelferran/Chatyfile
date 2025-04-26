import streamlit as st
import pandas as pd
# Import components from your layout file
from layout import setup_page_config, apply_custom_styles, show_header, show_footer
# Import our engine and utils
from engine import ChatEngine
from utils import parse_gemini_response # Import only necessary utility functions

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
# The ChatEngine class now handles the Gemini chat object internally

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
                 "content": [{"type": "text", "content": "¡Hola! He cargado tu archivo CSV. ¿En qué puedo ayudarte hoy?"}] # Welcome message as a list of elements
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
        for i, mensaje in enumerate(st.session_state.history):
            role = mensaje["role"]
            # Ensure 'content' is a list of elements, even if it's just one text element
            content_elements = mensaje.get("content", [])
            if not isinstance(content_elements, list):
                 # If somehow content is not a list (e.g., old format), wrap it
                 content_elements = [{"type": mensaje.get("type", "text"), "content": content_elements}]


            # Display content based on type
            # Note: We are now iterating through elements within a message
            # User messages are simple text, Assistant messages can be structured
            if role == "user":
                 # User messages are always text in this structure
                 # Assuming the content for user is a single text string
                 user_text_content = content_elements[0].get("content", "") if content_elements else ""
                 st.markdown(f'<div class="chat-message user-message">{user_text_content}</div>', unsafe_allow_html=True)
            elif role == "assistant":
                 # Assistant messages can contain multiple elements (text, table, plot)
                 for element in content_elements:
                    element_type = element.get("type", "text")
                    element_content = element.get("content", "")

                    if element_type == "text":
                         # Display text within the assistant message bubble
                         st.markdown(f'<div class="chat-message assistant-message">{element_content}</div>', unsafe_allow_html=True)
                    elif element_type == "dataframe":
                         # Display dataframe outside the custom message div for better rendering
                         # Add some spacing before the dataframe
                         st.markdown('<div style="margin-top: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
                         st.dataframe(element_content)
                         st.markdown('</div>', unsafe_allow_html=True)
                    elif element_type == "plot":
                         # Assuming 'content' for plot is a dictionary with plot specs
                         # We need the original dataframe to generate the plot here
                         try:
                             current_df = st.session_state.get('chat_engine').dataframe if st.session_state.get('chat_engine') else None
                             if current_df is not None:
                                 plot_data = element_content['data']
                                 plot_type = element_content['type']

                                 # Check if columns exist before plotting
                                 if plot_data['x'] in current_df.columns and plot_data['y'] in current_df.columns:
                                     # Add some spacing before the chart
                                     st.markdown('<div style="margin-top: 10px; margin-bottom: 10px;">', unsafe_allow_html=True)
                                     if plot_type == 'bar':
                                         st.bar_chart(current_df.set_index(plot_data['x'])[plot_data['y']])
                                     elif plot_type == 'line':
                                         st.line_chart(current_df.set_index(plot_data['x'])[plot_data['y']])
                                     elif plot_type == 'scatter':
                                          # Simple fallback for scatter
                                          st.line_chart(current_df.set_index(plot_data['x'])[plot_data['y']])
                                     else:
                                         st.warning(f"Tipo de gráfico no soportado para mostrar: {plot_type}")
                                     st.markdown('</div>', unsafe_allow_html=True)
                                 else:
                                     st.warning(f"Columnas '{plot_data['x']}' o '{plot_data['y']}' no encontradas en los datos para mostrar el gráfico.")
                             else:
                                  st.warning("No hay datos disponibles para mostrar el gráfico.")
                         except Exception as e:
                             st.warning(f"No se pudo mostrar el gráfico: {e}")
                             st.markdown(f'<div class="chat-message assistant-message">No se pudo mostrar el gráfico debido a un error.</div>', unsafe_allow_html=True)


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
        # Store user message as a list of text elements for consistency
        st.session_state.history.append({"role": "user", "content": [{"type": "text", "content": user_input}]})


        with st.spinner('⏳ Pensando la respuesta...'):
            # Process the question using the ChatEngine
            # The engine will use Gemini and return structured response
            respuesta_estructurada = st.session_state.chat_engine.process_question(user_input)

        # Add assistant response to history
        # respuesta_estructurada is expected to be a list of {"type": ..., "content": ...}
        st.session_state.history.append({"role": "assistant", "content": respuesta_estructurada}) # Store as a list of elements

        # Rerun the app to display the updated history
        st.rerun() # UNCOMMENTED to refresh the UI

else:
    # Display message if no file is loaded
    st.info("📂 Por favor carga un archivo CSV para comenzar.")

# --- Footer ---
show_footer() # Display footer using layout function
