import json
import pandas as pd
import streamlit as st

# --- Utility function to handle model response ---
def handle_response(response_text, df):
    """
    Procesa el texto de respuesta del modelo para identificar si debe mostrar tabla o gráfico.
    El modelo debe ser instruido para usar formatos específicos para indicar tabla o gráfico.
    Ejemplo de formato esperado del modelo:
    - Texto normal
    - <TABLE>
      {"data": [[...], [...]], "columns": [...]}
      </TABLE>
    - <CHART:type>
      {"data": [...], "x": "col_x", "y": "col_y", "title": "..."}
      </CHART>
      Donde type puede ser 'bar', 'line', 'scatter', etc.
    """
    parts = response_text.split('<')
    output_elements = []

    for part in parts:
        if part.startswith('TABLE>'):
            # Es una tabla
            table_json_str = part.split('</TABLE>')[0]
            try:
                table_data = json.loads(table_json_str)
                # Convertir a DataFrame y mostrar
                # Asegurarse de que las columnas existan en el JSON antes de crear el DataFrame
                if 'data' in table_data and 'columns' in table_data:
                    table_df = pd.DataFrame(table_data['data'], columns=table_data['columns'])
                    output_elements.append(('table', table_df))
                else:
                     output_elements.append(('text', "Error: Formato de datos de tabla inválido."))
            except json.JSONDecodeError:
                output_elements.append(('text', "Error al procesar los datos de la tabla (JSON inválido)."))
            except Exception as e:
                 output_elements.append(('text', f"Error al crear la tabla: {e}"))
        elif part.startswith('CHART:'):
            # Es un gráfico
            chart_type_end = part.find('>')
            if chart_type_end != -1:
                chart_type = part[len('CHART:'):chart_type_end].strip()
                chart_json_str = part[chart_type_end + 1:].split('</CHART>')[0]
                try:
                    chart_data = json.loads(chart_json_str)
                    # Generar y mostrar el gráfico
                    # Validar que los datos necesarios para el gráfico estén presentes
                    if 'x' in chart_data and 'y' in chart_data:
                         output_elements.append(('chart', {'type': chart_type, 'data': chart_data}))
                    else:
                         output_elements.append(('text', "Error: Formato de datos de gráfico inválido (faltan 'x' o 'y')."))
                except json.JSONDecodeError:
                    output_elements.append(('text', "Error al procesar los datos del gráfico (JSON inválido)."))
                except Exception as e:
                     output_elements.append(('text', f"Error al procesar el gráfico: {e}"))
            else:
                 output_elements.append(('text', "Formato de gráfico inválido."))
        else:
            # Es texto normal (o la parte antes de una etiqueta)
            # Asegurarse de que no se añadan partes vacías resultantes de la división
            text_content = part.split('>')[0] if '>' in part else part
            if text_content.strip(): # Añadir solo si no está vacío
                 output_elements.append(('text', text_content.strip()))

    return output_elements

# --- Function to display elements in chat ---
def display_chat_elements(elements, df):
    """Displays a list of output elements (text, table, chart) in the chat."""
    for element_type, content in elements:
        if element_type == 'text':
            st.write(content)
        elif element_type == 'table':
            st.dataframe(content)
        elif element_type == 'chart':
            chart_data = content['data']
            chart_type = content['type']
            try:
                # Usar el dataframe cargado para generar el gráfico
                if df is not None:
                    chart_df = df
                    # Validar columnas antes de graficar
                    if chart_data['x'] in chart_df.columns and chart_data['y'] in chart_df.columns:
                        if chart_type == 'bar':
                            st.bar_chart(chart_df.set_index(chart_data['x'])[chart_data['y']])
                        elif chart_type == 'line':
                            st.line_chart(chart_df.set_index(chart_data['x'])[chart_data['y']])
                        elif chart_type == 'scatter':
                            # Streamlit's scatter_chart is limited. Using line_chart as a fallback
                            # or you might consider using Altair/Plotly for more robust scatter plots.
                            st.line_chart(chart_df.set_index(chart_data['x'])[chart_data['y']]) # Simple fallback
                        else:
                            st.warning(f"Tipo de gráfico no soportado: {chart_type}")
                    else:
                        st.warning(f"Columnas '{chart_data['x']}' o '{chart_data['y']}' no encontradas para el gráfico.")
                else:
                    st.warning("No hay datos cargados para generar el gráfico.")
            except Exception as e:
                st.error(f"Error al generar el gráfico: {e}")

