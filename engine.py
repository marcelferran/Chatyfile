import io
import contextlib
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import google.generativeai as genai

class ChatEngine:
    def __init__(self, df):
        self.df = df
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat = self.model.start_chat(history=[
            {
                "role": "user",
                "parts": ["Tienes un DataFrame de pandas llamado df. Estas son las columnas reales que contiene: " + ", ".join(df.columns) + ". No traduzcas ni cambies ningún nombre de columna. Usa los nombres tal como están."]
            },
            {
                "role": "model",
                "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
            }
        ])

    def process_question(self, pregunta):
        try:
            prompt = f"""
Tienes un DataFrame llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(self.df.columns)}.
NO CAMBIES los nombres de las columnas.
SIEMPRE que crees un DataFrame nuevo, asígnalo a una variable llamada `result`.
SIEMPRE que crees un gráfico matplotlib, crea una variable `fig, ax = plt.subplots()` y guarda en `fig`.
Responde a esta pregunta:
{pregunta}
"""
            response = self.chat.send_message(prompt)
            code = response.text.strip("`python\n").strip("`").strip()

            exec_globals = {"df": self.df, "pd": pd, "plt": plt}

            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                exec(code, exec_globals)

            # Revisar si se generó un gráfico
            if plt.get_fignums():
                fig = plt.gcf()
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png', bbox_inches='tight')
                img_buffer.seek(0)
                plt.close(fig)
                return {"type": "plot", "content": img_buffer}

            # Revisar si se generó un result (DataFrame)
            if "result" in exec_globals and isinstance(exec_globals["result"], pd.DataFrame):
                return {"type": "dataframe", "content": exec_globals["result"]}

            # Revisar si hubo impresión de texto
            output = buffer.getvalue()
            if output.strip():
                return {"type": "text", "content": output.strip()}

            # Si no hubo nada
            return {"type": "text", "content": "✅ Código ejecutado sin salida."}

        except Exception as e:
            return {"type": "text", "content": f"❌ Error: {str(e)}"}
