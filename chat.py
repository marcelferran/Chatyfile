import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib
import os

# Configurar la API de Gemini con la variable de entorno de Streamlit Cloud
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    st.error("Error al configurar la API de Gemini. Asegúrate de que la variable de entorno GEMINI_API_KEY esté configurada en Streamlit Cloud.")
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Chatyfile",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #f0f2f6;
    }
    /* Cabecera con logotipo */
    .header {
        text-align: center;
        padding: 10px;
        background-color: #1f77b4;
        border-radius: 10px;
    }
    /* Título */
    h1 {
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    /* Barra lateral */
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 2px solid #1f77b4;
    }
    /* Botones */
    .stButton>button {
        background-color: #ff7f0e;
        color: white;
        border-radius: 5px;
    }
    /* Pie de página */
    .footer {
        text-align: center;
        padding: 10px;
        background-color: #1f77b4;
        color: white;
        position: fixed;
        bottom: 0;
        width: 100%;
        border-top: 2px solid #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Cabecera con logotipo
st markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo.jpeg", width=150)  # Asegúrate de tener logo en el repositorio
st.title("📄 Chatyfile")
st.markdown('</div>', unsafe_allow_html=True)

# Bienvenida
st.markdown("""
    <h3 style='text-align: center; color: #1f77b4;'>¡Bienvenido a Chatyfile!</h3>
    <p style='text-align: center;'>Sube tu archivo y haz preguntas sobre tus datos</p>
""", unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.header("📂 Opciones")
    uploaded_file = st.file_uploader("Sube tu archivo", type=["csv"])
    st.markdown("---")
    st.subheader("ℹ️ Instrucciones")
    st.write("1. Sube el archivo con tus datos.")
    st.write("2. Escribe tu pregunta.")
    st.write("3. Presiona 'Enviar' para obtener la respuesta.")
    st.write("4. Escribe 'salir' para finalizar.")

# Pie de página
st.markdown("""
    <div class="footer">
        <p>© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</p>
    </div>
""", unsafe_allow_html=True)

# Inicializar estado de la sesión
if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

# Lógica principal de la app
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")
    st.write("Columnas disponibles:", ", ".join(df.columns))

    # Inicializar el modelo y el chat si no está inicializado
    if st.session_state.chat is None:
        model = genai.GenerativeModel('gemini-2.0-flash')
        st.session_state.chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": ["Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: " + ", ".join(df.columns) + ". No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están."]
            },
            {
                "role": "model",
                "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
            }
        ])
        st.session_state.history.append("🟢 Asistente activo. Pregunta lo que quieras sobre tu DataFrame.")
        st.session_state.history.append("✏️ Escribe 'salir' para finalizar.")

    # Mostrar historial de la conversación
    for message in st.session_state.history:
        st.write(message)

    # Campo para la pregunta
    pregunta = st.text_input("🤔 Tu pregunta:", key="pregunta_input")

    # Botón para enviar la pregunta
    if st.button("Enviar"):
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Programa finalizado.")
            st.session_state.chat = None  # Reiniciar el chat
            st.rerun()
        else:
            try:
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("`python\n").strip("`").strip()

                exec_globals = {"df": df}
                buffer = io.StringIO()

                with contextlib.redirect_stdout(buffer):
                    try:
                        exec(code, exec_globals)
                    except Exception as e:
                        st.session_state.history.append(f"❌ Error al ejecutar el código: {str(e)}")

                output = buffer.getvalue()

                if output.strip():
                    st.session_state.history.append("💬 Respuesta:")
                    st.session_state.history.append(output)
                else:
                    st.session_state.history.append("✅ Código ejecutado sin salida.")

            except Exception as e:
                st.session_state.history.append(f"❌ Error al procesar o ejecutar: {str(e)}")

        st.rerun()  # Refrescar la página para mostrar el historial actualizado
else:
    st.warning("Por favor, sube un archivo para continuar.")
