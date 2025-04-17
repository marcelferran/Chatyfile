import io
import contextlib
import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import google.generativeai as genai

# Configura la página
st.set_page_config(page_title="ComprasGPT", layout="wide")
st.title("📊 ComprasGPT")

# Configura la API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# Cargar archivo
uploaded_file = st.file_uploader("Carga tu archivo (.csv o .xlsx)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Mostrar resumen
        st.success("✅ Archivo cargado correctamente")
        st.write(f"**Filas:** {df.shape[0]} | **Columnas:** {df.shape[1]}")

        # Resumen de columnas
        summary = pd.DataFrame({
            "Columna": df.columns,
            "Tipo de dato": df.dtypes.values,
            "Valores nulos": df.isnull().sum().values
        })
        st.subheader("📋 Resumen de columnas")
        st.dataframe(summary)

        # Muestra de datos
        st.subheader("🔍 Muestra de 10 filas")
        st.dataframe(df.sample(10))

        # Asistente interactivo
        st.subheader("🤖 Pregunta al asistente sobre tu DataFrame")

        # Iniciar chat con Gemini
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

Responde a esta pregunta escribiendo **código Python** que imprima una respuesta clara y amigable para el usuario.
La respuesta debe ser un texto legible, no solo valores crudos como tuplas o tipos numéricos.
Usa `print()` para mostrar la respuesta de forma descriptiva.

Pregunta:
{pregunta}
"""
                try:
                    response = chat.send_message(prompt)
                    code = response.text.strip("`python\n").strip("`").strip()

                    # Ejecutar código generado
                    exec_globals = {"df": df, "plt": plt, "px": px}
                    buffer = io.StringIO()

                    with contextlib.redirect_stdout(buffer):
                        try:
                            exec(code, exec_globals)
                        except Exception as e:
                            st.error(f"❌ Error al ejecutar el código: {str(e)}")

                    output = buffer.getvalue()

                    # Mostrar salida de texto si existe
                    if output.strip():
                        st.success("💬 Respuesta del asistente:")
                        st.code(output)

                    # Detectar y mostrar gráficos
                    if "plt" in code or "plotly" in code:
                        try:
                            if "plt" in code:
                                plt.figure()
                                exec(code, exec_globals)
                                st.pyplot(plt.gcf())
                                plt.close()
                            elif "plotly" in code:
                                exec_globals["fig"] = None
                                exec(code, exec_globals)
                                if exec_globals.get("fig") is not None:
                                    st.plotly_chart(exec_globals["fig"])
                                else:
                                    st.warning("⚠️ No se generó un gráfico de Plotly válido.")
                        except Exception as e:
                            st.error(f"❌ Error al generar el gráfico: {str(e)}")
                    else:
                        st.info("✅ Código ejecutado sin gráficos.")
                except Exception as e:
                    st.error(f"❌ Error al procesar la pregunta: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {str(e)}")
