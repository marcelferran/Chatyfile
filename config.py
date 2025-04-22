import streamlit as st
import google.generativeai as genai

def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    elif "GEMINI_API_KEY" in st.session_state:
        return st.session_state["GEMINI_API_KEY"]
    else:
        api_key = st.text_input("🔑 Introduce tu GEMINI_API_KEY", type="password")
        if api_key:
            st.session_state["GEMINI_API_KEY"] = api_key
        return api_key

def configure_genai(api_key):
    genai.configure(api_key=api_key)
