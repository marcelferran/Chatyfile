import io
import contextlib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai

# Función para iniciar el chat
def iniciar_chat(df):
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
    st.session_state.chat = chat
    # Inicializar el historial si no existe
    if 'history' not in st.session_state:
        st.session_state.history = [
            {"role": "system", "content": "🟢 Asistente activo. Pregunta lo que quieras sobre tu DataFrame."},
            {"role": "system", "content": "✏️ Escribe 'salir' para finalizar."}
        ]

# Función para mostrar el historial de conversación
def mostrar_historial():
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"**Usuario**: {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Asistente**: {msg['content']}")
            if "figure" in msg:
                st.pyplot(msg["figure"])
            elif "result_df" in msg:
                st.dataframe(msg["result_df"])
        else:
            st.markdown(f"{msg['content']}")

# Función para procesar la pregunta y generar la respuesta
def procesar_pregunta(pregunta, df):
    if pregunta.lower() == "salir":
        st.session_state.history.append({"role": "system", "content": "🛑 Chat finalizado."})
        return

    # Guardar la pregunta en el historial
    st.session_state.history.append({"role": "user", "content": pregunta})

    prompt = f"""
Tienes un DataFrame de pandas llamado df cargado en memoria.
Estas son las columnas reales: {', '.join(df.columns)}.
NO CAMBIES los nombres de las columnas.

Responde a esta pregunta escribiendo solamente el código Python que RETORNA la respuesta. NO uses print() ni muestres la salida directamente; solo retorna el resultado.

Para preguntas sobre productos, como 'urea', usa búsquedas flexibles que ignoren mayúsculas/minúsculas (por ejemplo, .str.contains('urea', case=False, na=False)) y consideren variaciones del texto (por ejemplo, 'Urea 46%', 'urea granulada').

Si la pregunta requiere una gráfica, genera la gráfica usando matplotlib y muéstrala con plt.figure(). En este caso, retorna None.

Si la pregunta pide mostrar el DataFrame o una tabla (por ejemplo, 'muestra las primeras 5 filas'), retorna el DataFrame directamente (por ejemplo, df.head(5)).

Pregunta:
{pregunta}
"""
    try:
        response = st.session_state.chat.send_message(prompt)
        code = response.text.strip("```python").strip("```").strip()

        if not code:
            st.session_state.history.append({"role": "assistant", "content": "❌ **No se generó código**. Intenta preguntar de otra forma."})
            return

        buffer = io.StringIO()
        exec_globals = {"df": df, "plt": plt, "pd": pd}
        fig = None

        with contextlib.redirect_stdout(buffer):
            try:
                # Ejecutar el código para capturar gráficas
                exec(code, exec_globals)
                if plt.get_fignums():
                    fig = plt.gcf()
                plt.close('all')
            except Exception as e:
                st.session_state.history.append({"role": "assistant", "content": f"❌ **Error al ejecutar el código**: {str(e)}"})
                return

        # Armar la respuesta sin mostrar el código
        DEBUG_MODE = False
        response_dict = {"role": "assistant", "content": ""}
        if DEBUG_MODE:
            response_dict["content"] += f"💻 **Código ejecutado**:\n```python\n{code}\n```"

        if fig:
            response_dict["figure"] = fig
            response_dict["content"] += "📊 **Gráfica generada:**"
        else:
            try:
                # Evaluar el código para obtener el resultado
                result = eval(code, {"df": df, "pd": pd})
                # Convertir el resultado en DataFrame si no lo es
                if isinstance(result, pd.DataFrame):
                    result_df = result
                elif isinstance(result, (list, tuple)):
                    result_df = pd.DataFrame(result, columns=["Resultado"])
                elif isinstance(result, (int, float, str)):
                    result_df = pd.DataFrame({"Resultado": [result]})
                elif result is None:
                    # Si el resultado es None, intentar manejar casos como df.head()
                    if "head(" in code or "tail(" in code or "df[" in code or "df." in code:
                        # Re-ejecutar el código en un entorno controlado para capturar el DataFrame
                        result_df = eval(code, {"df": df, "pd": pd})
                        if not isinstance(result_df, pd.DataFrame):
                            result_df = pd.DataFrame({"Resultado": ["No se pudo obtener un DataFrame"]})
                    else:
                        result_df = pd.DataFrame({"Resultado": ["No se retornó ningún valor"]})
                else:
                    result_df = pd.DataFrame({"Resultado": [str(result)]})

                # Redondear números a 2 decimales para columnas numéricas
                for col in result_df.select_dtypes(include=['float64', 'float32']).columns:
                    result_df[col] = result_df[col].round(2)

                response_dict["result_df"] = result_df
                response_dict["content"] += "\n📋 **Resultados:**"
            except Exception as e:
                # Si no se puede evaluar, usar la salida de texto como DataFrame
                output = buffer.getvalue().strip()
                if output:
                    result_df = pd.DataFrame({"Resultado": [output]})
                else:
                    result_df = pd.DataFrame({"Resultado": ["No se obtuvo ninguna salida"]})
                response_dict["result_df"] = result_df
                response_dict["content"] += "\n📋 **Resultados:**"

        # Guardar la respuesta en el historial
        st.session_state.history.append(response_dict)

    except Exception as e:
        st.session_state.history.append({"role": "assistant", "content": f"❌ **Algo salió mal con la consulta. Detalles**: {str(e)}"})

# Función para borrar el historial del chat
def borrar_historial():
    if st.button('Borrar chat'):
        st.session_state.history = [
            {"role": "system", "content": "🟢 Chat borrado. Comienza una nueva conversación."},
            {"role": "system", "content": "✏️ Escribe 'salir' para finalizar."}
        ]
        st.experimental_rerun()  # Refrescar la página para reflejar el historial limpio
