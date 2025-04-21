import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configurar la API de Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("La clave GEMINI_API_KEY no está configurada en los Secrets de Streamlit Cloud.")
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

# Cabecera con logotipo
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo.jpeg", width=400)
st.title("📄 Chatyfile")
st.markdown('</div>', unsafe_allow_html=True)

# Bienvenida
st.markdown("""
    <h3 style='text-align: center; color: #1f77b4;'>¡Bienvenido a Chatyfile!</h3>
    <p style='text-align: center;'>Sube tu archivo y haz preguntas sobre tus datos</p>
""", unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.header("🤖 Opciones")
    uploaded_file = st.file_uploader("Sube tu archivo", type=["csv"])
    st.markdown("---")
    st.subheader("⚠️ Instrucciones")
    st.write("1. Sube el archivo con tus datos.")
    st.write("2. Escribe tu pregunta y presiona 'Enter' o haz clic en 'Enviar'.")
    st.write("3. Escribe 'salir' para finalizar.")

# Pie de página
st.markdown("""
    <div class="footer">
        <p>© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</p>
    </div>
""", unsafe_allow_html=True)

# Estado inicial de sesión
if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

# Lógica principal
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")

    # Resumen del archivo
    st.write("**Resumen del archivo:**")
    st.write(f"- Número de filas: {df.shape[0]}")
    st.write(f"- Número de columnas: {df.shape[1]}")
    st.write("**Nombres de las columnas:**")
    st.table(pd.DataFrame(df.columns, columns=["Columnas"]))

    # Inicializar Gemini si no está hecho
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

    # Mostrar historial
    for message in st.session_state.history:
        st.write(message)

    # Entrada de pregunta
    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar")

    if submitted and pregunta:
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Adiós.")
            st.session_state.chat = None
            st.rerun()
        else:
            try:
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria con las columnas: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.
NO INTENTES CARGAR EL DATAFRAME CON pd.read_csv, ya está cargado como `df`.

Escribe solo el código Python necesario para responder la pregunta.
Usa búsquedas flexibles para productos como 'urea' (por ejemplo, .str.contains('urea', case=False, na=False)) para manejar variaciones (mayúsculas/minúsculas, 'Urea 46%', 'urea granulada').
Devuelve resultados numéricos o tabulares como DataFrame o valor claro.
Para gráficas (barras, líneas, pastel, boxplot), usa matplotlib/seaborn con figsize=(8, 6).
Para cálculos estadísticos (media, mediana, etc.), devuelve el resultado como DataFrame o valor claro.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("```python\n").strip("```").strip()
                
                # Correcciones automáticas al código generado
                code = code.replace("rint(", "print(").replace("figsize=(8, 6)", "figsize=(4.8, 3.6)")

                exec_globals = {
                    "df": df,
                    "pd": pd,
                    "plt": plt,
                    "sns": sns,
                    "np": np
                }

                buffer = io.StringIO()
                error_during_exec = None

                try:
                    with contextlib.redirect_stdout(buffer):
                        exec(code, exec_globals)
                except Exception as e:
                    error_during_exec = str(e)

                output = buffer.getvalue().strip()

                if error_during_exec:
                    st.session_state.history.append(f"❌ Error al ejecutar el código: {error_during_exec}")
                    st.rerun()

                # Mostrar gráfico si existe
                if plt.get_fignums():
                    st.pyplot(plt.gcf())
                    plt.clf()

                # Si hay texto en el buffer (como por print), lo mostramos
                if output:
                    # Si parece una tabla, tratar de evaluarla como tal
                    try:
                        possible_df = eval(output, exec_globals)
                        if isinstance(possible_df, pd.DataFrame):
                            st.dataframe(possible_df)
                        else:
                            st.code(output)
                    except:
                        st.code(output)
                else:
                    # Buscar variables tipo DataFrame distintas de 'df'
                    for key, val in exec_globals.items():
                        if isinstance(val, pd.DataFrame) and key != "df":
                            st.dataframe(val)
                            break
                    else:
                        for key, val in exec_globals.items():
                            if key.startswith("num_") and isinstance(val, (int, float, str)):
                                st.metric(label=key, value=val)
                                break
                        else:
                            st.success("✅ Código ejecutado sin salida visible.")
