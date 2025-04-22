import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib

# ==== CONFIGURAR LA API DE GEMINI ====
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
elif "GEMINI_API_KEY" in st.session_state:
    api_key = st.session_state["GEMINI_API_KEY"]
else:
    api_key = st.text_input("🔑 Introduce tu GEMINI_API_KEY", type="password")
    if api_key:
        st.session_state["GEMINI_API_KEY"] = api_key

if not api_key:
    st.warning("Por favor, introduce tu clave API para continuar.")
    st.stop()

genai.configure(api_key=api_key)

# ==== CONFIGURACIÓN DE LA PÁGINA ====
st.set_page_config(
    page_title="Chatyfile",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==== ESTILOS PERSONALIZADOS ====
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .header {
        display: flex;
        align-items: center;
        padding: 10px;
        background-color: #1f77b4;
        border-radius: 10px;
    }
    .header img {
        width: 400px;
        margin-right: 20px;
    }
    h1 {
        color: #ffffff;
        font-family: 'Arial', sans-serif;
        margin: 0;
    }
    .css-1d391kg {
        background-color: #ffffff;
        border-right: 2px solid #1f77b4;
    }
    .stButton>button {
        background-color: #ff7f0e;
        color: white;
        border-radius: 5px;
    }
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

# ==== CABECERA CON LOGO ====
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo.jpeg", width=400)
st.title("📄 Chatyfile")
st.markdown('</div>', unsafe_allow_html=True)

# ==== MENSAJE DE BIENVENIDA ====
st.markdown("""
    <h3 style='text-align: center; color: #1f77b4;'>¡Bienvenido a Chatyfile!</h3>
    <p style='text-align: center;'>Sube tu archivo y haz preguntas sobre tus datos</p>
""", unsafe_allow_html=True)

# ==== BARRA LATERAL ====
with st.sidebar:
    st.header("🤖 Opciones")
    uploaded_file = st.file_uploader("Sube tu archivo", type=["csv"])
    st.markdown("---")
    st.subheader("⚠️ Instrucciones")
    st.write("1. Sube el archivo con tus datos.")
    st.write("2. Escribe tu pregunta y presiona 'Enter' o haz clic en 'Enviar'.")
    st.write("3. Escribe 'salir' para finalizar.")

# ==== PIE DE PÁGINA ====
st.markdown("""
    <div class="footer">
        <p>© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</p>
    </div>
""", unsafe_allow_html=True)

# ==== INICIALIZAR ESTADO DE SESIÓN ====
if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

# ==== LÓGICA PRINCIPAL ====
if uploaded_file is not None:
    df_w5 = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")

    num_rows, num_cols = df_w5.shape
    st.write("**Resumen del archivo:**")
    st.write(f"- Número de filas: {num_rows}")
    st.write(f"- Número de columnas: {num_cols}")
    st.write("**Nombres de las columnas:**")
    st.table(pd.DataFrame(df_w5.columns, columns=["Columnas"]))

    # Inicializar chat si es la primera vez
    if st.session_state.chat is None:
        model = genai.GenerativeModel('gemini-2.0-flash')
        st.session_state.chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": [
                    "Tienes un DataFrame de pandas llamado df_w5. Estas son las columnas reales que contiene: " 
                    + ", ".join(df_w5.columns) 
                    + ". No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están."
                ]
            },
            {
                "role": "model",
                "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
            }
        ])
        st.session_state.history.append("🟢 Asistente activo. Pregunta lo que quieras sobre tu df_w5.")
        st.session_state.history.append("✏️  Escribe 'salir' para terminar.")

    # Mostrar historial de chat
    for message in st.session_state.history:
        st.write(message)

    # Formulario de pregunta
    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar")

    if submitted and pregunta:
        # Comando de salir
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Programa finalizado.")
            st.session_state.chat = None
            st.rerun()
        else:
            try:
                # Prompt igual al código original
                prompt = f"""
Tienes un DataFrame de pandas llamado `df_w5` cargado en memoria.
Estas son las columnas reales: {', '.join(df_w5.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("```python\n").strip("```").strip()

                # Ejecutar el código generado
                exec_globals = {"df_w5": df_w5}
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

            st.rerun()
else:
    st.warning("Por favor, sube un archivo para continuar.")
