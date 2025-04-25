import os
import re
import io
import pandas as pd
import numpy as np
import contextlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# (Opcional) Configurar la API de Google Generative AI con la clave correspondiente
try:
    import google.generativeai as genai
    API_KEY = os.getenv("GOOGLE_API_KEY", "")
    if API_KEY:
        genai.configure(api_key=API_KEY)
    # Modelo a usar (Gemini 2.0 Flash)
    MODEL_NAME = "gemini-2.0-flash"
except ImportError:
    genai = None
    MODEL_NAME = None

def extract_code_from_response(response: str) -> str:
    """
    Extrae el código Python contenido en un bloque de formato markdown del texto de respuesta del modelo.
    Devuelve la cadena de código sin los delimitadores de markdown.
    """
    code = ""
    # Buscar bloque de código markdown ```python ... ```
    match = re.search(r"```(?:python)?\n([\s\S]*?)```", response)
    if match:
        code = match.group(1)
    return code.strip()

def run_code(code: str, df: pd.DataFrame = None):
    """
    Ejecuta el código Python proporcionado en un entorno seguro, capturando la salida de texto, 
    cualquier DataFrame asignado a la variable 'result', y gráficos generados con matplotlib.
    Devuelve una tupla (output_text, result_obj, image_data, error), donde:
    - output_text: texto capturado de prints en el código.
    - result_obj: DataFrame/Series capturado si se asignó a 'result'.
    - image_data: imagen en bytes si se generó un gráfico.
    - error: mensaje de error en caso de excepción durante la ejecución (None si no hubo error).
    """
    # Preparar el entorno de ejecución
    env = {}
    if df is not None:
        env["df"] = df  # DataFrame disponible como df
    env["pd"] = pd
    env["np"] = np
    env["plt"] = plt

    output_text = ""
    result_obj = None
    image_data = None

    # Capturar la salida estándar durante la ejecución del código
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            exec(code, env)
    except Exception as e:
        # Capturar cualquier error ocurrido durante la ejecución
        error_msg = f"{type(e).__name__}: {e}"
        return "", None, None, error_msg
    finally:
        output_text = stdout.getvalue()

    # Obtener el objeto 'result' si el código lo produjo
    if "result" in env:
        result_obj = env["result"]

    # Capturar gráficos de matplotlib si se generaron
    fig_nums = plt.get_fignums()
    if fig_nums:
        # Tomar la última figura generada
        fig = plt.figure(fig_nums[-1])
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        image_data = buf.getvalue()
        # Cerrar todas las figuras para liberar memoria
        plt.close('all')

    return output_text, result_obj, image_data, None

def process_question(question: str, df: pd.DataFrame = None):
    """
    Envía la pregunta del usuario al modelo generativo y ejecuta cualquier código devuelto para obtener la respuesta.
    Retorna una tupla (text_output, df_output, image_output, error) con los componentes de la respuesta.
    """
    # Verificar que la API esté disponible
    if genai is None or MODEL_NAME is None:
        error_msg = "No se encontró la integración con la API de Generative AI."
        return "", None, None, error_msg

    # Obtener respuesta del modelo generativo (Gemini 2.0 Flash)
    try:
        # Usar método de chat o generación de texto según la biblioteca `google.generativeai`
        response = genai.generate_text(prompt=question, model=MODEL_NAME)
    except Exception as e:
        # Error llamando a la API
        error_msg = f"APIError: {e}"
        return "", None, None, error_msg

    # Extraer el contenido de texto de la respuesta del modelo
    if isinstance(response, str):
        content = response
    elif hasattr(response, "generated_text"):
        content = response.generated_text
    elif isinstance(response, dict):
        # Formato de respuesta de PaLM API: tomar el primer candidato
        content = response.get("candidates", [{}])[0].get("content", "")
    else:
        content = str(response)

    # Extraer el código de la respuesta del modelo (si lo hay)
    code = extract_code_from_response(content)
    if code:
        # Ejecutar el código generado y capturar salidas
        text_output, result_obj, image_data, exec_error = run_code(code, df)
        if exec_error:
            # Si hubo error en la ejecución, devolver el error
            return "", None, None, exec_error
        # Combinar cualquier texto explicativo fuera del bloque de código con la salida de texto capturada
        # (por ejemplo, si el modelo incluyó comentarios o explicaciones además del código)
        explanation_text = re.sub(r"```(?:python)?\n[\s\S]*?```", "", content).strip()
        if explanation_text:
            # Si hay texto explicativo, agregarlo antes de la salida de texto del código
            if text_output:
                text_output = explanation_text + "\n" + text_output
            else:
                text_output = explanation_text
        # Verificar si el resultado es un DataFrame/Series o algún otro tipo
        df_output = None
        final_text = text_output
        image_output = image_data
        if result_obj is not None:
            if isinstance(result_obj, pd.DataFrame):
                df_output = result_obj
            elif isinstance(result_obj, pd.Series):
                # Convertir Series a DataFrame para mostrarla como tabla
                df_output = result_obj.to_frame(name=result_obj.name if result_obj.name else "valor")
            else:
                # Si el resultado es un valor escalar u otro objeto, convertirlo a texto
                if final_text:
                    final_text = f"{final_text}\n{result_obj}"
                else:
                    final_text = str(result_obj)
        return final_text, df_output, image_output, None
    else:
        # Si la respuesta no contiene código, interpretarla como texto de respuesta directo
        content = content.strip()
        if not content:
            # Si no se generó contenido alguno
            return "", None, None, None
        return content, None, None, None
