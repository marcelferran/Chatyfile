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
                "parts": [
                    "Tienes un DataFrame llamado df. Estas son sus columnas: " + ", ".join(df.columns) + 
                    ". No traduzcas ni modifiques los nombres. Usa pandas y matplotlib solamente."
                ]
            },
            {
                "role": "model",
                "parts": ["Entendido. Usaré pandas y matplotlib respetando los nombres de columnas."]
            }
        ])

    def process_question(self, pregunta):
        try:
            prompt = f"""
Tienes un DataFrame de pandas llamado `df`.
Estas son las columnas: {', '.join(self.df.columns)}.
No cambies los nombres de columnas.
Si haces un cálculo o selección de datos, asigna el resultado a una variable llamada `result`.
Si haces una gráfica, usa matplotlib, crea una figura `fig, ax = plt.subplots()`.
Devuelve solo el código Python que ejecuta la respuesta.
Pregunta:
{pregunta}
"""
            response = self.chat.send_message(prompt)
            code = response.text.strip("`python\n").strip("`").strip()

            exec_globals = {"df": self.df, "pd": pd, "plt": plt}

            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                exec(code, exec_globals)

            # Revisar si hay figura
            if plt.get_fignums():
                fig = plt.gcf()
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png', bbox_inches='tight')
                img_buffer.seek(0)
                plt.close(fig)
                return {"type": "plot", "content": img_buffer}

            # Revisar si hay resultado tabular
            if "result" in exec_globals and isinstance(exec_globals["result"], pd.DataFrame):
                return {"type": "dataframe", "content": exec_globals["result"]}

            # Revisar si hay texto impreso
            output = buffer.getvalue()
            if output.strip():
                return {"type": "text", "content": output.strip()}

            return {"type": "text", "content": "✅ Código ejecutado sin salida."}

        except Exception as e:
            return {"type": "text", "content": f"❌ Error: {str(e)}"}
