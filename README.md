# 🌦️ Dashboard Meteorológico SGR

Dashboard interactivo para monitoreo de disponibilidad de red meteorológica del Sistema de Gestión de Riesgos (SGR).

**Versión:** 2.1 (Refactorizado)  
**Autor:** Sistema de Monitoreo Meteorológico - SGR  
**Fecha:** Noviembre 2025

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Uso](#uso)
- [Estructura de Datos](#estructura-de-datos)
- [Funcionalidades](#funcionalidades)
- [Configuración](#configuración)
- [Solución de Problemas](#solución-de-problemas)

---

## ✨ Características

- 📊 **Análisis Integral**: Visualización de disponibilidad por estación, sensor y variable meteorológica
- 🚨 **Sistema de Alertas**: Clasificación automática de prioridades (ALTA/MEDIA/BAJA)
- 📈 **Gráficos Interactivos**: 13+ visualizaciones con Plotly
- 🔍 **Filtros Dinámicos**: Búsqueda y filtrado por múltiples criterios
- 📥 **Exportación**: Descarga de datos en formato CSV
- 🎨 **Interfaz Moderna**: Diseño responsive con Streamlit
- ⚡ **Caché Inteligente**: Carga rápida de datos repetidos
- 📝 **Seguimiento de Incidencias**: Monitoreo de comentarios técnicos

---

## 💻 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

---

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd dashboard_meteorologico
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar instalación

```bash
streamlit --version
```

---

## 📁 Estructura del Proyecto

```
dashboard_meteorologico/
│
├── main.py                      # Aplicación principal ⭐
├── config.py                    # Configuración centralizada
├── requirements.txt             # Dependencias
├── README.md                    # Este archivo
├── .gitignore                   # Archivos ignorados por Git
│
├── modules/                     # Módulos de la aplicación
│   ├── __init__.py             # Inicialización del paquete
│   ├── file_handler.py         # Carga y validación de archivos
│   ├── data_processor.py       # Procesamiento de datos
│   ├── chart_builder.py        # Construcción de gráficos
│   └── ui_components.py        # Componentes de interfaz
│
└── reportes/                    # Carpeta de reportes Excel 📂
    └── (tus archivos .xlsx aquí)
```

---

## 🎯 Uso

### Ejecutar la aplicación

```bash
streamlit run main.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Cargar datos

Tienes dos opciones:

#### Opción 1: Subir archivo
1. Haz clic en **"Browse files"** en la barra lateral
2. Selecciona tu archivo Excel

#### Opción 2: Carpeta local
1. Coloca tus archivos en la carpeta `reportes/`
2. El dashboard cargará automáticamente el más reciente

---

## 📄 Estructura de Datos

### Archivo Excel Requerido

El archivo debe contener **3 hojas** con la siguiente estructura:

#### Hoja 1: **POR ESTACION**
Columnas requeridas:
- `DZ`: Zona de defensa
- `Estacion`: Nombre de la estación
- `disponibilidad`: % de disponibilidad
- `var_disp`: Variación de disponibilidad
- `f_inci`: Fecha de incidencia (formato: DD/MM/YYYY)
- `estado_inci`: Estado de la incidencia
- `comentario`: Observaciones técnicas

#### Hoja 2: **POR EQUIPAMIENTO**
Columnas requeridas:
- `DZ`: Zona de defensa
- `Estacion`: Nombre de la estación
- `Sensor`: Tipo de sensor/equipamiento
- `disponibilidad`: % de disponibilidad
- `var_disp`: Variación de disponibilidad

#### Hoja 3: **POR VARIABLE**
Columnas requeridas:
- `DZ`: Zona de defensa
- `Estacion`: Nombre de la estación
- `Sensor`: Variable meteorológica
- `frecuencia`: Frecuencia de medición
- `disponibilidad`: % de disponibilidad
- `var_disp`: Variación de disponibilidad
- `Datos_flag_C`: Datos correctos
- `Datos_flag_M`: Datos con error
- `Datos_esperados`: Total de datos esperados

### Formato de Nombre de Archivo

Patrón recomendado: `reporte_disponibilidad_SGR_DDMM_DDMM.xlsx`

Ejemplo: `reporte_disponibilidad_SGR_0810_1910.xlsx`
- Fechas: del 08/10 al 19/10

---

## 🎨 Funcionalidades

### 1. 🚨 Alertas y Prioridades

Clasificación automática de estaciones:

- **🔴 PRIORIDAD ALTA**: Nuevas (≤30 días) o críticas sin resolver
- **🟡 PRIORIDAD MEDIA**: Recurrentes o en monitoreo post-solución
- **⚪ INFORMATIVO**: Paralizadas (>30 días)

### 2. 📊 Métricas Globales

- Disponibilidad promedio de la red
- Número de estaciones críticas (<80%)
- Porcentaje de red en estado crítico
- Anomalías detectadas (>100%)
- DZ afectadas

### 3. 🏢 Análisis por Estación

- Histograma de distribución
- Gráfico de torta por categoría
- Disponibilidad promedio por DZ
- Ranking de estaciones críticas (Top 15)
- Filtros por categoría, prioridad y disponibilidad
- Exportación a CSV

### 4. 📡 Análisis por Sensor

- Boxplot de distribución
- Conteo por categoría
- Disponibilidad por tipo de sensor
- Tabla completa con métricas
- Exportación a CSV

### 5. 📈 Análisis por Variable

- Disponibilidad por variable meteorológica
- Top 10 variables con mayor pérdida de datos
- Análisis de datos con errores (Flag M)
- Métricas de datos esperados vs recibidos
- Exportación a CSV

### 6. 📝 Comentarios Técnicos

- Distribución de estados de incidencia
- Top 10 DZ con más incidencias
- Filtrado por estado
- Tabla detallada de comentarios
- Exportación a CSV

---

## ⚙️ Configuración

### Personalizar Umbrales

Edita el archivo `config.py`:

```python
# Umbrales de disponibilidad
THRESHOLD_CRITICAL: float = 80.0   # Cambiar umbral crítico
THRESHOLD_ANOMALY: float = 100.0   # Cambiar umbral de anomalía

# Clasificación de prioridades (días)
PRIORITY_HIGH_MAX_DAYS: int = 30   # Días para prioridad ALTA
PRIORITY_MEDIUM_MONITOR_DAYS: int = 5  # Días de monitoreo post-solución
```

### Cambiar Ruta de Reportes

En `config.py`:

```python
DEFAULT_REPORTS_PATH: str = "./reportes"  # Cambiar ruta
```

### Personalizar Colores

En `config.py`, clase `StyleConfig`:

```python
COLOR_CRITICAL: str = "#d62728"  # Color para alertas críticas
COLOR_WARNING: str = "#ff7f0e"   # Color para advertencias
```

---

## 🔧 Solución de Problemas

### Error: "No se encontraron archivos Excel"

**Solución:**
- Verifica que la carpeta `reportes/` existe
- Asegúrate de que los archivos tienen extensión `.xlsx` o `.xls`
- Verifica que no son archivos temporales (no deben empezar con `~$`)

### Error: "Columnas faltantes"

**Solución:**
- Revisa que las 3 hojas tengan exactamente los nombres:
  - `POR ESTACION`
  - `POR EQUIPAMIENTO`
  - `POR VARIABLE`
- Verifica que todas las columnas requeridas existen

### El dashboard no carga

**Solución:**
```bash
# Limpiar caché
streamlit cache clear

# Reiniciar aplicación
streamlit run main.py
```

### Errores de importación

**Solución:**
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

---

## 🤝 Contribuciones

Para reportar problemas o sugerir mejoras:

1. Documenta el problema claramente
2. Incluye capturas de pantalla si es posible
3. Especifica la versión del archivo Excel utilizado

---

## 📝 Notas de Versión

### Versión 2.1 (Noviembre 2025)
- ✅ Refactorización completa en arquitectura modular
- ✅ Separación en 5 módulos independientes
- ✅ Mejora en manejo de errores
- ✅ Validación robusta de datos
- ✅ Caché optimizado
- ✅ Documentación completa

### Versión 2.0 (Octubre 2025)
- ✅ Dashboard inicial funcional
- ✅ Sistema de prioridades
- ✅ 4 tabs de análisis
- ✅ Exportación CSV

---

## 📄 Licencia

Este proyecto es de uso interno del Sistema de Gestión de Riesgos (SGR).

---

## 👨‍💻 Soporte

Para soporte técnico, contacta al equipo de desarrollo SGR.

**Dashboard Meteorológico SGR** - Monitoreando la disponibilidad de nuestra red 🌦️