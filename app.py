import streamlit as st
import pandas as pd
from engine import start_new_chat # Import the chat engine
from layout import ( # Import layout components
    setup_page_config,
    display_header,
    file_uploader_section,
    display_chat_history,
    get_user_input,
    display_sidebar_notes
)
from utils import handle_response, display_chat_elements # Import utility functions

# --- Application Setup ---
setup_page_config()
display_header()

# --- File Upload and Data Loading ---
# The file_uploader_section function now handles loading and storing in session_state
file_uploader_section()
dataframe = st.session_state.get('dataframe', None) # Retrieve dataframe from session state

# --- Initialize Chat ---
# Initialize the chat object in session state if it doesn't exist
if 'chat' not in st.session_state or st.session_state['chat'] is None:
    st.session_state['chat'] = start_new_chat()

# Initialize chat history in session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# --- Display Chat History ---
display_chat_history() # Use the layout function to display history

# --- User Input and Model Interaction ---
user_query = get_user_input() # Get user input from the layout function

if user_query:
    # Add user query to chat history
    st.session_state['chat_history'].append({'role': 'user', 'content': [('text', user_query)]})

    # Display user query immediately
    with st.chat_message("user"):
        st.write(user_query)

    # Check if dataframe is loaded before interacting with the model
    if dataframe is not None:
        # Prepare prompt for the model
        df_info = f"Columnas: {list(dataframe.columns)}\n"
        df_info += f"Tipos de datos:\n{dataframe.dtypes}\n"
        # Use a smaller sample or summary for very large dataframes to keep prompt size manageable
        df_info += f"Primeras 5 filas:\n{dataframe.head().to_markdown(index=False)}\n"

        # Instructions for the model (can be moved to config or a separate prompt file if it grows)
        instructions = """
        Eres un asistente de chat amigable y útil experto en analizar datos CSV.
        Responde a las preguntas del usuario basándote ÚNICAMENTE en los datos proporcionados en el archivo CSV.
        Si la pregunta no se puede responder con los datos, díselo amablemente al usuario.
        Puedes responder con texto, mostrar tablas o sugerir gráficos.
        Para indicar una tabla, usa el siguiente formato:
        <TABLE>
        {"data": [[valor1, valor2], [valor3, valor4]], "columns": ["Columna A", "Columna B"]}
        </TABLE>
        Asegúrate de que los datos de la tabla sean un subconjunto relevante del dataframe.
        Para indicar un gráfico, usa el siguiente formato:
        <CHART:tipo_de_grafico>
        {"x": "nombre_columna_x", "y": "nombre_columna_y", "title": "Título del gráfico"}
        </CHART>
        Los tipos de gráfico soportados son: bar, line, scatter.
        Asegúrate de que las columnas 'x' y 'y' existan en el dataframe y sean apropiadas para el tipo de gráfico.
        Combina texto, tablas y gráficos según sea necesario para responder completamente.
        Para preguntas matemáticas o estadísticas, realiza los cálculos necesarios usando los datos.
        """

        prompt = f"{instructions}\n\nDatos del CSV:\n{df_info}\n\nPregunta del usuario: {user_query}"

        # Send message to Gemini model
        try:
            # Use the chat object from session state
            chat_session = st.session_state.get('chat')
            if chat_session:
                response = chat_session.send_message(prompt)
                response_text = response.text

                # Process the response using the utility function
                output_elements = handle_response(response_text, dataframe)

                # Add assistant response to chat history
                st.session_state['chat_history'].append({'role': 'assistant', 'content': output_elements})

                # Display assistant response
                with st.chat_message("assistant"):
                    display_chat_elements(output_elements, dataframe) # Use utility function to display

            else:
                 st.error("Error: El objeto de chat no está inicializado.")
                 st.session_state['chat_history'].append({'role': 'assistant', 'content': [('text', "Error interno: el chat no está listo.")]})
                 with st.chat_message("assistant"):
                      st.write("Error interno: el chat no está listo.")

        except Exception as e:
            st.error(f"Error al comunicarse con el modelo Gemini: {e}")
            st.session_state['chat_history'].append({'role': 'assistant', 'content': [('text', f"Lo siento, hubo un error al procesar tu solicitud: {e}")]})
            with st.chat_message("assistant"):
                 st.write(f"Lo siento, hubo un error al procesar tu solicitud: {e}")

    else:
        # If no dataframe loaded, inform the user
        st.warning("Por favor, sube un archivo CSV para empezar a chatear.")
        st.session_state['chat_history'].append({'role': 'assistant', 'content': [('text', "Por favor, sube un archivo CSV para empezar a chatear.")]})
        with st.chat_message("assistant"):
             st.write("Por favor, sube un archivo CSV para empezar a chatear.")


# --- Sidebar Notes ---
display_sidebar_notes() # Display notes using the layout function
