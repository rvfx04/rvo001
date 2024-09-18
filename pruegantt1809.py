import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
fig.update_yaxes(autorange="reversed")  # Esto invierte el eje Y para que los pedidos estén en orden

# Agregar marcas verticales para las fechas de colocación y entrega
fecha_colocacion = '2023-09-25'
fecha_entrega = '2023-10-15'

fig.add_vline(x=fecha_colocacion, line_width=2, line_dash="dash", line_color="green", annotation_text="Fecha Colocación", annotation_position="top right")
fig.add_vline(x=fecha_entrega, line_width=2, line_dash="dash", line_color="red", annotation_text="Fecha Entrega", annotation_position="top right")

# Mostrar la aplicación Streamlit
st.title("Avance de Procesos de Pedido")
st.write("Este es un gráfico de Gantt que muestra el avance de los procesos de los pedidos.")
st.plotly_chart(fig)
