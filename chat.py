import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib

# Configurar la API de Gemini (asegúrate de que la clave esté en Streamlit Cloud Secrets)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inicializar el estado de la sesión
if "chat" not in st.session_state:
    st.session_state.chat = None
if "history" not in st.session_state:
    st.session_state.history = []

# Cabecera con logotipo
st.markdown('<div class="header">', unsafe_allow_html=True)
st.image("logo.jpeg", width=150)
st.title("📄 Chatyfile")
st.markdown('</div>', unsafe_allow_html=True)

# Subir archivo CSV
uploaded_file = st.file_uploader("Sube tu archivo CSV", type=["csv"])

# Lógica principal de la app
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")
    st.write("Columnas disponibles:", ", ".join(df.columns))

    # Inicializar el modelo y el chat si no está inicializado
    if st.session_state.chat is None:
        try:
            st.info("🔧 Intentando inicializar el modelo Gemini...")
            model = genai.GenerativeModel('gemini-2.0-flash')  # Cambia a 'gemini-1.5-flash' si falla
            st.info("✅ Modelo Gemini cargado correctamente.")
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
            st.info("✅ Chat inicializado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al inicializar el modelo Gemini: {str(e)}")
            st.stop()

    # Mostrar historial de la conversación
    for message in st.session_state.history:
        st.write(message)

    # Formulario para la pregunta (se envía con "Enter")
    with st.form(key='pregunta_form', clear_on_submit=True):
        pregunta = st.text_input("🤔 Tu pregunta:", key="pregunta_input")
        submit_button = st.form_submit_button(label="Enviar")

    # Procesar la pregunta
    if submit_button and pregunta:
        st.info("🔄 Procesando tu pregunta...")
        if pregunta.lower() == "salir":
            st.session_state.history.append("👋 Programa finalizado.")
            st.session_state.chat = None
            st.rerun()
        else:
            try:
                st.info("📡 Enviando solicitud a Gemini...")
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Pregunta:
{pregunta}
"""
                response = st.session_state.chat.send_message(prompt)
                st.info("✅ Respuesta recibida de Gemini.")
                code = response.text.strip("`python\n").strip("`").strip()
                st.session_state.history.append(f"📄 Código generado:\n{code}")

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
