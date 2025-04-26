import os
import streamlit as st

# --- Configuration variables ---
MODEL_NAME = "gemini-2.0-flash"

# --- API Key Handling ---
def get_gemini_api_key():
    """
    Retrieves the Gemini API key from environment variables or Streamlit secrets.
    Exits the application if the key is not found.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except KeyError:
            st.error("Error: No se encontró la clave de API de Gemini.")
            st.markdown("Por favor, añade tu clave de API de Gemini como variable de entorno `GEMINI_API_KEY` o en los secretos de Streamlit Cloud (`st.secrets`).")
            st.stop() # Detiene la ejecución si no hay clave
    return api_key

