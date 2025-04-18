import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import traceback  # Para mostrar trazas de error

# Configura la página
st.set_page_config(page_title="ComprasGPT", layout="wide")
st.title("📊 ComprasGPT")

# Estilo CSS
st.markdown("""
    <style>
    .dataframe th, .dataframe td {
        white-space: normal !important;
        word-wrap: break-word;
        max-width: 500px;
        text-align: left;
    }
    .dataframe th {
        background-color: #f0f2f6;
        font-weight: bold;
    }
    .stDataFrame {
        max-width: 2000px !important;
        max-height: 1000px !important;
        overflow: auto;
    }
    .stPlotlyChart, .element-container img {
        max-width: 2000px !important;
        max-height: 1000px !important;
        object-fit: contain;
    }
    </style>
""", unsafe_allow_html=True)

# Configura la API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# Inicializa chat
def initialize_chat(df):
    return model.start_chat(history=[
        {"role": "user", "parts": ["Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: " + ", ".join(df.columns) + ". No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están."]},
        {"role": "model", "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]}
    ])

# Estado de sesión
if 'df' not in st.session_state: st.session_state.df = None
if 'chat' not in st.session_state: st.session_state.chat = None
if 'messages' not in st.session_state: st.session_state.messages = []

# Subida de archivo
st.header("1. Cargar archivo")
uploaded_file = st.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state.df = df
        st.session_state.chat = initialize_chat(df)
        st.success("✅ Archivo cargado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {str(e)}")

# Visualización si hay DataFrame
if st.session_state.df is not None:
    df = st.session_state.df
    
    st.header("2. Resumen del DataFrame")
    col1, col2 = st.columns(2)
    col1.metric("Número de filas", f"{df.shape[0]:,}")
    col2.metric("Número de columnas", df.shape[1])

    st.header("3. Detalles de las columnas")
    column_info = pd.DataFrame({
        'Columna': df.columns,
        'Tipo de dato': [str(dtype) for dtype in df.dtypes],
        'Valores nulos': [df[col].isna().sum() for col in df.columns]
    })
    st.dataframe(column_info, use_container_width=False)

    st.header("4. Muestra de 10 filas")
    st.dataframe(df.head(10), use_container_width=False)

    st.header("5. Haz tus preguntas")
    st.write("Escribe tu pregunta sobre el DataFrame. Escribe 'salir' para limpiar el chat.")
    st.markdown("""
        **Ejemplos:**
        - Top 10 proveedores por número de orden de compra
        - Gráfico de barras del top 5 de proveedores por órdenes
        - Cuántas órdenes de compra hay en total
    """)

    # Mostrar historial de mensajes previos
    for message in st.session_state.messages[:-1]:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("is_dataframe", False):
                st.markdown("📊 **Resultado**:")
                st.dataframe(message["content"], use_container_width=False)
            elif message["role"] == "assistant" and message.get("is_plot", False):
                st.markdown("📈 **Gráfico**:")
                st.pyplot(message["content"])
            else:
                st.markdown(message["content"])

    pregunta = st.chat_input("🤔 Tu pregunta:")

    if pregunta:
        with st.chat_message("user"):
            st.markdown(pregunta)
        st.session_state.messages.append({"role": "user", "content": pregunta})

        if pregunta.lower() == "salir":
            st.session_state.messages = []
            st.session_state.chat = initialize_chat(df)
            st.success("👋 Chat reiniciado.")
        else:
            try:
                prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo únicamente el código Python que da la respuesta...
(PARTE OMITIDA PARA BREVEDAD, MISMO PROMPT)
                Pregunta:
                {pregunta}
                """

                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("`python\n").strip("`").strip()

                with st.expander("📦 Código generado"):
                    st.code(code, language="python")

                exec_globals = {
                    "df": df,
                    "pd": pd,
                    "plt": plt,
                    "sns": sns,
                    "st": st
                }
                buffer = io.StringIO()

                with contextlib.redirect_stdout(buffer):
                    with st.spinner("Procesando..."):
                        try:
                            result = eval(code, exec_globals)
                        except:
                            exec(code, exec_globals)
                            result = None

                output = buffer.getvalue()

                with st.chat_message("assistant"):
                    if isinstance(result, pd.DataFrame):
                        st.markdown("📊 **Resultado**:")
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
                    elif 'st.pyplot' in code:
                        st.markdown("📈 **Gráfico generado**")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": plt.gcf(),
                            "is_plot": True
                        })
                    elif output.strip():
                        st.markdown(output)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": output.strip()
                        })
                    else:
                        st.markdown("✅ Código ejecutado correctamente pero no se generó salida visible.")
            except Exception as e:
                st.error("❌ Ocurrió un error al ejecutar el código.")
                st.exception(e)
                st.text("📋 Detalles del error:")
                st.text(traceback.format_exc())
