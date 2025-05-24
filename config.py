import streamlit as st

def configure_genai():
    try:
        import google.generativeai as genai
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except KeyError:
        st.error("❌ No se encontró la clave API en `st.secrets`. Por favor, configura `GOOGLE_API_KEY` en los secrets de Streamlit")
        st.stop()
