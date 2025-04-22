import io
import contextlib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai
import numpy as np
import ast

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

Responde a esta pregunta escribiendo SOLO el código Python que PRODUCE el resultado final. Para tablas, devuelve un DataFrame. Para gráficos, genera la gráfica con matplotlib y escribe None como la última línea. NO uses print(), return, .tolist(), .values, pandas.plot, ni muestres texto explicativo; solo escribe el código Python válido.

Instrucciones:
- Para tablas o datos calculados, siempre devuelve un DataFrame usando pd.DataFrame, .reset_index(), o métodos equivalentes.
- Para conteos (por ejemplo, 'cuántos proveedores'), usa .nunique() o .count() y envuelve el resultado en un DataFrame.
- Para sumas (por ejemplo, 'total comprado'), usa .sum() y devuelve un DataFrame.
- Para búsquedas de productos como 'urea', usa .str.contains('urea', case=False, na=False).
- Para listas con valores asociados (por ejemplo, 'lista de proveedores y monto'), usa .groupby() y .sum() para crear un DataFrame.
- Para intersecciones (por ejemplo, 'proveedores en Refacciones y Mano de Obra'), usa .isin() y devuelve un DataFrame.
- Para conteos de múltiples categorías (por ejemplo, 'proveedores de Refacciones y Mano de Obra'), crea un DataFrame con una columna para la categoría y otra para el total.
- Para gráficos, usa matplotlib (plt.figure(figsize=(4, 4)), plt.pie(), etc.), incluye etiquetas y porcentajes si es necesario, y escribe None como la última línea. Usa un tamaño de figura pequeño (4x4 pulgadas) para Streamlit.
- Usa la columna 'Categoría' para filtros de categorías como 'Refacciones' o 'Mano de Obra'.
- Usa las columnas exactas del DataFrame proporcionadas.

Ejemplos:
- Pregunta: "Muestra las primeras 5 filas"
  Código: df.head(5)
- Pregunta: "Cuantos proveedores de Urea hay?"
  Código: pd.DataFrame({{'Resultado': [df[df['Producto'].str.contains('urea', case=False, na=False)]['Proveedor'].nunique()]}})
- Pregunta: "Cuanto es el total comprado de refacciones 'urea' en 2025"
  Código: pd.DataFrame({{'Resultado': [df[(df['Producto'].str.contains('urea', case=False, na=False)) & (df['Año'] == 2025)]['Cantidad'].sum()]}})
- Pregunta: "Cuántos proveedores venden urea, lista y monto comprado"
  Código: df[df['Producto'].str.contains('urea', case=False, na=False)].groupby('Proveedor')['Cantidad'].sum().reset_index(name='Monto Total')
- Pregunta: "Proveedores en Refacciones y Mano de Obra"
  Código: pd.DataFrame({{'Proveedor': df[df['Categoría'] == 'Refacciones']['Proveedor'].unique()}}).merge(pd.DataFrame({{'Proveedor': df[df['Categoría'] == 'Mano de Obra']['Proveedor'].unique()}}), on='Proveedor')
- Pregunta: "Indica cuantos proveedores son de Refacciones y también cuantos de Mano de Obra"
  Código: pd.DataFrame({{'Categoría': ['Refacciones', 'Mano de Obra'], 'Total Proveedores': [df[df['Categoría'] == 'Refacciones']['Proveedor'].nunique(), df[df['Categoría'] == 'Mano de Obra']['Proveedor'].nunique()]}})
- Pregunta: "Gráfico de pastel del top 5 de proveedores por ventas totales"
  Código:
    top_5 = df.groupby('Proveedor')['Cantidad'].sum().nlargest(5)
    plt.figure(figsize=(4, 4))
    plt.pie(top_5, labels=top_5.index, autopct='%1.1f%%')
    None

Pregunta:
{pregunta}
"""
    try:
        response = st.session_state.chat.send_message(prompt)
        code = response.text.strip("```python").strip("```").strip()

        if not code:
            st.session_state.history.append({"role": "assistant", "content": "❌ **No se generó código**. Intenta preguntar de otra forma."})
            return

        # Validar que el código sea sintácticamente válido
        try:
            ast.parse(code)
        except SyntaxError as e:
            st.session_state.history.append({"role": "assistant", "content": f"❌ **Código generado inválido**: {code}\n**Error**: {str(e)}. Intenta reformular la pregunta."})
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
            st.session_state.history.append({"role": "assistant", "content": f"❌ **Error de sintaxis en el código generado**: {code}\n**Error**: {str(e)}. Intenta reformular la pregunta."})
            return
        except Exception as e:
            st.session_state.history.append({"role": "assistant", "content": f"❌ **Error al ejecutar el código**: {code}\n**Error**: {str(e)}. Intenta reformular la pregunta."})
            return

        # Armar la respuesta
        DEBUG_MODE = True  # Habilitado para depurar el código generado
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
