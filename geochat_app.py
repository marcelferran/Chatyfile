import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from contextlib import redirect_stdout
import google.generativeai as genai

st.set_page_config(page_title="Gemini Chatbot", layout="wide")
st.title("🤖 Gemini Data Analyst")
st.caption("Prototipo desarrollado por Marcel F. Castro")

# Configura la API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# Inicializar estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "df" not in st.session_state:
    st.session_state.df = None

# Subida de archivo en el sidebar
uploaded_file = st.sidebar.file_uploader("📁 **Carga un archivo CSV o Excel**", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    else:
        st.session_state.df = pd.read_excel(uploaded_file)

    df = st.session_state.df

    # Mostrar información básica del archivo cargado
    st.chat_message("assistant").markdown("📊 **Datos cargados:**")
    st.chat_message("assistant").markdown(f"🔢 **Filas:** {df.shape[0]} | 📁 **Columnas:** {df.shape[1]}")

    st.chat_message("assistant").markdown("🧾 **Resumen de columnas:**")
    resumen_columnas = pd.DataFrame({
        "Nombre": df.columns,
        "Tipo de dato": [df[col].dtype for col in df.columns],
        "¿Tiene nulos?": ["Sí" if df[col].isnull().any() else "No" for col in df.columns]
    })
    st.chat_message("assistant").dataframe(resumen_columnas)

    st.chat_message("assistant").markdown("🔍 **Vista previa aleatoria (10 filas):**")
    st.chat_message("assistant").dataframe(df.sample(10))

# Mostrar historial de mensajes
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("is_dataframe"):
            st.dataframe(msg["content"], use_container_width=False)
        elif msg.get("is_plot"):
            st.pyplot(msg["content"])
        else:
            st.markdown(msg["content"])

# Entrada del usuario
prompt = st.chat_input("Escribe tu mensaje o pregunta aquí...")

if prompt:
    # Mostrar mensaje del usuario
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    if st.session_state.df is not None:
        df = st.session_state.df

        # Contexto básico para el modelo
        context = f"Este es un DataFrame llamado df con columnas: {', '.join(df.columns)}. Responde en español y entrega solo la respuesta final, clara y directa."

        response = model.generate_content([
            context,
            prompt
        ])

        code = response.text

        # Ejecutar código
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                exec_globals = {"df": df, "pd": pd, "plt": plt, "st": st}
                exec(code, exec_globals)
                result = exec_globals.get("result", None)

            with st.chat_message("assistant"):
                if isinstance(result, pd.DataFrame):
                    formatted_df = result.copy()
                    for col in formatted_df.columns:
                        if formatted_df[col].dtype in ['int64', 'float64']:
                            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:,}")
                    st.dataframe(formatted_df, use_container_width=False)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result,
                        "is_dataframe": True
                    })

                elif isinstance(result, pd.Series):
                    st.dataframe(result.to_frame(), use_container_width=False)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result.to_frame(),
                        "is_dataframe": True
                    })

                elif isinstance(result, (list, dict)):
                    df_result = pd.DataFrame(result)
                    st.dataframe(df_result, use_container_width=False)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": df_result,
                        "is_dataframe": True
                    })

                elif 'plt' in code or plt.get_fignums():
                    st.pyplot(plt.gcf())
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": plt.gcf(),
                        "is_plot": True
                    })
                    plt.clf()

                elif output.getvalue().strip():
                    st.markdown(output.getvalue())
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": output.getvalue().strip()
                    })
                else:
                    st.markdown("✅ Código ejecutado correctamente pero no se generó salida visible.")

        except Exception as e:
            st.error(f"❌ Error al ejecutar el código: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error al ejecutar el código: {e}"
            })
    else:
        st.warning("Por favor carga un archivo para analizar tus datos.")
