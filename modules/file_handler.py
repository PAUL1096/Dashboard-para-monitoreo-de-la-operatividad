"""
modules/file_handler.py
Módulo de carga y validación de archivos Excel
Maneja la lectura de reportes y extracción de metadata
"""

import pandas as pd
import os
import re
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Tuple, List

from config import config, messages


# ============================================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================================

class FileValidationError(Exception):
    """Excepción para errores de validación de archivos"""
    pass


class FileLoadError(Exception):
    """Excepción para errores de carga de archivos"""
    pass


# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class ExcelFileHandler:
    """Manejador de archivos Excel del reporte meteorológico"""
    
    @staticmethod
    def extraer_fechas_nombre_archivo(nombre_archivo: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """
        Extrae fechas del nombre de archivo siguiendo el patrón:
        reporte_disponibilidad_SGR_DDMM_DDMM.xlsx
        
        Args:
            nombre_archivo: Nombre del archivo (ej: reporte_disponibilidad_SGR_0810_1910.xlsx)
            
        Returns:
            Tupla (fecha_inicio, fecha_fin, año) en formato DD/MM/YYYY
            Retorna (None, None, None) si no encuentra el patrón
            
        Examples:
            >>> extraer_fechas_nombre_archivo("reporte_disponibilidad_SGR_0810_1910.xlsx")
            ("08/10/2025", "19/10/2025", 2025)
        """
        try:
            # Patrón: 4 dígitos_4 dígitos.xlsx
            patron = r'(\d{4})_(\d{4})\.xlsx?'
            match = re.search(patron, nombre_archivo)
            
            if not match:
                return None, None, None
            
            fecha_inicio_str = match.group(1)
            fecha_fin_str = match.group(2)
            
            # Extraer día y mes (DDMM)
            dia_inicio, mes_inicio = fecha_inicio_str[:2], fecha_inicio_str[2:]
            dia_fin, mes_fin = fecha_fin_str[:2], fecha_fin_str[2:]
            
            # Inferir año basado en mes actual
            año_actual = datetime.now().year
            mes_actual = datetime.now().month
            
            # Si el mes final es muy posterior al actual, probablemente sea del año pasado
            año = año_actual - 1 if int(mes_fin) > mes_actual + 1 else año_actual
            
            fecha_inicio = f"{dia_inicio}/{mes_inicio}/{año}"
            fecha_fin = f"{dia_fin}/{mes_fin}/{año}"
            
            return fecha_inicio, fecha_fin, año
            
        except Exception as e:
            # Si hay cualquier error, retornar None
            return None, None, None
    
    @staticmethod
    def normalizar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza nombres de columnas para ser case-insensitive

        Args:
            df: DataFrame con columnas a normalizar

        Returns:
            DataFrame con columnas normalizadas
        """
        # Mapeo de nombres comunes (minúsculas -> forma correcta)
        mapeo_columnas = {
            'comentario': 'Comentario',
            'estacion': 'Estacion',
            'sensor': 'Sensor',
            'frecuencia': 'Frecuencia',
            'dz': 'DZ'
        }

        # Renombrar columnas encontradas
        columnas_nuevas = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in mapeo_columnas:
                columnas_nuevas[col] = mapeo_columnas[col_lower]

        if columnas_nuevas:
            df = df.rename(columns=columnas_nuevas)

        return df

    @staticmethod
    def validar_columnas(df: pd.DataFrame, columnas_requeridas: List[str], nombre_hoja: str) -> None:
        """
        Valida que el DataFrame contenga todas las columnas requeridas (case-insensitive)

        Args:
            df: DataFrame a validar
            columnas_requeridas: Lista de nombres de columnas que deben existir
            nombre_hoja: Nombre de la hoja (para mensaje de error)

        Raises:
            FileValidationError: Si faltan columnas requeridas
        """
        # Comparación case-insensitive
        columnas_df_lower = {col.lower(): col for col in df.columns}
        columnas_req_lower = {col.lower(): col for col in columnas_requeridas}

        columnas_faltantes = set(columnas_req_lower.keys()) - set(columnas_df_lower.keys())

        if columnas_faltantes:
            # Mostrar nombres originales requeridos
            nombres_faltantes = [columnas_req_lower[col] for col in columnas_faltantes]
            error_msg = (
                f"Hoja '{nombre_hoja}' - Columnas faltantes: {', '.join(nombres_faltantes)}\n"
                f"Columnas encontradas: {', '.join(df.columns)}"
            )
            raise FileValidationError(error_msg)
    
    @staticmethod
    def listar_archivos_excel(ruta_carpeta: str) -> List[str]:
        """
        Lista archivos Excel en una carpeta
        
        Args:
            ruta_carpeta: Ruta de la carpeta a explorar
            
        Returns:
            Lista de nombres de archivo ordenados por fecha (más reciente primero)
        """
        if not os.path.exists(ruta_carpeta):
            return []
        
        try:
            archivos = [
                f for f in os.listdir(ruta_carpeta)
                if f.endswith(('.xlsx', '.xls')) and not f.startswith('~$')  # Excluir temporales
            ]
            
            # Ordenar por fecha de modificación (más reciente primero)
            archivos_con_fecha = []
            for archivo in archivos:
                ruta_completa = os.path.join(ruta_carpeta, archivo)
                fecha_mod = os.path.getmtime(ruta_completa)
                archivos_con_fecha.append((archivo, fecha_mod))
            
            # Ordenar por fecha descendente
            archivos_ordenados = [
                archivo for archivo, _ in sorted(archivos_con_fecha, key=lambda x: x[1], reverse=True)
            ]
            
            return archivos_ordenados
            
        except Exception as e:
            return []
    
    @classmethod
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def cargar_excel(_cls, archivo_path) -> Optional[Dict]:
        """
        Carga archivo Excel con validación completa
        
        Args:
            archivo_path: Ruta al archivo Excel o objeto UploadedFile de Streamlit
            
        Returns:
            Dict con estructura:
            {
                'estaciones': DataFrame,
                'sensores': DataFrame,
                'variables': DataFrame,
                'metadata': {
                    'nombre_archivo': str,
                    'fecha_inicio': str,
                    'fecha_fin': str,
                    'año': int,
                    'fecha_carga': str
                }
            }
            
        Raises:
            FileLoadError: Si hay error al cargar el archivo
            FileValidationError: Si falta alguna columna requerida
        """
        try:
            # Cargar las 3 hojas requeridas
            df_estaciones = pd.read_excel(archivo_path, sheet_name=config.SHEET_ESTACIONES)
            df_sensores = pd.read_excel(archivo_path, sheet_name=config.SHEET_SENSORES)
            df_variables = pd.read_excel(archivo_path, sheet_name=config.SHEET_VARIABLES)

            # Normalizar nombres de columnas (comentario -> Comentario, etc.)
            df_estaciones = _cls.normalizar_nombres_columnas(df_estaciones)
            df_sensores = _cls.normalizar_nombres_columnas(df_sensores)
            df_variables = _cls.normalizar_nombres_columnas(df_variables)

            # Validar columnas de cada hoja (ahora case-insensitive)
            _cls.validar_columnas(
                df_estaciones,
                config.REQUIRED_COLUMNS[config.SHEET_ESTACIONES],
                config.SHEET_ESTACIONES
            )
            _cls.validar_columnas(
                df_sensores,
                config.REQUIRED_COLUMNS[config.SHEET_SENSORES],
                config.SHEET_SENSORES
            )
            _cls.validar_columnas(
                df_variables,
                config.REQUIRED_COLUMNS[config.SHEET_VARIABLES],
                config.SHEET_VARIABLES
            )
            
            # Extraer nombre del archivo
            if isinstance(archivo_path, str):
                nombre_archivo = os.path.basename(archivo_path)
            else:
                # Es un UploadedFile de Streamlit
                nombre_archivo = archivo_path.name
            
            # Extraer fechas del nombre
            fecha_inicio, fecha_fin, año = _cls.extraer_fechas_nombre_archivo(nombre_archivo)
            
            # Construir resultado
            resultado = {
                'estaciones': df_estaciones,
                'sensores': df_sensores,
                'variables': df_variables,
                'metadata': {
                    'nombre_archivo': nombre_archivo,
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'año': año,
                    'fecha_carga': datetime.now().strftime(config.DATETIME_FORMAT),
                    'num_estaciones': len(df_estaciones),
                    'num_sensores': len(df_sensores),
                    'num_variables': len(df_variables)
                }
            }
            
            return resultado
            
        except FileValidationError:
            # Re-lanzar errores de validación
            raise
            
        except Exception as e:
            # Cualquier otro error se convierte en FileLoadError
            raise FileLoadError(f"Error al cargar el archivo: {str(e)}")
    
    @staticmethod
    def exportar_csv(df: pd.DataFrame, prefijo: str = "export") -> bytes:
        """
        Exporta DataFrame a CSV con encoding UTF-8
        
        Args:
            df: DataFrame a exportar
            prefijo: Prefijo para el nombre del archivo (no se usa aquí, solo para referencia)
            
        Returns:
            Bytes del CSV codificado en UTF-8 con BOM (para Excel)
        """
        # Usar utf-8-sig para que Excel abra correctamente con tildes
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        return csv_data
    
    @staticmethod
    def crear_nombre_descarga(prefijo: str, extension: str = "csv") -> str:
        """
        Crea nombre de archivo para descarga con timestamp
        
        Args:
            prefijo: Prefijo del archivo (ej: 'estaciones', 'sensores')
            extension: Extensión del archivo (default: 'csv')
            
        Returns:
            Nombre de archivo con formato: prefijo_YYYYMMDD_HHMM.extension
            
        Examples:
            >>> crear_nombre_descarga('estaciones')
            'estaciones_20251104_1530.csv'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return f"{prefijo}_{timestamp}.{extension}"


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def verificar_estructura_carpeta(ruta: str) -> Dict[str, any]:
    """
    Verifica el estado de una carpeta de reportes
    
    Args:
        ruta: Ruta de la carpeta a verificar
        
    Returns:
        Dict con información:
        {
            'existe': bool,
            'num_archivos': int,
            'archivos': List[str],
            'ultimo_modificado': Optional[str]
        }
    """
    resultado = {
        'existe': False,
        'num_archivos': 0,
        'archivos': [],
        'ultimo_modificado': None
    }
    
    if not os.path.exists(ruta):
        return resultado
    
    resultado['existe'] = True
    
    handler = ExcelFileHandler()
    archivos = handler.listar_archivos_excel(ruta)
    
    resultado['num_archivos'] = len(archivos)
    resultado['archivos'] = archivos
    
    if archivos:
        ruta_ultimo = os.path.join(ruta, archivos[0])
        fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_ultimo))
        resultado['ultimo_modificado'] = fecha_mod.strftime(config.DATETIME_FORMAT)
    
    return resultado