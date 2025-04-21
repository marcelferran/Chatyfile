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
        width: 400px; /* Logo más grande */
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

# Cabecera con logotipo a la izquierda
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo.jpeg", width=400)  # Logo más grande
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

# Inicializar estado de la sesión
if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

# Lógica principal de la app
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")
    
    # Resumen del archivo
    num_rows, num_cols = df.shape
    st.write("**Resumen del archivo:**")
    st.write(f"- Número de filas: {num_rows}")
    st.write(f"- Número de columnas: {num_cols}")
    st.write("**Nombres de las columnas:**")
    st.table(pd.DataFrame(df.columns, columns=["Columnas"]))

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

    # Formulario para la pregunta (se envía con "Enter" o botón)
    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar", disabled=False)  # Botón habilitado

    # Procesar la pregunta si se envía el formulario
    if submitted and pregunta:
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Adios.")
            st.session_state.chat = None  # Reiniciar el chat
            st.rerun()
        else:
            try:
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.
NO INTENTES CARGAR EL DATAFRAME CON pd.read_csv, ya está cargado como `df`.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.
Para preguntas sobre productos, como 'urea', usa búsquedas flexibles que ignoren mayúsculas/minúsculas (por ejemplo, .str.contains('urea', case=False, na=False)) y consideren variaciones del texto (por ejemplo, 'Urea 46%', 'urea granulada').
Para resultados numéricos o tabulares, devuelve un DataFrame o un valor claro.
Para gráficas (barras, líneas, pastel, boxplot, etc.), usa matplotlib o seaborn con un tamaño de figura adecuado (por ejemplo, figsize=(8, 6)).
Para cálculos estadísticos (media, mediana, desviación estándar, correlaciones, etc.), devuelve el resultado en un formato claro, preferiblemente como DataFrame.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("```python\n").strip("```").strip()
                st.session_state.history.append(f"📄 Código generado:\n{code}")  # Depuración temporal

                exec_globals = {
                    "df": df,
                    "pd": pd,
                    "plt": plt,
                    "sns": sns,
                    "np": np
                }
                buffer = io.StringIO()

                with contextlib.redirect_stdout(buffer):
                    try:
                        exec(code, exec_globals)
                    except Exception as e:
                        st.session_state.history.append(f"❌ Error al ejecutar el código: {str(e)}")
                        st.rerun()

                output = buffer.getvalue().strip()

                # Mostrar resultados de forma amigable
                if "plt" in code or "sns" in code:
                    # Mostrar gráfica si el código genera una
                    st.pyplot(plt.gcf())
                    plt.clf()  # Limpiar la figura para la próxima gráfica
                elif output:
                    # Mostrar salida de texto como tabla si es un valor simple
                    st.table(pd.DataFrame({"Resultado": [output]}))
                else:
                    # Intentar mostrar un DataFrame si el código lo genera
                    for key, value in exec_globals.items():
                        if isinstance(value, pd.DataFrame) and key != "df":
                            st.dataframe(value)
                            break
                    else:
                        st.session_state.history.append("✅ Código ejecutado sin salida.")

            except Exception as e:
                st.session_state.history.append(f"❌ Error al procesar o ejecutar: {str(e)}")

        st.rerun()  # Refrescar la página para mostrar el historial actualizado
else:
    st.warning("Por favor, sube un archivo para continuar.")
