# Generador de Reportes - Dashboard Meteorológico SGR

Este módulo contiene los scripts para generar los reportes Excel que consume el Dashboard de Disponibilidad.

## Flujo de Generación de Reportes

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          FLUJO DE GENERACIÓN DE REPORTES                            │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   PASO 1-3       │     │     PASO 4       │     │     PASO 5       │     │     PASO 6       │
│    (Manual)      │────▶│ 00_extraccion    │────▶│ 01_procesamiento │────▶│ 02_postproceso   │
│                  │     │                  │     │                  │     │                  │
│ Descargar PDFs   │     │ PDFs → CSV       │     │ CSV → Excel      │     │ Consolidar       │
│ de herramienta   │     │ (disponibilidad  │     │ (3 hojas)        │     │ con histórico    │
│                  │     │  y fallas)       │     │                  │     │                  │
└──────────────────┘     └──────────────────┘     └──────────────────┘     └──────────────────┘
        │                        │                        │                        │
        ▼                        ▼                        ▼                        ▼
   input_pdfs/              output/                  output/                  ../reportes/
   ├── Reporte_DZ_1.pdf     ├── disponibilidad_*.csv ├── reporte_disp_*.xlsx  └── reporte_consolidado.xlsx
   ├── Reporte_DZ_2.pdf     └── fallas_*.csv
   └── ...
```

---

## Estructura del Módulo

```
generador_reportes/
├── README.md                    # Esta documentación
├── 00_extraccion_pdf.py        # Extrae datos de PDFs → CSV
├── 01_procesamiento.py         # Procesa CSV → Excel (3 hojas)
├── 02_postproceso.py           # Consolida reportes (comparación temporal)
├── data/
│   └── variables_frecuencia.xlsx  # Frecuencias de medición por variable
├── input_pdfs/                 # PDFs descargados de la herramienta
│   ├── Reporte_DZ_1.pdf       # Ejemplo de PDF de entrada
│   └── .gitkeep
└── output/                     # Archivos intermedios y de salida
    └── .gitkeep
```

---

## Scripts Detallados

### Paso 4: `00_extraccion_pdf.py` - Extracción de PDFs

**Descripción:** Extrae datos de los reportes PDF de cada Dirección Zonal usando `pdfplumber`.

**Entrada:**
- PDFs en carpeta configurada (default: `../automaticas_disp/`)
- Formato nombre: `Reporte_DZ_N.pdf`

**Salida:**
- `disponibilidad_[tipo]_[DDMM]_[DDMM].csv` - Datos de disponibilidad
- `fallas_[tipo]_[DDMM]_[DDMM].csv` - Datos de fallas de sensores

**Columnas CSV disponibilidad:**
| Columna | Descripción |
|---------|-------------|
| DZ | Dirección Zonal (extraída del nombre archivo) |
| Estacion | Nombre de la estación |
| Variable | Variable meteorológica |
| Datos_flag_C | Datos correctos |
| Datos_flag_M | Datos con error |
| Datos_flag_SD | Datos sin dato |
| Datos_esperados | Total esperado según PDF |
| Operatividad | % operatividad según PDF |

**Uso:**
```bash
cd generador_reportes
python 00_extraccion_pdf.py
# Ingresa: tipo de red (automatica/convencional)
# Ingresa: fecha inicio (dd/mm/yyyy)
# Ingresa: fecha fin (dd/mm/yyyy)
```

---

### Paso 5: `01_procesamiento.py` - Cálculo de Disponibilidad

**Descripción:** Procesa el CSV de disponibilidad, une con frecuencias reales y calcula métricas agregadas.

**Entrada:**
- `disponibilidad_*.csv` (generado por paso anterior)
- `data/variables_frecuencia.xlsx` (frecuencias correctas por variable/estación)

**Salida:**
- `reporte_disponibilidad_[DDMM]_[DDMM].xlsx` con 3 hojas:
  - **POR ESTACION**: Disponibilidad agregada por estación
  - **POR EQUIPAMIENTO**: Disponibilidad por tipo de sensor
  - **POR VARIABLE**: Detalle por variable meteorológica

**Lógica de cálculo:**
```python
# Datos esperados según frecuencia real (no la del PDF)
datos_esperados = {
    'minuto': 6 * 24 * nro_dias,    # 1008 para 7 días
    'horario': 24 * nro_dias,        # 168 para 7 días
    'diario': nro_dias               # 7 para 7 días
}

# Disponibilidad = (Datos_flag_C / Datos_esperados) * 100
```

**Clasificación de variables por sensor:**
El script clasifica cada variable en su tipo de sensor correspondiente:
- `s_temp`: Temperatura (N_AIRTEMP, N_AIRTEMP_INST, N_MAXAT, N_MINAT, etc.)
- `s_humre`: Humedad relativa (N_HUMEDAD, N_MAXRH, N_MINRH, etc.)
- `s_prec`: Precipitación (N_LLUVIA, N_DAYRAIN, N_RAIN_10M, etc.)
- `s_dir_viento`: Dirección de viento
- `s_vel_viento`: Velocidad de viento
- `s_presion`: Presión atmosférica
- `s_rad_solar`: Radiación solar
- `s_nivel`: Nivel de agua
- Y más...

**Uso:**
```bash
python 01_procesamiento.py
# Lee automáticamente el CSV de disponibilidad en el directorio actual
```

---

### Paso 6: `02_postproceso.py` - Consolidación Temporal

**Descripción:** Compara el reporte actual con el anterior para determinar estados de incidencia y generar reporte consolidado.

**Entrada:**
- Reporte anterior (con columnas f_inci, estado_inci, comentario)
- Reporte nuevo (generado por paso anterior)
- Fecha de referencia (fecha de corte del análisis)

**Salida:**
- `reporte_disponibilidad_consolidado.xlsx` con 4 hojas:
  - **POR ESTACION**: Consolidado con estados de incidencia
  - **Indicadores**: Métricas globales y por DZ
  - **POR EQUIPAMIENTO**: Copia del reporte nuevo
  - **POR VARIABLE**: Copia del reporte nuevo

**Estados de incidencia:**
| Estado | Condición |
|--------|-----------|
| Sin incidencia | Disponibilidad >= 80% y sin problemas previos |
| Nueva | Primera vez con disponibilidad < 80% |
| Recurrente | > 5 días desde que se reportó como Nueva |
| Solucionado | Antes tenía incidencia, ahora >= 80% |

**Reglas de clasificación:**
- Si disponibilidad actual >= 80%: Sin incidencia o Solucionado
- Si disponibilidad < 80% y no había incidencia previa: Nueva
- Si era "Nueva" y han pasado > 5 días: Recurrente
- Si era "Recurrente": Se mantiene Recurrente hasta que se solucione

**Uso:**
```bash
python 02_postproceso.py
# Ingresa: ruta reporte anterior
# Ingresa: ruta reporte nuevo
# Ingresa: fecha de referencia (dd/mm/yyyy)
```

---

## Archivo de Datos: `variables_frecuencia.xlsx`

Contiene las frecuencias de medición correctas para cada combinación DZ/Estación/Variable.

**Hoja: frecuencias**
| DZ | Estacion | Variable | Frecuencia |
|----|----------|----------|------------|
| 1 | SAUZAL | N_AIRTEMP_INST | horario |
| 1 | SAUZAL | N_DAYRAIN | diario |
| 1 | SAUZAL | N_RAIN_10M | minuto |
| ... | ... | ... | ... |

**Valores de Frecuencia:**
- `minuto`: Datos cada 10 minutos (6/hora)
- `horario`: Datos cada hora
- `diario`: Datos una vez al día

---

## Ejecución Completa

```bash
# 1. Descargar PDFs de la herramienta interna (manual)
#    - Seleccionar cada DZ
#    - Período: 7 días
#    - Guardar en input_pdfs/

# 2. Extraer datos de PDFs
cd generador_reportes
python 00_extraccion_pdf.py
# Tipo: automatica
# Fechas: según período descargado

# 3. Procesar y calcular disponibilidad
python 01_procesamiento.py

# 4. Consolidar con reporte anterior (si existe)
python 02_postproceso.py
# Ingresa rutas de reportes y fecha

# 5. Copiar reporte consolidado a ../reportes/
cp reporte_disponibilidad_consolidado.xlsx ../reportes/

# 6. Abrir Dashboard
cd ..
streamlit run main.py
```

---

## Estructura del PDF de Entrada

Cada PDF contiene reportes por estación con:

1. **Tabla de Disponibilidad de Datos:**
   - Variable
   - Datos con flag C (correctos)
   - Datos con flag M (erróneos)
   - Datos con flag SD (sin dato)
   - Datos Esperados
   - Operatividad (%)

2. **Tabla de Fallas en Sensores:**
   - Sensor ID
   - Nombre del Sensor
   - Variables con Falla

---

## Dependencias Adicionales

```bash
# Instalar dependencias para extracción de PDFs
pip install pdfplumber xlsxwriter
```

---

## Notas Importantes

1. **Frecuencias del PDF vs Reales:**
   - El PDF calcula "Datos Esperados" de forma estándar
   - El script `01_procesamiento.py` recalcula usando las frecuencias reales de `variables_frecuencia.xlsx`
   - Esto corrige casos donde el PDF muestra >100% de operatividad

2. **Parámetros Operacionales:**
   - Variables como `N_BATERIA` y `N_TEMP_INT_TRANS` se excluyen del análisis

3. **Tolerancia de 5 días:**
   - Una incidencia "Nueva" se convierte en "Recurrente" si persiste > 5 días
   - Esto permite tiempo para solución antes de escalar

4. **Comentarios y Fechas:**
   - El campo `comentario` se preserva del reporte anterior
   - El campo `f_inci` (fecha de incidencia) se usa para calcular antigüedad

---

## TODO para Automatización Futura

- [ ] Automatizar descarga de PDFs si hay API disponible
- [ ] Crear pipeline que ejecute los 3 scripts en secuencia
- [ ] Añadir validación de datos entre pasos
- [ ] Crear tests unitarios
- [ ] Implementar logging estructurado
- [ ] Añadir notificaciones por email de alertas críticas
