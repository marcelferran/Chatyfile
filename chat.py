import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from contextlib import redirect_stdout
import google.generativeai as genai

st.set_page_config(page_title="Compras-GPT", layout="centered")
st.title("🤖 Compras-GPT")
st.caption("Prototipo desarrollado por Marcel F. Castro Ponce de Leon")

# Estilo CSS mejorado para tablas
st.markdown("""
    <style>
    .dataframe {
        font-size: 14px;
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    .dataframe th, .dataframe td {
        padding: 10px;
        text-align: left;
        border: 1px solid #ccc;
        vertical-align: top;
    }
    .dataframe th {
        background-color: #e6e6e6;
        font-weight: bold;
        text-align: left;
    }
    .dataframe tr:nth-child(even) {
        background-color: #f8f8f8;
    }
    .dataframe tr:hover {
        background-color: #f0f0f0;
    }
    </style>
""", unsafe_allow_html=True)

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
        st.dataframe(column_info, use_container_width=True)

        st.markdown("🔍 **Vista previa aleatoria (10 filas):**")
        st.dataframe(df.sample(10), use_container_width=True)

        # Actualizar contexto del modelo con columnas reales
        columnas = ", ".join(df.columns)
        st.session_state.chat.send_message(f"Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: {columnas}. No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están.")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

# Función para formatear DataFrames
def format_dataframe(df):
    formatted_df = df.copy()
    # Reiniciar el índice para evitar índices desordenados
    if formatted_df.index.name is not None or not formatted_df.index.is_integer():
        formatted_df = formatted_df.reset_index(drop=True)
    
    for col in formatted_df.columns:
        if formatted_df[col].dtype in ['float64', 'float32']:
            formatted_df[col] = formatted_df[col].round(2).astype(str)  # Convertir a string para evitar problemas de formato
        elif formatted_df[col].dtype in ['datetime64[ns]', 'datetime64']:
            formatted_df[col] = formatted_df[col].dt.strftime('%Y-%m-%d')  # Formato de fecha
        elif formatted_df[col].dtype == 'object':
            formatted_df[col] = formatted_df[col].astype(str).fillna('N/A')  # Convertir a string y manejar nulos
        else:
            formatted_df[col] = formatted_df[col].astype(str)  # Convertir todo a string para consistencia
    
    return formatted_df

# Interfaz de chat
if st.session_state.df is not None:
    prompt = st.chat_input("Haz una pregunta sobre tus datos o pide un análisis...")

    if prompt:
        st.chat_message("user").markdown(prompt)

        try:
            # Construir prompt para el modelo con instrucción adicional para tablas
            full_prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(st.session_state.df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.
Si el resultado es una tabla, asegúrate de devolver un DataFrame con columnas claras y sin índices innecesarios (usa `reset_index()` si es necesario).

Pregunta:
{prompt}
"""
            response = st.session_state.chat.send_message(full_prompt)
            code = response.text.strip("`python\n").strip("`").strip()

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
                    formatted_result = format_dataframe(result)
                    st.dataframe(formatted_result, use_container_width=True, hide_index=True)
                elif isinstance(result, pd.Series):
                    st.markdown("📊 **Resultado (serie):**")
                    formatted_result = format_dataframe(result.to_frame().reset_index())
                    st.dataframe(formatted_result, use_container_width=True, hide_index=True)
                elif isinstance(result, (list, dict)):
                    st.markdown("📊 **Resultado (convertido en tabla):**")
                    formatted_result = format_dataframe(pd.DataFrame(result))
                    st.dataframe(formatted_result, use_container_width=True, hide_index=True)
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
