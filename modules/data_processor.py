"""
modules/data_processor.py
Módulo de procesamiento y transformación de datos meteorológicos
Maneja cálculos, clasificaciones y métricas
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict

from config import config


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class DataProcessor:
    """Procesador de datos del reporte meteorológico"""
    
    # ========================================================================
    # FUNCIONES DE CÁLCULO BASE
    # ========================================================================
    
    @staticmethod
    def normalizar_disponibilidad(valor: float) -> float:
        """
        Normaliza valores de disponibilidad (limita a 100%)
        
        Args:
            valor: Valor de disponibilidad (puede ser > 100%)
            
        Returns:
            Valor normalizado entre 0 y 100
            
        Examples:
            >>> normalizar_disponibilidad(105.5)
            100.0
            >>> normalizar_disponibilidad(85.3)
            85.3
        """
        if pd.isna(valor):
            return 0.0
        return min(float(valor), config.THRESHOLD_ANOMALY)
    
    @staticmethod
    def calcular_dias_desde_incidencia(
        f_inci: any,
        fecha_referencia: Optional[datetime] = None
    ) -> Optional[int]:
        """
        Calcula días transcurridos desde la fecha de incidencia
        
        Args:
            f_inci: Fecha de incidencia (str, datetime, o pd.Timestamp)
            fecha_referencia: Fecha de referencia (default: hoy)
            
        Returns:
            Número de días transcurridos, o None si no hay fecha válida
            
        Examples:
            >>> calcular_dias_desde_incidencia("01/10/2025")  # Si hoy es 04/11/2025
            34
        """
        # Validar entrada
        if pd.isna(f_inci) or f_inci == '' or f_inci is None:
            return None
        
        if fecha_referencia is None:
            fecha_referencia = datetime.now()
        
        try:
            # Convertir a datetime
            if isinstance(f_inci, str):
                fecha_inci = pd.to_datetime(f_inci, format=config.DATE_FORMAT, errors='coerce')
            else:
                fecha_inci = pd.to_datetime(f_inci, errors='coerce')
            
            if pd.isna(fecha_inci):
                return None
            
            # Calcular diferencia
            dias = (fecha_referencia - fecha_inci).days
            return dias
            
        except Exception:
            return None
    
    @staticmethod
    def clasificar_prioridad(row: pd.Series) -> str:
        """
        Clasifica prioridad de atención según estado y días de incidencia

        Reglas de clasificación (actualizadas Nov 2025):
        - ALTA: Incidencias nuevas (≤30 días) con disponibilidad crítica
        - MEDIA: Recurrentes (>30 días) o Solucionadas en monitoreo (≤5 días)
        - BAJA: Paralizadas (≥90 días + disponibilidad = 0%)
        - N/A: Sin incidencias o disponibilidad >= umbral

        Args:
            row: Fila del DataFrame con columnas:
                  'estado_inci', 'dias_desde_inci', 'disponibilidad'

        Returns:
            str: 'ALTA', 'MEDIA', 'BAJA', o 'N/A'
        """
        estado = str(row.get('estado_inci', '')).lower().strip()
        dias = row.get('dias_desde_inci')
        disponibilidad = row.get('disponibilidad', 100)

        # Sin incidencia y operativa
        if pd.isna(dias) and disponibilidad >= config.THRESHOLD_CRITICAL:
            return 'N/A'

        # Días por defecto si no hay valor
        if pd.isna(dias):
            dias = 0

        # Clasificación por estado explícito: "Nueva"
        if 'nueva' in estado:
            return 'ALTA' if dias <= config.PRIORITY_HIGH_MAX_DAYS else 'MEDIA'

        # Clasificación por estado explícito: "Recurrente"
        elif 'recurrente' in estado:
            return 'MEDIA'

        # Clasificación por estado explícito: "Solucionada"
        elif 'solucionado' in estado or 'solucionada' in estado:
            # Monitoreo post-solución
            return 'MEDIA' if dias <= config.PRIORITY_MEDIUM_MONITOR_DAYS else 'N/A'

        # Clasificación por estado explícito: "Paralizada"
        elif 'paralizada' in estado:
            # Paralizadas con disponibilidad 0% y >= 90 días
            if disponibilidad == 0 and dias >= config.PRIORITY_PARALIZADA_MIN_DAYS:
                return 'BAJA'
            else:
                return 'MEDIA'  # Paralizada reciente

        # Clasificación automática por disponibilidad y tiempo
        if disponibilidad < config.THRESHOLD_CRITICAL:
            if dias <= config.PRIORITY_HIGH_MAX_DAYS:
                return 'ALTA'
            elif dias >= config.PRIORITY_PARALIZADA_MIN_DAYS and disponibilidad == 0:
                return 'BAJA'  # Paralizada sin estado explícito
            else:
                return 'MEDIA'  # Recurrente sin estado explícito

        return 'N/A'

    @staticmethod
    def generar_razon_prioridad(row: pd.Series) -> str:
        """
        Genera explicación de por qué la estación tiene su prioridad

        Args:
            row: Fila con columnas: prioridad, estado_inci, dias_desde_inci, disponibilidad

        Returns:
            str: Explicación textual de la razón
        """
        prioridad = row.get('prioridad', 'N/A')
        estado = str(row.get('estado_inci', '')).strip()
        dias = row.get('dias_desde_inci')
        disponibilidad = row.get('disponibilidad', 100)

        if prioridad == 'N/A':
            return "Operativa - Sin incidencias críticas"

        if pd.isna(dias):
            dias_texto = "sin fecha"
        else:
            dias_texto = f"{int(dias)} días"

        # Alerta de clausura
        alerta_clausura = ""
        if not pd.isna(dias) and dias >= config.PRIORITY_CLAUSURA_MIN_DAYS:
            años = dias // 365
            alerta_clausura = f" ⚠️ CANDIDATA A CLAUSURA ({años} años)"

        if prioridad == 'ALTA':
            if disponibilidad < config.THRESHOLD_CRITICAL:
                return f"Nueva ({dias_texto}) + Disponibilidad crítica ({disponibilidad:.1f}%)"
            else:
                return f"Incidencia nueva ({dias_texto}) - Estado: {estado}"

        elif prioridad == 'MEDIA':
            if 'recurrente' in estado.lower():
                return f"Recurrente ({dias_texto}) - Requiere seguimiento continuo"
            elif 'solucionado' in estado.lower():
                return f"Solucionada - En monitoreo post-reparación ({dias_texto})"
            else:
                return f"En proceso ({dias_texto}) - Disponibilidad: {disponibilidad:.1f}%"

        elif prioridad == 'BAJA':
            return f"Paralizada ({dias_texto}) - Disponibilidad: {disponibilidad:.1f}%{alerta_clausura}"

        return f"Estado: {estado} - {dias_texto}"
    
    @staticmethod
    def crear_id_sensor_unico(row: pd.Series) -> str:
        """
        Crea identificador único para sensor: Estacion_Sensor
        
        Args:
            row: Fila con columnas 'Estacion' y 'Sensor'
            
        Returns:
            str: ID único en formato "Estacion_Sensor"
            
        Examples:
            >>> crear_id_sensor_unico({'Estacion': 'Lima01', 'Sensor': 'Temp'})
            'Lima01_Temp'
        """
        estacion = str(row.get('Estacion', 'UNKNOWN')).strip()
        sensor = str(row.get('Sensor', 'UNKNOWN')).strip()
        return f"{estacion}_{sensor}"
    
    # ========================================================================
    # PROCESADORES DE DATAFRAMES
    # ========================================================================
    
    @classmethod
    def procesar_estaciones(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa DataFrame de estaciones con clasificaciones y cálculos

        Agrega columnas:
        - dias_desde_inci: Días desde la incidencia
        - prioridad: Clasificación ALTA/MEDIA/BAJA/N/A
        - razon_prioridad: Explicación de por qué tiene esa prioridad
        - disponibilidad_norm: Disponibilidad normalizada (≤100%)
        - es_anomalia: Boolean si disponibilidad > 100%

        Args:
            df: DataFrame con datos de estaciones (hoja POR ESTACION)

        Returns:
            DataFrame procesado con columnas adicionales
        """
        df_proc = df.copy()

        # Calcular días desde incidencia
        df_proc['dias_desde_inci'] = df_proc['f_inci'].apply(
            cls.calcular_dias_desde_incidencia
        )

        # Clasificar prioridad
        df_proc['prioridad'] = df_proc.apply(cls.clasificar_prioridad, axis=1)

        # Generar razón de prioridad
        df_proc['razon_prioridad'] = df_proc.apply(cls.generar_razon_prioridad, axis=1)

        # Normalizar disponibilidad
        df_proc['disponibilidad_norm'] = df_proc['disponibilidad'].apply(
            cls.normalizar_disponibilidad
        )

        # Detectar anomalías
        df_proc['es_anomalia'] = df_proc['disponibilidad'] > config.THRESHOLD_ANOMALY

        return df_proc
    
    @classmethod
    def procesar_sensores(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa DataFrame de sensores/equipamiento
        
        Agrega columnas:
        - sensor_id: ID único Estacion_Sensor
        - disponibilidad_norm: Disponibilidad normalizada
        - es_anomalia: Boolean si disponibilidad > 100%
        
        Args:
            df: DataFrame con datos de sensores (hoja POR EQUIPAMIENTO)
            
        Returns:
            DataFrame procesado con columnas adicionales
        """
        df_proc = df.copy()
        
        # Crear ID único
        df_proc['sensor_id'] = df_proc.apply(cls.crear_id_sensor_unico, axis=1)
        
        # Normalizar disponibilidad
        df_proc['disponibilidad_norm'] = df_proc['disponibilidad'].apply(
            cls.normalizar_disponibilidad
        )
        
        # Detectar anomalías
        df_proc['es_anomalia'] = df_proc['disponibilidad'] > config.THRESHOLD_ANOMALY
        
        return df_proc
    
    @classmethod
    def procesar_variables(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa DataFrame de variables meteorológicas
        
        Agrega columnas:
        - variable_id: ID único Estacion_Sensor
        - datos_recibidos: Suma de datos con flag C y M
        - perdida_datos: Datos esperados - datos recibidos
        - pct_perdida: Porcentaje de pérdida de datos
        - pct_errores: Porcentaje de datos con flag M (error)
        - disponibilidad_norm: Disponibilidad normalizada
        - es_anomalia: Boolean si disponibilidad > 100%
        
        Args:
            df: DataFrame con datos de variables (hoja POR VARIABLE)
            
        Returns:
            DataFrame procesado con columnas adicionales
        """
        df_proc = df.copy()
        
        # Crear ID único
        df_proc['variable_id'] = df_proc.apply(cls.crear_id_sensor_unico, axis=1)
        
        # Cálculos de datos
        df_proc['datos_recibidos'] = (
            df_proc['Datos_flag_C'] + df_proc['Datos_flag_M']
        )
        
        df_proc['perdida_datos'] = (
            df_proc['Datos_esperados'] - df_proc['datos_recibidos']
        )
        
        # Porcentajes
        df_proc['pct_perdida'] = (
            (df_proc['perdida_datos'] / df_proc['Datos_esperados'] * 100)
            .fillna(0)
        )
        
        df_proc['pct_errores'] = (
            (df_proc['Datos_flag_M'] / df_proc['datos_recibidos'] * 100)
            .fillna(0)
        )
        
        # Normalizar disponibilidad
        df_proc['disponibilidad_norm'] = df_proc['disponibilidad'].apply(
            cls.normalizar_disponibilidad
        )
        
        # Detectar anomalías
        df_proc['es_anomalia'] = df_proc['disponibilidad'] > config.THRESHOLD_ANOMALY
        
        return df_proc
    
    # ========================================================================
    # CÁLCULO DE MÉTRICAS GLOBALES
    # ========================================================================
    
    @staticmethod
    def calcular_metricas_globales(df_estaciones: pd.DataFrame) -> Dict[str, any]:
        """
        Calcula métricas principales de la red
        
        Args:
            df_estaciones: DataFrame procesado de estaciones
            
        Returns:
            Dict con métricas:
            {
                'promedio_red': float,
                'estaciones_criticas': int,
                'total_estaciones': int,
                'estaciones_alta': int,
                'estaciones_media': int,
                'estaciones_baja': int,
                'estaciones_anomalias': int,
                'dz_afectadas': int
            }
        """
        metricas = {
            'promedio_red': df_estaciones['disponibilidad_norm'].mean(),
            'estaciones_criticas': (
                df_estaciones['disponibilidad'] < config.THRESHOLD_CRITICAL
            ).sum(),
            'total_estaciones': len(df_estaciones),
            'estaciones_alta': (df_estaciones['prioridad'] == 'ALTA').sum(),
            'estaciones_media': (df_estaciones['prioridad'] == 'MEDIA').sum(),
            'estaciones_baja': (df_estaciones['prioridad'] == 'BAJA').sum(),
            'estaciones_anomalias': df_estaciones['es_anomalia'].sum(),
            'dz_afectadas': df_estaciones[
                df_estaciones['disponibilidad'] < config.THRESHOLD_CRITICAL
            ]['DZ'].nunique()
        }
        
        return metricas
    
    # ========================================================================
    # AGREGACIONES Y ANÁLISIS
    # ========================================================================
    
    @staticmethod
    def agrupar_por_dz(df_estaciones: pd.DataFrame) -> pd.DataFrame:
        """
        Agrupa estaciones por DZ con estadísticas
        
        Args:
            df_estaciones: DataFrame procesado de estaciones
            
        Returns:
            DataFrame con columnas: DZ, Disponibilidad_Promedio, Total_Estaciones
            Ordenado por disponibilidad ascendente
        """
        dz_stats = df_estaciones.groupby('DZ').agg({
            'disponibilidad_norm': 'mean',
            'Estacion': 'count'
        }).reset_index()
        
        dz_stats.columns = ['DZ', 'Disponibilidad_Promedio', 'Total_Estaciones']
        dz_stats = dz_stats.sort_values('Disponibilidad_Promedio')
        
        return dz_stats
    
    @staticmethod
    def obtener_top_criticos(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
        """
        Obtiene las N estaciones más críticas
        
        Args:
            df: DataFrame de estaciones
            n: Número de estaciones a retornar (default: 15)
            
        Returns:
            DataFrame con las N estaciones de menor disponibilidad
        """
        return df.nsmallest(n, 'disponibilidad')
    
    @staticmethod
    def filtrar_por_prioridad(df: pd.DataFrame, prioridad: str) -> pd.DataFrame:
        """
        Filtra DataFrame por nivel de prioridad
        
        Args:
            df: DataFrame de estaciones procesado
            prioridad: 'ALTA', 'MEDIA', 'BAJA', o 'N/A'
            
        Returns:
            DataFrame filtrado
        """
        return df[df['prioridad'] == prioridad].copy()
    
    @staticmethod
    def obtener_comentarios_con_incidencias(df_estaciones: pd.DataFrame) -> pd.DataFrame:
        """
        Obtiene estaciones con comentarios y disponibilidad crítica
        
        Args:
            df_estaciones: DataFrame procesado de estaciones
            
        Returns:
            DataFrame filtrado con incidencias activas
        """
        df_comentarios = df_estaciones[
            (df_estaciones['Comentario'].notna()) &
            (df_estaciones['Comentario'] != '') &
            (df_estaciones['disponibilidad'] < config.THRESHOLD_CRITICAL)
        ].copy()
        
        return df_comentarios