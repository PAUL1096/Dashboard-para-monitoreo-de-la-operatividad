"""
01_procesar_pdfs.py
Procesamiento de PDFs de reportes meteorológicos por Dirección Zonal

Autor: Sistema de Monitoreo Meteorológico - SGR
Versión: 1.0
Fecha: Enero 2026

Este script extrae datos de los PDFs descargados de la herramienta interna
y genera un CSV consolidado con todas las estaciones y sus métricas.

Entrada: PDFs en input_pdfs/
Salida: CSV en output/datos_raw.csv
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

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
DEFAULT_INPUT_DIR = Path(__file__).parent / "input_pdfs"
DEFAULT_OUTPUT_FILE = Path(__file__).parent / "output" / "datos_raw.csv"

# Columnas esperadas en el CSV de salida
COLUMNAS_SALIDA = [
    'DZ',               # Dirección Zonal
    'Estacion',         # Nombre de la estación
    'Sensor',           # Tipo de sensor/variable
    'Frecuencia',       # Frecuencia de medición
    'Datos_flag_C',     # Datos correctos
    'Datos_flag_M',     # Datos con error
    'Datos_esperados',  # Total esperado
    'f_inci',           # Fecha de incidencia
    'estado_inci',      # Estado de incidencia
    'comentario'        # Observaciones técnicas
]


# ============================================================================
# FUNCIONES DE EXTRACCIÓN DE PDF
# ============================================================================

def extraer_datos_pdf(ruta_pdf: Path) -> pd.DataFrame:
    """
    Extrae datos de un PDF de reporte meteorológico.

    Args:
        ruta_pdf: Ruta al archivo PDF

    Returns:
        DataFrame con los datos extraídos del PDF

    TODO: Implementar lógica real de extracción según estructura del PDF
    """
    logger.info(f"Procesando: {ruta_pdf.name}")

    # =========================================================================
    # TODO: IMPLEMENTAR EXTRACCIÓN REAL
    # =========================================================================
    #
    # Opciones de librerías para extracción:
    #
    # 1. pdfplumber (recomendado para tablas):
    #    import pdfplumber
    #    with pdfplumber.open(ruta_pdf) as pdf:
    #        for page in pdf.pages:
    #            tables = page.extract_tables()
    #            text = page.extract_text()
    #
    # 2. tabula-py (para tablas estructuradas):
    #    import tabula
    #    df = tabula.read_pdf(ruta_pdf, pages='all')
    #
    # 3. PyPDF2 (para texto simple):
    #    from PyPDF2 import PdfReader
    #    reader = PdfReader(ruta_pdf)
    #    for page in reader.pages:
    #        text = page.extract_text()
    #
    # =========================================================================

    # Placeholder: Retorna DataFrame vacío con estructura correcta
    logger.warning(f"  ⚠️ Extracción no implementada - retornando datos vacíos")

    return pd.DataFrame(columns=COLUMNAS_SALIDA)


def extraer_dz_de_nombre(nombre_archivo: str) -> str:
    """
    Extrae la Dirección Zonal del nombre del archivo PDF.

    Args:
        nombre_archivo: Nombre del archivo (ej: reporte_DZ01_0801_1501.pdf)

    Returns:
        Código de DZ (ej: "DZ01")

    TODO: Ajustar patrón según nomenclatura real de archivos
    """
    # Placeholder: Extraer DZ del nombre
    # Ajustar regex según patrón real
    import re
    match = re.search(r'(DZ\d+)', nombre_archivo, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "DZ_DESCONOCIDA"


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def procesar_todos_los_pdfs(
    input_dir: Path,
    output_file: Path
) -> pd.DataFrame:
    """
    Procesa todos los PDFs en el directorio de entrada.

    Args:
        input_dir: Directorio con PDFs de entrada
        output_file: Ruta del archivo CSV de salida

    Returns:
        DataFrame consolidado con todos los datos
    """
    logger.info(f"Buscando PDFs en: {input_dir}")

    # Buscar archivos PDF
    archivos_pdf = list(input_dir.glob("*.pdf"))

    if not archivos_pdf:
        logger.warning("No se encontraron archivos PDF en el directorio")
        return pd.DataFrame(columns=COLUMNAS_SALIDA)

    logger.info(f"Encontrados {len(archivos_pdf)} archivos PDF")

    # Procesar cada PDF
    dataframes = []
    for pdf_path in archivos_pdf:
        try:
            df = extraer_datos_pdf(pdf_path)

            # Añadir DZ si no está en los datos
            if 'DZ' not in df.columns or df['DZ'].isna().all():
                df['DZ'] = extraer_dz_de_nombre(pdf_path.name)

            dataframes.append(df)

        except Exception as e:
            logger.error(f"Error procesando {pdf_path.name}: {e}")
            continue

    # Consolidar todos los DataFrames
    if dataframes:
        df_consolidado = pd.concat(dataframes, ignore_index=True)
    else:
        df_consolidado = pd.DataFrame(columns=COLUMNAS_SALIDA)

    # Guardar CSV
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df_consolidado.to_csv(output_file, index=False, encoding='utf-8')
    logger.info(f"CSV guardado en: {output_file}")
    logger.info(f"Total de registros: {len(df_consolidado)}")

    return df_consolidado


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

def main():
    """Punto de entrada del script"""
    parser = argparse.ArgumentParser(
        description='Procesa PDFs de reportes meteorológicos y genera CSV consolidado'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f'Directorio con PDFs de entrada (default: {DEFAULT_INPUT_DIR})'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=f'Archivo CSV de salida (default: {DEFAULT_OUTPUT_FILE})'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Mostrar información detallada'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validar directorio de entrada
    if not args.input.exists():
        logger.error(f"El directorio de entrada no existe: {args.input}")
        sys.exit(1)

    # Procesar PDFs
    logger.info("=" * 60)
    logger.info("INICIANDO PROCESAMIENTO DE PDFs")
    logger.info("=" * 60)

    df = procesar_todos_los_pdfs(args.input, args.output)

    logger.info("=" * 60)
    logger.info("PROCESAMIENTO COMPLETADO")
    logger.info("=" * 60)

    return df


if __name__ == "__main__":
    main()
