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

fig.add_shape(
    type="line",
    x0=fecha_colocacion, y0=0, x1=fecha_colocacion, y1=len(df),
    line=dict(color="green", width=2, dash="dash"),
    name="Fecha Colocación"
)

fig.add_shape(
    type="line",
    x0=fecha_entrega, y0=0, x1=fecha_entrega, y1=len(df),
    line=dict(color="red", width=2, dash="dash"),
    name="Fecha Entrega"
)

# Agregar anotaciones para las fechas de colocación y entrega
fig.add_annotation(
    x=fecha_colocacion, y=len(df) + 0.5,
    text="Fecha Colocación",
    showarrow=False,
    xshift=10,
    font=dict(color="green")
)

fig.add_annotation(
    x=fecha_entrega, y=len(df) + 0.5,
    text="Fecha Entrega",
    showarrow=False,
    xshift=10,
    font=dict(color="red")
)

# Mostrar la aplicación Streamlit
st.title("Avance de Procesos de Pedido")
st.write("Este es un gráfico de Gantt que muestra el avance de los procesos de los pedidos.")
st.plotly_chart(fig)
