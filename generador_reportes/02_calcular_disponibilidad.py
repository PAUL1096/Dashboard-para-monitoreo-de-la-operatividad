"""
02_calcular_disponibilidad.py
Cálculo de métricas de disponibilidad y generación de Excel

Autor: Sistema de Monitoreo Meteorológico - SGR
Versión: 1.0
Fecha: Enero 2026

Este script toma el CSV con datos raw y calcula las métricas de disponibilidad
agrupadas por estación, sensor y variable, generando un Excel con 3 hojas.

Entrada: CSV en output/datos_raw.csv
Salida: Excel en ../reportes/reporte_disponibilidad_SGR_DDMM_DDMM.xlsx
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Rutas por defecto
DEFAULT_INPUT_FILE = Path(__file__).parent / "output" / "datos_raw.csv"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "reportes"

# Nombres de hojas en el Excel de salida
HOJA_ESTACION = "POR ESTACION"
HOJA_EQUIPAMIENTO = "POR EQUIPAMIENTO"
HOJA_VARIABLE = "POR VARIABLE"


# ============================================================================
# FUNCIONES DE CÁLCULO DE DISPONIBILIDAD
# ============================================================================

def calcular_disponibilidad(datos_correctos: float, datos_esperados: float) -> float:
    """
    Calcula el porcentaje de disponibilidad.

    Args:
        datos_correctos: Cantidad de datos correctos (flag_C)
        datos_esperados: Cantidad de datos esperados

    Returns:
        Porcentaje de disponibilidad (0-100)
    """
    if datos_esperados is None or datos_esperados == 0:
        return 0.0

    disponibilidad = (datos_correctos / datos_esperados) * 100
    return round(disponibilidad, 2)


def calcular_variacion(disp_actual: float, disp_anterior: float = None) -> float:
    """
    Calcula la variación de disponibilidad respecto al período anterior.

    Args:
        disp_actual: Disponibilidad actual
        disp_anterior: Disponibilidad del período anterior (opcional)

    Returns:
        Variación en puntos porcentuales
    """
    if disp_anterior is None:
        return 0.0

    return round(disp_actual - disp_anterior, 2)


# ============================================================================
# FUNCIONES DE AGREGACIÓN POR NIVEL
# ============================================================================

def generar_hoja_estacion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la hoja 'POR ESTACION' con métricas agregadas por estación.

    Agrupa por: DZ, Estacion
    Calcula: disponibilidad promedio, variación, info de incidencia

    Args:
        df: DataFrame con datos raw

    Returns:
        DataFrame agregado por estación
    """
    logger.info("Generando hoja: POR ESTACION")

    # Agrupar por DZ y Estación
    df_estacion = df.groupby(['DZ', 'Estacion']).agg({
        'Datos_flag_C': 'sum',
        'Datos_esperados': 'sum',
        'f_inci': 'first',          # Tomar primera fecha de incidencia
        'estado_inci': 'first',     # Tomar primer estado
        'comentario': 'first'       # Tomar primer comentario
    }).reset_index()

    # Calcular disponibilidad
    df_estacion['disponibilidad'] = df_estacion.apply(
        lambda row: calcular_disponibilidad(row['Datos_flag_C'], row['Datos_esperados']),
        axis=1
    )

    # Calcular variación (placeholder - requiere datos históricos)
    df_estacion['var_disp'] = 0.0

    # Seleccionar y ordenar columnas para salida
    columnas_salida = [
        'DZ', 'Estacion', 'disponibilidad', 'var_disp',
        'f_inci', 'estado_inci', 'comentario'
    ]

    # Filtrar solo columnas que existen
    columnas_existentes = [c for c in columnas_salida if c in df_estacion.columns]
    df_salida = df_estacion[columnas_existentes].copy()

    logger.info(f"  - {len(df_salida)} estaciones procesadas")

    return df_salida


def generar_hoja_equipamiento(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la hoja 'POR EQUIPAMIENTO' con métricas por sensor/equipo.

    Agrupa por: DZ, Estacion, Sensor (tipo de equipamiento)
    Calcula: disponibilidad por tipo de sensor

    Args:
        df: DataFrame con datos raw

    Returns:
        DataFrame agregado por equipamiento
    """
    logger.info("Generando hoja: POR EQUIPAMIENTO")

    # Agrupar por DZ, Estación y Sensor
    df_equipo = df.groupby(['DZ', 'Estacion', 'Sensor']).agg({
        'Datos_flag_C': 'sum',
        'Datos_esperados': 'sum'
    }).reset_index()

    # Calcular disponibilidad
    df_equipo['disponibilidad'] = df_equipo.apply(
        lambda row: calcular_disponibilidad(row['Datos_flag_C'], row['Datos_esperados']),
        axis=1
    )

    # Calcular variación (placeholder)
    df_equipo['var_disp'] = 0.0

    # Seleccionar columnas para salida
    columnas_salida = ['DZ', 'Estacion', 'Sensor', 'disponibilidad', 'var_disp']
    df_salida = df_equipo[columnas_salida].copy()

    logger.info(f"  - {len(df_salida)} registros de equipamiento procesados")

    return df_salida


def generar_hoja_variable(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la hoja 'POR VARIABLE' con métricas detalladas por variable.

    Mantiene detalle por: DZ, Estacion, Sensor (variable), Frecuencia
    Incluye: disponibilidad, datos correctos, malos, esperados

    Args:
        df: DataFrame con datos raw

    Returns:
        DataFrame con detalle por variable
    """
    logger.info("Generando hoja: POR VARIABLE")

    # Copiar datos y calcular disponibilidad
    df_variable = df.copy()

    df_variable['disponibilidad'] = df_variable.apply(
        lambda row: calcular_disponibilidad(
            row.get('Datos_flag_C', 0),
            row.get('Datos_esperados', 0)
        ),
        axis=1
    )

    # Calcular variación (placeholder)
    df_variable['var_disp'] = 0.0

    # Seleccionar columnas para salida
    columnas_salida = [
        'DZ', 'Estacion', 'Sensor', 'Frecuencia',
        'disponibilidad', 'var_disp',
        'Datos_flag_C', 'Datos_flag_M', 'Datos_esperados'
    ]

    # Filtrar solo columnas que existen
    columnas_existentes = [c for c in columnas_salida if c in df_variable.columns]
    df_salida = df_variable[columnas_existentes].copy()

    logger.info(f"  - {len(df_salida)} registros de variables procesados")

    return df_salida


# ============================================================================
# FUNCIÓN DE GENERACIÓN DE EXCEL
# ============================================================================

def generar_excel(
    df_estacion: pd.DataFrame,
    df_equipamiento: pd.DataFrame,
    df_variable: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Genera el archivo Excel con las 3 hojas.

    Args:
        df_estacion: DataFrame de la hoja POR ESTACION
        df_equipamiento: DataFrame de la hoja POR EQUIPAMIENTO
        df_variable: DataFrame de la hoja POR VARIABLE
        output_path: Ruta del archivo Excel de salida
    """
    logger.info(f"Generando Excel: {output_path}")

    # Crear directorio si no existe
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Escribir Excel con las 3 hojas
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_estacion.to_excel(writer, sheet_name=HOJA_ESTACION, index=False)
        df_equipamiento.to_excel(writer, sheet_name=HOJA_EQUIPAMIENTO, index=False)
        df_variable.to_excel(writer, sheet_name=HOJA_VARIABLE, index=False)

    logger.info(f"Excel generado exitosamente: {output_path}")


def generar_nombre_archivo(fecha_inicio: str = None, fecha_fin: str = None) -> str:
    """
    Genera el nombre del archivo Excel con formato estándar.

    Args:
        fecha_inicio: Fecha de inicio del período (DDMM)
        fecha_fin: Fecha de fin del período (DDMM)

    Returns:
        Nombre del archivo (ej: reporte_disponibilidad_SGR_0801_1501.xlsx)
    """
    if fecha_inicio and fecha_fin:
        return f"reporte_disponibilidad_SGR_{fecha_inicio}_{fecha_fin}.xlsx"

    # Si no hay fechas, usar fecha actual
    hoy = datetime.now()
    hace_7_dias = hoy - pd.Timedelta(days=7)
    return f"reporte_disponibilidad_SGR_{hace_7_dias.strftime('%d%m')}_{hoy.strftime('%d%m')}.xlsx"


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def procesar_csv_a_excel(input_file: Path, output_dir: Path) -> Path:
    """
    Procesa el CSV de datos raw y genera el Excel con disponibilidad.

    Args:
        input_file: Ruta del CSV de entrada
        output_dir: Directorio para el Excel de salida

    Returns:
        Ruta del archivo Excel generado
    """
    logger.info(f"Leyendo CSV: {input_file}")

    # Leer CSV
    df = pd.read_csv(input_file, encoding='utf-8')
    logger.info(f"Registros cargados: {len(df)}")

    if df.empty:
        logger.warning("El CSV está vacío - generando Excel con estructura vacía")

    # Generar las 3 hojas
    df_estacion = generar_hoja_estacion(df)
    df_equipamiento = generar_hoja_equipamiento(df)
    df_variable = generar_hoja_variable(df)

    # Generar nombre de archivo
    nombre_archivo = generar_nombre_archivo()
    output_path = output_dir / nombre_archivo

    # Generar Excel
    generar_excel(df_estacion, df_equipamiento, df_variable, output_path)

    return output_path


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Punto de entrada del script"""
    parser = argparse.ArgumentParser(
        description='Calcula métricas de disponibilidad y genera Excel con 3 hojas'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=DEFAULT_INPUT_FILE,
        help=f'Archivo CSV de entrada (default: {DEFAULT_INPUT_FILE})'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f'Directorio de salida para Excel (default: {DEFAULT_OUTPUT_DIR})'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validar archivo de entrada
    if not args.input.exists():
        logger.error(f"El archivo de entrada no existe: {args.input}")
        logger.info("Ejecuta primero: python 01_procesar_pdfs.py")
        sys.exit(1)

    # Procesar y generar Excel
    logger.info("=" * 60)
    logger.info("INICIANDO CÁLCULO DE DISPONIBILIDAD")
    logger.info("=" * 60)

    output_path = procesar_csv_a_excel(args.input, args.output)

    logger.info("=" * 60)
    logger.info("PROCESO COMPLETADO")
    logger.info(f"Archivo generado: {output_path}")
    logger.info("=" * 60)

    return output_path


if __name__ == "__main__":
    main()
