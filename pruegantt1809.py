import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Crear el DataFrame original (Ejemplo de un solo pedido)
data = {
   'PEDIDO': [1198],
    'IdDocumento': [441563],
    'F_EMISION': ['2024-06-20'],
    'F_ENTREGA': ['2024-09-06'],
    'DIAS': [78],
    'CLIENTE': ['THE BEAUFORT BO'],
    'KG_ARMP': ['114%'],
    'KG_TENIDP': ['114%'],
    'KG_TELAPROBP': ['102%'],
    'CORTADOP': ['113%'],
    'COSIDOP': ['19%'],
    'FMINARM': ['2024-06-25'],
    'FMAXARM': ['2024-07-05'],
    'FMINTENID': ['2024-06-28'],
    'FMAXTENID': ['2024-07-20'],
    'FMINTELAPROB': ['2024-07-12'],
    'FMAXTELAPROB': ['2024-09-06'],
    'FMINCORTE': ['2024-07-17'],
    'FMAXCORTE': ['2024-09-09'],
    'FMINCOSIDO': ['2024-08-08'],
    'FMAXCOSIDO': ['2024-09-12']
}

df = pd.DataFrame(data)

# Parámetros constantes
FACTOR = 0.06
DARM = 0.2
DTENID = 0.25
DTELAPROB = 0.27
DCORTADO = 0.25
DCOSIDO = 0.62

# Calcular las fechas de inicio y fin
f_emision = datetime.strptime(df['F_EMISION'][0], '%Y-%m-%d')
dias = df['DIAS'][0]

# Start: F_EMISION + n*FACTOR*DIAS
start_armado = f_emision + timedelta(days=FACTOR * dias)
start_tenido = f_emision + timedelta(days=2 * FACTOR * dias)
start_telaprob = f_emision + timedelta(days=3 * FACTOR * dias)
start_corte = f_emision + timedelta(days=4 * FACTOR * dias)
start_costura = f_emision + timedelta(days=5 * FACTOR * dias)

# Finish: F_EMISION + (n*FACTOR + DURACION_PROCESO)*DIAS
finish_armado = f_emision + timedelta(days=(FACTOR + DARM) * dias)
finish_tenido = f_emision + timedelta(days=(2 * FACTOR + DTENID) * dias)
finish_telaprob = f_emision + timedelta(days=(3 * FACTOR + DTELAPROB) * dias)
finish_corte = f_emision + timedelta(days=(4 * FACTOR + DCORTADO) * dias)
finish_costura = f_emision + timedelta(days=(5 * FACTOR + DCOSIDO) * dias)

# Crear un nuevo DataFrame con los procesos y sus fechas correspondientes
df_gantt = pd.DataFrame({
    'Proceso': ['ARMADO', 'TEÑIDO', 'TELA_APROB', 'CORTE', 'COSTURA'],
    'Start': [start_armado, start_tenido, start_telaprob, start_corte, start_costura],
    'Finish': [finish_armado, finish_tenido, finish_telaprob, finish_corte, finish_costura],
    'Start Real': [df['FMINARM'][0], df['FMINTENID'][0], df['FMINTELAPROB'][0], df['FMINCORTE'][0], df['FMINCOSIDO'][0]],
    'Finish Real': [df['FMAXARM'][0], df['FMAXTENID'][0], df['FMAXTELAPROB'][0], df['FMAXCORTE'][0], df['FMAXCOSIDO'][0]],
    'Avance': [df['KG_ARMP'][0], df['KG_TENIDP'][0], df['KG_TELAPROBP'][0], df['CORTADOP'][0], df['COSIDOP'][0]]
})

st.dataframe(df_gantt)

# Crear el gráfico de Gantt
fig = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Proceso", text="Avance")

# Ajustar el diseño del gráfico
fig.update_yaxes(autorange="reversed")  # Esto invierte el eje Y para que los pedidos estén en orden

# Ajustar el eje X para que las etiquetas aparezcan cada 7 días
fig.update_xaxes(dtick="D7")  # 'D7' ajusta las etiquetas del eje X cada 7 días


# Agregar las barras de las fechas reales
fig.add_trace(go.Scatter(
    x=df_gantt['Start Real'],
    y=df_gantt['Proceso'],
    mode='markers',
    marker=dict(color='black', size=10),
    name='Start Real'
))

fig.add_trace(go.Scatter(
    x=df_gantt['Finish Real'],
    y=df_gantt['Proceso'],
    mode='markers',
    marker=dict(color='red', size=10),
    name='Finish Real'
))

# Fechas de colocación y entrega
fecha_colocacion = df['F_EMISION'][0]
fecha_entrega = df['F_ENTREGA'][0]

# Agregar líneas verticales para las fechas de colocación y entrega
fig.add_shape(
    type="line",
    x0=fecha_colocacion, y0=0, x1=fecha_colocacion, y1=len(df_gantt),
    line=dict(color="green", width=2, dash="dash"),
    name="Fecha Colocación"
)

fig.add_shape(
    type="line",
    x0=fecha_entrega, y0=0, x1=fecha_entrega, y1=len(df_gantt),
    line=dict(color="red", width=2, dash="dash"),
    name="Fecha Entrega"
)

# Obtener la fecha actual
fecha_actual = datetime.now().strftime('%Y-%m-%d')

# Agregar una línea vertical para la fecha actual
fig.add_shape(
    type="line",
    x0=fecha_actual, y0=0, x1=fecha_actual, y1=len(df_gantt),
    line=dict(color="black", width=2, dash="dash"),
    name="Fecha Actual"
)
# Agregar líneas verticales muy tenues cada 2 días
start_date = datetime.strptime(df['F_EMISION'][0], '%Y-%m-%d')
end_date = datetime.strptime(df['F_ENTREGA'][0], '%Y-%m-%d')

# Iterar cada 2 días desde la fecha de emisión hasta la fecha de entrega
current_date = start_date
while current_date <= end_date:
    fig.add_shape(
        type="line",
        x0=current_date, y0=0, x1=current_date, y1=len(df_gantt),
        line=dict(color="gray", width=1, dash="dot"),
    )
    current_date += timedelta(days=2)  # Incrementar 2 días

# Mostrar la aplicación Streamlit
pedido = df['PEDIDO'][0]
st.title("Pedido:  " + str(df['PEDIDO'][0]))
st.write("Cliente:  " + str(df['CLIENTE'][0]))
st.plotly_chart(fig)
