import io
import contextlib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go


# Función para iniciar el chat
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


# Función para procesar la pregunta y generar la respuesta
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
        # Aquí estamos capturando el texto de la respuesta del modelo
        response = st.session_state.chat.send_message(prompt)
        code = response.text.strip("```python").strip("```").strip()

        if not code:
            st.session_state.history.append("❌ **No se generó código**. Intenta preguntar de otra forma.")

        buffer = io.StringIO()
        exec_globals = {"df": df, "plt": plt}  # Asegúrate de incluir plt en exec_globals
        
        with contextlib.redirect_stdout(buffer):
            try:
                exec(code, exec_globals)
            except Exception as e:
                st.session_state.history.append(f"❌ **Error al ejecutar el código**: {str(e)}")
                return  # Salir de la función si hay error al ejecutar el código
        
        output = buffer.getvalue()

        if output.strip():
            if "plt.show()" in code:
                st.session_state.history.append("📊 **Gráfica generada:**")
                # Guardar la figura generada en la sesión
                st.session_state.graph = plt.gcf()  # Usar plt.gcf() para obtener la figura actual
                st.pyplot(st.session_state.graph)
            else:
                result_df = pd.DataFrame([output.split("\n")]).T
                result_df.columns = ["Resultados"]
                st.session_state.history.append("💬 **Respuesta:**")
                st.session_state.history.append(result_df)

    except Exception as e:
        # Si algo falla en el proceso de la conversación, mostramos el error
        st.session_state.history.append(f"❌ **Algo salió mal con la consulta. Detalles**: {str(e)}")


# Mostrar respuestas guardadas en el historial
def mostrar_historial():
    if "history" in st.session_state:
        for entry in st.session_state.history:
            if isinstance(entry, pd.DataFrame):
                st.dataframe(entry)
            else:
                st.write(entry)


# Función principal
def main():
    # Configuración inicial
    st.set_page_config(page_title="Chatyfile", page_icon="📄", layout="wide", initial_sidebar_state="expanded")
    
    # Cargar archivo y mostrar el resumen
    uploaded_file = st.sidebar.file_uploader("Sube un archivo", type=["csv", "xlsx"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df  # Guardar el DataFrame en el estado de la sesión

        # Mostrar resumen del DataFrame
        mostrar_resumen_df(df)

        if "chat" not in st.session_state:  # Inicia chat solo si no se ha iniciado
            iniciar_chat(df)

        # Mostrar historial de respuestas y gráficas
        mostrar_historial()

        with st.form(key='pregunta_form', clear_on_submit=True):
            pregunta = st.text_input("🤖 Pregunta:")
            submitted = st.form_submit_button(label="Enviar")

        if submitted and pregunta:
            if pregunta.lower() == "salir":
                st.session_state.history.append("👋 Adios.")
                st.session_state.chat = None
                st.stop()
            else:
                procesar_pregunta(pregunta, df)


# Ejecutar la aplicación
if __name__ == "__main__":
    main()
                

# Función para borrar el historial del chat
def borrar_historial():
    if st.button('Borrar chat'):
        st.session_state.history = ["Chat borrado. Comienza una nueva conversación."]
