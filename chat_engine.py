import io
import ast
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai

from utils import cargar_csv, inferir_tipos_columnas, corregir_nombres_columnas

# Función para iniciar el chat
def iniciar_chat(df):
    tipos = inferir_tipos_columnas(df)
    st.session_state.tipos_columnas = tipos

    model = genai.GenerativeModel('gemini-2.0-flash')
    columnas = ", ".join(df.columns)
    chat = model.start_chat(history=[
        {
            "role": "user",
            "parts": [
                f"Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: {columnas}. No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están."
            ]
        },
        {
            "role": "model",
            "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
        }
    ])
    st.session_state.chat = chat

    if 'history' not in st.session_state:
        st.session_state.history = [
            {"role": "system", "content": "🟢 Asistente activo. Pregunta lo que quieras sobre tu DataFrame."},
            {"role": "system", "content": "✏️ Escribe 'salir' para finalizar."}
        ]

# Función para mostrar historial
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

# Función para procesar pregunta
def procesar_pregunta(pregunta, df):
    if pregunta.lower() == "salir":
        st.session_state.history.append({"role": "system", "content": "🛑 Chat finalizado."})
        return

    pregunta = corregir_nombres_columnas(pregunta, list(df.columns))
    st.session_state.history.append({"role": "user", "content": pregunta})

    instrucciones = f"""
You are working with a pandas DataFrame named `df`. Here are the rules:
- Do not create example data or define df; only use the existing one.
- Do not include Spanish comments or explanations.
- If the query involves a month name in Spanish (e.g. 'febrero'), use `meses['febrero']` to get the corresponding numeric value.
- For filtering, use `df[...]` with conditions.
- Always assign the final result to a variable named `__result__`.
- For plots, use `plt.figure(figsize=(8, 6), dpi=100)` and set `__result__ = None`.

Question:
{pregunta}
"""

    try:
        response = st.session_state.chat.send_message(instrucciones)
        code = response.text.strip("```python").strip("```").strip()

        if not code:
            st.session_state.history.append({"role": "assistant", "content": "❌ No se generó código. Intenta preguntar de otra forma."})
            return

        # Normalizar columnas de fecha y mes
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        if 'mes' in df.columns:
            if df['mes'].dtype == 'object':
                meses_map = {
                    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                }
                df['mes'] = df['mes'].str.lower().map(meses_map).fillna(df['mes'])
            df['mes'] = pd.to_numeric(df['mes'], errors='coerce')

        if 'Año' in df.columns:
            df['año'] = pd.to_numeric(df['Año'], errors='coerce')

        # Validar sintaxis del código generado
        code_lines = [line for line in code.split('\n') if not any(bad in line.lower() for bad in ['crear', 'ejemplo', 'filtrar', 'asumiendo'])]
        code = '\n'.join(code_lines).strip()

        try:
            ast.parse(code)
        except SyntaxError as e:
            st.session_state.history.append({"role": "assistant", "content": f"❌ Código inválido:\n\n{code}\n\n**Error:** {str(e)}"})
            return

        meses_dict = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }

        exec_globals = {"df": df.copy(), "plt": plt, "pd": pd, "np": np, "__result__": None, "meses": meses_dict}
        fig = None

        try:
            exec(code, exec_globals)
            result = exec_globals.get("__result__", None)

            if plt.get_fignums():
                fig = plt.gcf()
            plt.close('all')
        except Exception as e:
            st.session_state.history.append({"role": "assistant", "content": f"❌ Error al ejecutar el código:\n\n{code}\n\n**Error:** {str(e)}"})
            return

        response_dict = {"role": "assistant", "content": ""}
        if fig:
            response_dict["figure"] = fig
            response_dict["content"] = "📊 Gráfica generada:"
        else:
            if isinstance(result, pd.DataFrame):
                result_df = result
            elif isinstance(result, pd.Series):
                result_df = result.reset_index(name='Resultado')
            elif isinstance(result, (list, tuple, np.ndarray)):
                result_df = pd.DataFrame({'Resultado': result})
            elif isinstance(result, (int, float, str)):
                result_df = pd.DataFrame({'Resultado': [result]})
            elif result is None:
                result_df = pd.DataFrame({'Resultado': ['No se retornó ningún valor.']})
            else:
                result_df = pd.DataFrame({'Resultado': [str(result)]})

            for col in result_df.select_dtypes(include=['float64', 'float32']).columns:
                result_df[col] = result_df[col].round(2)

            response_dict["result_df"] = result_df
            response_dict["content"] = "📋 Resultados:"

        st.session_state.history.append(response_dict)

    except Exception as e:
        st.session_state.history.append({"role": "assistant", "content": f"❌ Error inesperado: {str(e)}"})
