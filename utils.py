import pandas as pd
import streamlit as st

def mostrar_resumen_df(df):
    st.success("✅ Archivo cargado correctamente.")
    num_rows, num_cols = df.shape
    st.write("**Resumen del archivo:**")
    st.write(f"- Número de filas: {num_rows}")
    st.write(f"- Número de columnas: {num_cols}")
    st.write("**Nombres de las columnas:**")
    st.dataframe(pd.DataFrame(df.columns, columns=["Columnas"]))
