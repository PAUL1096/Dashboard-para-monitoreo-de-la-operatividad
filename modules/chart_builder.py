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

    @staticmethod
    def crear_boxplot_sensor_por_dz(df_filtrado: pd.DataFrame, sensor_seleccionado: str) -> go.Figure:
        """
        Crea boxplot de disponibilidad de un sensor específico por DZ con puntos individuales

        Args:
            df_filtrado: DataFrame filtrado por sensor con columnas: Estacion, DZ, disponibilidad
            sensor_seleccionado: Nombre del sensor seleccionado para el título

        Returns:
            Figura de Plotly con boxplot y puntos de estaciones
        """
        # Función para asignar color según disponibilidad
        def asignar_color(disp):
            if disp > 100:
                return '#F843CE'  # Magenta
            elif 80 <= disp <= 100:
                return '#129F16'  # Verde
            elif 30 <= disp < 80:
                return '#F89F16'  # Naranja
            elif 0 < disp < 30:
                return '#F84316'  # Rojo
            else:  # disp == 0
                return '#999C9D'  # Gris

        # Asignar colores a cada punto
        df_filtrado = df_filtrado.copy()
        df_filtrado['color'] = df_filtrado['disponibilidad'].apply(asignar_color)

        # Ordenar DZ alfabéticamente para consistencia
        dzs_ordenadas = sorted(df_filtrado['DZ'].unique())

        # Crear figura
        fig = go.Figure()

        # Agregar boxplot para cada DZ
        for dz in dzs_ordenadas:
            df_dz = df_filtrado[df_filtrado['DZ'] == dz]

            # Boxplot (sin mostrar puntos, los agregamos manualmente)
            fig.add_trace(go.Box(
                y=df_dz['disponibilidad'],
                name=dz,
                boxmean='sd',  # Mostrar media y desviación estándar
                marker_color='lightgray',
                line_color='gray',
                fillcolor='rgba(200, 200, 200, 0.3)',
                showlegend=False,
                hoverinfo='skip'  # No mostrar hover del boxplot
            ))

        # Agregar puntos individuales coloreados por disponibilidad
        for dz in dzs_ordenadas:
            df_dz = df_filtrado[df_filtrado['DZ'] == dz]

            for _, row in df_dz.iterrows():
                fig.add_trace(go.Scatter(
                    x=[dz],
                    y=[row['disponibilidad']],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=row['color'],
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate=(
                        f"<b>{row['Estacion']}</b><br>"
                        f"Disponibilidad: {row['disponibilidad']:.1f}%<br>"
                        "<extra></extra>"
                    ),
                    showlegend=False
                ))

        # Configurar layout
        fig.update_layout(
            title=f'Distribución de Disponibilidad: {sensor_seleccionado} por DZ',
            xaxis_title='Dirección Zonal',
            yaxis_title='Disponibilidad (%)',
            height=500,
            hovermode='closest',
            plot_bgcolor='white',
            yaxis=dict(
                gridcolor='lightgray',
                range=[-5, max(df_filtrado['disponibilidad'].max() + 10, 105)]
            )
        )

        # Agregar línea de umbral crítico
        fig.add_hline(
            y=config.THRESHOLD_CRITICAL,
            line_dash='dash',
            line_color='red',
            annotation_text=f'Umbral Crítico ({config.THRESHOLD_CRITICAL}%)',
            annotation_position='right'
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
    Prepara estadísticas por variable meteorológica
    
    Args:
        df_variables: DataFrame procesado de variables
        
    Returns:
        DataFrame agregado con estadísticas por variable
    """
    var_stats = df_variables.groupby('Sensor').agg({
        'disponibilidad_norm': 'mean',
        'variable_id': 'count'
    }).reset_index()
    
    var_stats.columns = ['Variable', 'Disponibilidad', 'Cantidad']
    var_stats = var_stats.sort_values('Disponibilidad')
    
    return var_stats


def preparar_stats_perdida_datos(df_variables: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Prepara top N variables con mayor pérdida de datos
    
    Args:
        df_variables: DataFrame procesado de variables
        top_n: Número de variables a retornar
        
    Returns:
        DataFrame con top N variables ordenadas por pérdida
    """
    perdida = df_variables.groupby('Sensor').agg({
        'perdida_datos': 'sum',
        'Datos_esperados': 'sum'
    }).reset_index()
    
    perdida['pct_perdida'] = (
        (perdida['perdida_datos'] / perdida['Datos_esperados'] * 100)
        .fillna(0)
    )
    
    perdida = perdida.sort_values('pct_perdida', ascending=False).head(top_n)
    
    return perdida