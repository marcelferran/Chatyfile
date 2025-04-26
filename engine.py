import google.generativeai as genai
import streamlit as st
import pandas as pd
import json
import os
from config import get_gemini_api_key, MODEL_NAME
from utils import parse_gemini_response # Import utility for parsing response

class ChatEngine:
    """
    Manages the interaction with the Gemini model for CSV data analysis.
    """
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initializes the ChatEngine with the dataframe and configures Gemini.
        """
        self.dataframe = dataframe
        self._configure_gemini()
        self._initialize_chat()

    def _configure_gemini(self):
        """Configures the Gemini API with the retrieved key."""
        api_key = get_gemini_api_key()
        if not api_key:
             # get_gemini_api_key already handles st.error and st.stop
             # but adding a check here ensures self.chat is not initialized with a bad key
             self.chat = None
             return
        genai.configure(api_key=api_key)


    def _initialize_chat(self):
        """
        Initializes the Gemini chat object.
        Resets the chat history when a new engine is created (new file uploaded).
        """
        if self.chat is not None: # Avoid re-initializing if key was missing
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                # Start a new chat session, history is managed in Streamlit's session_state
                # The model's internal history is reset here.
                self.chat = model.start_chat(history=[])
            except Exception as e:
                # Log the error and set chat to None
                print(f"Error initializing Gemini model: {e}") # Print to console for debugging
                st.error(f"Error al inicializar el modelo Gemini: {e}")
                self.chat = None # Ensure chat is None if model loading fails
                # st.stop() # Avoid stopping here, let the app continue with an error message


    def process_question(self, user_query: str):
        """
        Processes the user's question using the Gemini model and the loaded dataframe.
        Returns a structured response (list of dictionaries) for display.
        """
        if self.dataframe is None or self.chat is None:
            return [{"type": "text", "content": "No hay datos cargados o el motor de chat no está disponible. Por favor, sube un archivo CSV y asegúrate de que la clave API sea válida."}]

        # Prepare the prompt for the model
        # Include information about the dataframe (columns, types, sample rows)
        df_info = f"Columnas del CSV: {list(self.dataframe.columns)}\n"
        df_info += f"Tipos de datos:\n{self.dataframe.dtypes.to_string()}\n" # Use to_string() for better formatting
        # Use a smaller sample or summary for very large dataframes to keep prompt size manageable
        # Ensure to_markdown is available (requires tabulate)
        try:
             df_info += f"Primeras 5 filas:\n{self.dataframe.head().to_markdown(index=False)}\n"
        except ImportError:
             df_info += f"Primeras 5 filas:\n{self.dataframe.head().to_string()}\n"
             df_info += "Nota: Instala 'tabulate' (`pip install tabulate`) para mejor formato de tabla en el prompt.\n"


        # Instructions for the model on how to respond
        # Emphasize using the specified formats for tables and charts
        instructions = """
        Eres un asistente de chat amigable y útil experto en analizar datos CSV.
        Responde a las preguntas del usuario basándote ÚNICAMENTE en los datos proporcionados en el archivo CSV.
        Si la pregunta no se puede responder con los datos, díselo amablemente al usuario.
        Puedes responder con texto, mostrar tablas o sugerir gráficos.
        Para indicar una tabla, usa el siguiente formato EXACTO:
        <TABLE>
        {"data": [[valor1, valor2], [valor3, valor4]], "columns": ["Columna A", "Columna B"]}
        </TABLE>
        Asegúrate de que los datos de la tabla sean un subconjunto relevante y pequeño del dataframe, apropiado para mostrar.
        Para indicar un gráfico, usa el siguiente formato EXACTO:
        <CHART:tipo_de_grafico>
        {"x": "nombre_columna_x", "y": "nombre_columna_y", "title": "Título del gráfico"}
        </CHART>
        Los tipos de gráfico soportados son: bar, line, scatter.
        Asegúrate de que las columnas 'x' y 'y' existan en el dataframe y sean apropiadas para el tipo de gráfico (numéricas para y, categóricas o numéricas para x dependiendo del gráfico).
        Combina texto, tablas y gráficos según sea necesario para responder completamente.
        Para preguntas matemáticas o estadísticas, realiza los cálculos necesarios usando los datos y presenta el resultado en texto o tabla.
        Si pides un gráfico, asegúrate de que las columnas 'x' y 'y' sean válidas y existan en el dataframe.
        """

        prompt = f"{instructions}\n\nDatos del CSV:\n{df_info}\n\nPregunta del usuario: {user_query}"

        # Call the Gemini model with error handling
        try:
            # Send the message to the chat session
            response = self.chat.send_message(prompt)
            raw_response_text = response.text

            # Parse the raw response text into structured elements
            structured_response = parse_gemini_response(raw_response_text, self.dataframe) # Pass dataframe for validation

            return structured_response

        except Exception as e:
            # Catch any errors during the API call or initial response processing
            print(f"Error during Gemini API call or response processing: {e}") # Print to console for debugging
            # Return a structured error message
            return [{"type": "text", "content": f"Lo siento, hubo un error al procesar tu solicitud: {e}. Por favor, intenta de nuevo."}]

