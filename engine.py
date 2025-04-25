import pandas as pd

class Engine:
    def __init__(self):
        self.df = None
        # Inicialización de modelo/cliente LLM si es necesario (por ejemplo, API de Gemini 2.0 Flash)
        # self.model = ...

    def set_data(self, dataframe: pd.DataFrame):
        """Carga el DataFrame para futuras consultas."""
        self.df = dataframe

    def answer_question(self, question: str):
        """Genera una respuesta a la pregunta usando el DataFrame cargado."""
        if self.df is None:
            return "⚠️ No hay datos cargados. Por favor, carga un archivo CSV primero."
        q_lower = question.lower()
        try:
            # Ejemplo: responder a preguntas de conteo "¿Cuántos ... hay?"
            if "cuántos" in q_lower or "cuantos" in q_lower:
                item = None
                if " hay" in q_lower and " de " in q_lower:
                    # Extraer el texto entre "de " y " hay"
                    start = q_lower.index(" de ") + len(" de ")
                    end = q_lower.index(" hay", start)
                    item = q_lower[start:end].strip()
                if item:
                    # Contar filas donde cualquier columna contenga el texto buscado (no distingue singular/plural)
                    mask = self.df.apply(lambda col: col.astype(str).str.contains(item, case=False, na=False))
                    count = int(mask.any(axis=1).sum())
                    return str(count)
            # Si no se pudo manejar la pregunta con lógica específica, aquí se podría integrar el modelo LLM
            return "Lo siento, no puedo responder a esa pregunta con los datos proporcionados."
        except Exception as e:
            return f"Error al procesar la pregunta: {e}"
