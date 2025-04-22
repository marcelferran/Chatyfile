import streamlit as st
import pandas as pd
from config import get_api_key, configure_genai, get_graph_settings
from layout import apply_custom_styles, show_header, show_footer, show_welcome_message, sidebar_file_uploader
from chat_engine import iniciar_chat, mostrar_historial, procesar_pregunta
from utils import mostrar_resumen_df
import plotly.express as px

st.set_page_config(
    page_title="Chatyfile",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()
show_header()
show_welcome_message()
uploaded_file = sidebar_file_uploader()
show_footer()

# Obtener la clave de la API
api_key = get_api_key()
if not api_key:
    st.warning("Por favor, introduce tu clave API para continuar.")
    st.stop()

configure_genai(api_key)

# Configuración dinámica para gráficos y tablas
plot_size, color_palette = get_graph_settings()

if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    mostrar_resumen_df(df)

    # Iniciar el chat si no ha sido iniciado
    if st.session_state.chat is None:
        iniciar_chat(df)

    mostrar_historial()

    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar", disabled=False)

    if submitted and pregunta:
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Adios.")
            st.session_state.chat = None
            st.rerun()
        else:
            procesar_pregunta(pregunta, df)
            st.rerun()

else:
    st.warning("Por favor, sube un archivo para continuar.")

# --- Modificación de la visualización de gráficas con la configuración dinámica ---
def mostrar_grafica(df, tipo_grafico="scatter"):
    # Ajustar el tamaño de la gráfica y la paleta de colores
    if tipo_grafico == "scatter":
        fig = px.scatter(df, x='columna_x', y='columna_y', color='columna_z', color_continuous_scale=color_palette)
    elif tipo_grafico == "line":
        fig = px.line(df, x='columna_x', y='columna_y', color='columna_z', color_continuous_scale=color_palette)
    elif tipo_grafico == "bar":
        fig = px.bar(df, x='columna_x', y='columna_y', color='columna_z', color_continuous_scale=color_palette)
    else:
        st.warning("Tipo de gráfico no soportado.")

    # Ajustar el tamaño de la figura
    fig.update_layout(width=plot_size[0]*100, height=plot_size[1]*100)

    # Mostrar la gráfica interactiva
    st.plotly_chart(fig)

# Llamar a la función para mostrar la gráfica según sea necesario
# Puedes colocar esto en donde necesites mostrar las gráficas
# Ejemplo:
# mostrar_grafica(df, tipo_grafico="line")
