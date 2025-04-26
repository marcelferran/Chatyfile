import google.generativeai as genai
import streamlit as st
from config import get_gemini_api_key, MODEL_NAME

# --- Configure Gemini API ---
def configure_gemini():
    """Configures the Gemini API with the retrieved key."""
    api_key = get_gemini_api_key()
    genai.configure(api_key=api_key)

# --- Initialize Gemini Model and Chat ---
def get_gemini_model():
    """
    Initializes and returns the Gemini GenerativeModel.
    Handles potential errors during model loading.
    """
    configure_gemini()
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        return model
    except Exception as e:
        st.error(f"Error al cargar el modelo {MODEL_NAME}: {e}")
        st.stop()
        return None # Should not reach here due to st.stop()

def start_new_chat():
    """Starts a new chat session with the configured model."""
    model = get_gemini_model()
    if model:
        return model.start_chat(history=[])
    return None
