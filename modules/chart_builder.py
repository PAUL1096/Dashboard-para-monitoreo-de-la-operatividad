"""
modules/chart_builder.py
Módulo de construcción de gráficos Plotly
Genera todas las visualizaciones del dashboard
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

from config import config, charts


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class ChartBuilder:
    """Constructor de gráficos para el dashboard meteorológico"""
    
    # ========================================================================
    # GRÁFICOS DE ESTACIONES
    # ========================================================================
    
    @staticmethod
    def crear_histograma_disponibilidad(df_estaciones: pd.DataFrame) -> go.Figure:
        """Crea histograma de distribución de disponibilidad"""
        
        # Extraer valores válidos
        valores = df_estaciones['disponibilidad_norm'].dropna().tolist()
        
        # USAR go.Figure directamente (más confiable)
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=valores,
            nbinsx=charts.HISTOGRAM_BINS,
            marker=dict(
                color=charts.COLOR_PRIMARY,
                line=dict(color='white', width=1)
            ),
            name='Estaciones',
            hovertemplate='Disponibilidad: %{x:.1f}%<br>Cantidad: %{y}<extra></extra>'
        ))
        
        # Línea de umbral
        fig.add_vline(
            x=config.THRESHOLD_CRITICAL,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Umbral {config.THRESHOLD_CRITICAL}%",
            annotation_position="top right"
        )
        
        # Layout explícito
        fig.update_layout(
            title={
                'text': 'Distribución de Disponibilidad',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis=dict(
                title="Disponibilidad (%)",
                range=[0, 105],
                dtick=10,
                showgrid=False,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title="Cantidad de Estaciones",
                showgrid=True
            ),
            plot_bgcolor='white',
            showlegend=False,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def crear_grafico_torta_categorias(df_estaciones: pd.DataFrame) -> go.Figure:
        """
        Crea gráfico de torta con distribución por categoría
        
        Args:
            df_estaciones: DataFrame procesado de estaciones
            
        Returns:
            Figura de Plotly con gráfico de torta
        """
        conteo_cat = df_estaciones['var_disp'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=conteo_cat.index,
                values=conteo_cat.values,
                hole=0.3  # Dona
            )
        ])
        
        fig.update_layout(
            title='Distribución por Categoría',
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def crear_barras_disponibilidad_dz(df_dz_stats: pd.DataFrame) -> go.Figure:
        """Crea gráfico de barras horizontales de disponibilidad por DZ"""
        
        if len(df_dz_stats) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No hay datos por DZ",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Ordenar por disponibilidad
        df_sorted = df_dz_stats.sort_values('Disponibilidad_Promedio', ascending=True).copy()
        
        # Preparar datos como strings para DZ
        df_sorted['DZ_str'] = 'DZ ' + df_sorted['DZ'].astype(str)
        
        # Asignar colores según disponibilidad
        colors = []
        for val in df_sorted['Disponibilidad_Promedio']:
            if val < 60:
                colors.append('#d62728')  # Rojo
            elif val < 80:
                colors.append('#ff7f0e')  # Naranja
            else:
                colors.append('#2ca02c')  # Verde
        
        # USAR px.bar que es más confiable con escalas
        fig = px.bar(
            df_sorted,
            x='Disponibilidad_Promedio',
            y='DZ_str',
            orientation='h',
            title='Disponibilidad Promedio por DZ'
        )
        
        # Actualizar trazos con colores personalizados
        fig.update_traces(
            marker_color=colors,
            marker_line_color='white',
            marker_line_width=1,
            text=[
                f"{disp:.1f}% ({est} est.)" 
                for disp, est in zip(
                    df_sorted['Disponibilidad_Promedio'], 
                    df_sorted['Total_Estaciones']
                )
            ],
            textposition='outside',
            textfont=dict(size=11, color='black'),
            hovertemplate='<b>%{y}</b><br>Disponibilidad: %{x:.1f}%<extra></extra>'
        )
        
        # Línea de umbral
        fig.add_vline(
            x=config.THRESHOLD_CRITICAL,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Umbral {config.THRESHOLD_CRITICAL}%",
            annotation_position="top right",
            annotation_font_size=10
        )
        
        # LAYOUT CON ESCALA EXPLÍCITA Y CORRECTA
        fig.update_layout(
            title={
                'text': 'Disponibilidad Promedio por DZ',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16}
            },
            xaxis=dict(
                title="Disponibilidad Promedio (%)",
                range=[0, 100],              # ← Cambiar a 100 en lugar de 105
                dtick=10,                     # ← Marcas cada 10%
                showgrid=True,
                gridcolor='#E5E5E5',
                gridwidth=1,
                side='bottom',                # ← Asegurar que esté abajo
                type='linear'                 # ← CRÍTICO: tipo lineal explícito
            ),
            yaxis=dict(
                title="DZ",
                showgrid=False,
                type='category'               # ← CRÍTICO: tipo categoría
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            height=max(450, len(df_sorted) * 40),
            margin=dict(l=60, r=200, t=80, b=60),  # Más margen derecho
            bargap=0.15                        # Espaciado entre barras
        )
        
        # FORZAR configuración de ejes
        fig.update_xaxes(
            constrain='domain',
            range=[0, 100]                    # ← Forzar nuevamente
        )
        
        return fig
    
    @staticmethod
    def crear_ranking_criticos(df_criticos: pd.DataFrame) -> go.Figure:
        """
        Crea ranking de estaciones más críticas
        
        Args:
            df_criticos: DataFrame con las estaciones críticas (top N)
            
        Returns:
            Figura de Plotly con barras horizontales
        """
        fig = px.bar(
            df_criticos,
            x='disponibilidad',
            y='Estacion',
            orientation='h',
            title=f'Top {len(df_criticos)} Estaciones Más Críticas',
            color='disponibilidad',
            color_continuous_scale=charts.COLOR_SCALE_DIVERGING,
            hover_data=['DZ', 'disponibilidad']
        )
        
        # Ordenar por disponibilidad ascendente
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=charts.RANKING_HEIGHT,
            xaxis_title="Disponibilidad (%)",
            yaxis_title="Estación"
        )
        
        return fig
    
    # ========================================================================
    # GRÁFICOS DE SENSORES
    # ========================================================================
    
    @staticmethod
    def crear_boxplot_sensores(df_sensores: pd.DataFrame) -> go.Figure:
        """
        Crea boxplot de distribución de disponibilidad por tipo de sensor

        Args:
            df_sensores: DataFrame procesado de sensores

        Returns:
            Figura de Plotly con boxplot por tipo de sensor
        """
        # Agrupar por tipo de sensor
        fig = px.box(
            df_sensores,
            x='Sensor',
            y='disponibilidad',
            title='Distribución de Disponibilidad por Tipo de Sensor',
            labels={
                'Sensor': 'Tipo de Sensor',
                'disponibilidad': 'Disponibilidad (%)'
            },
            color='Sensor',
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        # Agregar línea de umbral crítico
        fig.add_hline(
            y=config.THRESHOLD_CRITICAL,
            line_dash=charts.CRITICAL_LINE_DASH,
            line_color=charts.CRITICAL_LINE_COLOR,
            annotation_text=f"Umbral Crítico ({config.THRESHOLD_CRITICAL}%)",
            annotation_position="right"
        )

        # Mejorar layout
        fig.update_layout(
            yaxis_title="Disponibilidad (%)",
            xaxis_title="Tipo de Sensor",
            showlegend=False,
            height=500,
            xaxis={'categoryorder': 'total descending'}  # Ordenar por mediana
        )

        # Rotar etiquetas del eje X si hay muchos sensores
        if df_sensores['Sensor'].nunique() > 5:
            fig.update_xaxes(tickangle=-45)

        return fig
    
    @staticmethod
    def crear_barras_sensores_categoria(df_sensores: pd.DataFrame) -> go.Figure:
        """
        Crea gráfico de barras de sensores por categoría
        
        Args:
            df_sensores: DataFrame procesado de sensores
            
        Returns:
            Figura de Plotly con barras horizontales
        """
        cat_sensores = df_sensores['var_disp'].value_counts()
        
        fig = px.bar(
            x=cat_sensores.values,
            y=cat_sensores.index,
            orientation='h',
            title='Sensores por Categoría',
            labels={'x': 'Cantidad', 'y': 'Categoría'},
            color_discrete_sequence=[charts.COLOR_PRIMARY]
        )
        
        fig.update_layout(
            xaxis_title="Cantidad de Sensores",
            yaxis_title="Categoría"
        )
        
        return fig
    
    @staticmethod
    def crear_barras_tipo_sensor(df_tipo_stats: pd.DataFrame) -> go.Figure:
        """
        Crea gráfico de barras de disponibilidad por tipo de sensor
        
        Args:
            df_tipo_stats: DataFrame con columnas: Tipo, Disponibilidad_Promedio, Cantidad
            
        Returns:
            Figura de Plotly con barras horizontales
        """
        fig = px.bar(
            df_tipo_stats,
            x='Disponibilidad_Promedio',
            y='Tipo',
            orientation='h',
            title='Disponibilidad Promedio por Tipo de Sensor',
            color='Disponibilidad_Promedio',
            color_continuous_scale=charts.COLOR_SCALE_DIVERGING,
            hover_data=['Cantidad']
        )
        
        fig.update_layout(
            xaxis_title="Disponibilidad Promedio (%)",
            yaxis_title="Tipo de Sensor"
        )
        
        return fig
    
    # ========================================================================
    # GRÁFICOS DE VARIABLES
    # ========================================================================
    
    @staticmethod
    def crear_barras_variable_disponibilidad(df_var_stats: pd.DataFrame) -> go.Figure:
        """
        Crea gráfico de disponibilidad por variable meteorológica
        
        Args:
            df_var_stats: DataFrame con columnas: Variable, Disponibilidad, Cantidad
            
        Returns:
            Figura de Plotly con barras horizontales
        """
        fig = px.bar(
            df_var_stats,
            x='Disponibilidad',
            y='Variable',
            orientation='h',
            title='Disponibilidad por Variable Meteorológica',
            color='Disponibilidad',
            color_continuous_scale=charts.COLOR_SCALE_DIVERGING,
            hover_data=['Cantidad']
        )
        
        fig.update_layout(
            xaxis_title="Disponibilidad Promedio (%)",
            yaxis_title="Variable"
        )
        
        return fig
    
    @staticmethod
    def crear_barras_perdida_datos(df_perdida: pd.DataFrame) -> go.Figure:
        """
        Crea gráfico de top variables con mayor pérdida de datos
        
        Args:
            df_perdida: DataFrame con columnas: Sensor, pct_perdida
            
        Returns:
            Figura de Plotly con barras horizontales
        """
        fig = px.bar(
            df_perdida,
            x='pct_perdida',
            y='Sensor',
            orientation='h',
            title=f'Top {len(df_perdida)} Variables con Mayor Pérdida de Datos',
            color='pct_perdida',
            color_continuous_scale=charts.COLOR_SCALE_SEQUENTIAL,
            labels={'pct_perdida': '% Pérdida', 'Sensor': 'Variable'}
        )
        
        fig.update_layout(
            xaxis_title="Pérdida de Datos (%)",
            yaxis_title="Variable"
        )
        
        return fig
    
    # ========================================================================
    # GRÁFICOS DE COMENTARIOS/INCIDENCIAS
    # ========================================================================
    
    @staticmethod
    def crear_torta_estados_incidencia(df_comentarios: pd.DataFrame) -> go.Figure:
        """
        Crea gráfico de torta con distribución de estados de incidencia
        
        Args:
            df_comentarios: DataFrame con incidencias
            
        Returns:
            Figura de Plotly con gráfico de torta
        """
        estado_counts = df_comentarios['estado_inci'].value_counts()
        
        fig = px.pie(
            values=estado_counts.values,
            names=estado_counts.index,
            title='Distribución por Estado de Incidencia',
            hole=0.3
        )
        
        return fig
    
    @staticmethod
    def crear_barras_dz_incidencias(df_comentarios: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """
        Crea gráfico de top DZ con más incidencias
        
        Args:
            df_comentarios: DataFrame con incidencias
            top_n: Número de DZ a mostrar (default: 10)
            
        Returns:
            Figura de Plotly con barras horizontales
        """
        dz_counts = df_comentarios['DZ'].value_counts().head(top_n)
        
        fig = px.bar(
            x=dz_counts.values,
            y=dz_counts.index,
            orientation='h',
            title=f'Top {top_n} DZ con Más Incidencias',
            labels={'x': 'Cantidad de Incidencias', 'y': 'DZ'},
            color_discrete_sequence=[charts.COLOR_PRIMARY]
        )
        
        fig.update_layout(
            xaxis_title="Cantidad de Incidencias",
            yaxis_title="DZ"
        )
        
        return fig
    
    # ========================================================================
    # GRÁFICOS DE ANÁLISIS AVANZADO (PROBLEMAS OCULTOS / RESUMEN)
    # ========================================================================

    @staticmethod
    def crear_heatmap_variables_por_estacion(
        df_variables: pd.DataFrame,
        top_n: int = 30
    ) -> go.Figure:
        """
        Heatmap Estación × Variable coloreado por disponibilidad.
        Muestra estaciones con al menos una variable crítica (<80%).
        """
        # Columna de nombre de variable individual: 'Variable' o fallback 'Sensor'
        col_var = 'Variable' if 'Variable' in df_variables.columns else 'Sensor'

        # Seleccionar estaciones con variables críticas (más informativo)
        est_con_criticas = df_variables[
            df_variables['disponibilidad_norm'] < 80
        ]['Estacion'].unique()

        df_sub = df_variables[df_variables['Estacion'].isin(est_con_criticas)].copy()

        # Limitar a top_n estaciones con más variables críticas
        conteo = (
            df_sub[df_sub['disponibilidad_norm'] < 80]
            .groupby('Estacion')[col_var]
            .count()
            .nlargest(top_n)
        )
        df_sub = df_sub[df_sub['Estacion'].isin(conteo.index)]

        if len(df_sub) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No hay datos para mostrar", x=0.5, y=0.5,
                               xref='paper', yref='paper', showarrow=False)
            return fig

        # Etiqueta de variable: nombre + frecuencia si existe
        if 'Frecuencia' in df_sub.columns:
            df_sub = df_sub.copy()
            df_sub['_var_label'] = df_sub[col_var].astype(str) + '\n[' + df_sub['Frecuencia'].astype(str) + ']'
        else:
            df_sub['_var_label'] = df_sub[col_var].astype(str)

        # Pivot: estaciones × variables
        pivot = df_sub.pivot_table(
            index='Estacion',
            columns='_var_label',
            values='disponibilidad_norm',
            aggfunc='mean'
        )

        # Ordenar estaciones por disponibilidad promedio (peores arriba)
        pivot = pivot.loc[pivot.mean(axis=1).sort_values().index]

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale='RdYlGn',
            zmin=0,
            zmax=100,
            colorbar=dict(
                title='Disp. (%)',
                tickvals=[0, 20, 40, 60, 80, 100],
            ),
            hovertemplate=(
                '<b>Estación:</b> %{y}<br>'
                '<b>Variable:</b> %{x}<br>'
                '<b>Disponibilidad:</b> %{z:.1f}%<extra></extra>'
            )
        ))

        fig.update_layout(
            title='Heatmap: Disponibilidad por Estación y Variable',
            xaxis=dict(title='Variable / Sensor', tickangle=-45, showgrid=False),
            yaxis=dict(title='Estación', showgrid=False, autorange='reversed'),
            height=max(400, len(pivot) * 22 + 120),
            margin=dict(l=160, r=80, t=60, b=100),
        )

        return fig

    @staticmethod
    def crear_grafico_problemas_ocultos(df_ocultos: pd.DataFrame) -> go.Figure:
        """
        Barras horizontales comparando disponibilidad de la estación
        vs disponibilidad del sensor/variable crítico (top 15 por brecha).
        """
        if len(df_ocultos) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No se detectaron problemas ocultos",
                               x=0.5, y=0.5, xref='paper', yref='paper', showarrow=False)
            return fig

        top = df_ocultos.nlargest(15, 'brecha').copy()
        top['etiqueta'] = (
            top['Estacion'].astype(str) + ' — ' +
            top['nivel'] + ': ' + top['nombre'].astype(str)
        )

        # Colores por significatividad
        colores_item = [
            '#EF4444' if sig else '#F59E0B'
            for sig in top['es_significativa']
        ]

        fig = go.Figure()

        # Barra de fondo: disponibilidad de la estación
        fig.add_trace(go.Bar(
            y=top['etiqueta'],
            x=top['disponibilidad_estacion'],
            orientation='h',
            name='Disp. Estación',
            marker_color='rgba(0,180,220,0.25)',
            marker_line_color='rgba(0,180,220,0.6)',
            marker_line_width=1,
            hovertemplate='Estación: %{x:.1f}%<extra></extra>'
        ))

        # Barra frontal: disponibilidad del item crítico
        fig.add_trace(go.Bar(
            y=top['etiqueta'],
            x=top['disponibilidad_item'],
            orientation='h',
            name='Disp. Sensor/Variable',
            marker_color=colores_item,
            marker_line_width=0,
            hovertemplate='%{x:.1f}% (brecha: ' + top['brecha'].round(1).astype(str) + '%)<extra></extra>'
        ))

        # Línea de umbral 80%
        fig.add_vline(
            x=80, line_dash='dash', line_color='rgba(255,255,255,0.3)',
            annotation_text='80%', annotation_font_size=10
        )

        fig.update_layout(
            title='Estaciones OK con Sensores/Variables Críticos Ocultos',
            barmode='overlay',
            xaxis=dict(title='Disponibilidad (%)', range=[0, 105]),
            yaxis=dict(title='', autorange='reversed'),
            legend=dict(orientation='h', y=1.08, x=0),
            height=max(400, len(top) * 32 + 120),
            margin=dict(l=300, r=40, t=80, b=60),
            annotations=[
                dict(
                    x=top.iloc[i]['disponibilidad_item'] + 1,
                    y=top.iloc[i]['etiqueta'],
                    text='⚠️' if top.iloc[i]['es_significativa'] else '',
                    showarrow=False,
                    font=dict(size=12),
                    xanchor='left'
                )
                for i in range(len(top))
            ]
        )

        return fig

    @staticmethod
    def crear_radar_dz(df_dz_radar: pd.DataFrame) -> go.Figure:
        """
        Gráfico radar (spider) comparando las DZs en múltiples dimensiones:
        - Disponibilidad promedio
        - % Estaciones operativas
        - % Estaciones críticas (invertida: menor es mejor)
        - Incidencias activas (invertida)
        - Problemas ocultos (invertida)
        """
        if len(df_dz_radar) == 0:
            fig = go.Figure()
            fig.add_annotation(text="Sin datos para radar", x=0.5, y=0.5,
                               xref='paper', yref='paper', showarrow=False)
            return fig

        # Normalizar métricas a 0-100 para que sean comparables en el radar
        df = df_dz_radar.copy()
        df['DZ_label'] = 'DZ ' + df['DZ'].astype(str)

        def norm_0_100(s, invert=False):
            mn, mx = s.min(), s.max()
            if mx == mn:
                return pd.Series([50.0] * len(s), index=s.index)
            n = (s - mn) / (mx - mn) * 100
            return 100 - n if invert else n

        df['dim_disp'] = norm_0_100(df['disponibilidad_prom'])
        df['dim_op'] = norm_0_100(df['pct_operativas'])
        df['dim_crit'] = norm_0_100(df['pct_criticas'], invert=True)
        df['dim_inci'] = norm_0_100(df['incidencias'], invert=True)
        df['dim_ocultos'] = norm_0_100(df['n_ocultos'], invert=True)

        categorias = [
            'Disponibilidad', 'Operativas', 'Sin Críticas',
            'Sin Incidencias', 'Sin Ocultos'
        ]

        colors = px.colors.qualitative.Set2[:len(df)]

        fig = go.Figure()

        for i, row in df.iterrows():
            valores = [
                row['dim_disp'], row['dim_op'], row['dim_crit'],
                row['dim_inci'], row['dim_ocultos']
            ]
            # Cerrar el polígono
            valores_cierre = valores + [valores[0]]
            cats_cierre = categorias + [categorias[0]]

            fig.add_trace(go.Scatterpolar(
                r=valores_cierre,
                theta=cats_cierre,
                fill='toself',
                name=row['DZ_label'],
                line=dict(width=1.5),
                opacity=0.6,
                hovertemplate=(
                    f"<b>{row['DZ_label']}</b><br>"
                    f"Disponibilidad: {row['disponibilidad_prom']:.1f}%<br>"
                    f"Operativas: {row['pct_operativas']:.1f}%<br>"
                    f"Críticas: {row['pct_criticas']:.1f}%<br>"
                    f"Incidencias: {int(row['incidencias'])}<br>"
                    f"Ocultos: {int(row['n_ocultos'])}<extra></extra>"
                )
            ))

        fig.update_layout(
            title='Comparativa de DZs — Radar Multidimensional',
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
                angularaxis=dict(tickfont=dict(size=11))
            ),
            showlegend=True,
            legend=dict(orientation='v', x=1.05, y=0.5),
            height=500,
            margin=dict(l=60, r=160, t=60, b=60)
        )

        return fig

    # ========================================================================
    # UTILIDADES DE GRÁFICOS
    # ========================================================================
    
    @staticmethod
    def aplicar_tema_comun(fig: go.Figure, altura: Optional[int] = None) -> go.Figure:
        """
        Aplica tema común a un gráfico
        
        Args:
            fig: Figura de Plotly a modificar
            altura: Altura del gráfico (opcional)
            
        Returns:
            Figura modificada
        """
        layout_updates = {
            'template': 'plotly_white',
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'hovermode': 'closest'
        }
        
        if altura:
            layout_updates['height'] = altura
        
        fig.update_layout(**layout_updates)
        
        return fig
    
    @staticmethod
    def agregar_linea_umbral(
        fig: go.Figure,
        valor: float,
        orientacion: str = 'v',
        label: Optional[str] = None
    ) -> go.Figure:
        """
        Agrega línea de umbral a un gráfico existente
        
        Args:
            fig: Figura de Plotly
            valor: Valor del umbral
            orientacion: 'v' (vertical) o 'h' (horizontal)
            label: Etiqueta opcional para la línea
            
        Returns:
            Figura modificada
        """
        if orientacion == 'v':
            fig.add_vline(
                x=valor,
                line_dash=charts.CRITICAL_LINE_DASH,
                line_color=charts.CRITICAL_LINE_COLOR,
                annotation_text=label
            )
        else:
            fig.add_hline(
                y=valor,
                line_dash=charts.CRITICAL_LINE_DASH,
                line_color=charts.CRITICAL_LINE_COLOR,
                annotation_text=label
            )
        
        return fig


# ============================================================================
# FUNCIONES DE PREPARACIÓN DE DATOS PARA GRÁFICOS
# ============================================================================

def preparar_stats_tipo_sensor(df_sensores: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara estadísticas por tipo de sensor para gráficos
    
    Args:
        df_sensores: DataFrame procesado de sensores
        
    Returns:
        DataFrame agregado con estadísticas por tipo
    """
    tipo_stats = df_sensores.groupby('Sensor').agg({
        'disponibilidad_norm': 'mean',
        'sensor_id': 'count'
    }).reset_index()
    
    tipo_stats.columns = ['Tipo', 'Disponibilidad_Promedio', 'Cantidad']
    tipo_stats = tipo_stats.sort_values('Disponibilidad_Promedio')
    
    return tipo_stats


def preparar_stats_variables(df_variables: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara estadísticas por variable meteorológica.
    Agrupa por la columna 'Variable' (nombre individual) si existe, si no por 'Sensor'.
    """
    col_var = 'Variable' if 'Variable' in df_variables.columns else 'Sensor'

    var_stats = df_variables.groupby(col_var).agg({
        'disponibilidad_norm': 'mean',
        'variable_id': 'count'
    }).reset_index()

    var_stats.columns = ['Variable', 'Disponibilidad', 'Cantidad']
    var_stats = var_stats.sort_values('Disponibilidad')

    return var_stats


def preparar_stats_perdida_datos(df_variables: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Prepara top N variables con mayor pérdida de datos.
    Agrupa por la columna 'Variable' (nombre individual) si existe, si no por 'Sensor'.
    """
    col_var = 'Variable' if 'Variable' in df_variables.columns else 'Sensor'

    perdida = df_variables.groupby(col_var).agg({
        'perdida_datos': 'sum',
        'Datos_esperados': 'sum'
    }).reset_index()

    perdida['pct_perdida'] = (
        (perdida['perdida_datos'] / perdida['Datos_esperados'] * 100)
        .fillna(0)
    )

    perdida = perdida.sort_values('pct_perdida', ascending=False).head(top_n)
    perdida = perdida.rename(columns={col_var: 'Sensor'})  # Mantener nombre de columna esperado

    return perdida