import io
import contextlib
import numpy as np
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

Responde a esta pregunta escribiendo SOLO el código Python que PRODUCE el resultado final como un DataFrame. NO uses print(), return, .tolist(), .values, ni muestres la salida directamente; escribe solo la expresión o las operaciones que generan un DataFrame.

Instrucciones:
- Siempre devuelve un DataFrame, incluso para listas, conteos, o intersecciones. Usa pd.DataFrame, .reset_index(), o métodos equivalentes para asegurar que el resultado sea un DataFrame.
- Para preguntas que piden mostrar una tabla o DataFrame (por ejemplo, 'muestra las primeras 5 filas'), usa operaciones como df.head(5).
- Para preguntas que piden contar elementos (por ejemplo, 'cuántos proveedores'), usa .nunique() o .count() y envuelve el resultado en un DataFrame.
- Para preguntas que piden sumas o totales (por ejemplo, 'total comprado'), usa .sum() y devuelve un DataFrame.
- Para preguntas sobre productos como 'urea', usa búsquedas flexibles con .str.contains('urea', case=False, na=False) y considera variaciones (por ejemplo, 'Urea 46%', 'urea granulada').
- Para preguntas que piden listas con valores asociados (por ejemplo, 'lista de proveedores y monto comprado'), usa .groupby() y .sum() para crear un DataFrame con las columnas adecuadas.
- Para preguntas que piden intersecciones (por ejemplo, 'proveedores en Refacciones y Mano de Obra'), filtra por cada categoría, encuentra la intersección de proveedores usando .isin(), y devuelve un DataFrame con los resultados.
- Si la pregunta requiere una gráfica, genera la gráfica con matplotlib, usa plt.figure(), y escribe None como la última línea.
- Asegúrate de usar las columnas exactas del DataFrame proporcionadas.

Ejemplos:
- Pregunta: "Muestra las primeras 5 filas"
  Código: df.head(5)
- Pregunta: "Cuántos productos contienen 'urea'"
  Código: pd.DataFrame({{'Resultado': [df[df['Producto'].str.contains('urea', case=False, na=False)]['Producto'].count()]}})
- Pregunta: "Total de Cantidad para 'urea' en 2025"
  Código: pd.DataFrame({{'Resultado': [df[(df['Producto'].str.contains('urea', case=False, na=False)) & (df['Año'] == 2025)]['Cantidad'].sum()]}})
- Pregunta: "Cuántos proveedores venden urea, lista y monto comprado"
  Código: df[df['Producto'].str.contains('urea', case=False, na=False)].groupby('Proveedor')['Cantidad'].sum().reset_index(name='Monto Total')
- Pregunta: "Proveedores en Refacciones y Mano de Obra"
  Código: pd.DataFrame({{'Proveedor': df[df['Categoría'] == 'Refacciones']['Proveedor'].unique()}}).merge(pd.DataFrame({{'Proveedor': df[df['Categoría'] == 'Mano de Obra']['Proveedor'].unique()}}), on='Proveedor')

Pregunta:
{pregunta}
"""
    try:
        response = st.session_state.chat.send_message(prompt)
        code = response.text.strip("```python").strip("```").strip()

        if not code:
            st.session_state.history.append({"role": "assistant", "content": "❌ **No se generó código**. Intenta preguntar de otra forma."})
            return

        # Limpiar el código para evitar 'return' o líneas inválidas
        code_lines = [line for line in code.split('\n') if not line.strip().startswith('return ')]
        code = '\n'.join(code_lines)

        # Entorno para ejecutar el código
        exec_globals = {"df": df, "plt": plt, "pd": pd, "np": np, "__result__": None}
        fig = None

        try:
            # Ejecutar el código y capturar el resultado
            exec(f"__result__ = {code}", exec_globals)
            result = exec_globals["__result__"]
            # Capturar gráfica si existe
            if plt.get_fignums():
                fig = plt.gcf()
            plt.close('all')
        except SyntaxError as e:
            st.session_state.history.append({"role": "assistant", "content": f"❌ **Error de sintaxis en el código generado**: {str(e)}. Intenta reformular la pregunta."})
            return
        except Exception as e:
            st.session_state.history.append({"role": "assistant", "content": f"❌ **Error al ejecutar el código**: {str(e)}. Intenta reformular la pregunta."})
            return

        # Armar la respuesta
        DEBUG_MODE = False
        response_dict = {"role": "assistant", "content": ""}
        if DEBUG_MODE:
            response_dict["content"] += f"💻 **Código ejecutado**:\n```python\n{code}\n```"

        if fig:
            response_dict["figure"] = fig
            response_dict["content"] += "📊 **Gráfica generada:**"
        else:
            # Convertir el resultado en DataFrame
            if isinstance(result, pd.DataFrame):
                result_df = result
            elif isinstance(result, pd.Series):
                result_df = result.reset_index(name='Resultado')
            elif isinstance(result, (list, tuple, np.ndarray)):
                # Convertir listas o arrays en DataFrame con columna 'Proveedor' si la pregunta menciona proveedores
                if 'proveedor' in pregunta.lower():
                    result_df = pd.DataFrame({'Proveedor': result})
                else:
                    result_df = pd.DataFrame({'Resultado': result})
            elif isinstance(result, (int, float, str)):
                result_df = pd.DataFrame({'Resultado': [result]})
            elif result is None:
                result_df = pd.DataFrame({'Resultado': ['No se retornó ningún valor. Intenta reformular la pregunta.']})
            else:
                result_df = pd.DataFrame({'Resultado': [str(result)]})

            # Redondear números a 2 decimales para columnas numéricas
            for col in result_df.select_dtypes(include=['float64', 'float32']).columns:
                result_df[col] = result_df[col].round(2)

            response_dict["result_df"] = result_df
            response_dict["content"] += "\n📋 **Resultados:**"

        # Guardar la respuesta en el historial
        st.session_state.history.append(response_dict)

    except Exception as e:
        st.session_state.history.append({"role": "assistant", "content": f"❌ **Algo salió mal con la consulta. Detalles**: {str(e)}. Intenta reformular la pregunta."})

# Función para borrar el historial del chat
def borrar_historial():
    if st.button('Borrar chat'):
        st.session_state.history = [
            {"role": "system", "content": "🟢 Chat borrado. Comienza una nueva conversación."},
            {"role": "system", "content": "✏️ Escribe 'salir' para finalizar."}
        ]
        st.experimental_rerun()  # Refrescar la página para reflejar el historial limpio
