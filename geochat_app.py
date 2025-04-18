import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from contextlib import redirect_stdout

st.set_page_config(page_title="Gemini Chatbot", layout="centered")
st.title("🤖 Gemini Data Analyst")
st.caption("Prototipo desarrollado por Marcel F. Castro")

# Inicializar estado de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

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

    # Cargar datos si hay archivo subido
    uploaded_file = st.sidebar.file_uploader("Carga tu archivo CSV o Excel", type=["csv", "xlsx"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Contexto básico para el modelo
        context = f"Este es un DataFrame llamado df con columnas: {', '.join(df.columns)}. Responde en español."

        from openai import OpenAI
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        code = response.choices[0].message.content

        # Mostrar respuesta como código
        with st.chat_message("assistant"):
            st.markdown("```python\n" + code + "\n```")

        # Ejecutar código
        try:
            output = io.StringIO()
            with redirect_stdout(output):
                exec_globals = {"df": df, "pd": pd, "plt": plt, "st": st}
                exec(code, exec_globals)
                result = exec_globals.get("result", None)

            # Mostrar resultados
            if isinstance(result, pd.DataFrame):
                st.markdown("📊 **Resultado:**")
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
                st.markdown("📊 **Resultado (serie convertida en tabla):**")
                st.dataframe(result.to_frame(), use_container_width=False)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result.to_frame(),
                    "is_dataframe": True
                })

            elif isinstance(result, (list, dict)):
                st.markdown("📊 **Resultado (convertido en tabla):**")
                df_result = pd.DataFrame(result)
                st.dataframe(df_result, use_container_width=False)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": df_result,
                    "is_dataframe": True
                })

            elif 'plt' in code or plt.get_fignums():
                st.markdown("📈 **Gráfico generado**")
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
