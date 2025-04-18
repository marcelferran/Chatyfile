import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from contextlib import redirect_stdout
import google.generativeai as genai

st.set_page_config(page_title="Compras-GPT", layout="centered")
st.title("🤖 Compras-GPT")
st.caption("Prototipo desarrollado por Marcel F. Castro Ponce de Leon")

# Configura la API key de Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# Inicializar sesión
if "df" not in st.session_state:
    st.session_state.df = None

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": ["Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: "]
        },
        {
            "role": "model",
            "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
        }
    ])

# Subir archivo
uploaded_file = st.sidebar.file_uploader("📁 Carga un archivo CSV o Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.session_state.df = df

        st.subheader("📊 Información del archivo")

        st.markdown(f"🔢 **Filas:** {df.shape[0]}  \n📁 **Columnas:** {df.shape[1]}")

        st.markdown("🧾 **Resumen de columnas:**")
        column_info = pd.DataFrame({
            "Columna": df.columns,
            "Tipo de dato": [str(df[col].dtype) for col in df.columns],
            "¿Tiene nulos?": [df[col].isnull().any() for col in df.columns]
        })
        st.dataframe(column_info)

        st.markdown("🔍 **Vista previa aleatoria (10 filas):**")
        st.dataframe(df.sample(10))

        # Actualizar contexto del modelo con columnas reales
        columnas = ", ".join(df.columns)
        st.session_state.chat.send_message(f"Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: {columnas}. No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

# Interfaz de chat
if st.session_state.df is not None:
    prompt = st.chat_input("Haz una pregunta sobre tus datos o pide un análisis...")

    if prompt:
        st.chat_message("user").markdown(prompt)

        try:
            # Construir prompt para el modelo
            full_prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(st.session_state.df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Pregunta:
{prompt}
"""
            response = st.session_state.chat.send_message(full_prompt)
            code = response.text.strip("`python\n").strip("`").strip()

            st.chat_message("assistant").markdown(f"```python\n{code}\n```")

            # Ejecutar código
            exec_globals = {"df": st.session_state.df, "pd": pd, "plt": plt}
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                exec(code, exec_globals)

            output = buffer.getvalue()

            # Mostrar resultados
            if "result" in exec_globals:
                result = exec_globals["result"]
                if isinstance(result, pd.DataFrame):
                    st.markdown("📊 **Resultado:**")
                    st.dataframe(result)
                elif isinstance(result, pd.Series):
                    st.markdown("📊 **Resultado (serie):**")
                    st.dataframe(result.to_frame())
                elif isinstance(result, (list, dict)):
                    st.markdown("📊 **Resultado (convertido en tabla):**")
                    st.dataframe(pd.DataFrame(result))
                else:
                    st.markdown("📝 **Resultado:**")
                    st.write(result)
            elif 'plt' in code or plt.get_fignums():
                st.markdown("📈 **Gráfico generado**")
                st.pyplot(plt.gcf())
                plt.clf()
            elif output.strip():
                st.markdown("💬 **Respuesta:**")
                st.text(output)
            else:
                st.markdown("✅ Código ejecutado correctamente pero no se generó salida visible.")

        except Exception as e:
            st.error(f"❌ Error al ejecutar el código: {e}")
else:
    st.info("💡 Carga un archivo para comenzar el análisis.")
