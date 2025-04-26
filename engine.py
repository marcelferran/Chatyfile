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
        # Initialize self.chat to None by default
        self.chat = None
        # Configure Gemini API - this will get the key and set it internally if successful
        self._configure_gemini()
        # Always attempt to initialize the chat after configuration
        # The _initialize_chat method will handle potential errors if configuration failed
        self._initialize_chat()


    def _configure_gemini(self):
        """Configures the Gemini API with the retrieved key."""
        api_key = get_gemini_api_key()
        # get_gemini_api_key already handles st.error and st.stop if the key is missing.
        # If the app continues past get_gemini_api_key, we assume the key was found
        # or handled appropriately by config.py.
        try:
            # This call configures the API internally.
            # If api_key is None or invalid, configure might raise an error depending on the library version.
            genai.configure(api_key=api_key)
            # If configuration is successful, the API is ready for use.
            # self.chat will be initialized in _initialize_chat.
        except Exception as e:
            print(f"Error configuring Gemini API: {e}") # Print to console for debugging
            st.error(f"Error al configurar la API de Gemini: {e}")
            # If configuration fails, self.chat remains None, which is handled in process_question.
            self.chat = None # Ensure chat is None on configuration failure


    def _initialize_chat(self):
        """
        Initializes the Gemini chat object.
        Ensures self.chat is assigned a value (chat object or None).
        This method is called after _configure_gemini.
        """
        # Attempt to initialize the model and chat.
        # If genai.configure failed, this might also fail, and the exception is caught.
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            # Start a new chat session. The model's internal history is reset here.
            self.chat = model.start_chat(history=[])
            # print("DEBUG: Chat object initialized successfully.") # Debug line removed
        except Exception as e:
            # Catch any errors during model loading or chat start
            print(f"Error initializing Gemini model or chat: {e}") # Print to console for debugging
            st.error(f"Error al inicializar el modelo Gemini o el chat: {e}")
            self.chat = None # Ensure chat is None if initialization fails


    def process_question(self, user_query: str):
        """
        Processes the user's question using the Gemini model and the loaded dataframe.
        Returns a structured response (list of dictionaries) for display.
        """
        # print("DEBUG: process_question called.") # Debug line removed

        # Robustly check if the chat object is available before using it
        if self.dataframe is None or self.chat is None:
            # print("DEBUG: Dataframe or chat is None.") # Debug line removed
            return [{"type": "text", "content": "No hay datos cargados o el motor de chat no está disponible. Por favor, sube un archivo CSV y asegúrate de que la clave API sea válida y el modelo se inicialice correctamente."}]

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

        # print("DEBUG: Prompt preparado.") # Debug line removed
        # print(f"DEBUG: Prompt: {prompt[:500]}...") # Debug line removed


        # Call the Gemini model with error handling
        try:
            # print("DEBUG: Calling self.chat.send_message...") # Debug line removed
            # Send the message to the chat session
            response = self.chat.send_message(prompt)
            # print("DEBUG: Received response from send_message.") # Debug line removed

            raw_response_text = response.text
            # print(f"DEBUG: Raw response text: {raw_response_text[:500]}...") # Debug line removed

            # print("DEBUG: Calling parse_gemini_response...") # Debug line removed
            # Parse the raw response text into structured elements
            structured_response = parse_gemini_response(raw_response_text, self.dataframe) # Pass dataframe for validation
            # print("DEBUG: parse_gemini_response finished.") # Debug line removed
            # print("DEBUG: Structured response:") # Debug line removed
            # print(structured_response) # Debug line removed

            return structured_response

        except Exception as e:
            # Catch any errors during the API call or initial response processing
            print(f"Error during Gemini API call or response processing: {e}") # Print to console for debugging
            st.error(f"Error al procesar tu solicitud: {e}. Por favor, intenta de nuevo.") # Display error in Streamlit
            # print(f"DEBUG: Exception caught in process_question: {e}") # Debug line removed
            # Return a structured error message
            return [{"type": "text", "content": f"Lo siento, hubo un error al procesar tu solicitud: {e}. Por favor, intenta de nuevo."}]
