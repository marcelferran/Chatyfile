import google.generativeai as genai
import io
import contextlib
import matplotlib.pyplot as plt
import pandas as pd

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
                    "Si haces comparaciones de texto, recuerda usar `.str.lower()` o `case=False` para evitar errores por mayúsculas. "
                    "No uses librerías externas como plotly o seaborn, solo puedes usar pandas, numpy y matplotlib."
                ]
            },
            {
                "role": "model",
                "parts": ["Entendido. Seguiré tus instrucciones y respetaré nombres de columnas."]
            }
        ])

    def process_question(self, pregunta):
        try:
            prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(self.df.columns)}.
NO CAMBIES los nombres de las columnas.

Si haces filtrados de texto, recuerda usar `.str.lower()` o `case=False`.
Si haces gráficos, usa matplotlib, no plotly.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Pregunta:
{pregunta}
"""

            response = self.chat.send_message(prompt)
            code = response.text.strip("`python\n").strip("`").strip()

            # Preparar entorno de ejecución
            exec_globals = {"df": self.df, "pd": pd, "plt": plt}
            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                try:
                    exec(code, exec_globals)
                except Exception as e:
                    return f"❌ Error al ejecutar el código: {str(e)}"

            output = buffer.getvalue()

            # Buscar resultados
            new_df = exec_globals.get("result", None)
            if isinstance(new_df, pd.DataFrame):
                st.dataframe(new_df)
                return ""
            elif plt.get_fignums():
                fig = plt.gcf()
                st.pyplot(fig)
                plt.clf()  # Limpiar figura después de mostrar
                return ""
            elif output.strip():
                return output
            else:
                return "✅ Código ejecutado sin salida."

        except Exception as e:
            return f"❌ Error al procesar o ejecutar: {str(e)}"
