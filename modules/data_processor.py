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
        - BAJA: Paralizadas (≥90 días + disponibilidad ≤ 0.5%) - MÁXIMA PRIORIDAD
        - ALTA: Incidencias nuevas (≤30 días) con disponibilidad crítica
        - MEDIA: Recurrentes (>30 días) o Solucionadas en monitoreo (≤5 días)
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

        # VERIFICACIÓN PRIORITARIA: Estación paralizada
        # Esta condición tiene precedencia sobre cualquier estado explícito
        if disponibilidad <= 0.5 and dias >= config.PRIORITY_PARALIZADA_MIN_DAYS:
            return 'BAJA'

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
            # Si llegó aquí, es porque no cumple condiciones de BAJA
            return 'MEDIA'  # Paralizada reciente o con disponibilidad > 0.5%

        # Clasificación automática por disponibilidad y tiempo
        if disponibilidad < config.THRESHOLD_CRITICAL:
            if dias <= config.PRIORITY_HIGH_MAX_DAYS:
                return 'ALTA'
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
        
        # Crear ID único: Estacion_Sensor_Variable_Frecuencia
        def crear_variable_id(row):
            est = str(row.get('Estacion', '')).strip()
            sen = str(row.get('Sensor', '')).strip()
            var = str(row.get('Variable', '')).strip()
            frec = str(row.get('Frecuencia', '')).strip()
            return f"{est}_{sen}_{var}_{frec}"

        df_proc['variable_id'] = df_proc.apply(crear_variable_id, axis=1)
        
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
    def detectar_problemas_ocultos(
        df_variables: pd.DataFrame,
        df_sensores: pd.DataFrame,
        df_estaciones: pd.DataFrame,
        umbral: float = 80.0
    ) -> pd.DataFrame:
        """
        Detecta problemas ocultos en la jerarquía Estación → Sensor → Variable.

        Jerarquía real del Excel:
          POR ESTACION  : una fila por (DZ, Estacion)
          POR EQUIPAMIENTO: una fila por (DZ, Estacion, Sensor)
          POR VARIABLE  : una fila por (DZ, Estacion, Sensor, Variable, Frecuencia)
          Join sensor↔variable: (DZ, Estacion, Sensor)

        Dos tipos de problema oculto:
          1. Sensor oculto  : estacion >= umbral  PERO  sensor < umbral
             brecha = disponibilidad_estacion - disponibilidad_sensor
          2. Variable oculta: sensor >= umbral    PERO  variable < umbral
             (independiente del estado de la estación)
             brecha = disponibilidad_sensor - disponibilidad_variable
             Se excluyen variables cuyo sensor ya es crítico (tipo 1)
             para evitar ruido redundante.

        Solo se analizan items con disponibilidad <= 100% (los >100% van a
        detectar_anomalias_configuracion).

        Returns:
            DataFrame con columnas:
              DZ, Estacion, Sensor, disponibilidad_referencia, disponibilidad_estacion,
              nivel ('Sensor' | 'Variable'), nombre, disponibilidad_item,
              brecha, es_significativa (brecha >= 30 pts)
        """
        col_empty = [
            'DZ', 'Estacion', 'Sensor', 'disponibilidad_referencia',
            'disponibilidad_estacion', 'nivel', 'nombre',
            'disponibilidad_item', 'brecha', 'es_significativa'
        ]

        # Trabajar solo con disponibilidades <= 100%
        df_sens = df_sensores[df_sensores['disponibilidad_norm'] <= 100.0].copy()
        df_var  = df_variables[df_variables['disponibilidad_norm'] <= 100.0].copy()

        # Tabla base de estaciones (disponibilidad normalizada)
        est_base = df_estaciones[['DZ', 'Estacion', 'disponibilidad_norm']].copy()
        est_base = est_base.rename(columns={'disponibilidad_norm': 'disponibilidad_estacion'})

        resultados = []

        # ── Tipo 1: Sensor oculto (estación OK pero sensor crítico) ──────────
        est_ok = est_base[est_base['disponibilidad_estacion'] >= umbral]

        sens_criticos = df_sens[df_sens['disponibilidad_norm'] < umbral][
            ['DZ', 'Estacion', 'Sensor', 'disponibilidad_norm']
        ].copy()

        if len(sens_criticos) > 0:
            m = est_ok.merge(sens_criticos, on=['DZ', 'Estacion'], how='inner')
            if len(m) > 0:
                m['nivel'] = 'Sensor'
                m['nombre'] = m['Sensor']
                m['disponibilidad_item'] = m['disponibilidad_norm']
                m['disponibilidad_referencia'] = m['disponibilidad_estacion']
                resultados.append(m[[
                    'DZ', 'Estacion', 'Sensor', 'disponibilidad_referencia',
                    'disponibilidad_estacion', 'nivel', 'nombre', 'disponibilidad_item'
                ]])

        # ── Tipo 2: Variable oculta (sensor OK pero variable crítica) ────────
        # Base: sensores con disponibilidad >= umbral
        sens_ok = df_sens[df_sens['disponibilidad_norm'] >= umbral][
            ['DZ', 'Estacion', 'Sensor', 'disponibilidad_norm']
        ].copy()
        sens_ok = sens_ok.rename(columns={'disponibilidad_norm': 'disponibilidad_sensor'})

        # Variables con 'Variable' como columna de nombre individual
        col_var_nombre = 'Variable' if 'Variable' in df_var.columns else 'Sensor'
        var_criticas = df_var[df_var['disponibilidad_norm'] < umbral][
            ['DZ', 'Estacion', 'Sensor', col_var_nombre, 'Frecuencia', 'disponibilidad_norm']
        ].drop_duplicates().copy()

        if len(var_criticas) > 0 and len(sens_ok) > 0:
            m2 = sens_ok.merge(var_criticas, on=['DZ', 'Estacion', 'Sensor'], how='inner')
            if len(m2) > 0:
                # Agregar disponibilidad de estación para contexto
                m2 = m2.merge(est_base, on=['DZ', 'Estacion'], how='left')
                m2['nivel'] = 'Variable'
                m2['nombre'] = m2[col_var_nombre].astype(str) + ' [' + m2['Frecuencia'].astype(str) + ']'
                m2['disponibilidad_item'] = m2['disponibilidad_norm']
                m2['disponibilidad_referencia'] = m2['disponibilidad_sensor']
                resultados.append(m2[[
                    'DZ', 'Estacion', 'Sensor', 'disponibilidad_referencia',
                    'disponibilidad_estacion', 'nivel', 'nombre', 'disponibilidad_item'
                ]])

        if not resultados:
            return pd.DataFrame(columns=col_empty)

        df_result = pd.concat(resultados, ignore_index=True)
        df_result['disponibilidad_estacion'] = df_result['disponibilidad_estacion'].fillna(0)
        df_result['brecha'] = df_result['disponibilidad_referencia'] - df_result['disponibilidad_item']
        df_result['es_significativa'] = df_result['brecha'] >= 30.0
        df_result = df_result.sort_values('brecha', ascending=False).drop_duplicates()

        return df_result

    @staticmethod
    def detectar_anomalias_configuracion(
        df_variables: pd.DataFrame,
        df_sensores: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Detecta sensores y variables con disponibilidad > 100%.
        Indica error de configuración (frecuencia incorrecta o datos esperados mal calculados).

        Returns:
            DataFrame con columnas:
              DZ, Estacion, Sensor, nivel, nombre, disponibilidad_item, exceso
        """
        resultados = []

        # Sensores > 100%
        anomalos_s = df_sensores[df_sensores['disponibilidad'] > 100.0].copy()
        if len(anomalos_s) > 0:
            anomalos_s['nivel'] = 'Sensor'
            anomalos_s['nombre'] = anomalos_s['Sensor']
            anomalos_s['disponibilidad_item'] = anomalos_s['disponibilidad']
            resultados.append(
                anomalos_s[['DZ', 'Estacion', 'Sensor', 'nivel', 'nombre', 'disponibilidad_item']]
            )

        # Variables > 100%
        col_var_nombre = 'Variable' if 'Variable' in df_variables.columns else 'Sensor'
        anomalos_v = df_variables[df_variables['disponibilidad'] > 100.0].copy()
        if len(anomalos_v) > 0:
            anomalos_v['nivel'] = 'Variable'
            freq_str = anomalos_v[col_var_nombre].astype(str)
            if 'Frecuencia' in anomalos_v.columns:
                freq_str = freq_str + ' [' + anomalos_v['Frecuencia'].astype(str) + ']'
            anomalos_v['nombre'] = freq_str
            anomalos_v['disponibilidad_item'] = anomalos_v['disponibilidad']
            resultados.append(
                anomalos_v[['DZ', 'Estacion', 'Sensor', 'nivel', 'nombre', 'disponibilidad_item']]
            )

        if not resultados:
            return pd.DataFrame(columns=[
                'DZ', 'Estacion', 'Sensor', 'nivel', 'nombre', 'disponibilidad_item', 'exceso'
            ])

        df_result = pd.concat(resultados, ignore_index=True)
        df_result['exceso'] = df_result['disponibilidad_item'] - 100.0
        df_result = df_result.sort_values(['DZ', 'Estacion', 'exceso'], ascending=[True, True, False])
        df_result = df_result.drop_duplicates()

        return df_result

    @staticmethod
    def calcular_metricas_radar_dz(
        df_estaciones: pd.DataFrame,
        df_ocultos: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calcula métricas por DZ para el gráfico radar del resumen ejecutivo.

        Returns:
            DataFrame con columnas:
              DZ, disponibilidad_prom, pct_operativas, pct_criticas,
              n_incidencias, n_ocultos
        """
        dz_stats = df_estaciones.groupby('DZ').agg(
            disponibilidad_prom=('disponibilidad_norm', 'mean'),
            total=('Estacion', 'count'),
            operativas=('disponibilidad_norm', lambda x: (x >= 80).sum()),
            criticas=('disponibilidad_norm', lambda x: (x < 80).sum()),
            incidencias=('prioridad', lambda x: (x.isin(['ALTA', 'MEDIA'])).sum()),
        ).reset_index()

        dz_stats['pct_operativas'] = dz_stats['operativas'] / dz_stats['total'] * 100
        dz_stats['pct_criticas'] = dz_stats['criticas'] / dz_stats['total'] * 100

        # Problemas ocultos por DZ
        if len(df_ocultos) > 0:
            ocultos_dz = df_ocultos.groupby('DZ')['Estacion'].nunique().reset_index()
            ocultos_dz.columns = ['DZ', 'n_ocultos']
            dz_stats = dz_stats.merge(ocultos_dz, on='DZ', how='left')
        else:
            dz_stats['n_ocultos'] = 0

        dz_stats['n_ocultos'] = dz_stats['n_ocultos'].fillna(0)

        return dz_stats

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