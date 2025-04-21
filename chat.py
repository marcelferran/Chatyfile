import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar la API de Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("La clave GEMINI_API_KEY no está configurada en los Secrets de Streamlit Cloud.")
    st.stop()

# Configuración de la página (sin cambios)
st.set_page_config(
    page_title="Chatyfile",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (sin cambios)
st.markdown("""
    <style>
    /* ... tus estilos CSS ... */
    </style>
""", unsafe_allow_html=True)

# Cabecera (sin cambios)
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo.jpeg", width=400)
st.title("📄 Chatyfile")
st.markdown('</div>', unsafe_allow_html=True)

# Bienvenida (sin cambios)
st.markdown("""
    <h3 style='text-align: center; color: #1f77b4;'>¡Bienvenido a Chatyfile!</h3>
    <p style='text-align: center;'>Sube tu archivo y haz preguntas sobre tus datos</p>
""", unsafe_allow_html=True)

# Barra lateral (sin cambios)
with st.sidebar:
    st.header("🤖 Opciones")
    uploaded_file = st.file_uploader("Sube tu archivo", type=["csv"])
    st.markdown("---")
    st.subheader("⚠️ Instrucciones")
    st.write("1. Sube el archivo con tus datos.")
    st.write("2. Escribe tu pregunta y presiona 'Enter' o haz clic en 'Enviar'.")
    st.write("3. Escribe 'salir' para finalizar.")

# Pie de página (sin cambios)
st.markdown("""
    <div class="footer">
        <p>© 2025 Chatyfile. Todos los derechos reservados. Propiedad intelectual protegida.</p>
    </div>
""", unsafe_allow_html=True)

# Inicializar estado de la sesión (sin cambios)
if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

# Lógica principal de la app
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")

    # Resumen del archivo (sin cambios)
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

    # Formulario para la pregunta
    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤖 Pregunta:", key="pregunta_input")
        submitted = st.form_submit_button(label="Enviar", disabled=False)

    # Procesar la pregunta si se envía el formulario
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

Responde a la pregunta del usuario de forma amigable y legible.
Si la pregunta requiere mostrar una tabla, genera el código Python necesario para crear el DataFrame resultante y luego utiliza `st.table(resultado_df)` o `st.dataframe(resultado_df)` para mostrarlo. Asegúrate de que el DataFrame resultante se llame `resultado_df`.
Si la pregunta requiere mostrar una gráfica, genera el código Python completo utilizando las bibliotecas `matplotlib` o `seaborn` (plt y sns) para crear la figura y los ejes, y luego finaliza el código con `plt.show()`.

**Importante:** En tu respuesta de texto principal, describe los resultados o la gráfica. **NO INCLUYAS el código Python en tu respuesta de texto principal.** El código generado se ejecutará por separado.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                answer_text = response.text.strip()
                st.session_state.history.append(f"🤖 Chatyfile: {answer_text}")

                # Intenta ejecutar el código generado (si lo hay) para mostrar tablas o gráficos
                code_blocks = [part.text for part in response.parts if isinstance(part, genai.types.Part.from_dict({"text": ""}).__class__)]
                if code_blocks:
                    code = code_blocks[0].strip("```python\n").strip("```").strip()
                    exec_globals = {"df": df, "pd": pd, "plt": plt, "sns": sns, "st": st}
                    buffer = io.StringIO()

                    with contextlib.redirect_stdout(buffer):
                        try:
                            exec(code, exec_globals)
                        except Exception as e:
                            st.session_state.history.append(f"❌ Error al ejecutar el código para la visualización: {str(e)}")
                        finally:
                            # Mostrar el gráfico si plt.show() fue llamado
                            if 'plt' in exec_globals and hasattr(exec_globals['plt'], '_Gcf') and exec_globals['plt']._Gcf.get_active():
                                st.pyplot(exec_globals['plt'])

            except Exception as e:
                st.session_state.history.append(f"❌ Error al procesar la pregunta: {str(e)}")

        st.rerun()
else:
    st.warning("Por favor, sube un archivo para continuar.")
