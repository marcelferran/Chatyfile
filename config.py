import streamlit as st

# Configuraciones predeterminadas
DEFAULT_PLOT_SIZE = (8, 6)  # Tamaño por defecto de las gráficas
DEFAULT_COLOR_PALETTE = 'blues'  # Paleta de colores por defecto para las gráficas

def configure_genai(api_key):
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
