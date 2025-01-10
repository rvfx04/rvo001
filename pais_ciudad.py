import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Filtro de Ciudades por País")

# Carga del archivo Excel
uploaded_file = st.file_uploader("Sube un archivo Excel con dos columnas: País y Ciudad", type=["xlsx"])

if uploaded_file:
    # Lectura del archivo Excel
    try:
        df = pd.read_excel(uploaded_file)
        
        # Validación de columnas
        if "País" in df.columns and "Ciudad" in df.columns:
            # Selección de país
            pais_seleccionado = st.selectbox("Selecciona un país", df["País"].unique())
            
            # Filtrar ciudades por el país seleccionado
            ciudades = df[df["País"] == pais_seleccionado]["Ciudad"].unique()
            
            # Mostrar las ciudades
            st.write(f"Ciudades en **{pais_seleccionado}**:")
            st.write(ciudades)
        else:
            st.error("El archivo debe contener las columnas 'País' y 'Ciudad'.")
    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo: {e}")
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
