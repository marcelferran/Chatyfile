import streamlit as st

# Configuraciones predeterminadas
DEFAULT_PLOT_SIZE = (12, 10)  # Tamaño por defecto de las gráficas
DEFAULT_COLOR_PALETTE = 'blues'  # Paleta de colores por defecto para las gráficas

# Función para obtener la clave de API
def get_api_key():
    # Primero verificamos si la clave está en st.secrets
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    # Luego verificamos si la clave está en st.session_state (para no pedirla cada vez)
    elif "GEMINI_API_KEY" in st.session_state:
        return st.session_state["GEMINI_API_KEY"]
    # Si no está en ninguna de las dos opciones, le pedimos al usuario que la ingrese
    else:
        api_key = st.text_input("🔑 Introduce tu GEMINI_API_KEY", type="password")
        if api_key:
            # Guardamos la API Key en st.session_state para evitar pedirla nuevamente
            st.session_state["GEMINI_API_KEY"] = api_key
        return api_key

def configure_genai(api_key):
    if api_key:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

# Función para obtener la configuración del tamaño de las gráficas y tablas
def get_graph_settings():
    # Permitir que el usuario ajuste el tamaño de las gráficas y tablas
    plot_width = st.sidebar.slider("Ancho de la gráfica", 8, 20, DEFAULT_PLOT_SIZE[0], 1)
    plot_height = st.sidebar.slider("Alto de la gráfica", 6, 20, DEFAULT_PLOT_SIZE[1], 1)
    color_palette = st.sidebar.selectbox(
        "Selecciona la paleta de colores",
        ['blues', 'grays', 'reds', 'greens', 'purples'],
        index=['blues', 'grays', 'reds', 'greens', 'purples'].index(DEFAULT_COLOR_PALETTE)
    )
    
    # Devuelve los valores seleccionados
    return (plot_width, plot_height), color_palette
