import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib
import matplotlib.pyplot as plt

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
    .stApp { background-color: #f0f2f6; }
    .header {
        display: flex; align-items: center; padding: 10px;
        background-color: #1f77b4; border-radius: 10px;
    }
    .header img { width: 400px; margin-right: 20px; }
    h1 { color: #ffffff; font-family: 'Arial', sans-serif; margin: 0; }
    .footer {
        text-align: center; padding: 10px; background-color: #1f77b4;
        color: white; position: fixed; bottom: 0; width: 100%;
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
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")

    num_rows, num_cols = df.shape
    st.write("**Resumen del archivo:**")
    st.write(f"- Número de filas: {num_rows}")
    st.write(f"- Número de columnas: {num_cols}")
    st.write("**Nombres de las columnas:**")
    st.dataframe(pd.DataFrame(df.columns, columns=["Columnas"]))

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

    for message in st.session_state.history:
        st.write(message)

    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar", disabled=False)

    if submitted and pregunta:
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Adios.")
            st.session_state.chat = None
            st.rerun()
        else:
            try:
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Para preguntas sobre productos, como 'urea', usa búsquedas flexibles que ignoren mayúsculas/minúsculas (por ejemplo, `.str.contains('urea', case=False, na=False)`) y consideren variaciones del texto (por ejemplo, 'Urea 46%', 'urea granulada').

Si la pregunta requiere una gráfica, genera la gráfica usando `matplotlib` y muéstrala con `st.pyplot()`.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("```python\n").strip("```").strip()

                exec_globals = {"df": df, "plt": plt}
                buffer = io.StringIO()

                with contextlib.redirect_stdout(buffer):
                    try:
                        exec(code, exec_globals)
                    except Exception as e:
                        st.session_state.history.append(f"❌ Error al ejecutar el código: {str(e)}")

                output = buffer.getvalue()

                if output.strip():
                    if "plt.show()" in code:
                        st.session_state.history.append("📊 **Gráfica generada:**")
                        st.pyplot()
                    else:
                        result_df = pd.DataFrame([output.split("\n")]).T
                        result_df.columns = ["Resultados"]
                        st.session_state.history.append("💬 **Respuesta:**")
                        st.session_state.history.append(result_df)

            except Exception as e:
                st.session_state.history.append(f"❌ Error al procesar o ejecutar: {str(e)}")

        st.rerun()
else:
    st.warning("Por favor, sube un archivo para continuar.")

