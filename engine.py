import google.generativeai as genai
import io
import contextlib

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
                    "Si vas a hacer comparaciones de texto, recuerda que pueden contener mayúsculas y minúsculas diferentes."
                ]
            },
            {
                "role": "model",
                "parts": ["Entendido. Usaré los nombres de columna exactamente como los proporcionaste."]
            }
        ])

    def process_question(self, pregunta):
        try:
            prompt = f"""
Tienes un DataFrame de pandas llamado `df` cargado en memoria.
Estas son las columnas reales: {', '.join(self.df.columns)}.
NO CAMBIES los nombres de las columnas.

Si la pregunta implica filtrar por texto, recuerda que puede haber variaciones de mayúsculas y minúsculas como 'Urea', 'urea', 'UREA'.
Usa comparaciones robustas como `.str.lower()` o `case=False` en `.str.contains()`.

Responde a esta pregunta escribiendo solamente el código Python que da la respuesta.

Pregunta:
{pregunta}
"""

            response = self.chat.send_message(prompt)
            code = response.text.strip("`python\n").strip("`").strip()

            exec_globals = {"df": self.df}
            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                try:
                    exec(code, exec_globals)
                except Exception as e:
                    return f"❌ Error al ejecutar el código: {str(e)}"

            output = buffer.getvalue()

            if output.strip():
                return output
            else:
                return "✅ Código ejecutado sin salida."

        except Exception as e:
            return f"❌ Error al procesar o ejecutar: {str(e)}"
