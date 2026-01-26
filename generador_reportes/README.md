# Generador de Reportes - Dashboard Meteorológico SGR

Este módulo contiene los scripts para generar los reportes Excel que consume el Dashboard de Disponibilidad.

## Flujo de Generación de Reportes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUJO DE GENERACIÓN DE REPORTES                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   PASO 1-3       │     │     PASO 4       │     │     PASO 5       │
│    (Manual)      │────▶│  procesar_pdfs   │────▶│ calcular_disp    │
│                  │     │                  │     │                  │
│ Descargar PDFs   │     │ PDFs → CSV       │     │ CSV → Excel      │
│ de herramienta   │     │                  │     │ (3 hojas)        │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
   input_pdfs/              output/                  ../reportes/
   ├── DZ_01.pdf            └── datos_raw.csv        └── reporte_DDMM_DDMM.xlsx
   ├── DZ_02.pdf
   └── ...
```

---

## Pasos Detallados

### Paso 1-3: Descarga Manual de PDFs

1. **Acceder** a la herramienta interna del área
2. **Seleccionar** la Dirección Zonal (DZ)
3. **Configurar** el período a consultar (7 días)
4. **Descargar** el reporte PDF
5. **Repetir** para cada Dirección Zonal
6. **Guardar** todos los PDFs en la carpeta `input_pdfs/`

**Nomenclatura sugerida para PDFs:**
```
reporte_DZ01_DDMM_DDMM.pdf
reporte_DZ02_DDMM_DDMM.pdf
...
```

---

### Paso 4: Procesamiento de PDFs → CSV

**Script:** `01_procesar_pdfs.py`

**Entrada:** PDFs de cada Dirección Zonal en `input_pdfs/`

**Salida:** CSV consolidado en `output/datos_raw.csv`

**Datos extraídos:**
| Campo | Descripción |
|-------|-------------|
| DZ | Dirección Zonal |
| Estacion | Nombre de la estación |
| Sensor | Tipo de sensor/variable |
| Frecuencia | Frecuencia de medición |
| Datos_flag_C | Datos correctos |
| Datos_flag_M | Datos con error/malos |
| Datos_esperados | Total de datos esperados |
| f_inci | Fecha de incidencia |
| estado_inci | Estado de la incidencia |
| comentario | Observaciones técnicas |

**Uso:**
```bash
python 01_procesar_pdfs.py --input input_pdfs/ --output output/datos_raw.csv
```

---

### Paso 5: Cálculo de Disponibilidad → Excel

**Script:** `02_calcular_disponibilidad.py`

**Entrada:** CSV con datos raw de `output/datos_raw.csv`

**Salida:** Excel con 3 hojas en `../reportes/reporte_disponibilidad_SGR_DDMM_DDMM.xlsx`

**Cálculos realizados:**

#### Hoja 1: POR ESTACION
```
disponibilidad = (Datos_flag_C / Datos_esperados) * 100
var_disp = disponibilidad_actual - disponibilidad_anterior
```
Agrupa por: DZ, Estacion

#### Hoja 2: POR EQUIPAMIENTO
```
disponibilidad = (Datos_flag_C / Datos_esperados) * 100
```
Agrupa por: DZ, Estacion, Sensor (tipo de equipamiento)

#### Hoja 3: POR VARIABLE
```
disponibilidad = (Datos_flag_C / Datos_esperados) * 100
```
Detalle por: DZ, Estacion, Sensor (variable), Frecuencia

**Uso:**
```bash
python 02_calcular_disponibilidad.py --input output/datos_raw.csv --output ../reportes/
```

---

## Estructura de Carpetas

```
generador_reportes/
├── README.md                      # Esta documentación
├── 01_procesar_pdfs.py           # Script: PDFs → CSV
├── 02_calcular_disponibilidad.py # Script: CSV → Excel
├── config_generador.py           # Configuración del generador
├── utils.py                      # Funciones auxiliares
├── input_pdfs/                   # PDFs descargados (no versionados)
│   └── .gitkeep
└── output/                       # Archivos intermedios (no versionados)
    └── .gitkeep
```

---

## Requisitos Adicionales

```
# Añadir a requirements.txt o crear requirements_generador.txt
pdfplumber>=0.9.0      # Extracción de texto/tablas de PDFs
# o alternativamente:
PyPDF2>=3.0.0          # Lectura de PDFs
tabula-py>=2.7.0       # Extracción de tablas de PDFs
```

---

## Configuración

Editar `config_generador.py` para ajustar:

- Rutas de entrada/salida
- Patrones de nombres de archivo
- Mapeo de columnas del PDF
- Umbrales y validaciones

---

## Ejecución Completa

```bash
# 1. Colocar PDFs en input_pdfs/

# 2. Procesar PDFs a CSV
python 01_procesar_pdfs.py

# 3. Generar Excel con disponibilidad
python 02_calcular_disponibilidad.py

# 4. Verificar reporte en ../reportes/

# 5. Abrir Dashboard
cd ..
streamlit run main.py
```

---

## TODO para Agente IA

Tareas pendientes para automatización:

- [ ] Implementar `01_procesar_pdfs.py` con lógica real de extracción
- [ ] Implementar `02_calcular_disponibilidad.py` con cálculos de métricas
- [ ] Añadir validación de datos extraídos
- [ ] Crear tests unitarios para los scripts
- [ ] Documentar estructura exacta de los PDFs de entrada
- [ ] Añadir logging y manejo de errores
- [ ] Opcional: Automatizar descarga de PDFs si hay API disponible

---

## Notas

- Los PDFs y archivos intermedios no se versionan (están en `.gitignore`)
- El Excel final se genera en `../reportes/` para uso directo del Dashboard
- Mantener nomenclatura `reporte_disponibilidad_SGR_DDMM_DDMM.xlsx` para detección automática de fechas
