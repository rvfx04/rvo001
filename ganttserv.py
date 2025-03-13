import streamlit as st
import pyodbc
import pandas as pd
import plotly.express as px

# Configuración de la conexión a la base de datos usando st.secrets
def get_db_connection():
    try:
        conn_str = (
            f"DRIVER={st.secrets['db_credentials']['driver']};"
            f"SERVER={st.secrets['db_credentials']['server']};"
            f"DATABASE={st.secrets['db_credentials']['database']};"
            f"UID={st.secrets['db_credentials']['uid']};"
            f"PWD={st.secrets['db_credentials']['pwd']};"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        return None

# Función para ejecutar la consulta y obtener los datos
def get_data(conn):
    query = """
    SELECT 
        c.CodDocumento AS OS_OT,
        i.CoddocOrdenProduccion AS OP,
        MAX(d.NommaeAnexoProveedor) AS PROVEEDOR,
        MAX(w.NommaeEstilo) AS ESTILO,
        MAX(z.dMinutos) AS MIN_COST,
        MAX(z.dMinutos) * SUM(a.dCantidadProgramado - a.dCantidadProducido) AS MIN_PEND,
        SUM(a.dCantidadProgramado) AS PROG,
        SUM(a.dCantidadProducido) AS PROD,
        SUM(a.dCantidadProgramado - a.dCantidadProducido) AS PENDIENT,
        MAX(dbo.fneFechaRegistroMaximo_NotaInventario_Documento(
            131,  -- @IdtdDocumentoForm_NotaInventario_IngresoProduccion
            a.IdDocumento,
            a.IdmaeItem_Inventario)) AS MAX_ING,
        MIN(dbo.fneFechaRegistroMinimo_NotaInventario_Documento(
            130,  -- @IdtdDocumentoForm_NotaInventario_SalidaProduccion
            a.IdDocumento,
            a.IdmaeItem_Inventario)) AS MIN_SAL,
        ISNULL(DATEDIFF(DAY, MIN(dbo.fneFechaRegistroMinimo_NotaInventario_Documento(
            130,  -- @IdtdDocumentoForm_NotaInventario_SalidaProduccion
            a.IdDocumento,
            a.IdmaeItem_Inventario)), GETDATE()), 0) AS DIAS_DESDE_MIN_SAL,
        MAX(k.NommaeAnexoCliente) AS CLIENTE,
        MAX(v.CoddocOrdenVenta) AS PEDIDO,
        MIN(i.dtFechaEntrega) AS F_ENT
    FROM (
        SELECT 
            a.IdDocumento,
            a.IdmaeItem_Inventario,
            a.dCantidadProgramado,
            a.dCantidadProducido
        FROM dbo.fntOrdenItem_Seguimiento_ServicioProduccion_Historico(13) a  -- @IdFiltro
    ) a
    INNER JOIN dbo.fntDocumento_Produccion() c
        ON a.IdDocumento = c.IdDocumento
    INNER JOIN dbo.maeAnexoProveedor d WITH (NOLOCK)
        ON c.IdmaeAnexo = d.IdmaeAnexo_Proveedor
    INNER JOIN dbo.maeItemInventario e WITH (NOLOCK)
        ON a.IdmaeItem_Inventario = e.IdmaeItem_Inventario
    INNER JOIN dbo.maeUnidadMedida f WITH (NOLOCK)
        ON e.IdmaeUnidadMedida_Almacen = f.IdmaeUnidadMedida
    INNER JOIN dbo.maeCombo g WITH (NOLOCK)
        ON e.IdmaeCombo = g.IdmaeCombo
    INNER JOIN dbo.docOrdenProduccion i WITH (NOLOCK)
        ON c.IdDocumento_Referencia = i.IdDocumento_OrdenProduccion
    INNER JOIN dbo.maeCentroCosto j WITH (NOLOCK)
        ON c.IdmaeCentroCosto = j.IdmaeCentroCosto
    INNER JOIN dbo.maeAnexoCliente k WITH (NOLOCK)
        ON i.IdmaeAnexo_Cliente = k.IdmaeAnexo_Cliente 
    INNER JOIN dbo.docOrdenVenta v WITH (NOLOCK) 
        ON i.IdDocumento_Referencia = v.IdDocumento_OrdenVenta
    INNER JOIN dbo.maeEstilo w WITH (NOLOCK) 
        ON e.IdmaeEstilo = w.IdmaeEstilo
    INNER JOIN dbo.maeEstiloRuta z WITH (NOLOCK) 
        ON e.IdmaeEstilo = z.IdmaeEstilo AND z.idmaeCentroCosto = 47
    WHERE j.IdmaeCentroCosto = 47
    GROUP BY c.CodDocumento, i.CoddocOrdenProduccion
    ORDER BY c.CodDocumento;
    """
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error al ejecutar la consulta: {e}")
        return pd.DataFrame()

# Función principal de la aplicación Streamlit
def main():
    st.title("Visualización de Datos de Producción")

    # Conectar a la base de datos
    conn = get_db_connection()
    if conn:
        # Obtener los datos
        df = get_data(conn)
        if not df.empty:
            # Filtrar los registros donde PENDIENT sea mayor a 4
            df_filtered = df[df['PENDIENT'] > 4]

            # Agrupar por proveedor y sumar MIN_PEND para evitar duplicación de barras
            df_grouped = df_filtered.groupby('PROVEEDOR', as_index=False).agg({
                'MIN_PEND': 'sum',
                'CLIENTE': 'first',  # Tomar el primer cliente para cada proveedor
                'OS_OT': 'first',     # Tomar el primer OS_OT para cada proveedor
                'MIN_SAL': 'first'    # Tomar la primera fecha MIN_SAL para cada proveedor
            })

            # Ordenar los datos por PROVEEDOR y MIN_PEND
            df_sorted = df_grouped.sort_values(by=['PROVEEDOR', 'MIN_PEND'], ascending=[True, False])

            # Redondear MIN_PEND a enteros
            df_sorted['MIN_PEND'] = df_sorted['MIN_PEND'].round().astype(int)

            # Formatear MIN_SAL en formato corto (solo la fecha)
            df_sorted['MIN_SAL'] = pd.to_datetime(df_sorted['MIN_SAL']).dt.strftime('%Y-%m-%d')

            # Truncar los nombres de los clientes a los primeros 15 caracteres
            df_sorted['CLIENTE'] = df_sorted['CLIENTE'].str.slice(0, 15)

            # Crear el gráfico de barras horizontales
            fig = px.bar(
                df_sorted,
                x="MIN_PEND",       # Eje X: Tamaño de la barra basado en MIN_PEND (redondeado)
                y="PROVEEDOR",      # Eje Y: Proveedor
                color="CLIENTE",    # Color por cliente
                title="OS por servicio (Ancho de barras proporcional a minutos de costura)",
                labels={
                    "MIN_PEND": "Minutos Pendientes",
                    "PROVEEDOR": "Proveedor",
                    "CLIENTE": "Cliente"
                },
                text="OS_OT",       # Mostrar el código de la orden (OS_OT) en las barras
                hover_data={
                    "MIN_SAL": True,   # Mostrar MIN_SAL en el hover (formato corto)
                    "CLIENTE": False   # Ocultar CLIENTE en el hover
                }
            )

            # Personalizar el gráfico
            fig.update_traces(
                textposition='inside',  # Mover el texto dentro de las barras
                insidetextanchor='middle'  # Centrar el texto dentro de las barras
            )
            fig.update_layout(
                xaxis_title="Minutos Pendientes",  # Título del eje X
                yaxis_title="Proveedor",
                showlegend=True,
                height=600,  # Ajustar la altura del gráfico
                margin=dict(l=50, r=50, b=100, t=100, pad=10)  # Ajustar los márgenes
            )

            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig, use_container_width=True)  # Usar el ancho completo del contenedor

        # Cerrar la conexión a la base de datos
        conn.close()

if __name__ == "__main__":
    main()
