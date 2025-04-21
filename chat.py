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

Responde a la siguiente pregunta de forma amigable y legible.
Si es necesario mostrar datos, genera **únicamente** el código Python para hacerlo usando Streamlit (`st.table()`, `st.dataframe()`, `st.metric()`, `st.write()`) y/o Matplotlib/Seaborn (`plt.show()`). Asegúrate de que el código sea completo y ejecutable.

**Importante:** Tu respuesta de texto debe explicar los resultados o la acción realizada. **EVITA incluir bloques de código Python completos en tu respuesta de texto.** Solo menciona que se mostrará una tabla, un gráfico, una métrica, etc.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                full_response = response.text.strip()
                st.session_state.history.append(f"🤖 Chatyfile: {full_response}")

                code = ""
                # Buscar bloques de código en la respuesta (más robusto)
                code_blocks = [part.text for part in response.parts if isinstance(part, genai.types.Part.from_dict({"text": ""}).__class__)]
                if code_blocks:
                    code = code_blocks[0].strip("```python\n").strip("```").strip()
                    st.session_state.history.append(f"🤖 Código generado por la IA:") # Para depuración
                    st.code(code) # Mostrar el código generado (temporalmente para depuración)

                exec_globals = {"df": df, "pd": pd, "plt": plt, "sns": sns, "st": st}
                buffer = io.StringIO()
                output = None
                error = None
                plot_generated = False

                with contextlib.redirect_stdout(buffer):
                    try:
                        exec(code, exec_globals)
                        output = buffer.getvalue()
                        if 'plt' in exec_globals and hasattr(exec_globals['plt'], '_Gcf') and exec_globals['plt']._Gcf.get_active():
                            plot_generated = True
                    except Exception as e:
                        error = str(e)

                st.session_state.history.append(f"🤖 Ejecución del código:") # Para depuración
                if output:
                    st.session_state.history.append(f"Salida (print): {output}") # Para depuración
                if error:
                    st.session_state.history.append(f"Error al ejecutar el código: {error}") # Para depuración

                if plot_generated:
                    st.pyplot(exec_globals['plt'])
                # No necesitamos mostrar output aquí, se espera que st.write en el código generado lo haga

            except Exception as e:
                st.session_state.history.append(f"❌ Error general al procesar: {str(e)}")

        st.rerun()
else:
    st.warning("Por favor, sube un archivo para continuar.")
