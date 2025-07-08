import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO


def main():
    st.set_page_config(page_title="Consolidador de Packing List", layout="wide")

    st.title("📦 Consolidador de Packing List")
    st.markdown("---")

    # Sidebar para cargar archivo
    with st.sidebar:
        st.header("📁 Cargar Archivo")
        uploaded_file = st.file_uploader(
            "Selecciona tu archivo Excel",
            type=['xlsx', 'xls'],
            help="El archivo debe contener las pestañas: Packing List y UPC"
        )

        if uploaded_file:
            st.success("✅ Archivo cargado correctamente")

    if uploaded_file is not None:
        try:
            # Leer las pestañas del Excel
            with st.spinner("Procesando archivo..."):
                excel_data = pd.read_excel(uploaded_file, sheet_name=None)

                # Verificar que existan las pestañas necesarias
                available_sheets = list(excel_data.keys())

                st.sidebar.write("**Pestañas encontradas:**")
                for sheet in available_sheets:
                    st.sidebar.write(f"- {sheet}")

            # Buscar las pestañas correctas (flexible con nombres)
            packing_sheet = None
            upc_sheet = None

            for sheet_name in available_sheets:
                if 'PL' in sheet_name.upper() or 'PACKING' in sheet_name.upper():
                    packing_sheet = sheet_name
                elif 'UPC' in sheet_name.upper():
                    upc_sheet = sheet_name

            if packing_sheet and upc_sheet:
                # Leer los datos
                packing_data = excel_data[packing_sheet]
                upc_data = excel_data[upc_sheet]

                # Mostrar pestañas
                tab1, tab2, tab3 = st.tabs(["📋 Packing List", "🏷️ UPC Data", "📊 Consolidado"])

                with tab1:
                    st.header("Packing List Original")
                    st.dataframe(packing_data, use_container_width=True)
                    st.info(f"Total de registros: {len(packing_data)}")

                with tab2:
                    st.header("Datos UPC")
                    st.dataframe(upc_data, use_container_width=True)
                    st.info(f"Total de UPCs: {len(upc_data)}")

                with tab3:
                    st.header("Resumen Consolidado")

                    # Procesar los datos para el consolidado
                    consolidated_data = process_consolidation(packing_data, upc_data)

                    if consolidated_data is not None and not consolidated_data.empty:
                        st.dataframe(consolidated_data, use_container_width=True)

                        # Estadísticas del consolidado
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Total UPCs", len(consolidated_data))

                        with col2:
                            total_units = consolidated_data[
                                'Units'].sum() if 'Units' in consolidated_data.columns else 0
                            st.metric("Total Unidades", f"{total_units:,}")

                        with col3:
                            unique_styles = consolidated_data[
                                'style #'].nunique() if 'style #' in consolidated_data.columns else 0
                            st.metric("Estilos Únicos", unique_styles)

                        with col4:
                            unique_colors = consolidated_data[
                                'Color'].nunique() if 'Color' in consolidated_data.columns else 0
                            st.metric("Colores Únicos", unique_colors)

                        # Botón para descargar el consolidado
                        st.markdown("---")
                        download_excel = create_download_file(consolidated_data)
                        st.download_button(
                            label="📥 Descargar Consolidado",
                            data=download_excel,
                            file_name="consolidado_packing_list.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("No se pudo generar el consolidado. Verifica la estructura de los datos.")

            else:
                st.error(f"No se encontraron las pestañas necesarias. Disponibles: {available_sheets}")

        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
            st.info("Asegúrate de que el archivo tenga el formato correcto y contenga las pestañas necesarias.")

    else:
        # Mostrar información sobre el formato esperado
        st.info("👆 Carga tu archivo Excel para comenzar")

        with st.expander("ℹ️ Formato de archivo esperado"):
            st.markdown("""
            **Tu archivo Excel debe contener:**

            **Pestaña 1 - Packing List:**
            - Información detallada de cada prenda
            - Columnas: Style, Color, Description, Tallas (2Y, 3Y, 4Y, etc.)
            - Cantidades por talla

            **Pestaña 2 - UPC:**
            - Códigos UPC únicos por combinación
            - Columnas: PO, UPC, Estilo, Color, Talla

            **Resultado - Consolidado:**
            - UPC, Style, Description, Color, Size, PO, Units
            """)


def process_consolidation(packing_data, upc_data):
    """
    Procesa los datos del packing list y UPC para generar el consolidado
    """
    try:
        consolidated_rows = []

        # Limpiar nombres de columnas
        packing_data.columns = packing_data.columns.astype(str).str.strip()
        upc_data.columns = upc_data.columns.astype(str).str.strip()

        # Función para encontrar columnas de manera flexible
        def find_column(df, possible_names):
            for name in possible_names:
                for col in df.columns:
                    if name.lower() in col.lower():
                        return col
            return None

        # Identificar columnas importantes en UPC data
        upc_style_col = find_column(upc_data, ['style', 'estilo', 'style #'])
        upc_color_col = find_column(upc_data, ['color', 'colour'])
        upc_size_col = find_column(upc_data, ['talla', 'size', 'tall'])
        upc_code_col = find_column(upc_data, ['upc', 'code'])
        upc_po_col = find_column(upc_data, ['po', 'order'])  # Agregar búsqueda de PO en UPC data

        # Identificar columnas importantes en packing data
        packing_style_col = find_column(packing_data, ['style', 'estilo', 'style #'])
        packing_color_col = find_column(packing_data, ['color', 'colour'])
        packing_desc_col = find_column(packing_data, ['description', 'desc'])
        packing_po_col = find_column(packing_data, ['po', 'order'])

        # Verificar que se encontraron las columnas necesarias
        if not all([upc_style_col, upc_color_col, upc_size_col, upc_code_col]):
            st.error(
                f"No se encontraron todas las columnas necesarias en UPC data. Columnas disponibles: {list(upc_data.columns)}")
            return None

        if not all([packing_style_col, packing_color_col]):
            st.error(
                f"No se encontraron todas las columnas necesarias en Packing data. Columnas disponibles: {list(packing_data.columns)}")
            return None

        # Identificar columnas de tallas en packing_data
        size_columns = []
        for col in packing_data.columns:
            if any(size in str(col).upper() for size in
                   ['0/3M', '3/6M', '6/12M', '12/18M', '18/24M', '2Y', '3Y', '4Y', '5Y', '6Y', '7Y', '8Y', '10Y', '12Y',
                    '14Y']):
                size_columns.append(col)

        st.info(f"Columnas de tallas encontradas: {size_columns}")

        # Procesar cada fila del packing list
        for idx, row in packing_data.iterrows():
            style = str(row.get(packing_style_col, '')).strip()
            color = str(row.get(packing_color_col, '')).strip()
            description = str(row.get(packing_desc_col, '')).strip() if packing_desc_col else ''
            po_packing = str(row.get(packing_po_col, '912')).strip() if packing_po_col else '912'

            # Procesar cada talla
            for size_col in size_columns:
                quantity = row.get(size_col, 0)

                # Convertir cantidad a numérico de forma segura
                try:
                    quantity = float(quantity) if pd.notna(quantity) else 0
                except:
                    quantity = 0

                if quantity > 0:
                    # Extraer el tamaño del nombre de la columna
                    size = str(size_col).strip()

                    # Buscar el UPC correspondiente - convertir todo a string para comparación
                    try:
                        # Crear máscaras booleanas paso a paso para mejor debugging
                        style_mask = upc_data[upc_style_col].astype(str).str.strip() == style
                        color_mask = upc_data[upc_color_col].astype(str).str.strip().str.lower() == color.lower()
                        size_mask = upc_data[upc_size_col].astype(str).str.strip() == size

                        # Combinar todas las máscaras
                        combined_mask = style_mask & color_mask & size_mask
                        upc_match = upc_data[combined_mask]

                    except Exception as match_error:
                        st.error(f"Error al buscar UPC para {style}-{color}-{size}: {match_error}")
                        continue

                    if not upc_match.empty:
                        upc_code = str(upc_match.iloc[0][upc_code_col]).strip()

                        # Obtener el PO de la tabla UPC, si no existe usar el del packing
                        if upc_po_col:
                            po_from_upc = str(upc_match.iloc[0][upc_po_col]).strip()
                        else:
                            po_from_upc = po_packing

                        consolidated_rows.append({
                            'UPC': upc_code,
                            'style #': style,
                            'Description': description,
                            'Color': color,
                            'Talla': size,
                            'PO': po_from_upc,  # Usar el PO de la tabla UPC
                            'Units': int(quantity)
                        })
                    else:
                        # Debug: mostrar información cuando no se encuentra match
                        st.warning(f"No se encontró UPC para: {style} | {color} | {size}")

        # Crear DataFrame consolidado
        if consolidated_rows:
            consolidated_df = pd.DataFrame(consolidated_rows)

            # Agrupar por UPC para sumar cantidades duplicadas
            consolidated_df = consolidated_df.groupby(
                ['UPC', 'style #', 'Description', 'Color', 'Talla', 'PO']
            )['Units'].sum().reset_index()

            # Ordenar por Style, Color, Size
            consolidated_df = consolidated_df.sort_values(['style #', 'Color', 'Talla'])

            return consolidated_df
        else:
            st.warning(
                "No se encontraron datos para consolidar. Verifica que las columnas de tallas tengan valores y que existan UPCs coincidentes.")

            # Mostrar algunos ejemplos para debugging
            st.write("**Ejemplos de datos en Packing List:**")
            sample_packing = packing_data.head(3)[[packing_style_col, packing_color_col] + size_columns[:3]]
            st.dataframe(sample_packing)

            st.write("**Ejemplos de datos en UPC:**")
            sample_upc = upc_data.head(10)[[upc_style_col, upc_color_col, upc_size_col, upc_code_col]]
            st.dataframe(sample_upc)

            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error en el procesamiento: {str(e)}")
        st.error(f"Columnas en UPC data: {list(upc_data.columns)}")
        st.error(f"Columnas en Packing data: {list(packing_data.columns)}")
        return None


def create_download_file(dataframe):
    """
    Crea un archivo Excel para descargar usando openpyxl en lugar de xlsxwriter
    """
    output = BytesIO()

    try:
        # Usar openpyxl que viene incluido con pandas
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, sheet_name='Consolidado', index=False)

            # Obtener el workbook y worksheet
            workbook = writer.book
            worksheet = writer.sheets['Consolidado']

            # Ajustar ancho de columnas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)
        return output.read()

    except ImportError:
        # Si openpyxl no está disponible, usar un método más simple
        st.warning("Openpyxl no está disponible. Generando archivo CSV en su lugar.")
        output = BytesIO()
        csv_data = dataframe.to_csv(index=False)
        output.write(csv_data.encode('utf-8'))
        output.seek(0)
        return output.read()


if __name__ == "__main__":
    main()
