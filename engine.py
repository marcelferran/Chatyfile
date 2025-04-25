import io
import builtins
import contextlib
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import google.generativeai as genai

class ChatEngine:
    def __init__(self, df):
        self.df = df
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat = self.model.start_chat(history=[
            {
                "role": "user",
                "parts": [
                    "Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: " +
                    ", ".join(df.columns) +
                    ". No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están. "
                    "Cuando filtres por texto (como 'Urea' o 'Motocicletas'), usa `.str.contains('valor', case=False)`. "
                    "No uses librerías externas como plotly o seaborn, solo pandas, numpy y matplotlib."
                ]
            },
            {
                "role": "model",
                "parts": ["Entendido. Seguiré tus instrucciones y respetaré nombres de columna."]
            }
        ])

    def process_question(self, pregunta):
        try:
            prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(self.df.columns)}.
NO CAMBIES los nombres de las columnas.

Cuando filtres texto (como 'Urea' o 'Motocicletas'), usa `.str.contains('valor', case=False)`.
No uses librerías externas como plotly, seaborn. Solo pandas, numpy, matplotlib.

Responde a esta pregunta escribiendo SOLAMENTE el código Python que da la respuesta.
No expliques nada, solo código.

Pregunta:
{pregunta}
"""
            response = self.chat.send_message(prompt)
            code = response.text.strip("`python\n").strip("`").strip()

            # Preparamos el entorno
            exec_globals = {"df": self.df, "pd": pd, "plt": plt, "st": st, "builtins": builtins}

            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                try:
                    exec(code, exec_globals)
                except Exception as e:
                    return f"❌ Error al ejecutar el código: {str(e)}"

            output = buffer.getvalue()

            # Mostrar figura si existe
            if plt.get_fignums():
                fig = plt.gcf()
                st.pyplot(fig)
                plt.clf()
                return ""

            # Mostrar DataFrame si se genera uno llamado 'result'
            if "result" in exec_globals and isinstance(exec_globals["result"], pd.DataFrame):
                st.dataframe(exec_globals["result"])
                return ""

            # Mostrar print capturado si existe
            if output.strip():
                return output

            return "✅ Código ejecutado sin salida."

        except Exception as e:
            return f"❌ Error al procesar o ejecutar: {str(e)}"
