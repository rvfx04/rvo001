import streamlit as st
import pandas as pd
import plotly.express as px

# Datos de ejemplo para el gráfico de Gantt
data = {
    'Task': ['Pedido 1', 'Pedido 2', 'Pedido 3'],
    'Start': ['2023-10-01', '2023-10-03', '2023-10-05'],
    'Finish': ['2023-10-05', '2023-10-07', '2023-10-10'],
    'Resource': ['Proceso A', 'Proceso B', 'Proceso C']
}

# Convertir los datos a un DataFrame
df = pd.DataFrame(data)

# Crear el gráfico de Gantt
fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource", text="Resource")

# Ajustar el diseño del gráfico
--fig.update_yaxes(autorange="reversed")  # Esto invierte el eje Y para que los pedidos estén en orden

# Mostrar la aplicación Streamlit
st.title("Avance de Procesos de Pedido")
st.write("Este es un gráfico de Gantt que muestra el avance de los procesos de los pedidos.")
st.plotly_chart(fig)
