import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración inicial
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("📊 Chatyfile")
st.markdown("Hazle preguntas a tu archivo CSV usando Gemini ✨")

uploaded_file = st.file_uploader("📁 Sube un archivo CSV", type=["csv"])

if "chat" not in st.session_state:
    st.session_state.chat = None
    st.session_state.history = []

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Archivo cargado correctamente.")
    st.markdown("### 👁️ Vista previa del archivo")
    st.dataframe(df.head())

    if st.session_state.chat is None:
        model = genai.GenerativeModel('gemini-1.5-pro')
        st.session_state.chat = model.start_chat(history=[
            {
                "role": "user",
                "parts": ["Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: " + ", ".join(df.columns)]
            },
            {
                "role": "model",
                "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
            }
        ])

    st.markdown("### 🧠 Pregunta para Gemini:")
    pregunta = st.text_input("Haz una pregunta sobre el archivo (escribe 'salir' para reiniciar):")

    if pregunta:
        if pregunta.lower() == "salir":
            st.session_state.chat = None
            st.rerun()
        else:
            with st.spinner("🔄 Obteniendo respuesta de Gemini..."):
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria con estas columnas: {', '.join(df.columns)}.
No intentes volver a cargarlo, ya está disponible.

Genera solo el código Python para responder la siguiente pregunta:
{pregunta}
"""

                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("```python\n").strip("```").strip()

            st.markdown("### 🤖 Respuesta de Gemini (código):")
            st.code(code, language="python")

            st.markdown("### ▶️ Ejecutando código...")
            try:
                exec_globals = {"df": df, "pd": pd, "plt": plt, "sns": sns, "np": np}
                buffer = io.StringIO()

                with contextlib.redirect_stdout(buffer):
                    exec(code, exec_globals)

                output = buffer.getvalue()

                if output:
                    st.markdown("### 🖨️ Resultado del código:")
                    st.code(output)

                # Mostrar gráfico si se generó
                if plt.get_fignums():
                    st.markdown("### 📊 Gráfico generado:")
                    st.pyplot(plt.gcf())
                    plt.clf()

                # Mostrar variables nuevas tipo DataFrame
                for var, val in exec_globals.items():
                    if isinstance(val, pd.DataFrame) and var != "df":
                        st.markdown(f"### 📋 DataFrame generado: `{var}`")
                        st.dataframe(val)

                # Mostrar valores individuales como métricas
                for var, val in exec_globals.items():
                    if isinstance(val, (int, float)) and not var.startswith("__"):
                        st.metric(label=f"📈 {var}", value=val)

                if not output and not plt.get_fignums():
                    st.success("✅ Código ejecutado, pero no hubo salida visible.")

            except Exception as e:
                st.error(f"❌ Error al ejecutar el código:\n\n{str(e)}")
