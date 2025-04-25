import io
import ast
import contextlib
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from fuzzywuzzy import process
import matplotlib.pyplot as plt
import google.generativeai as genai



# Configurar API de Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("❌ No se encontró la clave API en st.secrets. Por favor, configura 'GEMINI_API_KEY'.")
    st.stop()


# Inicializar historial
if 'history' not in st.session_state:
    st.session_state.history = []
    

# Función para cargar el CSV
def cargar_csv(file):
    try:
        df = pd.read_csv(file, encoding='utf-8', low_memory=False, dtype_backend='numpy_nullable')
        st.write("Debug: Columnas del DataFrame crudo:", list(df.columns))

        date_keywords = ['date', 'day', 'month', 'year', 'dia', 'mes', 'ano']

        for col in df.columns:
            sample = df[col].head(100)
            if len(sample) == 0:
                continue
            try:
                numeric_ratio = pd.to_numeric(sample, errors='coerce').notna().mean()
                if numeric_ratio > 0.9:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            except:
                pass

            col_lower = col.lower()
            if any(keyword in col_lower for keyword in date_keywords):
                st.write(f"Debug: Valores crudos de la columna '{col}':", sample.head(5).tolist())

                try:
                    if 'fecha' in col_lower or 'date' in col_lower:
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
                    elif 'mes-año' in col_lower or 'month-year' in col_lower:
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m')
                    elif 'año' in col_lower or 'year' in col_lower:
                        df[col] = pd.to_datetime(df[col].astype(str) + '-01-01', errors='coerce').dt.strftime('%Y-%m-%d')
                    elif 'mes' in col_lower or 'month' in col_lower:
                        year = 2025
                        if 'Año' in df.columns:
                            year = df['Año'].iloc[0] if pd.notna(df['Año'].iloc[0]) else year
                        df[col] = df[col].str.lower().map({
                            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                        }).fillna(df[col])
                        df[col] = pd.to_datetime(str(year) + '-' + df[col] + '-01', errors='coerce').dt.strftime('%Y-%m-%d')
                    elif 'dia' in col_lower or 'day' in col_lower:
                        year = 2025
                        month = '01'
                        if 'Año' in df.columns:
                            year = df['Año'].iloc[0] if pd.notna(df['Año'].iloc[0]) else year
                        if 'Mes' in df.columns:
                            month = df['Mes'].str.lower().map({
                                'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                                'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                                'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                            }).fillna(df['Mes']).iloc[0] if pd.notna(df['Mes'].iloc[0]) else month
                        df[col] = pd.to_datetime(str(year) + '-' + month + '-' + df[col].astype(str).str.zfill(2), errors='coerce').dt.strftime('%Y-%m-%d')
                    st.write(f"Debug: Columna '{col}' convertida")
                except Exception as e:
                    st.write(f"Debug: Error al convertir '{col}': {str(e)}")

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype('string').fillna(pd.NA)

        df = df.dropna(how='all')

        if df.empty:
            st.error("El CSV está vacío o no contiene datos válidos.")
            return None

        st.write("Debug: Columnas del DataFrame final:", list(df.columns))
        return df

    except Exception as e:
        st.error(f"Error al cargar el CSV: {str(e)}")
        return None
        

# Función para iniciar el chat
def iniciar_chat(df):
    model = genai.GenerativeModel('gemini-2.0-flash')
    tipos_columnas = inferir_tipos_columnas(df)
    primeras_filas = df.head(10)
    chat = model.start_chat(history=[
        {"role": "user", "parts": [f"Tienes un DataFrame de pandas llamado df. Tipos inferidos: {tipos_columnas}. Usa los nombres de columna tal como están. NO los traduzcas ni los cambies."]},
        {"role": "model", "parts": ["Entendido. Usaré los nombres de columna y tipos inferidos exactamente como los proporcionaste."]}
    ])
    st.session_state.chat = chat
    st.session_state.history.append({"role": "system", "content": "🟢 Asistente activo. Pregunta lo que quieras sobre tu DataFrame."})
    st.session_state.history.append({"role": "system", "content": "📋 **Primeras 10 filas del DataFrame:**", "result_df": primeras_filas})
    

# Función para mostrar historial
def mostrar_historial():
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(f"**Usuario:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Asistente:** {msg['content']}")
            if "figure" in msg:
                st.pyplot(msg["figure"], use_container_width=True)
            if "result_df" in msg:
                st.dataframe(msg["result_df"])
        else:
            st.markdown(msg["content"])
            if "result_df" in msg:
                st.dataframe(msg["result_df"])
                

# Función para borrar historial
def borrar_historial():
    if st.button('🗑️ Borrar historial'):
        st.session_state.history = []
        st.success("Historial borrado. Puedes iniciar nuevas preguntas.")
        

# Función para inferir tipos
def inferir_tipos_columnas(df):
    tipos = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            tipos[col] = 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            tipos[col] = 'datetime'
        elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            tipos[col] = 'categorical'
        else:
            tipos[col] = 'other'
    return tipos
    

# Función para procesar preguntas
def procesar_pregunta(pregunta, df):
    if pregunta.lower() == "salir":
        st.session_state.history.append({"role": "system", "content": "🛑 Chat finalizado."})
        return

    st.session_state.history.append({"role": "user", "content": pregunta})

    try:
        prompt = f"Tienes el siguiente DataFrame:\n{df.head(5).to_string()}\nContesta: {pregunta} en formato de código Python válido. No expliques, solo da el código."
        response = st.session_state.chat.send_message(prompt)

        code = response.text.strip().strip('```python').strip('```')

        st.write("Debug: Código generado:", code)

        exec_globals = {"df": df, "pd": pd, "np": np, "sns": sns, "plt": plt}
        exec_locals = {}

        with contextlib.redirect_stdout(io.StringIO()):
            exec(code, exec_globals, exec_locals)

        if plt.get_fignums():
            fig = plt.gcf()
            st.session_state.history.append({"role": "assistant", "content": "📊 Gráfica generada:", "figure": fig})
        else:
            output = None
            for var in exec_locals.values():
                if isinstance(var, (pd.DataFrame, pd.Series)):
                    output = var
                    break

            if output is not None:
                if isinstance(output, pd.Series):
                    output = output.to_frame()
                st.session_state.history.append({"role": "assistant", "content": "📋 Resultados:", "result_df": output})
            else:
                st.session_state.history.append({"role": "assistant", "content": "⚠️ No se generaron resultados."})

    except Exception as e:
        st.session_state.history.append({"role": "assistant", "content": f"❌ Error al procesar la pregunta: {str(e)}"})
