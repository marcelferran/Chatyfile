import io
import contextlib
import pandas as pd
import streamlit as st
import google.generativeai as genai

# Configura la página antes de cualquier otro componente
st.set_page_config(page_title="Char de Geomecánica", layout="wide")

# Configura la API key desde los secretos
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Ahora puedes hacer consultas a la API
model = genai.GenerativeModel('gemini-2.0-flash')

response = model.generate_content("Hola, ¿quién eres?")
st.write(response.text)
st.title("📊 Asistente de Geomecánica con Gemini")

# 1. Cargar archivo CSV o XLSX
uploaded_file = st.file_uploader("Carga tu archivo (.csv o .xlsx)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # 2. Mostrar resumen
        st.success("✅ Archivo cargado correctamente")
        st.write(f"**Filas:** {df.shape[0]} | **Columnas:** {df.shape[1]}")

        # 3. Mostrar tabla resumen de columnas
        summary = pd.DataFrame({
            "Columna": df.columns,
            "Tipo de dato": df.dtypes.values,
            "Valores nulos": df.isnull().sum().values
        })
        st.subheader("📋 Resumen de columnas")
        st.dataframe(summary)

        # 4. Mostrar sample
        st.subheader("🔍 Muestra de 10 filas")
        st.dataframe(df.head(10))

        # 5. Asistente interactivo
        st.subheader("🤖 Pregunta al asistente sobre tu DataFrame")

        # Iniciar modelo Gemini
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

        pregunta = st.text_input("✏️ Escribe tu pregunta sobre los datos (escribe 'salir' para terminar):")

        if pregunta:
            if pregunta.lower() == "salir":
                st.warning("👋 Programa finalizado.")
            else:
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Pregunta:
{pregunta}
"""
                try:
                    response = chat.send_message(prompt)
                    code = response.text.strip("`python\n").strip("`").strip()

                    # Ejecutar código generado
                    exec_globals = {"df": df}
                    buffer = io.StringIO()

                    with contextlib.redirect_stdout(buffer):
                        try:
                            exec(code, exec_globals)
                        except Exception as e:
                            st.error(f"❌ Error al ejecutar el código: {str(e)}")

                    output = buffer.getvalue()

                    if output.strip():
                        st.success("💬 Respuesta del asistente:")
                        st.code(output)
                    else:
                        st.info("✅ Código ejecutado sin salida.")
                except Exception as e:
                    st.error(f"❌ Error al procesar la pregunta: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {str(e)}")
