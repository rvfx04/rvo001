import streamlit as st
import pandas as pd
import pyodbc
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq

def reiniciar_chat():
    """Reinicia el historial del chat"""
    st.toast("Datos actualizados", icon='🔄')
    if "messages" in st.session_state:
        st.session_state.messages = []
        prompt_sistema = "Vas a actuar como un analista de datos experto, dando siempre respuestas claras y concretas en español. Si te piden tablas o listas, las generas en markdown."
        st.session_state.messages.append({"role": "system", "content": prompt_sistema})

def obtener_datos(fecha_inicio, fecha_fin):
    """Ejecuta la consulta SQL y devuelve un DataFrame"""
    consulta = """
    declare @F1 date, @F2 date;

set @F1 = '2025-01-01';
set @F2 = '2025-12-31';

;WITH ProductionCTE AS (
    Select 
        convert(date,sc.Fecha) as Fecha, 
        convert(int,sum(sc.Kg_Hilado)) AS Produccion_Hilado,
        convert(int,sum(sc.Kg_Tejido)) AS Produccion_Tejido,
        convert(int,sum(sc.Kg_Armados)) AS Produccion_Armado,
        convert(int,sum(sc.Kg_Teñidos)) AS Produccion_Teñido,
        convert(int,sum(sc.Unid_Cortadas)) AS Produccion_Corte,
        convert(int,sum(Unid_Cosidas)) AS Produccion_Costura
    From
    (
        --Hilado
        select 
            b.dtFechaRegistro AS Fecha, 
            a.dCantidadIng AS Kg_Hilado, 
            0 AS Kg_Tejido, 
            0 AS Kg_Armados,
            0 AS Kg_Teñidos,
            0 AS Unid_Cortadas,
            0 AS Unid_Cosidas
        from docNotaInventarioItem a 
        inner join docNotaInventario b
        on b.IdDocumento_NotaInventario = a.IdDocumento_NotaInventario
        where a.IdtdItemForm=19 and a.dCantidadIng>0 and 
        a.IdmaeCentroCosto=7 
        and b.IdtdDocumentoForm=1 
        and b.IdmaeArea_Almacen=6 
        and b.dtFechaRegistro between @F1 and @F2

        union all

        --Tejido
        select 
            dtFechaEmision, 
            0 AS Kg_Hilado, 
            dpeso as Kg_Tejido, 
            0 AS Kg_Armados,
            0 AS Kg_Teñidos,
            0 AS Unid_Cortadas,
            0 AS Unid_Cosidas
        from docOrdenProduccionRollo
        where dtFechaEmision between @F1 and @F2

        union all

        --Partidas armadas
        select 
            dtFechaEmision,  
            0 AS Kg_Hilado, 
            0 as Kg_Tejido, 
            dCantidad AS Kg_Armados,
            0 AS Kg_Teñidos,
            0 AS Unid_Cortadas,
            0 AS Unid_Cosidas
        from docOrdenProduccion
        where IdtdDocumentoForm=138 and bAnulado=0
        and dtFechaEmision between @F1 and @F2

        union all

        --Teñido
        select  
            cast(convert(char(8), Fechacerrado, 112) as datetime) AS Fecha, 
            0 AS Kg_Hilado, 
            0 as Kg_Tejido, 
            0 AS Kg_Armados,
            dCantidad AS Kg_Teñidos,
            0 AS Unid_Cortadas,
            0 AS Unid_Cosidas
        from docOrdenProduccion
        where IdtdDocumentoForm=138 and bAnulado=0 and bCerrado=1
        and cast(convert(char(8), Fechacerrado, 112) as datetime) between @F1 and @F2

        union all

        --Corte
        SELECT  
            a.dtFechaRegistro,
            0 AS Kg_Hilado, 
            0 as Kg_Tejido, 
            0 AS Kg_Armados,
            0 AS Kg_Teñidos,
            b.dCantidadIng AS Unid_Cortadas,
            0 AS Unid_Cosidas
        FROM dbo.docNotaInventario a WITH (NOLOCK)	
        INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK)      	
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario     	
            AND b.dCantidadIng <> 0     	
        INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK)      	
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion    	
            AND c.bCerrado = 0      	
            AND c.bAnulado = 0    	
            AND c.IdtdDocumentoForm = 127
        WHERE (a.IdtdDocumentoForm = 131)
            AND (a.bDevolucion = 0)      	
            AND (a.bDesactivado = 0)      	
            AND (a.bAnulado = 0)      	
            AND (a.IdDocumento_OrdenProduccion <> 0) 	
            and a.dtFechaRegistro between @F1 and @F2
            and a.IdmaeCentroCosto=29

        union all

        --Costura
        SELECT  
            a.dtFechaRegistro, 
            0 AS Kg_Hilado, 
            0 as Kg_Tejido, 
            0 AS Kg_Armados,
            0 AS Kg_Teñidos,
            0 AS Unid_Cortadas,
            b.dCantidadIng AS Unid_Cosidas  	
        FROM dbo.docNotaInventario a WITH (NOLOCK)	
        INNER JOIN dbo.docNotaInventarioItem b WITH (NOLOCK)      	
            ON a.IdDocumento_NotaInventario = b.IdDocumento_NotaInventario     	
            AND b.dCantidadIng <> 0     	
        INNER JOIN dbo.docOrdenProduccion c WITH (NOLOCK)      	
            ON a.IdDocumento_OrdenProduccion = c.IdDocumento_OrdenProduccion    	
            AND c.bCerrado = 0      	
            AND c.bAnulado = 0    	
            AND c.IdtdDocumentoForm = 127
        WHERE (a.IdtdDocumentoForm = 131)
            AND (a.bDevolucion = 0)      	
            AND (a.bDesactivado = 0)      	
            AND (a.bAnulado = 0)      	
            AND (a.IdDocumento_OrdenProduccion <> 0) 	
            and a.dtFechaRegistro between @F1 and @F2
            and a.IdmaeCentroCosto=47
    ) sc
    group by sc.Fecha
)
SELECT 
    Fecha,
    Proceso,
    Cantidad
FROM ProductionCTE
UNPIVOT
(
    Cantidad FOR Proceso IN 
    (
        Produccion_Hilado,
        Produccion_Tejido,
        Produccion_Armado,
        Produccion_Teñido,
        Produccion_Corte,
        Produccion_Costura
    )
) AS UnpivotedData
ORDER BY Fecha, Proceso;
    """
    
    try:


        
        # Obtener credenciales de los secretos
        connection_string = (
            f"DRIVER={{odbc driver 17 for sql server}};"
            f"SERVER={st.secrets["server"]};"
            f"DATABASE={st.secrets["database"};"
            f"UID={st.secrets["username"]};"
            f"PWD={st.secrets["password"]}"
        )
        
        conn = pyodbc.connect(connection_string)
        df = pd.read_sql(consulta, conn, params=(fecha_inicio, fecha_fin))
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error en la conexión: {str(e)}")
        return None

# Configuración inicial
st.set_page_config(
    page_title="Análisis de Producción",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar LLM
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    api_key=st.secrets["GROQ_API"],
)

# Sidebar para parámetros
with st.sidebar:
    st.header("📅 Rango de Fechas")
    fecha_inicio = st.date_input("Fecha inicial")
    fecha_fin = st.date_input("Fecha final")
    
    if st.button("Cargar Datos", use_container_width=True):
        with st.spinner("Conectando con la base de datos..."):
            df = obtener_datos(fecha_inicio, fecha_fin)
            
            if df is not None:
                st.session_state.df = df
                st.session_state.agent = create_pandas_dataframe_agent(
                    llm, df, allow_dangerous_code=True
                )
                reiniciar_chat()
                st.success(f"Datos cargados: {len(df)} registros encontrados")

# Interfaz principal
st.title("📈 Análisis de Producción en Tiempo Real")
st.caption("Sistema de consulta inteligente de datos de producción")

# Verificar que los secretos estén configurados
if not all(key in st.secrets.sql_server for key in ['server', 'database', 'username', 'password']):
    st.error("Faltan configuraciones en los secretos. Verifica que tengas:")
    st.code("""
    [sql_server]
    server = "tu_servidor"
    database = "tu_base_de_datos"
    username = "tu_usuario"
    password = "tu_contraseña"
    """)
    st.stop()

# Historial de chat
if "messages" not in st.session_state:
    reiniciar_chat()

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Input de usuario
if prompt := st.chat_input("Haz tu pregunta sobre la producción"):
    if "agent" not in st.session_state:
        st.warning("Primero carga los datos desde el sidebar")
        st.stop()
        
    # Mostrar pregunta
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtener respuesta
    with st.chat_message("assistant"):
        with st.spinner("Analizando..."):
            try:
                respuesta = st.session_state.agent.run({
                    "input": prompt,
                    "chat_history": st.session_state.messages
                })
                st.markdown(respuesta)
            except Exception as e:
                st.error(f"Error en el análisis: {str(e)}")
    
    # Actualizar historial
    st.session_state.messages.extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": respuesta}
    ])
