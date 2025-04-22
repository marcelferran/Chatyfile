import io
import contextlib
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import google.generativeai as genai

def iniciar_chat(df):
    model = genai.GenerativeModel('gemini-2.0-flash')
    chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": ["Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: " + ", ".join(df.columns) + ". No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están."]
        },
        {
            "role": "model",
            "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
        }
    ])
    st.session_state.chat = chat
    st.session_state.history = [
        "🟢 Asistente activo. Pregunta lo que quieras sobre tu DataFrame.",
        "✏️ Escribe 'salir' para finalizar."
    ]

def mostrar_historial():
    for msg in st.session_state.history:
        st.write(msg)

def procesar_pregunta(pregunta, df):
    prompt = f"""
Tienes un DataFrame de pandas llamado df cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Para preguntas sobre productos, como 'urea', usa búsquedas flexibles que ignoren mayúsculas/minúsculas (por ejemplo, .str.contains('urea', case=False, na=False)) y consideren variaciones del texto (por ejemplo, 'Urea 46%', 'urea granulada').

Si la pregunta requiere una gráfica, genera la gráfica usando matplotlib y muéstrala con st.pyplot().

Pregunta:
{pregunta}
"""
    try:
        response = st.session_state.chat.send_message(prompt)
        code = response.text.strip("```python").strip("```").strip()
        buffer = io.StringIO()
        exec_globals = {"df": df, "plt": plt}

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
