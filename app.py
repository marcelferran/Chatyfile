import streamlit as st
import pandas as pd
from engine import process_question

# Configuración de la página
st.set_page_config(page_title="Chatyfile", page_icon="🤖", layout="wide")

# Aplicar estilos de diseño personalizados (definidos en layout.py si corresponde)
try:
    import layout
    layout.apply_styles()  # Supongamos que layout.py define esta función para aplicar CSS
except ImportError:
    pass

# Inicializar estado de la sesión
if "history" not in st.session_state:
    st.session_state["history"] = []
if "df" not in st.session_state:
    st.session_state["df"] = None

# Barra lateral para cargar archivo CSV
st.sidebar.title("Cargar archivo CSV")
st.sidebar.info("Selecciona un archivo CSV")
uploaded_file = st.sidebar.file_uploader("Drag and drop file here\nLimit 200MB per file • CSV", type=["csv"])
if uploaded_file is not None:
    try:
        st.session_state["df"] = pd.read_csv(uploaded_file)
        st.session_state["history"] = []  # Reiniciar historial al cargar un nuevo archivo
        st.sidebar.success("¡Archivo cargado exitosamente!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el CSV: {e}")
        st.session_state["df"] = None

# Título y subtítulo principal
st.title("Chatyfile")
st.subheader("Tu asistente de análisis de datos CSV, rápido y sencillo.")
st.markdown("🤖 **Asistente de DataFrame**")

# Verificar que haya un DataFrame cargado antes de permitir preguntas
if st.session_state["df"] is None:
    st.write("📂 Por favor, carga un archivo CSV para comenzar.")
else:
    # Cuadro de entrada de pregunta del usuario
    user_question = st.text_input("Escribe tu pregunta aquí...", key="question_input")
    send_clicked = st.button("Enviar")
    if send_clicked and user_question:
        # Agregar mensaje del usuario al historial
        st.session_state["history"].append({"role": "user", "content": user_question})
        # Obtener respuesta usando el motor (LLM + ejecución de código)
        with st.spinner("Analizando..."):
            text_output, df_output, image_output, error = process_question(user_question, st.session_state["df"])
        # Procesar la respuesta del asistente
        if error:
            # En caso de error, mostrar el mensaje de error
            assistant_msg = {"role": "assistant", "type": "text", "content": f"❌ {error}"}
        else:
            if text_output and df_output is not None and image_output is None:
                # Respuesta con texto explicativo y una tabla (DataFrame)
                assistant_msg = {"role": "assistant", "type": "dataframe", "content": df_output, "text": text_output}
            elif text_output and image_output is not None:
                # Respuesta con texto explicativo y una imagen (gráfico)
                assistant_msg = {"role": "assistant", "type": "image", "content": image_output, "text": text_output}
            elif df_output is not None:
                # Respuesta solo como tabla (DataFrame)
                assistant_msg = {"role": "assistant", "type": "dataframe", "content": df_output}
            elif image_output is not None:
                # Respuesta solo como imagen (gráfico)
                assistant_msg = {"role": "assistant", "type": "image", "content": image_output}
            elif text_output:
                # Respuesta solo de texto
                assistant_msg = {"role": "assistant", "type": "text", "content": text_output}
            else:
                # Sin salida generada
                assistant_msg = {"role": "assistant", "type": "text", "content": "No se generó ningún resultado"}
        # Agregar mensaje del asistente al historial
        st.session_state["history"].append(assistant_msg)
        # Limpiar el campo de entrada de texto para la siguiente pregunta
        st.session_state["question_input"] = ""

    # Mostrar el historial de la conversación
    for msg in st.session_state["history"]:
        if msg["role"] == "user":
            # Mensaje del usuario (burbuja azul)
            st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            # Mensaje del asistente
            if msg.get("text"):
                # Mostrar texto explicativo del asistente (si lo hay) en burbuja gris
                st.markdown(f"<div class='assistant-bubble'>{msg['text']}</div>", unsafe_allow_html=True)
            # Mostrar contenido principal de la respuesta del asistente
            if msg["type"] == "dataframe":
                # Mostrar DataFrame en formato interactivo
                st.dataframe(msg["content"])
            elif msg["type"] == "image":
                # Mostrar gráfico/imágen generado
                st.image(msg["content"], use_column_width=True)
            elif msg["type"] == "text" and not msg.get("text"):
                # Mostrar respuesta de solo texto en burbuja gris
                st.markdown(f"<div class='assistant-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
