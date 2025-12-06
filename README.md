# 🌦️ Dashboard Meteorológico SGR

Dashboard interactivo para monitoreo de disponibilidad de red meteorológica del Sistema de Gestión de Riesgos (SGR).

**Versión:** 2.2 (Mejoras Críticas)
**Autor:** Sistema de Monitoreo Meteorológico - SGR
**Fecha:** Diciembre 2025

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
- 🚨 **Sistema de Alertas Mejorado**: Clasificación automática de prioridades (ALTA/MEDIA/BAJA) con razones explicativas
- 🗺️ **Filtro por Dirección Zonal**: Visualización focalizada por DZ o vista global de toda la red
- ⚪ **Monitoreo de Paralizadas**: Sección dedicada para estaciones paralizadas con alertas de clausura (>2 años)
- 📈 **Gráficos Interactivos**: 13+ visualizaciones con Plotly, incluyendo boxplot por tipo de sensor
- 🔍 **Filtros Dinámicos**: Búsqueda y filtrado por múltiples criterios
- 📥 **Exportación**: Descarga de datos en formato CSV
- 🎨 **Interfaz Moderna**: Diseño responsive con Streamlit y CSS gradientes
- ⚡ **Caché Inteligente**: Carga rápida de datos repetidos
- 📝 **Seguimiento de Incidencias**: Monitoreo de comentarios técnicos con tarjetas expandibles
- 🔤 **Validación Flexible**: Procesamiento case-insensitive de columnas Excel

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

Clasificación automática de estaciones con razones explicativas:

- **🔴 PRIORIDAD ALTA**: Incidencias nuevas (≤30 días) con disponibilidad crítica (<80%)
- **🟡 PRIORIDAD MEDIA**: Recurrentes (>30 días) o en monitoreo post-solución (≤5 días)
- **⚪ PRIORIDAD BAJA** (Paralizadas): Estaciones con ≥90 días de incidencia y disponibilidad ≤0.5%
  - ⚠️ Alerta especial para candidatas a clausura (>730 días / 2 años)

**Columna "Razón de Prioridad"**: Cada estación incluye explicación automática de su clasificación, mostrando días transcurridos, disponibilidad y estado de incidencia.

### 2. 📊 Métricas Globales

- Disponibilidad promedio de la red (filtrable por DZ)
- Número de estaciones críticas (<80%)
- Contadores de prioridad: ALTA, MEDIA y BAJA (paralizadas)
- Porcentaje de red en estado crítico
- Anomalías detectadas (>100%)
- DZ afectadas

**🗺️ Filtro por Dirección Zonal**: Selector en sidebar para ver métricas y gráficos de una DZ específica o de toda la red ("Todas")

### 3. 🏢 Análisis por Estación

**Sección de Alertas:**
- Tarjetas compactas con estaciones de prioridad ALTA (expandibles)
- Sección dedicada para estaciones PARALIZADAS (BAJA) con:
  - Tabla resumen ordenada por días de paralización
  - Alerta especial para candidatas a clausura (>2 años)
  - Tarjetas expandibles con comentarios técnicos
  - Diferenciación visual: borde rojo para >2 años, gris para <2 años

**Análisis y Visualizaciones:**
- Histograma de distribución de disponibilidad
- Gráfico de torta por categoría
- Disponibilidad promedio por DZ
- Ranking de estaciones críticas (Top 15)
- Filtros por categoría, prioridad y disponibilidad
- Exportación a CSV con "Razón de Prioridad"

### 4. 📡 Análisis por Sensor

- **Boxplot mejorado**: Distribución de disponibilidad por tipo de sensor (permite comparar comportamiento entre diferentes tipos)
- Conteo por categoría de disponibilidad
- Disponibilidad promedio por tipo de sensor
- Tabla completa con métricas normalizadas
- Detección de anomalías (>100%)
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
PRIORITY_HIGH_MAX_DAYS: int = 30              # Días para prioridad ALTA
PRIORITY_MEDIUM_MONITOR_DAYS: int = 5         # Días de monitoreo post-solución
PRIORITY_PARALIZADA_MIN_DAYS: int = 90        # Días para clasificar como paralizada (3 meses)
PRIORITY_CLAUSURA_MIN_DAYS: int = 730         # Días para alerta de clausura (2 años)
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

**Nota:** El sistema ahora acepta columnas en mayúsculas o minúsculas (case-insensitive). Por ejemplo:
- `Comentario`, `comentario`, `COMENTARIO` → Todos funcionan
- `Estacion`, `estacion` → Ambos válidos
- `DZ`, `dz` → Ambos aceptados

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

### Versión 2.2 (Diciembre 2025) - MEJORAS CRÍTICAS

**🔧 Correcciones Críticas:**
- ✅ **FIX**: Detección correcta de estaciones paralizadas (BAJA)
  - Problema: Clasificación incorrecta cuando `estado_inci` contradecía disponibilidad real
  - Solución: Prioridad de verificación por condiciones reales (disponibilidad + días) sobre estado explícito
- ✅ **FIX**: Validación case-insensitive de columnas Excel
  - Ahora acepta "comentario", "Comentario", "COMENTARIO", etc.

**🎨 Nuevas Funcionalidades:**
- ✅ **Filtro por Dirección Zonal (DZ)** en sidebar con selector "Todas" o DZ específica
- ✅ **Sección de Estaciones Paralizadas** con:
  - Tabla ordenada por días de paralización
  - Alertas para candidatas a clausura (>2 años)
  - Tarjetas expandibles con diferenciación visual (rojo: >2 años, gris: <2 años)
- ✅ **Columna "Razón de Prioridad"**: Explicación automática de clasificación
- ✅ **Boxplot mejorado por sensor**: Comparación de distribución entre tipos de sensores

**📊 Mejoras de UI:**
- ✅ Tarjetas de alerta más compactas con gradientes CSS
- ✅ Tablas con altura dinámica según contenido
- ✅ Contadores de prioridad: ALTA, MEDIA, BAJA (paralizadas)
- ✅ Descripciones detalladas en cada sección

**⚙️ Nuevos Parámetros de Configuración:**
- `PRIORITY_PARALIZADA_MIN_DAYS = 90` (3 meses)
- `PRIORITY_CLAUSURA_MIN_DAYS = 730` (2 años)

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