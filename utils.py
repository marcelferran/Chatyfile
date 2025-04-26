import json
import pandas as pd
import streamlit as st
# No need to import plotting libraries here, Streamlit handles basic plots

def parse_gemini_response(response_text: str, df: pd.DataFrame):
    """
    Procesa el texto de respuesta RAW del modelo para identificar y extraer
    texto, datos de tabla y especificaciones de gráfico basadas en etiquetas.
    Retorna una lista de diccionarios con el formato {"type": ..., "content": ...}.
    """
    parts = response_text.split('<')
    output_elements = []

    for part in parts:
        if part.startswith('TABLE>'):
            # Es una tabla
            table_json_str = part.split('</TABLE>')[0]
            try:
                table_data = json.loads(table_json_str)
                # Validar la estructura básica del JSON de tabla
                if isinstance(table_data, dict) and 'data' in table_data and 'columns' in table_data:
                    # Validar que los datos y columnas sean listas
                    if isinstance(table_data['data'], list) and isinstance(table_data['columns'], list):
                         # Convertir a DataFrame. Añadir validación básica de columnas vs datos
                         if not table_data['data'] or (table_data['data'] and len(table_data['data'][0]) == len(table_data['columns'])):
                            table_df = pd.DataFrame(table_data['data'], columns=table_data['columns'])
                            output_elements.append({'type': 'dataframe', 'content': table_df})
                         else:
                             output_elements.append({'type': 'text', 'content': "Error: Los datos de la tabla no coinciden con las columnas."})
                    else:
                         output_elements.append({'type': 'text', 'content': "Error: Los datos o columnas de la tabla no son listas válidas."})
                else:
                     output_elements.append({'type': 'text', 'content': "Error: Formato de datos de tabla inválido."})
            except json.JSONDecodeError:
                output_elements.append({'type': 'text', 'content': "Error al procesar los datos de la tabla (JSON inválido)."})
            except Exception as e:
                 output_elements.append({'type': 'text', 'content': f"Error al crear la tabla: {e}."})

        elif part.startswith('CHART:'):
            # Es un gráfico
            chart_type_end = part.find('>')
            if chart_type_end != -1:
                chart_type = part[len('CHART:'):chart_type_end].strip().lower() # Convert type to lowercase
                chart_json_str = part[chart_type_end + 1:].split('</CHART>')[0]
                try:
                    chart_data = json.loads(chart_json_str)
                    # Validar la estructura básica del JSON de gráfico
                    if isinstance(chart_data, dict) and 'x' in chart_data and 'y' in chart_data:
                         # Validar que las columnas existan en el dataframe original
                         # Note: Validation against df happens in app.py before plotting
                         output_elements.append({'type': 'plot', 'content': {'type': chart_type, 'data': chart_data}})
                    else:
                         output_elements.append({'type': 'text', 'content': "Error: Formato de datos de gráfico inválido (faltan 'x' o 'y')."})
                except json.JSONDecodeError:
                    output_elements.append({'type': 'text', 'content': "Error al procesar los datos del gráfico (JSON inválido)."})
                except Exception as e:
                     output_elements.append({'type': 'text', 'content': f"Error al procesar el gráfico: {e}."})
            else:
                 output_elements.append({'type': 'text', 'content': "Formato de gráfico inválido."})
        else:
            # Es texto normal (o la parte antes de una etiqueta)
            # Asegurarse de que no se añadan partes vacías resultantes de la división
            text_content = part.split('>')[0] if '>' in part else part
            if text_content.strip(): # Añadir solo si no está vacío
                 output_elements.append({'type': 'text', 'content': text_content.strip()})

    # If no elements were parsed, treat the whole response as text
    if not output_elements and response_text.strip():
         output_elements.append({'type': 'text', 'content': response_text.strip()})


    return output_elements

# The display_message_content function is no longer needed as display logic is in app.py
# def display_message_content(message_element, df):
#     """Displays a single message element (text, dataframe, plot)."""
#     element_type = message_element['type']
#     content = message_element['content']
#
#     if element_type == 'text':
#         st.write(content) # Or use st.markdown with appropriate classes if needed
#     elif element_type == 'dataframe':
#         st.dataframe(content)
#     elif element_type == 'plot':
#         chart_data = content['data']
#         chart_type = content['type']
#         try:
#             if df is not None:
#                 chart_df = df
#                 if chart_data['x'] in chart_df.columns and chart_data['y'] in chart_df.columns:
#                     if chart_type == 'bar':
#                         st.bar_chart(chart_df.set_index(chart_data['x'])[chart_data['y']])
#                     elif chart_type == 'line':
#                         st.line_chart(chart_df.set_index(chart_data['x'])[chart_data['y']])
#                     elif chart_type == 'scatter':
#                          # Streamlit's scatter_chart is limited. Using line_chart as a fallback
#                          st.line_chart(chart_df.set_index(chart_data['x'])[chart_data['y']]) # Simple fallback
#                     else:
#                         st.warning(f"Tipo de gráfico no soportado: {chart_type}")
#                 else:
#                     st.warning(f"Columnas '{chart_data['x']}' o '{chart_data['y']}' no encontradas para el gráfico.")
#             else:
#                 st.warning("No hay datos cargados para generar el gráfico.")
#         except Exception as e:
#             st.error(f"Error al generar el gráfico: {e}")

