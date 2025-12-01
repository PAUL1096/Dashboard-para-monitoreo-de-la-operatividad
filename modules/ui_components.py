"""
modules/ui_components.py
Módulo de componentes de interfaz de usuario
Maneja la renderización de todas las secciones del dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Optional

from config import config, messages, charts
from modules.chart_builder import (
    ChartBuilder, 
    preparar_stats_tipo_sensor,
    preparar_stats_variables,
    preparar_stats_perdida_datos
)
from modules.data_processor import DataProcessor
from modules.file_handler import ExcelFileHandler


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class UIComponents:
    """Componentes de interfaz de usuario del dashboard"""
    
    def __init__(self):
        self.chart_builder = ChartBuilder()
        self.data_processor = DataProcessor()
        self.file_handler = ExcelFileHandler()
    
    # ========================================================================
    # SECCIÓN: ALERTAS Y PRIORIDADES
    # ========================================================================
    
    def mostrar_seccion_alertas(self, df_estaciones: pd.DataFrame):
        """
        Muestra sección de alertas y prioridades

        Args:
            df_estaciones: DataFrame procesado de estaciones
        """
        st.header("🚨 Alertas y Prioridades")

        prioridades = df_estaciones['prioridad'].value_counts()

        col1, col2, col3 = st.columns(3)

        with col1:
            alta_count = prioridades.get('ALTA', 0)
            st.markdown(f"""
            <div class="prioridad-alta">
                <p class="prioridad-title">🔴 PRIORIDAD ALTA</p>
                <p class="prioridad-number">{alta_count}</p>
                <p class="prioridad-desc">Requieren atención inmediata</p>
                <p class="prioridad-detail">Nuevas (≤30 días) o críticas sin resolver</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            media_count = prioridades.get('MEDIA', 0)
            st.markdown(f"""
            <div class="prioridad-media">
                <p class="prioridad-title">🟡 PRIORIDAD MEDIA</p>
                <p class="prioridad-number">{media_count}</p>
                <p class="prioridad-desc">En monitoreo o recurrentes</p>
                <p class="prioridad-detail">Requieren seguimiento técnico continuo</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            baja_count = prioridades.get('BAJA', 0)
            st.markdown(f"""
            <div class="prioridad-baja">
                <p class="prioridad-title">⚪ INFORMATIVO</p>
                <p class="prioridad-number">{baja_count}</p>
                <p class="prioridad-desc">Paralizadas (≥90 días)</p>
                <p class="prioridad-detail">Disponibilidad 0% - Candidatas a clausura si >2 años</p>
            </div>
            """, unsafe_allow_html=True)

        # Mostrar tabla de prioridad alta si hay
        if alta_count > 0:
            st.markdown("")  # Espacio
            st.subheader("📋 Estaciones de Prioridad Alta - Acción Requerida")

            df_alta = df_estaciones[df_estaciones['prioridad'] == 'ALTA'].sort_values(
                'dias_desde_inci', ascending=False
            )

            # Incluir columna razon_prioridad si existe
            cols_mostrar = [
                'DZ', 'Estacion', 'disponibilidad', 'razon_prioridad',
                'estado_inci', 'dias_desde_inci'
            ]
            cols_disponibles = [col for col in cols_mostrar if col in df_alta.columns]

            # Tabla más compacta con mejor altura
            st.dataframe(
                df_alta[cols_disponibles],
                use_container_width=True,
                height=min(300, 50 + len(df_alta) * 35),  # Altura dinámica pero limitada
                column_config={
                    "razon_prioridad": st.column_config.TextColumn(
                        "Razón de Prioridad",
                        width="large"
                    ),
                    "disponibilidad": st.column_config.NumberColumn(
                        "Disponibilidad (%)",
                        format="%.2f%%"
                    )
                }
            )

            # Expandible con tarjetas individuales
            with st.expander("📝 Ver detalle completo por estación (con comentarios técnicos)"):
                for idx, row in df_alta.iterrows():
                    # Detectar alerta de clausura
                    dias = row.get('dias_desde_inci', 0)
                    alerta_clausura = ""
                    if pd.notna(dias) and dias >= 730:  # 2 años
                        años = int(dias // 365)
                        alerta_clausura = f' <span style="color: #d62728; font-weight: bold;">⚠️ CANDIDATA A CLAUSURA ({años} años)</span>'

                    st.markdown(f"""
                    <div style="border: 2px solid #d62728; border-radius: 8px; padding: 12px; margin: 10px 0; background: #fff5f5;">
                        <h4 style="margin: 0 0 8px 0; color: #d62728;">
                            🔴 {row['Estacion']} ({row['DZ']}){alerta_clausura}
                        </h4>
                        <p style="margin: 4px 0;"><strong>📉 Disponibilidad:</strong> {row['disponibilidad']:.2f}%</p>
                        <p style="margin: 4px 0;"><strong>📅 Estado:</strong> {row['estado_inci']} - {row.get('dias_desde_inci', 'N/A')} días</p>
                        <p style="margin: 4px 0;"><strong>🎯 Razón:</strong> {row.get('razon_prioridad', 'N/A')}</p>
                        <p style="margin: 8px 0 0 0; padding-top: 8px; border-top: 1px solid #ffcccc;">
                            <strong>💬 Comentario Técnico:</strong><br>
                            <em>{row.get('Comentario', 'Sin comentarios')}</em>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ========================================================================
    # SECCIÓN: MÉTRICAS GLOBALES
    # ========================================================================
    
    def mostrar_metricas_globales(self, metricas: Dict[str, any]):
        """
        Muestra métricas globales de la red
        
        Args:
            metricas: Diccionario con métricas calculadas
        """
        st.header("📊 Métricas Globales de la Red")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Disponibilidad Promedio",
                f"{metricas['promedio_red']:.1f}%"
            )
        
        with col2:
            st.metric(
                "Estaciones Críticas",
                metricas['estaciones_criticas'],
                delta=f"de {metricas['total_estaciones']} total",
                delta_color="inverse"
            )
        
        with col3:
            pct_criticas = (
                metricas['estaciones_criticas'] / metricas['total_estaciones'] * 100
            ) if metricas['total_estaciones'] > 0 else 0
            st.metric("% Red Crítico", f"{pct_criticas:.1f}%")
        
        with col4:
            st.metric("Anomalías (>100%)", metricas['estaciones_anomalias'])
        
        with col5:
            st.metric("DZ Afectadas", metricas['dz_afectadas'])
    
    # ========================================================================
    # TAB 1: POR ESTACIÓN
    # ========================================================================
    
    def mostrar_tab_estaciones(self, df_estaciones: pd.DataFrame):
        """
        Renderiza contenido del tab de estaciones
        
        Args:
            df_estaciones: DataFrame procesado de estaciones
        """
        st.subheader("Análisis de Disponibilidad por Estación")
        
        # Gráficos principales
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = self.chart_builder.crear_histograma_disponibilidad(df_estaciones)
            st.plotly_chart(fig_hist, use_container_width=True, key = "hist_disp")
        
        with col2:
            fig_pie = self.chart_builder.crear_grafico_torta_categorias(df_estaciones)
            st.plotly_chart(fig_pie, use_container_width=True, key = "pie_cat")
        
        # Disponibilidad por DZ
        st.subheader("🗺️ Disponibilidad por DZ")
        dz_stats = self.data_processor.agrupar_por_dz(df_estaciones)
        fig_dz = self.chart_builder.crear_barras_disponibilidad_dz(dz_stats)

        # IMPORTANTE: Agregar config explícito
        st.plotly_chart(
            fig_dz, 
            use_container_width=True,
            config={
                'displayModeBar': True,
                'displaylogo': False,
                'responsive': True
            }
        )
        
        # Top críticos
        st.subheader(f"📻 Top {charts.TOP_N_CRITICAL} Estaciones Más Críticas")
        df_ranking = self.data_processor.obtener_top_criticos(
            df_estaciones, 
            n=charts.TOP_N_CRITICAL
        )
        fig_ranking = self.chart_builder.crear_ranking_criticos(df_ranking)
        st.plotly_chart(fig_ranking, use_container_width=True)
        
        # Tabla completa con filtros
        st.subheader("📋 Tabla Completa de Estaciones")
        df_filtrado = self._renderizar_filtros_estaciones(df_estaciones)
        
        # Mostrar tabla
        st.dataframe(df_filtrado, use_container_width=True, height=400)
        st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df_estaciones)} estaciones")
        
        # Botón de descarga
        csv = self.file_handler.exportar_csv(df_filtrado)
        nombre_archivo = self.file_handler.crear_nombre_descarga('estaciones')
        st.download_button(
            "📥 Descargar CSV",
            csv,
            nombre_archivo,
            'text/csv'
        )
    
    def _renderizar_filtros_estaciones(self, df_estaciones: pd.DataFrame) -> pd.DataFrame:
        """
        Renderiza filtros para tabla de estaciones
        
        Args:
            df_estaciones: DataFrame de estaciones
            
        Returns:
            DataFrame filtrado
        """
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categorias = ['Todas'] + sorted(df_estaciones['var_disp'].unique().tolist())
            cat_filtro = st.selectbox(
                'Filtrar por categoría',
                categorias,
                help=messages.TOOLTIP_CATEGORY
            )
        
        with col2:
            prioridades = ['Todas', 'ALTA', 'MEDIA', 'BAJA', 'N/A']
            pri_filtro = st.selectbox(
                'Filtrar por prioridad',
                prioridades,
                help=messages.TOOLTIP_PRIORITY
            )
        
        with col3:
            min_disp = st.slider(
                'Disponibilidad mínima (%)',
                0, 100, 0
            )
        
        # Aplicar filtros
        df_filtrado = df_estaciones.copy()
        
        if cat_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['var_disp'] == cat_filtro]
        
        if pri_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['prioridad'] == pri_filtro]
        
        df_filtrado = df_filtrado[
            df_filtrado['disponibilidad'] >= min_disp
        ].sort_values('disponibilidad')
        
        return df_filtrado
    
    # ========================================================================
    # TAB 2: POR SENSOR
    # ========================================================================
    
    def mostrar_tab_sensores(self, df_sensores: pd.DataFrame):
        """
        Renderiza contenido del tab de sensores
        
        Args:
            df_sensores: DataFrame procesado de sensores
        """
        st.subheader("Análisis por Sensor/Equipamiento")
        
        # Métricas de sensores
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Sensores", len(df_sensores))
        
        with col2:
            operativos = (df_sensores['disponibilidad'] >= config.THRESHOLD_CRITICAL).sum()
            pct_op = (operativos / len(df_sensores) * 100) if len(df_sensores) > 0 else 0
            st.metric("Operativos", f"{operativos} ({pct_op:.1f}%)")
        
        with col3:
            criticos = (df_sensores['disponibilidad'] < config.THRESHOLD_CRITICAL).sum()
            st.metric("Críticos", criticos)
        
        st.markdown("---")
        
        # Gráficos de distribución
        col1, col2 = st.columns(2)
        
        with col1:
            fig_box = self.chart_builder.crear_boxplot_sensores(df_sensores)
            st.plotly_chart(fig_box, use_container_width=True)
        
        with col2:
            fig_bar = self.chart_builder.crear_barras_sensores_categoria(df_sensores)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Por tipo de sensor
        st.subheader("🔧 Por Tipo de Sensor")
        tipo_stats = preparar_stats_tipo_sensor(df_sensores)
        fig_tipo = self.chart_builder.crear_barras_tipo_sensor(tipo_stats)
        st.plotly_chart(fig_tipo, use_container_width=True)
        
        # Tabla completa
        st.subheader("📋 Tabla Completa de Sensores")
        st.dataframe(
            df_sensores.sort_values('disponibilidad'),
            use_container_width=True,
            height=400
        )
        
        # Botón de descarga
        csv = self.file_handler.exportar_csv(df_sensores)
        nombre_archivo = self.file_handler.crear_nombre_descarga('sensores')
        st.download_button(
            "📥 Descargar CSV",
            csv,
            nombre_archivo,
            'text/csv'
        )
    
    # ========================================================================
    # TAB 3: POR VARIABLE
    # ========================================================================
    
    def mostrar_tab_variables(self, df_variables: pd.DataFrame):
        """
        Renderiza contenido del tab de variables
        
        Args:
            df_variables: DataFrame procesado de variables
        """
        st.subheader("Análisis por Variable Meteorológica")
        
        # Métricas de variables
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Registros", len(df_variables))
        
        with col2:
            st.metric(
                "Datos Esperados",
                f"{df_variables['Datos_esperados'].sum():,}"
            )
        
        with col3:
            st.metric(
                "Datos Recibidos",
                f"{df_variables['datos_recibidos'].sum():,}"
            )
        
        with col4:
            errores = df_variables['Datos_flag_M'].sum()
            total_recibidos = df_variables['datos_recibidos'].sum()
            pct_err = (errores / total_recibidos * 100) if total_recibidos > 0 else 0
            st.metric(
                "Con Error (Flag M)",
                f"{errores:,} ({pct_err:.1f}%)"
            )
        
        st.markdown("---")
        
        # Gráficos de análisis
        col1, col2 = st.columns(2)
        
        with col1:
            var_stats = preparar_stats_variables(df_variables)
            fig_var = self.chart_builder.crear_barras_variable_disponibilidad(var_stats)
            st.plotly_chart(fig_var, use_container_width=True)
        
        with col2:
            perdida = preparar_stats_perdida_datos(df_variables, top_n=charts.TOP_N_LOSS)
            fig_perd = self.chart_builder.crear_barras_perdida_datos(perdida)
            st.plotly_chart(fig_perd, use_container_width=True)
        
        # Información sobre Flag M
        with st.expander("ℹ️ Información sobre Datos con Flag M"):
            st.markdown("""
            **Datos con Flag M**: Datos que **superan umbrales operacionales SGR**
            - Se consideran disponibles pero con errores
            - NO se incluyen en cálculo de disponibilidad
            - Requieren revisión técnica
            """)
        
        # Tabla completa
        st.subheader("📋 Tabla Completa de Variables")
        st.dataframe(
            df_variables.sort_values('disponibilidad'),
            use_container_width=True,
            height=400
        )
        
        # Botón de descarga
        csv = self.file_handler.exportar_csv(df_variables)
        nombre_archivo = self.file_handler.crear_nombre_descarga('variables')
        st.download_button(
            "📥 Descargar CSV",
            csv,
            nombre_archivo,
            'text/csv'
        )
    
    # ========================================================================
    # TAB 4: COMENTARIOS TÉCNICOS
    # ========================================================================
    
    def mostrar_tab_comentarios(self, df_estaciones: pd.DataFrame):
        """
        Renderiza contenido del tab de comentarios técnicos
        
        Args:
            df_estaciones: DataFrame procesado de estaciones
        """
        st.subheader("📝 Comentarios Técnicos y Causas de Incidencias")
        
        # Obtener incidencias
        df_comentarios = self.data_processor.obtener_comentarios_con_incidencias(
            df_estaciones
        )
        
        if len(df_comentarios) > 0:
            # Métricas de incidencias
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Incidencias", len(df_comentarios))
            
            with col2:
                st.metric(
                    "Disponibilidad Promedio",
                    f"{df_comentarios['disponibilidad'].mean():.1f}%"
                )
            
            with col3:
                estados = df_comentarios['estado_inci'].value_counts()
                estado_comun = estados.index[0] if len(estados) > 0 else "N/A"
                st.metric("Estado Más Común", estado_comun)
            
            with col4:
                st.metric("DZ Afectadas", df_comentarios['DZ'].nunique())
            
            st.markdown("---")
            
            # Gráficos de análisis
            col1, col2 = st.columns(2)
            
            with col1:
                fig_est = self.chart_builder.crear_torta_estados_incidencia(df_comentarios)
                st.plotly_chart(fig_est, use_container_width=True)
            
            with col2:
                fig_dz = self.chart_builder.crear_barras_dz_incidencias(df_comentarios)
                st.plotly_chart(fig_dz, use_container_width=True)
            
            # Tabla detallada con filtro
            st.subheader("📋 Detalle de Incidencias")
            
            tipo_filtro = st.selectbox(
                'Filtrar por estado',
                ['Todos'] + sorted(df_comentarios['estado_inci'].unique().tolist())
            )
            
            if tipo_filtro != 'Todos':
                df_comentarios = df_comentarios[
                    df_comentarios['estado_inci'] == tipo_filtro
                ]
            
            cols_comentarios = [
                'DZ', 'Estacion', 'disponibilidad', 'estado_inci',
                'dias_desde_inci', 'f_inci', 'Comentario'
            ]
            cols_disp = [col for col in cols_comentarios if col in df_comentarios.columns]
            
            st.dataframe(
                df_comentarios[cols_disp].sort_values('disponibilidad'),
                use_container_width=True,
                height=500
            )
            
            # Botón de descarga
            csv = self.file_handler.exportar_csv(df_comentarios[cols_disp])
            nombre_archivo = self.file_handler.crear_nombre_descarga('incidencias')
            st.download_button(
                "📥 Descargar Incidencias",
                csv,
                nombre_archivo,
                'text/csv'
            )
        else:
            st.info("✅ No hay incidencias registradas con disponibilidad < 80%")
    
    # ========================================================================
    # UTILIDADES DE UI
    # ========================================================================
    
    @staticmethod
    def mostrar_estructura_excel():
        """Muestra la estructura requerida del archivo Excel"""
        st.markdown("""
        ### El archivo debe tener 3 hojas:
        
        **Hoja 1: POR ESTACION**
        - DZ, Estacion, disponibilidad, var_disp
        - f_inci (dd/mm/YYYY), estado_inci, Comentario
        
        **Hoja 2: POR EQUIPAMIENTO**
        - DZ, Estacion, Sensor, disponibilidad, var_disp
        
        **Hoja 3: POR VARIABLE**
        - DZ, Estacion, Sensor, frecuencia, disponibilidad, var_disp
        - Datos_flag_C, Datos_flag_M, Datos_esperados
        
        **Ejemplo de nombre:** `reporte_disponibilidad_SGR_0810_1910.xlsx`
        """)
    
    @staticmethod
    def mostrar_footer():
        """Muestra el footer del dashboard"""
        st.markdown("---")
        st.markdown(f"""
        <div class="footer">
            Dashboard de Monitoreo Meteorológico SGR | 
            Última actualización: {datetime.now().strftime(config.DATETIME_FORMAT)} | 
            Desarrollado con Streamlit y Python | Versión {config.VERSION}
        </div>
        """, unsafe_allow_html=True)