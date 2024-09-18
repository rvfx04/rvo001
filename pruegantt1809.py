import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Datos de ejemplo para el gráfico de Gantt
data = {
    'Task': ['Pedido 1', 'Pedido 2', 'Pedido 3'],
    'Start': ['2023-09-01', '2023-09-10', '2023-09-20'],
    'Finish': ['2023-10-01', '2023-10-10', '2023-10-20'],
    'Start Real': ['2023-09-02', '2023-09-12', '2023-09-22'],
    'Finish Real': ['2023-10-03', '2023-10-13', '2023-10-23'],
    'Resource': ['Proceso A', 'Proceso B', 'Proceso C']
}

# Convertir los datos a un DataFrame
df = pd.DataFrame(data)

# Crear el gráfico de Gantt
fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource", text="Resource", title="Avance de Procesos de Pedido")

# Ajustar el diseño del gráfico
fig.update_yaxes(autorange="reversed")  # Esto invierte el eje Y para que los pedidos estén en orden

# Agregar las barras de las fechas reales
fig.add_trace(go.Scatter(
    x=df['Start Real'],
    y=df['Task'],
    mode='markers',
    marker=dict(color='blue', size=10),
    name='Start Real'
))

fig.add_trace(go.Scatter(
    x=df['Finish Real'],
    y=df['Task'],
    mode='markers',
    marker=dict(color='red', size=10),
    name='Finish Real'
))

# Obtener la fecha actual
fecha_actual = datetime.now().strftime('%Y-%m-%d')

# Agregar una línea vertical para la fecha actual
fig.add_shape(
    type="line",
    x0=fecha_actual, y0=0, x1=fecha_actual, y1=len(df),
    line=dict(color="black", width=2, dash="dash"),
    name="Fecha Actual"
)

# Agregar anotaciones para las fechas de colocación y entrega
fig.add_annotation(
    x=fecha_actual, y=len(df) + 0.5,
    text="Fecha Actual: " + fecha_actual,
    showarrow=False,
    xshift=10,
    font=dict(color="black", size=12)
)

# Mostrar la aplicación Streamlit
st.title("Avance de Procesos de Pedido")
st.write("Este es un gráfico de Gantt que muestra el avance de los procesos de los pedidos.")
st.plotly_chart(fig)
