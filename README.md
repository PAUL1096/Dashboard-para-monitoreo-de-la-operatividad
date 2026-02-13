# 🌦️ Dashboard Meteorológico SGR

Dashboard interactivo para monitoreo de disponibilidad de red meteorológica del Sistema de Gestión de Riesgos (SGR).

**Versión:** 3.0
**Autor:** Sistema de Monitoreo Meteorológico - SGR
**Fecha:** Febrero 2026

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Entorno de Ejecución](#entorno-de-ejecución)
- [Ejecución de Pipelines](#ejecución-de-pipelines)
- [Ejecutar el Dashboard](#ejecutar-el-dashboard)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Estructura de Datos](#estructura-de-datos)
- [Funcionalidades](#funcionalidades)
- [Configuración](#configuración)
- [Solución de Problemas](#solución-de-problemas)

---

---

## ⚠️ Entorno de Ejecución

Todos los scripts (pipeline y dashboard) requieren el entorno conda **`proyecto_monitoreodash`**.

**Activar antes de cualquier ejecución:**

```bash
# Abrir Anaconda Prompt desde el menú Inicio, luego:
conda activate proyecto_monitoreodash
cd "C:\Users\PAUL\OneDrive\Trabajo\SENAMHI - SGR\2026\automatización\Dashboard-para-monitoreo-de-la-operatividad"
```

> Sin este entorno activo, los comandos `python` y `streamlit` no encontrarán las dependencias.

---

## 🔄 Ejecución de Pipelines

> **Requisito previo:** Estar conectado a la red interna (SISMOP disponible en `172.25.150.27`) y tener Chrome instalado para la descarga automática de PDFs.

---

### 🤖 Estaciones Automáticas — Todos los Viernes (7 días)

Los reportes cubren el período viernes–jueves. Ejecutar el viernes por la mañana.

**Caso habitual — pipeline completo desde cero:**
```bash
cd PIPELINE/automaticas
python ejecutar_pipeline_auto.py
```
Descarga PDFs de las 13 DZs → extrae CSVs → calcula disponibilidad e incidencias.
Tiempo estimado: ~15–20 minutos (la descarga es el paso más lento).

**Si los PDFs ya fueron descargados** (descarga parcial o manual previa):
```bash
python ejecutar_pipeline_auto.py --skip-download
```

**Si solo cambiaron parámetros y los CSVs ya existen** (recalcular sin reextracción):
```bash
python ejecutar_pipeline_auto.py --solo-procesar
```

Reporte generado en:
```
DATA/automaticas/04_consolidados/reporte_disponibilidad_consolidado_DDMM_DDMM.xlsx
```

---

### 📋 Estaciones Convencionales — Mensual / Trimestral / Semestral

**Pipeline completo** (el script pedirá las fechas de inicio y fin durante la ejecución):
```bash
cd PIPELINE/convencionales
python ejecutar_pipeline_conv.py
```

Periodos soportados: 30, 90 o 180 días según lo que se seleccione en SISMOP.

**Si los PDFs ya están descargados:**
```bash
python ejecutar_pipeline_conv.py --skip-download
```

**Solo recalcular (CSVs ya existen):**
```bash
python ejecutar_pipeline_conv.py --solo-procesar
```

Reporte generado en:
```
DATA/convencionales/04_consolidados/reporte_disponibilidad_consolidado_convencional_*.xlsx
```

---

### 📂 ¿Dónde quedan los datos intermedios?

| Paso | Carpeta | Contenido |
|------|---------|-----------|
| 1. Descarga | `DATA/{tipo}/01_pdfs/` | PDFs descargados de SISMOP |
| 2. Extracción | `DATA/{tipo}/02_csv/` | CSVs de disponibilidad y fallas |
| 3. Procesamiento | `DATA/{tipo}/03_reportes/` | Reporte por semana/periodo |
| 4. Consolidación | `DATA/{tipo}/04_consolidados/` | **Reporte final con historial** ⭐ |

> `{tipo}` = `automaticas` o `convencionales`

---

## 🎯 Ejecutar el Dashboard

Después de generar el reporte (o en cualquier momento para ver el histórico):

```bash
# Desde la raíz del proyecto, con el entorno activo:
streamlit run main.py
```

El dashboard abre automáticamente en `http://localhost:8501` y **carga el reporte más reciente** de forma automática. También puedes subir un archivo diferente desde la barra lateral.

---

## ✨ Características

- 📊 **Resumen Ejecutivo**: KPIs globales + radar multidimensional por Dirección Zonal
- 🚨 **Sistema de Alertas**: Clasificación automática ALTA/MEDIA/BAJA con razones explicativas
- 🔍 **Detección de Problemas Ocultos**: Identifica sensores/variables críticos en estaciones aparentemente operativas
- ⚙️ **Anomalías de Configuración**: Detecta items con disponibilidad >100% (error de frecuencia)
- 🗺️ **Heatmap Estación × Variable**: Vista cruzada de disponibilidad por variable individual
- 🌐 **Radar por DZ**: Comparativa multidimensional de las 13 Direcciones Zonales
- 🎨 **Interfaz Centro de Control**: Tema oscuro con tipografía técnica (Bebas Neue + IBM Plex Mono)
- ⚡ **Auto-carga**: El reporte más reciente se carga automáticamente al iniciar
- 📥 **Exportación CSV**: Descarga disponible en cada sección
- 🔤 **Validación Flexible**: Columnas Excel con matching case-insensitive

---

## 📁 Estructura del Proyecto

```
Dashboard-para-monitoreo-de-la-operatividad/
│
├── main.py                          # Dashboard Streamlit ⭐
├── config.py                        # Configuración y estilos CSS
├── requirements.txt                 # Dependencias del dashboard
├── CLAUDE.md                        # Guía para desarrollo con IA
├── README.md                        # Este archivo
│
├── modules/                         # Módulos del dashboard
│   ├── file_handler.py             # Carga y validación de Excel
│   ├── data_processor.py           # Cálculos y clasificaciones
│   ├── chart_builder.py            # Gráficos Plotly
│   └── ui_components.py            # Componentes de interfaz
│
├── PIPELINE/                        # Pipelines de procesamiento
│   ├── compartido/
│   │   └── extractor_pdf.py        # Extracción PDF (compartido)
│   ├── automaticas/
│   │   ├── ejecutar_pipeline_auto.py   # Orquestador ⭐
│   │   ├── descargar_reportes.py
│   │   ├── procesamiento.py
│   │   └── config/
│   │       └── variables_frecuencia.xlsx
│   └── convencionales/
│       ├── ejecutar_pipeline_conv.py   # Orquestador ⭐
│       ├── descargar_reportes.py
│       ├── procesamiento.py
│       └── config/
│           └── variables-instrumento-convencionales.xlsx
│
└── DATA/                            # Datos (no versionados en Git)
    ├── automaticas/
    │   ├── 01_pdfs/                # PDFs descargados de SISMOP
    │   ├── 02_csv/                 # CSVs extraídos
    │   ├── 03_reportes/            # Reportes semanales
    │   └── 04_consolidados/        # Reportes finales ⭐
    └── convencionales/
        ├── 01_pdfs/
        ├── 02_csv/
        ├── 03_reportes/
        └── 04_consolidados/        # Reportes finales ⭐
```

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
- `DZ`: Dirección Zonal
- `Estacion`: Nombre de la estación
- `Sensor`: Tipo de sensor al que pertenece la variable (ej: `s_humre`, `s_temp`)
- `Variable`: Nombre individual de la variable meteorológica (ej: `N_MAXRH`, `N_MINAT`)
- `Frecuencia`: Frecuencia de medición (`minuto`, `horario`, `diario`)
- `disponibilidad`: % de disponibilidad
- `var_disp`: Categoría de disponibilidad
- `Datos_flag_C`: Datos correctos recibidos
- `Datos_flag_M`: Datos con error (fuera de rango)
- `Datos_esperados`: Total de datos esperados según frecuencia

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

### Versión 3.0 (Febrero 2026) - REDISEÑO Y ANÁLISIS AVANZADO

**🎨 Interfaz:**
- Tema oscuro tipo "Centro de Control Meteorológico" (Bebas Neue + IBM Plex Mono)
- Paleta cian/rojo/ámbar con grid CSS, tarjetas animadas y scrollbar personalizada
- Sidebar simplificado: auto-carga del reporte más reciente, sin controles redundantes
- Nuevo orden de 6 tabs orientado a decisores

**📊 Nuevas Visualizaciones:**
- **Radar DZ**: Comparativa multidimensional de las 13 Direcciones Zonales
- **Heatmap Estación × Variable**: Disponibilidad cruzada con RdYlGn
- **Gráfico de Problemas Ocultos**: Barras comparativas referencia vs item crítico

**🔍 Nuevas Funcionalidades de Análisis:**
- **Tab Resumen Ejecutivo**: KPIs + radar DZ + top 5 situaciones urgentes
- **Tab Problemas Ocultos**: Detección de sensores/variables críticos en estaciones con buena disponibilidad global
  - Tipo 1: Estación ≥80% pero sensor <80% (brecha = disp\_estación − disp\_sensor)
  - Tipo 2: Sensor ≥80% pero variable <80% (brecha = disp\_sensor − disp\_variable)
  - Sin duplicados: variables cuyo sensor ya es crítico no se repiten
- **Anomalías de Configuración**: Sección separada para items con disponibilidad >100%

**🔧 Correcciones de Datos:**
- Columna `Variable` ahora reconocida correctamente en hoja POR VARIABLE
- `variable_id` incluye Sensor + Variable + Frecuencia para ser único
- Stats de variables agrupan por `Variable`, no por `Sensor`

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