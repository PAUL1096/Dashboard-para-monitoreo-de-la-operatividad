"""
config.py
Configuración centralizada del Dashboard Meteorológico SGR
Versión: 2.2
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
    VERSION: str = "2.2"
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
    PRIORITY_HIGH_MAX_DAYS: int = 30  # <= 30 días = ALTA (Nueva)
    PRIORITY_MEDIUM_MONITOR_DAYS: int = 5  # Monitoreo post-solución
    PRIORITY_PARALIZADA_MIN_DAYS: int = 90  # >= 90 días (3 meses) + disp=0% = BAJA (Paralizada)
    PRIORITY_CLAUSURA_MIN_DAYS: int = 730  # >= 730 días (2 años) = Candidata a clausura
    
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
                'DZ', 'Estacion', 'Sensor', 'Variable', 'Frecuencia', 'disponibilidad',
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
        background: linear-gradient(135deg, #ffe6e6 0%, #fff0f0 100%);
        padding: 0.8rem 1rem;
        border-radius: 0.6rem;
        border-left: 4px solid #d62728;
        box-shadow: 0 2px 4px rgba(214, 39, 40, 0.1);
        transition: transform 0.2s;
    """

    CSS_PRIORITY_MEDIA: str = """
        background: linear-gradient(135deg, #fff4e6 0%, #fff9f0 100%);
        padding: 0.8rem 1rem;
        border-radius: 0.6rem;
        border-left: 4px solid #ff7f0e;
        box-shadow: 0 2px 4px rgba(255, 127, 14, 0.1);
        transition: transform 0.2s;
    """

    CSS_PRIORITY_BAJA: str = """
        background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
        padding: 0.8rem 1rem;
        border-radius: 0.6rem;
        border-left: 4px solid #9e9e9e;
        box-shadow: 0 2px 4px rgba(127, 127, 127, 0.1);
        transition: transform 0.2s;
    """
    
    CSS_FOOTER: str = """
        text-align: center;
        color: #666;
        font-size: 0.9rem;
    """
    
    def get_full_css(self) -> str:
        """Retorna el CSS completo para inyectar en Streamlit"""
        return """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

        /* ===== FONDO Y ESTRUCTURA GLOBAL ===== */
        .stApp {
            background-color: #07090F;
            background-image:
                linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            font-family: 'IBM Plex Sans', sans-serif;
        }

        /* ===== HEADER PRINCIPAL ===== */
        .main-header {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2.8rem;
            letter-spacing: 0.08em;
            color: #E8F4FD;
            text-align: left;
            padding: 1.2rem 0 0.4rem 0;
            border-bottom: 2px solid #00D4FF;
            text-shadow: 0 0 30px rgba(0, 212, 255, 0.4);
            margin-bottom: 0.2rem;
            line-height: 1.1;
        }

        /* ===== SIDEBAR ===== */
        [data-testid="stSidebar"] {
            background-color: #0D1117 !important;
            border-right: 1px solid rgba(0, 212, 255, 0.2) !important;
        }
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #8BA5B8 !important;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.82rem;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #00D4FF !important;
            font-family: 'Bebas Neue', sans-serif !important;
            letter-spacing: 0.06em;
            font-size: 1.1rem !important;
        }

        /* ===== SIDEBAR - INPUTS ===== */
        [data-testid="stSidebar"] [data-baseweb="input"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] div,
        [data-testid="stSidebar"] textarea {
            background-color: #131A22 !important;
            border: 1px solid rgba(0, 212, 255, 0.25) !important;
            color: #C9D8E4 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.82rem !important;
            border-radius: 3px !important;
        }
        [data-testid="stSidebar"] [data-baseweb="input"] input:focus,
        [data-testid="stSidebar"] [data-baseweb="select"]:focus-within div {
            border-color: #00D4FF !important;
            box-shadow: 0 0 0 1px rgba(0, 212, 255, 0.3) !important;
        }

        /* ===== MAIN CONTENT AREA ===== */
        .main .block-container {
            padding: 1.5rem 2rem 2rem 2rem;
        }

        /* ===== HEADERS EN CONTENIDO ===== */
        h1, h2, h3, h4 {
            font-family: 'IBM Plex Sans', sans-serif !important;
            color: #C9D8E4 !important;
        }
        h2 {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.04em;
            color: #A0BDD0 !important;
            border-bottom: 1px solid rgba(0, 212, 255, 0.15);
            padding-bottom: 0.4rem;
            margin-top: 1.5rem !important;
        }
        h3 {
            font-size: 1rem !important;
            font-weight: 500 !important;
            color: #7A9BB0 !important;
        }

        /* ===== TABS ===== */
        [data-baseweb="tab-list"] {
            background-color: #0D1117 !important;
            border-bottom: 1px solid rgba(0, 212, 255, 0.2) !important;
            gap: 0 !important;
        }
        [data-baseweb="tab"] {
            background-color: transparent !important;
            color: #5A7A90 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase !important;
            border-bottom: 2px solid transparent !important;
            padding: 0.7rem 1.2rem !important;
            transition: all 0.2s ease !important;
        }
        [data-baseweb="tab"]:hover {
            color: #00D4FF !important;
            background-color: rgba(0, 212, 255, 0.05) !important;
        }
        [aria-selected="true"][data-baseweb="tab"] {
            color: #00D4FF !important;
            border-bottom: 2px solid #00D4FF !important;
            background-color: rgba(0, 212, 255, 0.07) !important;
        }

        /* ===== MÉTRICAS ===== */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #0D1520 0%, #111C28 100%);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-top: 2px solid #00D4FF;
            border-radius: 4px;
            padding: 1rem 1.2rem !important;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        [data-testid="stMetric"]:hover {
            border-color: rgba(0, 212, 255, 0.4);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.08);
        }
        [data-testid="stMetricLabel"] p {
            color: #5A7A90 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.72rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.1em !important;
            text-transform: uppercase !important;
        }
        [data-testid="stMetricValue"] {
            color: #E8F4FD !important;
            font-family: 'Bebas Neue', sans-serif !important;
            font-size: 2.2rem !important;
            letter-spacing: 0.05em !important;
        }
        [data-testid="stMetricDelta"] {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.78rem !important;
        }

        /* ===== TARJETAS DE PRIORIDAD ===== */
        .prioridad-alta {
            background: linear-gradient(135deg, #180C0C 0%, #1E1010 100%);
            padding: 1.2rem 1.4rem;
            border-radius: 4px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-left: 3px solid #EF4444;
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.08), inset 0 0 40px rgba(239, 68, 68, 0.03);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }
        .prioridad-alta::before {
            content: '';
            position: absolute;
            top: 0; right: 0;
            width: 60px; height: 60px;
            background: radial-gradient(circle at top right, rgba(239, 68, 68, 0.15), transparent 70%);
        }

        .prioridad-media {
            background: linear-gradient(135deg, #171108 0%, #1D1609 100%);
            padding: 1.2rem 1.4rem;
            border-radius: 4px;
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-left: 3px solid #F59E0B;
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.08), inset 0 0 40px rgba(245, 158, 11, 0.03);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }
        .prioridad-media::before {
            content: '';
            position: absolute;
            top: 0; right: 0;
            width: 60px; height: 60px;
            background: radial-gradient(circle at top right, rgba(245, 158, 11, 0.15), transparent 70%);
        }

        .prioridad-baja {
            background: linear-gradient(135deg, #0E1218 0%, #121820 100%);
            padding: 1.2rem 1.4rem;
            border-radius: 4px;
            border: 1px solid rgba(100, 120, 140, 0.3);
            border-left: 3px solid #4A6070;
            box-shadow: 0 0 20px rgba(74, 96, 112, 0.06), inset 0 0 40px rgba(74, 96, 112, 0.02);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }

        .prioridad-alta:hover, .prioridad-media:hover, .prioridad-baja:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        }
        .prioridad-alta:hover { border-color: rgba(239, 68, 68, 0.6); }
        .prioridad-media:hover { border-color: rgba(245, 158, 11, 0.6); }
        .prioridad-baja:hover { border-color: rgba(74, 96, 112, 0.6); }

        .prioridad-title {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin: 0 0 0.6rem 0;
            color: #6A8A9E;
        }
        .prioridad-alta .prioridad-title { color: #F87171; }
        .prioridad-media .prioridad-title { color: #FBB95A; }
        .prioridad-baja .prioridad-title { color: #5A7A90; }

        .prioridad-number {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.8rem;
            line-height: 1;
            margin: 0.2rem 0;
            letter-spacing: 0.02em;
        }
        .prioridad-alta .prioridad-number { color: #EF4444; text-shadow: 0 0 20px rgba(239,68,68,0.5); }
        .prioridad-media .prioridad-number { color: #F59E0B; text-shadow: 0 0 20px rgba(245,158,11,0.5); }
        .prioridad-baja .prioridad-number { color: #4A6070; }

        .prioridad-desc {
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.82rem;
            font-weight: 400;
            margin: 0.5rem 0 0 0;
            line-height: 1.4;
        }
        .prioridad-alta .prioridad-desc { color: #C99090; }
        .prioridad-media .prioridad-desc { color: #C9A878; }
        .prioridad-baja .prioridad-desc { color: #5A7A90; }

        .prioridad-detail {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.7rem;
            margin-top: 0.6rem;
            padding-top: 0.6rem;
            border-top: 1px solid rgba(255,255,255,0.05);
            color: #3A5060;
            line-height: 1.4;
        }

        /* ===== DATAFRAMES / TABLAS ===== */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(0, 212, 255, 0.15) !important;
            border-radius: 4px !important;
        }
        [data-testid="stDataFrame"] iframe {
            border-radius: 4px;
        }

        /* ===== ALERTS / MENSAJES ===== */
        [data-testid="stAlert"] {
            border-radius: 3px !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.82rem !important;
        }
        .stSuccess {
            background-color: rgba(0, 180, 90, 0.1) !important;
            border: 1px solid rgba(0, 180, 90, 0.3) !important;
            color: #50D890 !important;
        }
        .stInfo {
            background-color: rgba(0, 150, 200, 0.1) !important;
            border: 1px solid rgba(0, 150, 200, 0.3) !important;
            color: #60C0E0 !important;
        }
        .stWarning {
            background-color: rgba(245, 158, 11, 0.1) !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
            color: #F59E0B !important;
        }
        .stError {
            background-color: rgba(239, 68, 68, 0.1) !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
            color: #EF4444 !important;
        }

        /* ===== BOTONES ===== */
        .stButton > button,
        .stDownloadButton > button {
            background: transparent !important;
            border: 1px solid rgba(0, 212, 255, 0.4) !important;
            color: #00D4FF !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            border-radius: 3px !important;
            padding: 0.5rem 1.2rem !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover {
            background: rgba(0, 212, 255, 0.1) !important;
            border-color: #00D4FF !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.2) !important;
        }

        /* ===== SELECTBOX / SLIDERS ===== */
        [data-baseweb="select"] > div,
        [data-baseweb="input"] input {
            background-color: #0D1520 !important;
            border: 1px solid rgba(0, 212, 255, 0.2) !important;
            color: #C9D8E4 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.82rem !important;
            border-radius: 3px !important;
        }
        [data-baseweb="select"] > div:hover,
        [data-baseweb="input"] input:hover {
            border-color: rgba(0, 212, 255, 0.4) !important;
        }

        /* ===== SLIDER ===== */
        [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
            background-color: #00D4FF !important;
            border-color: #00D4FF !important;
        }

        /* ===== EXPANDER ===== */
        [data-testid="stExpander"] {
            background-color: #0D1117 !important;
            border: 1px solid rgba(0, 212, 255, 0.15) !important;
            border-radius: 4px !important;
        }
        [data-testid="stExpander"] summary {
            color: #5A7A90 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.82rem !important;
            font-weight: 500 !important;
        }
        [data-testid="stExpander"] summary:hover {
            color: #00D4FF !important;
        }

        /* ===== DIVISORES ===== */
        hr {
            border: none !important;
            border-top: 1px solid rgba(0, 212, 255, 0.1) !important;
            margin: 1.5rem 0 !important;
        }

        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploader"] {
            background-color: #0D1520 !important;
            border: 1px dashed rgba(0, 212, 255, 0.3) !important;
            border-radius: 4px !important;
        }
        [data-testid="stFileUploader"]:hover {
            border-color: #00D4FF !important;
            background-color: rgba(0, 212, 255, 0.03) !important;
        }

        /* ===== TEXTO GENERAL ===== */
        p, li, span, label {
            color: #8BA5B8;
            font-family: 'IBM Plex Sans', sans-serif;
        }
        strong, b {
            color: #C9D8E4;
        }
        code {
            background-color: rgba(0, 212, 255, 0.1) !important;
            color: #00D4FF !important;
            border: 1px solid rgba(0, 212, 255, 0.2) !important;
            font-family: 'IBM Plex Mono', monospace !important;
            border-radius: 2px !important;
            padding: 0.15em 0.4em !important;
        }

        /* ===== TOP BAR DE STREAMLIT ===== */
        [data-testid="stHeader"] {
            background-color: #07090F !important;
            border-bottom: 1px solid rgba(0, 212, 255, 0.1) !important;
        }
        [data-testid="stToolbar"] {
            background-color: #07090F !important;
        }

        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #07090F; }
        ::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.2); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(0, 212, 255, 0.4); }

        /* ===== FOOTER ===== */
        .footer {
            text-align: center;
            color: #2A4050;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            padding: 1rem 0;
        }

        /* ===== ANIMACIÓN SUTIL NÚMEROS ===== */
        @keyframes glow-pulse {
            0%, 100% { text-shadow: 0 0 20px rgba(239,68,68,0.5); }
            50% { text-shadow: 0 0 35px rgba(239,68,68,0.8), 0 0 60px rgba(239,68,68,0.3); }
        }
        .prioridad-alta .prioridad-number {
            animation: glow-pulse 3s ease-in-out infinite;
        }

        /* ===== BADGE DZ FILTRO ===== */
        [data-testid="stInfo"] {
            background-color: rgba(0, 150, 212, 0.08) !important;
            border: 1px solid rgba(0, 150, 212, 0.25) !important;
            border-left: 3px solid #00A8D4 !important;
            border-radius: 3px !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.82rem !important;
        }

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