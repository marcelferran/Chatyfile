import streamlit as st
import pandas as pd
import google.generativeai as genai
import io
import contextlib
import matplotlib.pyplot as plt
import seaborn as sns
import copy

# Configura la página
st.set_page_config(page_title="ComprasGPT", layout="wide")
st.title("📊 ComprasGPT")

# Estilo CSS para mejorar la presentación de tablas y gráficos
st.markdown("""
    <style>
    .dataframe th, .dataframe td {
        white-space: normal !important;
        word-wrap: break-word;
        max-width: 200px;
        text-align: left;
    }
    .dataframe th {
        background-color: #f0f2f6;
        font-weight: bold;
    }
    /* Limitar tamaño de las tablas */
    .stDataFrame {
        max-width: 600px !important;
        max-height: 300px !important;
        overflow: auto;
    }
    /* Limitar tamaño de los gráficos */
    .stPlotlyChart, .element-container img {
        max-width: 600px !important;
        max-height: 300px !important;
        object-fit: contain;
    }
    </style>
""", unsafe_allow_html=True)

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
        st.metric("Número de filas", f"{df.shape[0]:,}")
    with col2:
        st.metric("Número de columnas", df.shape[1])
    
    # 3. Tabla con información de columnas
    st.header("3. Detalles de las columnas")
    column_info = pd.DataFrame({
        'Columna': df.columns,
        'Tipo de dato': [str(dtype) for dtype in df.dtypes],
        'Valores nulos': [df[col].isna().sum() for col in df.columns]
    })
    st.dataframe(column_info, use_container_width=False)
    
    # 4. Muestra de 10 filas
    st.header("4. Muestra de 10 filas")
    st.dataframe(df.head(10), use_container_width=False)
    
    # 5. Sección de preguntas
    st.header("5. Haz tus preguntas")
    st.write("Escribe tu pregunta sobre el DataFrame. Escribe 'salir' para limpiar el chat.")
    st.markdown("""
        **Ejemplos de preguntas:**
        - Dame una tabla con el top 10 de proveedores por número de orden de compra
        - Muestra un gráfico de barras del top 5 de proveedores por número de órdenes
        - Cuántas órdenes de compra hay en total
    """)

    # Mostrar historial de mensajes (excluyendo el mensaje actual)
    for message in st.session_state.messages[:-1]:  # Excluir el último mensaje
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("is_dataframe", False):
                st.markdown("📊 **Resultado**:")
                st.dataframe(message["content"], use_container_width=False)
            elif message["role"] == "assistant" and message.get("is_plot", False):
                st.markdown("📈 **Gráfico**:")
                st.pyplot(message["content"])
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

                Responde a esta pregunta escribiendo únicamente el código Python que da la respuesta.
                - Si la pregunta pide una tabla, un ranking (como un top 10), o cualquier resultado tabular, SIEMPRE devuelve un pandas DataFrame con columnas claras y nombres descriptivos en español (ejemplo: 'Proveedor', 'Número de Órdenes', 'Total Gastado'). Usa .reset_index() y .rename() si es necesario para evitar Series.
                - Si la pregunta incluye un año (como 2024), filtra el DataFrame usando la columna de fecha relevante (por ejemplo, 'Fecha') y extrae el año con .dt.year.
                - Si la pregunta pide un total gastado, usa la columna relevante (por ejemplo, 'Total') para la suma.
                - Si la pregunta pide un gráfico (como un gráfico de barras, pastel, etc.), usa matplotlib o seaborn, crea el gráfico con `plt.figure(figsize=(8, 4))` para un tamaño compacto, y muestra el gráfico en Streamlit con `st.pyplot(plt.gcf())`. Asegúrate de importar las librerías necesarias (matplotlib.pyplot como plt, seaborn como sns). NO uses plt.show(), plt.clf(), plt.close(), ni cualquier otra función que cierre o limpie la figura.
                - Asegúrate de que el código sea conciso y no incluya comentarios, prints, ni texto explicativo innecesarios.
                - Si la pregunta no requiere una tabla ni un gráfico, devuelve el resultado adecuado (como un número o texto), pero evita usar print a menos que se pida explícitamente.

                Ejemplo 1:
                Pregunta: "Dame una tabla con el top 10 de proveedores por número de orden de compra"
                Código: df['Proveedor'].value_counts().head(10).reset_index().rename(columns={{'index': 'Proveedor', 'Proveedor': 'Número de Órdenes'}})

                Ejemplo 2:
                Pregunta: "Muestra un gráfico de barras del top 5 de proveedores por número de órdenes"
                Código: 
                import matplotlib.pyplot as plt
                import seaborn as sns
                top_5 = df['Proveedor'].value_counts().head(5)
                plt.figure(figsize=(8, 4))
                sns.barplot(x=top_5.values, y=top_5.index)
                plt.xlabel('Número de Órdenes')
                plt.ylabel('Proveedor')
                plt.title('Top 5 Proveedores por Número de Órdenes')
                st.pyplot(plt.gcf())

                Ejemplo 3:
                Pregunta: "Dame una tabla con el top 10 de proveedores por número de orden de compra y total en 2024"
                Código:
                df_2024 = df[df['Fecha'].dt.year == 2024]
                result = df_2024.groupby('Proveedor').agg({{'Orden de Compra': 'count', 'Total': 'sum'}}).reset_index().rename(columns={{'Orden de Compra': 'Número de Órdenes', 'Total': 'Total Gastado'}}).sort_values('Número de Órdenes', ascending=False).head(10)

                Pregunta:
                {pregunta}
                """
                response = st.session_state.chat.send_message(prompt)
                code = response.text.strip("`python\n").strip("`").strip()
                
                # Opcional: Descomentar para depurar el código generado
                # st.write(f"**Debug: Código generado**:\n```python\n{code}\n```")
                
                # Ejecutar el código
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
                            # Intentar evaluar el código como expresión; si falla, ejecutarlo
                            result = eval(code, exec_globals)
                        except:
                            # Si eval falla, ejecutar el código (para plots or print statements)
                            exec(code, exec_globals)
                            result = None
                
                output = buffer.getvalue()
                
                # Mostrar la respuesta
                with st.chat_message("assistant"):
                    if isinstance(result, pd.DataFrame):
                        st.markdown("📊 **Resultado**:")
                        # Formatear números en el DataFrame para mejor legibilidad
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
                        # El gráfico ya se mostró en el código ejecutado; solo agregar header
                        st.markdown("📈 **Gráfico**:")
                        # Almacenar para el historial
                        fig = copy.deepcopy(plt.gcf())
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": fig,
                            "is_plot": True
                        })
                        # Limpiar la figura después de almacenar
                        plt.clf()
                    elif output.strip():
                        st.markdown(f"💬 **Resultado**:\n\n{output}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": output
                        })
                    elif result is not None:
                        st.markdown(f"💬 **Resultado**: {result}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": str(result)
                        })
                    else:
                        st.error(f"❌ No se generó una tabla, gráfico o resultado claro para la consulta.")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "❌ No se generó una tabla, gráfico o resultado claro para la consulta."
                        })
                
            except Exception as e:
                with st.chat_message("assistant"):
                    st.error(f"❌ Error al procesar o ejecutar: {str(e)}")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Error al procesar o ejecutar: {str(e)}"})
        
        # Actualizar la interfaz solo si no es un gráfico
        if 'st.pyplot' not in code:
            st.rerun()

else:
    st.info("Por favor, carga un archivo para comenzar.")
