import streamlit as st
import pandas as pd
from engine import Engine

# Configuración de la página
st.set_page_config(page_title="Chatyfile - Asistente CSV", page_icon="🤖", layout="wide")

# Estilos generales (colores azul y gris claro)
st.markdown("""<style>
body { background-color: #F5F7FA; }
</style>""", unsafe_allow_html=True)

# Inicializar estado
if "history" not in st.session_state:
    st.session_state.history = []
if "engine" not in st.session_state:
    st.session_state.engine = Engine()
if "file_name" not in st.session_state:
    st.session_state.file_name = None

# Barra lateral para cargar archivo
with st.sidebar:
    st.subheader("📂 Cargar archivo CSV")
    uploaded_file = st.file_uploader("Selecciona un archivo CSV", type=["csv"])
    if uploaded_file is not None:
        # Leer el CSV en un DataFrame
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error al leer el CSV: {e}")
            st.stop()
        # Si se carga un nuevo archivo, reiniciar el historial
        if st.session_state.file_name != uploaded_file.name:
            st.session_state.history = []
        st.session_state.file_name = uploaded_file.name
        # Cargar DataFrame en el motor de preguntas
        st.session_state.engine.set_data(df)
        st.success(f"📁 {uploaded_file.name} cargado correctamente.")

# Título y descripción
st.title("Chatyfile")
st.caption("Tu asistente de análisis de datos CSV, rápido y sencillo.")
st.subheader("🤖 Asistente de DataFrame")

# Contenedores para chat y respuestas
chat_placeholder = st.empty()
output_placeholder = st.empty()

if st.session_state.engine.df is not None:
    # Formulario de entrada de pregunta
    with st.form(key="question_form", clear_on_submit=True):
        question_text = st.text_input("Escribe tu pregunta aquí...", key="question_input")
        submitted = st.form_submit_button("Enviar")
    if submitted and question_text:
        # Obtener respuesta del motor
        answer = st.session_state.engine.answer_question(question_text)
        # Guardar en el historial la pregunta y la respuesta
        st.session_state.history.append({"question": question_text, "answer": answer})
        # Limpiar visualización previa si la nueva respuesta es solo texto
        if isinstance(answer, str):
            output_placeholder.empty()
        # Si la respuesta es un gráfico o tabla, muéstrala directamente debajo del chat
        if not isinstance(answer, str):
            # Mostrar respuesta no textual en el contenedor de salida
            with output_placeholder.container():
                # Agregar un pequeño espacio de separación
                st.write('')
                if isinstance(answer, pd.DataFrame):
                    st.dataframe(answer)
                elif hasattr(answer, 'to_html') and callable(getattr(answer, 'to_html')):
                    st.write(answer)
                elif hasattr(answer, 'savefig'):
                    st.pyplot(answer)
                elif str(type(answer)).endswith("plotly.graph_objs._figure.Figure'>"):
                    st.plotly_chart(answer)
                elif "altair.vegalite" in str(type(answer)):
                    st.altair_chart(answer)
                else:
                    st.write(answer)
    # Mostrar historial de conversación
    # Creamos un contenedor con fondo blanco para la conversación
    chat_container_html = "<div style='background-color: #FFFFFF; padding: 15px; border-radius: 10px; min-height: 300px;'>"
    for entry in st.session_state.history:
        user_q = entry.get("question", "")
        answer = entry.get("answer", "")
        # Añadir burbuja de pregunta (usuario) alineada a la derecha
        chat_container_html += f"<div style='text-align: right; margin: 5px 0;'><span style='display: inline-block; background-color: #007BFF; color: white; padding: 8px 12px; border-radius: 10px 10px 0px 10px;'>{user_q}</span></div>"
        # Añadir burbuja de respuesta (asistente) alineada a la izquierda
        if isinstance(answer, str):
            chat_container_html += f"<div style='text-align: left; margin: 5px 0;'><span style='display: inline-block; background-color: #F0F0F0; color: #000000; padding: 8px 12px; border-radius: 0px 10px 10px 10px;'>{answer}</span></div>"
        else:
            # Si la respuesta es un objeto (tabla/gráfico), mostrar un marcador de posición de texto
            chat_container_html += f"<div style='text-align: left; margin: 5px 0;'><span style='display: inline-block; background-color: #F0F0F0; color: #000000; padding: 8px 12px; border-radius: 0px 10px 10px 10px;'>[Respuesta mostrada abajo]</span></div>"
    chat_container_html += "</div>"
    chat_placeholder.markdown(chat_container_html, unsafe_allow_html=True)
