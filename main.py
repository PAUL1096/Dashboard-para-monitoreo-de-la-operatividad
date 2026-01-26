"""
main.py
Dashboard Interactivo para Monitoreo de Disponibilidad de Red Meteorológica
Autor: Sistema de Monitoreo Meteorológico - SGR
Versión: 2.2 (Mejoras Críticas)
Fecha: Diciembre 2025

Punto de entrada principal de la aplicación
"""

import streamlit as st
import os
import sys

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config, styles, messages, get_streamlit_config
from modules.file_handler import ExcelFileHandler, FileValidationError, FileLoadError
from modules.data_processor import DataProcessor
from modules.ui_components import UIComponents


# ============================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ============================================================================

class DashboardApp:
    """Clase principal que orquesta el dashboard meteorológico"""
    
    def __init__(self):
        """Inicializa los componentes de la aplicación"""
        self.file_handler = ExcelFileHandler()
        self.data_processor = DataProcessor()
        self.ui = UIComponents()
    
    def configurar_pagina(self):
        """Configura la página de Streamlit con estilos"""
        st.set_page_config(**get_streamlit_config())
        st.markdown(styles.get_full_css(), unsafe_allow_html=True)

        # Configuración adicional para Plotly
        st.markdown("""
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        """, unsafe_allow_html=True)
    
    def mostrar_header(self):
        """Muestra el encabezado principal del dashboard"""
        st.markdown(
            f'<p class="main-header">{config.APP_ICON} Dashboard de Disponibilidad - '
            f'Red Meteorológica SGR</p>',
            unsafe_allow_html=True
        )
    
    def cargar_datos_sidebar(self):
        """
        Maneja la carga de datos desde la barra lateral
        
        Returns:
            Tupla (datos, nombre_archivo) o (None, None) si no hay datos
        """
        st.sidebar.header("📂 Carga de Datos")
        
        # Opción 1: Subir archivo
        archivo_subido = st.sidebar.file_uploader(
            "Selecciona un archivo Excel",
            type=['xlsx', 'xls'],
            help=messages.TOOLTIP_UPLOAD
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("**O selecciona de carpeta local:**")
        
        # Opción 2: Desde carpeta
        ruta_carpeta = st.sidebar.text_input(
            "Ruta de carpeta de reportes",
            value=config.DEFAULT_REPORTS_PATH,
            help=messages.TOOLTIP_FOLDER
        )
        
        datos = None
        nombre_archivo = None
        
        # Intentar cargar desde archivo subido
        if archivo_subido is not None:
            try:
                datos = self.file_handler.cargar_excel(archivo_subido)
                nombre_archivo = archivo_subido.name
            except FileValidationError as e:
                st.sidebar.error(f"❌ Error de validación:\n{str(e)}")
                return None, None
            except FileLoadError as e:
                st.sidebar.error(f"❌ {str(e)}")
                return None, None
            except Exception as e:
                st.sidebar.error(f"❌ Error inesperado: {str(e)}")
                return None, None
        
        # Intentar cargar desde carpeta
        elif os.path.exists(ruta_carpeta):
            archivos = self.file_handler.listar_archivos_excel(ruta_carpeta)
            
            if archivos:
                archivo_seleccionado = st.sidebar.selectbox(
                    "Selecciona un reporte",
                    archivos,
                    index=0,
                    help=messages.TOOLTIP_SELECT
                )
                
                ruta_completa = os.path.join(ruta_carpeta, archivo_seleccionado)
                
                try:
                    datos = self.file_handler.cargar_excel(ruta_completa)
                    nombre_archivo = archivo_seleccionado
                    
                    # Mensaje de éxito para el más reciente
                    if archivo_seleccionado == archivos[0]:
                        st.sidebar.success("✅ Cargado: **Reporte más reciente**")
                
                except Exception as e:
                    st.sidebar.error(f"❌ Error al cargar: {str(e)}")
                    return None, None
            else:
                st.sidebar.warning(messages.MSG_NO_FILES)
        else:
            st.sidebar.info(f"{messages.MSG_FOLDER_NOT_EXIST.replace('{ruta_carpeta}', ruta_carpeta)}")
        
        # Mostrar información del archivo cargado
        if datos and nombre_archivo:
            st.sidebar.success(f"✅ Archivo: {nombre_archivo}")
            
            if datos['metadata']['fecha_inicio']:
                periodo = (
                    f"{datos['metadata']['fecha_inicio']} al "
                    f"{datos['metadata']['fecha_fin']}"
                )
                st.sidebar.info(f"📅 Período: {periodo}")
            
            # Mostrar estadísticas básicas
            with st.sidebar.expander("📊 Estadísticas del archivo"):
                st.write(f"**Estaciones:** {datos['metadata']['num_estaciones']}")
                st.write(f"**Sensores:** {datos['metadata']['num_sensores']}")
                st.write(f"**Variables:** {datos['metadata']['num_variables']}")
                st.write(f"**Cargado:** {datos['metadata']['fecha_carga']}")
        
        # Botón de recarga
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Recargar datos", help="Limpia la caché y recarga"):
            st.cache_data.clear()
            st.rerun()

        return datos, nombre_archivo

    def filtrar_por_dz_sidebar(self, df_estaciones, df_sensores, df_variables):
        """
        Renderiza selector de DZ en sidebar y filtra los DataFrames

        Args:
            df_estaciones: DataFrame de estaciones
            df_sensores: DataFrame de sensores
            df_variables: DataFrame de variables

        Returns:
            Tupla (df_estaciones_filtrado, df_sensores_filtrado, df_variables_filtrado, dz_seleccionada)
        """
        st.sidebar.markdown("---")
        st.sidebar.header("🗺️ Filtro por Dirección Zonal")

        # Obtener lista única de DZ ordenadas
        dzs_disponibles = sorted(df_estaciones['DZ'].unique().tolist())

        # Agregar opción "Todas" al inicio
        opciones_dz = ['Todas'] + dzs_disponibles

        # Selector de DZ
        dz_seleccionada = st.sidebar.selectbox(
            "Selecciona una DZ:",
            opciones_dz,
            index=0,
            help="Filtra todas las métricas, gráficos y tablas por Dirección Zonal"
        )

        # Aplicar filtro si no es "Todas"
        if dz_seleccionada == 'Todas':
            st.sidebar.info(f"📊 Mostrando **{len(dzs_disponibles)} DZ** en total")
            return df_estaciones, df_sensores, df_variables, dz_seleccionada
        else:
            # Filtrar DataFrames
            df_est_filtrado = df_estaciones[df_estaciones['DZ'] == dz_seleccionada].copy()
            df_sen_filtrado = df_sensores[df_sensores['DZ'] == dz_seleccionada].copy()
            df_var_filtrado = df_variables[df_variables['DZ'] == dz_seleccionada].copy()

            # Mostrar info del filtro
            st.sidebar.success(f"✅ Filtrando por: **{dz_seleccionada}**")
            st.sidebar.info(
                f"📊 **{len(df_est_filtrado)}** estaciones\n\n"
                f"📡 **{len(df_sen_filtrado)}** sensores\n\n"
                f"📈 **{len(df_var_filtrado)}** variables"
            )

            return df_est_filtrado, df_sen_filtrado, df_var_filtrado, dz_seleccionada
    
    def mostrar_instrucciones_carga(self, ruta_carpeta: str):
        """
        Muestra instrucciones cuando no hay datos cargados
        
        Args:
            ruta_carpeta: Ruta de la carpeta configurada
        """
        st.info(messages.MSG_NO_DATA)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(messages.INSTRUCTIONS_UPLOAD)
        
        with col2:
            st.markdown(
                messages.INSTRUCTIONS_FOLDER.replace(
                    'carpeta de reportes',
                    f'`{ruta_carpeta}`'
                )
            )
        
        # Expandible con estructura requerida
        with st.expander("📋 Ver estructura requerida del archivo Excel"):
            self.ui.mostrar_estructura_excel()
    
    def procesar_datos(self, datos: dict):
        """
        Procesa los datos cargados
        
        Args:
            datos: Diccionario con DataFrames cargados
            
        Returns:
            Tupla (df_estaciones, df_sensores, df_variables) procesados
            
        Raises:
            Exception: Si hay error en el procesamiento
        """
        try:
            df_estaciones = self.data_processor.procesar_estaciones(datos['estaciones'])
            df_sensores = self.data_processor.procesar_sensores(datos['sensores'])
            df_variables = self.data_processor.procesar_variables(datos['variables'])
            
            return df_estaciones, df_sensores, df_variables
        
        except Exception as e:
            raise Exception(f"Error procesando datos: {str(e)}")
    
    def renderizar_dashboard(self, df_estaciones, df_sensores, df_variables):
        """
        Renderiza todas las secciones del dashboard
        
        Args:
            df_estaciones: DataFrame procesado de estaciones
            df_sensores: DataFrame procesado de sensores
            df_variables: DataFrame procesado de variables
        """
        # Sección de alertas
        self.ui.mostrar_seccion_alertas(df_estaciones)
        st.markdown("---")
        
        # Métricas globales
        metricas = self.data_processor.calcular_metricas_globales(df_estaciones)
        self.ui.mostrar_metricas_globales(metricas)
        st.markdown("---")
        
        # Tabs principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏢 Por Estación",
            "📡 Por Sensor",
            "📈 Por Variable",
            "📝 Comentarios Técnicos"
        ])
        
        with tab1:
            self.ui.mostrar_tab_estaciones(df_estaciones)
        
        with tab2:
            self.ui.mostrar_tab_sensores(df_sensores)
        
        with tab3:
            self.ui.mostrar_tab_variables(df_variables)
        
        with tab4:
            self.ui.mostrar_tab_comentarios(df_estaciones)
        
        # Footer
        self.ui.mostrar_footer()
    
    def run(self):
        """Ejecuta la aplicación principal"""
        # Configurar página
        self.configurar_pagina()

        # Mostrar header
        self.mostrar_header()

        # Cargar datos
        datos, nombre_archivo = self.cargar_datos_sidebar()

        # Si no hay datos, mostrar instrucciones
        if datos is None:
            self.mostrar_instrucciones_carga(config.DEFAULT_REPORTS_PATH)
            return

        # Procesar datos
        try:
            df_estaciones, df_sensores, df_variables = self.procesar_datos(datos)
        except Exception as e:
            st.error(f"❌ {str(e)}")
            st.info("💡 Verifica que el archivo tenga la estructura correcta.")
            return

        # Aplicar filtro por DZ
        df_estaciones, df_sensores, df_variables, dz_seleccionada = self.filtrar_por_dz_sidebar(
            df_estaciones, df_sensores, df_variables
        )

        # Mostrar indicador de filtro en el header si aplica
        if dz_seleccionada != 'Todas':
            st.info(f"🗺️ **Vista filtrada por:** {dz_seleccionada}")

        # Renderizar dashboard
        try:
            self.renderizar_dashboard(df_estaciones, df_sensores, df_variables)
        except Exception as e:
            st.error(f"❌ Error al renderizar dashboard: {str(e)}")
            st.info("💡 Por favor, reporta este error al equipo de desarrollo.")
            return


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Función principal de entrada"""
    try:
        app = DashboardApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Error crítico en la aplicación: {str(e)}")
        st.info("💡 Por favor, reinicia la aplicación o contacta al soporte técnico.")


if __name__ == "__main__":
    main()