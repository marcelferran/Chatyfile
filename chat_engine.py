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
                st.pyplot(msg["figure"], use_container_width=False)
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

Responde a esta pregunta escribiendo SOLO el código Python que PRODUCE el resultado final. Para tablas, devuelve un DataFrame. Para gráficos, genera la gráfica con matplotlib y escribe None como la última línea. NO uses print(), return, .tolist(), .values, pandas.plot, import statements (como import pandas as pd), ni muestres texto explicativo; solo escribe el código Python válido usando pd, plt, np, que ya están disponibles. Usa EXCLUSIVAMENTE 'pd' como el alias para pandas (por ejemplo, pd.DataFrame, pd.Series); no uses otros alias como 'd'. NO definas funciones auxiliares (como def mi_funcion(...)); escribe el código directamente en una sola expresión o bloque.

Instrucciones:
- Para tablas o datos calculados, siempre devuelve un DataFrame usando pd.DataFrame, .reset_index(), o métodos equivalentes.
- Para conteos de valores únicos (por ejemplo, 'cuántos tipos'), usa .nunique() y envuelve el resultado en un DataFrame.
- Para sumas (por ejemplo, 'total comprado'), usa .sum() y devuelve un DataFrame. Usa una columna numérica adecuada según la pregunta.
- Para búsquedas de texto (por ejemplo, 'urea'), usa .str.contains('texto', case=False, na=False).
- Para listas de valores únicos (por ejemplo, 'dame los nombres'), usa .unique() y .dropna(), y convierte la lista en una cadena con ', '.join() si es necesario.
- Para listas con valores asociados (por ejemplo, 'lista de X y su total'), usa .groupby() y .sum() para crear un DataFrame.
- Para identificar el valor máximo dentro de grupos anidados (por ejemplo, 'qué X generó más Y en cada Z'), usa .groupby(), .sum(), .sort_values(), y .first() para seleccionar el valor máximo por grupo.
- Para intersecciones (por ejemplo, 'valores en A y B'), usa .isin() y devuelve un DataFrame.
- Para conteos de múltiples categorías, crea un DataFrame con una columna para la categoría y otra para el total.
- Para gráficos, usa matplotlib (plt.figure(figsize=(8, 6), dpi=100), plt.pie(), plt.bar(), etc.), incluye etiquetas y porcentajes si es necesario, y escribe None como la última línea. No modifiques el tamaño de la figura; usa siempre figsize=(8, 6) y dpi=100 para todas las gráficas en Streamlit. Para gráficas de barras que comparan grupos, alinea los datos con reindex si es necesario, rellenando con ceros.
- Usa las columnas exactas del DataFrame proporcionadas.

Ejemplos:
- Pregunta: "Muestra las primeras 5 filas"
  Código: df.head(5)
- Pregunta: "Cuántos tipos de Litología hay y dame sus nombres"
  Código: pd.DataFrame({'Cantidad': [df['Litologia'].nunique()], 'Litologias': [', '.join(df['Litologia'].dropna().unique())]})
- Pregunta: "Cuántos valores únicos hay en la columna X"
  Código: pd.DataFrame({'Resultado': [df['X'].nunique()]}})
- Pregunta: "Dame una lista de los valores únicos en la columna Y"
  Código: pd.DataFrame({'Valores': df['Y'].dropna().unique()}})
- Pregunta: "Cuánto es el total de la columna Z para valores que contengan 'texto' en la columna W"
  Código: pd.DataFrame({'Resultado': [df[df['W'].str.contains('texto', case=False, na=False)]['Z'].sum()]}})
- Pregunta: "Dame una lista de valores en la columna A y su suma de la columna B"
  Código: df.groupby('A')['B'].sum().reset_index(name='Suma Total')
- Pregunta: "Qué evento generó más NPT en cada pozo"
  Código: (df.groupby(['Pozo', 'Evento'])['NPT'].sum().reset_index().sort_values(['Pozo', 'NPT'], ascending=[True, False]).groupby('Pozo').first().reset_index())
- Pregunta: "Gráfico de pastel del top 5 de la columna A por suma de la columna B"
  Código:
    top_5 = df.groupby('A')['B'].sum().nlargest(5)
    plt.figure(figsize=(8, 6), dpi=100)
    plt.pie(top_5, labels=top_5.index, autopct='%1.1f%%')
    None
- Pregunta: "Gráfica de barras comparando la suma de la columna B por la columna C"
  Código:
    sums = df.groupby('C')['B'].sum()
    plt.figure(figsize=(8, 6), dpi=100)
    plt.bar(sums.index, sums)
    plt.xlabel('C')
    plt.ylabel('Suma de B')
    plt.xticks(rotation=45)
    plt.tight_layout()
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

        # Filtrar líneas que comiencen con 'import'
        code_lines = [line for line in code.split('\n') if not line.strip().startswith('import')]
        code = '\n'.join(code_lines).strip()

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
