import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Datos de ejemplo para el gráfico de Gantt
data = {
    'Task': ['Pedido 1', 'Pedido 2', 'Pedido 3', 'Pedido 4', 'Pedido 5'],
    'Start': ['2024-09-01', '2024-09-10', '2024-09-20', '2024-10-01', '2024-10-10'],
    'Finish': ['2024-09-15', '2024-09-25', '2024-10-05', '2024-10-15', '2024-10-25'],
    'Start Real': ['2024-09-02', '2024-09-12', '2024-09-22', '2024-10-02', '2024-10-12'],
    'Finish Real': ['2024-09-16', '2024-09-26', '2024-10-06', '2024-10-16', '2024-10-26'],
    'Resource': ['Proceso A', 'Proceso B', 'Proceso C', 'Proceso D', 'Proceso E']
}

# Convertir los datos a un DataFrame
df = pd.DataFrame(data)

# Crear el gráfico de Gantt
fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color=Grey, text="Resource")

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

# Fechas de colocación y entrega
fecha_colocacion = '2024-08-15'
fecha_entrega = '2024-10-31'

# Agregar líneas verticales para las fechas de colocación y entrega
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

# Obtener la fecha actual
fecha_actual = datetime.now().strftime('%Y-%m-%d')

# Agregar una línea vertical para la fecha actual
fig.add_shape(
    type="line",
    x0=fecha_actual, y0=0, x1=fecha_actual, y1=len(df),
    line=dict(color="black", width=2, dash="dash"),
    name="Fecha Actual"
)

# Agregar anotaciones para las fechas de colocación, entrega y actual
fig.add_annotation(
    x=fecha_colocacion, y=len(df) + 0.5,
    text="Emisión: ", #+ fecha_colocacion,
    showarrow=False,
    xshift=10,
    font=dict(color="green", size=12)
)

fig.add_annotation(
    x=fecha_entrega, y=len(df) + 0.5,
    text="Entrega: ", #+ fecha_entrega,
    showarrow=False,
    xshift=10,
    font=dict(color="red", size=12)
)

#fig.add_annotation(
    #x=fecha_actual, y=len(df) + 0.5,
    #text="Fecha Actual: " + fecha_actual,
    #showarrow=False,
    #xshift=10,
    #font=dict(color="black", size=12)
#)

# Mostrar la aplicación Streamlit
st.title("Avance de Procesos de Pedido")
st.write("Este es un gráfico de Gantt que muestra el avance de los procesos de los pedidos.")
st.plotly_chart(fig)
