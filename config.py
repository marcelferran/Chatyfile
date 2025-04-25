import streamlit as st
import google.generativeai as genai

def configure_genai():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("❌ No se encontró la clave API en los Secrets de Streamlit.")
        st.stop()
