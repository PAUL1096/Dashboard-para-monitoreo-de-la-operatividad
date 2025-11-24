"""
config.py
Configuración centralizada del Dashboard Meteorológico SGR
Versión: 2.1
"""

from dataclasses import dataclass
from typing import Dict, List


# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

@dataclass
class AppConfig:
    """Configuración principal de la aplicación"""
    
    # Información de la aplicación
    APP_TITLE: str = "Dashboard Meteorológico SGR"
    APP_ICON: str = "🌦️"
    VERSION: str = "2.1"
    AUTHOR: str = "Sistema de Monitoreo Meteorológico - SGR"
    
    # Configuración de Streamlit
    PAGE_TITLE: str = "Dashboard Meteorológico SGR"
    LAYOUT: str = "wide"
    SIDEBAR_STATE: str = "expanded"
    
    # Rutas
    DEFAULT_REPORTS_PATH: str = "./reportes"
    
    # Nombres de hojas Excel (CRÍTICO - deben coincidir exactamente)
    SHEET_ESTACIONES: str = "POR ESTACION"
    SHEET_SENSORES: str = "POR EQUIPAMIENTO"
    SHEET_VARIABLES: str = "POR VARIABLE"
    
    # Umbrales de disponibilidad
    THRESHOLD_CRITICAL: float = 80.0  # Bajo este valor es crítico
    THRESHOLD_ANOMALY: float = 100.0  # Sobre este valor es anomalía
    
    # Clasificación de prioridades (días)
    PRIORITY_HIGH_MAX_DAYS: int = 30  # <= 30 días = ALTA
    PRIORITY_MEDIUM_MONITOR_DAYS: int = 5  # Monitoreo post-solución
    
    # Formatos de fecha
    DATE_FORMAT: str = "%d/%m/%Y"  # Formato en Excel
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M"  # Para display
    FILE_DATE_FORMAT: str = "%Y%m%d"  # Para nombres de archivo
    
    # Columnas requeridas por hoja (validación)
    REQUIRED_COLUMNS: Dict[str, List[str]] = None
    
    def __post_init__(self):
        """Inicializa columnas requeridas después de crear la instancia"""
        self.REQUIRED_COLUMNS = {
            self.SHEET_ESTACIONES: [
                'DZ', 'Estacion', 'disponibilidad', 'var_disp',
                'f_inci', 'estado_inci', 'Comentario'
            ],
            self.SHEET_SENSORES: [
                'DZ', 'Estacion', 'Sensor', 'disponibilidad', 'var_disp'
            ],
            self.SHEET_VARIABLES: [
                'DZ', 'Estacion', 'Sensor', 'Frecuencia', 'disponibilidad',
                'var_disp', 'Datos_flag_C', 'Datos_flag_M', 'Datos_esperados'
            ]
        }


# ============================================================================
# CONFIGURACIÓN DE ESTILOS CSS
# ============================================================================

@dataclass
class StyleConfig:
    """Configuración de estilos visuales"""
    
    # Colores principales
    COLOR_PRIMARY: str = "#1f77b4"
    COLOR_CRITICAL: str = "#d62728"
    COLOR_WARNING: str = "#ff7f0e"
    COLOR_SUCCESS: str = "#2ca02c"
    COLOR_INFO: str = "#7f7f7f"
    
    # Estilos CSS como strings
    CSS_MAIN_HEADER: str = """
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    """
    
    CSS_PRIORITY_ALTA: str = """
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #d62728;
        margin: 0.5rem 0;
    """
    
    CSS_PRIORITY_MEDIA: str = """
        background-color: #fff4e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff7f0e;
        margin: 0.5rem 0;
    """
    
    CSS_PRIORITY_BAJA: str = """
        background-color: #f0f0f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #7f7f7f;
        margin: 0.5rem 0;
    """
    
    CSS_FOOTER: str = """
        text-align: center;
        color: #666;
        font-size: 0.9rem;
    """
    
    def get_full_css(self) -> str:
        """Retorna el CSS completo para inyectar en Streamlit"""
        return f"""
        <style>
        .main-header {{
            {self.CSS_MAIN_HEADER}
        }}
        .prioridad-alta {{
            {self.CSS_PRIORITY_ALTA}
        }}
        .prioridad-media {{
            {self.CSS_PRIORITY_MEDIA}
        }}
        .prioridad-baja {{
            {self.CSS_PRIORITY_BAJA}
        }}
        .footer {{
            {self.CSS_FOOTER}
        }}
        </style>
        """


# ============================================================================
# CONFIGURACIÓN DE GRÁFICOS
# ============================================================================

@dataclass
class ChartConfig:
    """Configuración de gráficos Plotly"""
    
    # Paletas de colores
    COLOR_SCALE_DIVERGING: str = "RdYlGn"  # Rojo-Amarillo-Verde
    COLOR_SCALE_SEQUENTIAL: str = "Reds"  # Escala de rojos
    COLOR_PRIMARY: str = "#1f77b4"  # Azul principal
    
    # Configuración de gráficos
    HISTOGRAM_BINS: int = 20
    TOP_N_CRITICAL: int = 15  # Top estaciones críticas
    TOP_N_LOSS: int = 10  # Top variables con pérdida
    
    # Alturas por defecto
    DEFAULT_HEIGHT: int = 400
    RANKING_HEIGHT: int = 500
    TABLE_HEIGHT: int = 400
    
    # Configuración de líneas de referencia
    CRITICAL_LINE_COLOR: str = "red"
    CRITICAL_LINE_DASH: str = "dash"


# ============================================================================
# CONFIGURACIÓN DE MENSAJES
# ============================================================================

@dataclass
class MessagesConfig:
    """Mensajes del sistema"""
    
    # Mensajes de carga
    MSG_LOADING: str = "Cargando datos..."
    MSG_PROCESSING: str = "Procesando información..."
    MSG_SUCCESS: str = "✅ Datos cargados correctamente"
    MSG_ERROR_LOAD: str = "❌ Error al cargar el archivo"
    MSG_ERROR_VALIDATION: str = "❌ Error de validación de datos"
    
    # Mensajes informativos
    MSG_NO_DATA: str = "👆 **No se encontró ningún reporte.** Por favor:"
    MSG_NO_FILES: str = "No se encontraron archivos Excel en la carpeta."
    MSG_FOLDER_NOT_EXIST: str = "📁 La carpeta no existe. Créala o cambia la ruta."
    
    # Instrucciones
    INSTRUCTIONS_UPLOAD: str = """
    ### 📤 Opción 1: Subir archivo
    1. Usa el botón **"Browse files"** en la barra lateral
    2. Selecciona tu archivo Excel de reporte semanal
    """
    
    INSTRUCTIONS_FOLDER: str = """
    ### 📁 Opción 2: Usar carpeta local
    1. Coloca tus archivos Excel en la carpeta de reportes
    2. El dashboard cargará automáticamente el más reciente
    """
    
    # Tooltips
    TOOLTIP_UPLOAD: str = "Sube el reporte semanal en formato Excel"
    TOOLTIP_FOLDER: str = "Ruta donde se almacenan los reportes semanales"
    TOOLTIP_SELECT: str = "Archivos ordenados del más reciente al más antiguo"
    TOOLTIP_CATEGORY: str = "Filtra estaciones por categoría de variación"
    TOOLTIP_PRIORITY: str = "Filtra por nivel de prioridad de atención"


# ============================================================================
# INSTANCIAS GLOBALES (Singleton pattern)
# ============================================================================

# Crear instancias únicas que se importarán en otros módulos
config = AppConfig()
styles = StyleConfig()
charts = ChartConfig()
messages = MessagesConfig()


# ============================================================================
# FUNCIONES AUXILIARES DE CONFIGURACIÓN
# ============================================================================

def get_streamlit_config() -> dict:
    """
    Retorna configuración para st.set_page_config()
    
    Returns:
        dict: Diccionario con configuración de Streamlit
    """
    return {
        "page_title": config.PAGE_TITLE,
        "page_icon": config.APP_ICON,
        "layout": config.LAYOUT,
        "initial_sidebar_state": config.SIDEBAR_STATE
    }


def validate_config() -> bool:
    """
    Valida que la configuración sea correcta
    
    Returns:
        bool: True si la configuración es válida
    """
    # Validar umbrales
    assert 0 < config.THRESHOLD_CRITICAL < 100, "Umbral crítico debe estar entre 0 y 100"
    assert config.THRESHOLD_CRITICAL < config.THRESHOLD_ANOMALY, "Umbral anomalía debe ser mayor al crítico"
    
    # Validar días de prioridad
    assert config.PRIORITY_HIGH_MAX_DAYS > 0, "Días de prioridad alta debe ser positivo"
    assert config.PRIORITY_MEDIUM_MONITOR_DAYS > 0, "Días de monitoreo debe ser positivo"
    
    # Validar hojas requeridas
    assert len(config.REQUIRED_COLUMNS) == 3, "Deben haber 3 hojas configuradas"
    
    return True


# Validar configuración al importar
validate_config()