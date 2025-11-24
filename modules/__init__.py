"""
modules/__init__.py
Paquete de módulos del Dashboard Meteorológico SGR

Este paquete contiene:
- file_handler: Carga y validación de archivos Excel
- data_processor: Procesamiento y transformación de datos
- chart_builder: Construcción de gráficos Plotly
- ui_components: Componentes de interfaz de usuario
"""

__version__ = "2.1"
__author__ = "Sistema de Monitoreo Meteorológico - SGR"

# Facilitar imports directos
from .file_handler import ExcelFileHandler
from .data_processor import DataProcessor
from .chart_builder import ChartBuilder
from .ui_components import UIComponents

__all__ = [
    'ExcelFileHandler',
    'DataProcessor',
    'ChartBuilder',
    'UIComponents'
]