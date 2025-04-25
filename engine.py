import io
import pandas as pd
import matplotlib.pyplot as plt
import contextlib
import google.generativeai as genai
from io import BytesIO

class ChatEngine:
    def __init__(self, df):
        self.df = df
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat = self.model.start_chat(history=[
            {"role": "user", "parts": [
                "Tienes un DataFrame de pandas llamado df. Estas son las columnas: " + ", ".join(df.columns) +
                ". Usa solo pandas y matplotlib. No uses plotly, seaborn, ni librerías externas. " +
                "Siempre asigna cualquier DataFrame que generes a una variable llamada result."
            ]},
            {"role": "model", "parts": ["Entendido."]}
        ])

    def process_question(self, pregunta):
        try:
            prompt = f"""
Tienes un DataFrame llamado df con columnas: {', '.join(self.df.columns)}.
Siempre asigna resultados tabulares a una variable llamada result.
Responde a esta pregunta:
{pregunta}
"""
            response = self.chat.send_message(prompt)
            code = response.text.strip("`python\n").strip("`").strip()

            exec_globals = {"df": self.df, "pd": pd, "plt": plt}
            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                exec(code, exec_globals)

            # Si se generó una figura
            if plt.get_fignums():
                fig = plt.gcf()
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png', bbox_inches='tight')
                img_buffer.seek(0)
                plt.close(fig)
                return {"role": "assistant", "type": "plot", "content": img_buffer}

            # Si se generó un result
            if "result" in exec_globals and isinstance(exec_globals["result"], pd.DataFrame):
                return {"role": "assistant", "type": "dataframe", "content": exec_globals["result"]}

            # Si solo hay texto
            output_text = buffer.getvalue().strip()
            if output_text:
                return {"role": "assistant", "type": "text", "content": output_text}

            return {"role": "assistant", "type": "text", "content": "✅ Código ejecutado sin salida."}

        except Exception as e:
            return {"role": "assistant", "type": "text", "content": f"❌ Error: {str(e)}"}
