import io
import builtins
import contextlib
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import google.generativeai as genai
from io import BytesIO

class ChatEngine:
    def __init__(self, df):
        self.df = df
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat = self.model.start_chat(history=[
            {"role": "user", "parts": [
                "Tienes un DataFrame de pandas llamado df. Columnas: " + ", ".join(df.columns) + ". No cambies nombres. Usa .str.contains('valor', case=False) para filtros. No uses plotly ni seaborn. Solo pandas, numpy, matplotlib."
            ]},
            {"role": "model", "parts": ["Entendido."]}
        ])

    def process_question(self, pregunta):
        try:
            prompt = f"""
Tienes un DataFrame llamado df.
Estas son las columnas reales: {', '.join(self.df.columns)}.
Responde a esta pregunta escribiendo SOLO el código Python.
Asigna cualquier resultado tabular a una variable llamada result.
"""
            response = self.chat.send_message(prompt + "\n\nPregunta:\n" + pregunta)
            code = response.text.strip("`python\n").strip("`").strip()

            exec_globals = {"df": self.df, "pd": pd, "plt": plt, "st": st, "builtins": builtins}
            buffer = io.StringIO()
            output = []

            with contextlib.redirect_stdout(buffer):
                try:
                    exec(code, exec_globals)
                except Exception as e:
                    output.append({"role": "assistant", "type": "text", "content": f"Error al ejecutar el código: {str(e)}"})
                    return output

            if plt.get_fignums():
                fig = plt.gcf()
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png', bbox_inches='tight')
                img_buffer.seek(0)
                output.append({"role": "assistant", "type": "plot", "content": img_buffer})
                plt.close(fig)
                return output

            if "result" in exec_globals and isinstance(exec_globals["result"], pd.DataFrame):
                output.append({"role": "assistant", "type": "table", "content": exec_globals["result"]})
                return output

            text_output = buffer.getvalue().strip()
            if text_output:
                output.append({"role": "assistant", "type": "text", "content": text_output})
                return output

            output.append({"role": "assistant", "type": "text", "content": "Código ejecutado sin salida."})
            return output

        except Exception as e:
            return [{"role": "assistant", "type": "text", "content": f"Error inesperado: {str(e)}"}]
