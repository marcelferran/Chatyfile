import streamlit as st

def configure_genai(api_key):
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
