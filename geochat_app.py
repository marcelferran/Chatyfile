import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib

# Configura la página
st.set_page_config(page_title="ComprasGPT", layout="wide")
st.title("📊 ComprasGPT")

# Configura la API key
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash')

# Función para inicializar el chat con el modelo
def initialize_chat(df):
    return model.start_chat(history=[
        {
            "role": "user",
            "parts": ["Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: " + ", ".join(df.columns) + ". No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están."]
        },
        {
            "role": "model",
            "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
        }
    ])

# Estado de la sesión para almacenar el DataFrame y el chat
if 'df' not in st.session_state:
    st.session_state.df = None
if 'chat' not in st.session_state:
    st.session_state.chat = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Sección para cargar el archivo
st.header("1. Cargar archivo")
uploaded_file = st.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    try:
        # Leer el archivo según su extensión
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Almacenar el DataFrame en el estado de la sesión
        st.session_state.df = df
        st.session_state.chat = initialize_chat(df)
        st.success("✅ Archivo cargado correctamente.")
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {str(e)}")

# Si hay un DataFrame cargado, mostrar la información
if st.session_state.df is not None:
    df = st.session_state.df
    
    # 2. Resumen de filas y columnas
    st.header("2. Resumen del DataFrame")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Número de filas", df.shape[0])
    with col2:
        st.metric("Número de columnas", df.shape[1])
    
    # 3. Tabla con información de columnas
    st.header("3. Detalles de las columnas")
    column_info = pd.DataFrame({
        'Columna': df.columns,
        'Tipo de dato': [str(dtype) for dtype in df.dtypes],
        'Valores nulos': [df[col].isna().sum() for col in df.columns]
    })
    st.dataframe(column_info, use_container_width=True, hide_index=True)
    
    # 4. Muestra de 10 filas
    st.header("4. Muestra de 10 filas")
    st.dataframe(df.head(10), use_container_width=True)
    
    # 5. Sección de preguntas
    st.header("5. Haz tus preguntas")
    st.write("Escribe tu pregunta sobre el DataFrame. Escribe 'salir' para limpiar el chat.")

    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("is_dataframe", False):
                st.dataframe(message["content"], use_container_width=True)
            else:
                st.markdown(message["content"])
    
    # Entrada de la pregunta
    pregunta = st.chat_input("🤔 Tu pregunta:")
    
    if pregunta:
        # Mostrar la pregunta del usuario
        with st.chat_message("user"):
            st.markdown(pregunta)
        
        # Agregar la pregunta al historial
        st.session_state.messages.append({"role": "user", "content": pregunta})
        
        if pregunta.lower() == "salir":
            st.session_state.messages = []
            st.session_state.chat = initialize_chat(df)
            st.success("👋 Chat reiniciado.")
        else:
            try:
                # Preparar el prompt
                prompt = f"""
                Tienes un DataFrame de pandas llamado `df` cargado en memoria.
                Estas son las columnas reales: {', '.join(df.columns)}.
                NO CAMBIES los nombres de las columnas.

                Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.
                Si la pregunta pide una tabla o un ranking (como un top 10), devuelve un DataFrame con columnas claras y nombres descriptivos.
                Por ejemplo, para un top 10 de proveedores por número de órdenes de compra, usa nombres como 'Proveedor' y 'Número de Órdenes'.

                Pregunta:
                {pregunta}
                """
                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("`python\n").strip("`").strip()
                
                # Ejecutar el código
                exec_globals = {"df": df, "pd": pd}
                buffer = io.StringIO()
                
                with contextlib.redirect_stdout(buffer):
                    try:
                        # Ejecutar el código y capturar el resultado
                        result = eval(code, exec_globals) if 'print' not in code else exec(code, exec_globals)
                    except Exception as e:
                        st.error(f"❌ Error al ejecutar el código: {str(e)}")
                        st.session_state.messages.append({"role": "assistant", "content": f"❌ Error al ejecutar el código: {str(e)}"})
                        st.rerun()
                
                output = buffer.getvalue()
                
                # Mostrar la respuesta
                with st.chat_message("assistant"):
                    if isinstance(result, pd.DataFrame):
                        st.markdown(f"📊 **Resultado**:")
                        st.dataframe(result, use_container_width=True)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result,
                            "is_dataframe": True
                        })
                    elif output.strip():
                        st.markdown(f"💬 **Resultado**:\n\n{output}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": output
                        })
                    else:
                        st.markdown("✅ Código ejecutado sin salida.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "✅ Código ejecutado sin salida."
                        })
                
            except Exception as e:
                with st.chat_message("assistant"):
                    st.error(f"❌ Error al procesar o ejecutar: {str(e)}")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Error al procesar o ejecutar: {str(e)}"})
        
        # Actualizar la interfaz
        st.rerun()

else:
    st.info("Por favor, carga un archivo para comenzar.")
