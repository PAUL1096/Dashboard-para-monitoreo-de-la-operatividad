# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Entorno de Ejecución

**Conda environment:** `proyecto_monitoreodash`

Siempre usar este entorno para ejecutar scripts Python o inspeccionar datos:
```bash
conda run -n proyecto_monitoreodash python script.py
# o activar primero:
conda activate proyecto_monitoreodash
```

## Project Overview

Dashboard meteorológico for SENAMHI-SGR (Sistema de Monitoreo de Operatividad) that monitors the operational status of automated and conventional meteorological stations across 13 Direcciones Zonales (DZs) in Peru.

The system consists of two main components:
1. **Data Processing Pipelines** (`PIPELINE/`) - Separate pipelines for automatic and conventional stations
2. **Streamlit Dashboard** (root directory) - Interactive visualization of station availability, incidents, and alerts

## Project Structure

```
Dashboard-para-monitoreo-de-la-operatividad/
├── main.py                    # Streamlit dashboard entry point
├── config.py                  # Dashboard configuration
├── modules/                   # Dashboard UI modules
│   ├── file_handler.py
│   ├── data_processor.py
│   ├── chart_builder.py
│   └── ui_components.py
│
├── PIPELINE/                  # Data processing pipelines
│   ├── compartido/
│   │   └── extractor_pdf.py   # Shared PDF extraction (serves both types)
│   │
│   ├── automaticas/           # Pipeline for automatic stations (7 days)
│   │   ├── descargar_reportes.py
│   │   ├── 01_procesamiento.py
│   │   ├── 02_postproceso.py
│   │   ├── ejecutar_pipeline_auto.py  # Master orchestrator
│   │   └── config/
│   │       └── variables_frecuencia.xlsx
│   │
│   └── convencionales/        # Pipeline for conventional stations (30/90/180 days)
│       ├── descargar_reportes.py
│       ├── 01_procesamiento.py
│       ├── 02_postproceso.py
│       ├── ejecutar_pipeline_conv.py  # Master orchestrator
│       └── config/
│           └── variables-instrumento-convencionales.xlsx
│
└── DATA/                      # All data storage
    ├── automaticas/
    │   ├── 01_pdfs/           # Downloaded PDFs
    │   ├── 02_csv/            # Intermediate CSVs
    │   ├── 03_reportes/       # Processed reports (3 sheets)
    │   └── 04_consolidados/   # Final consolidated reports (4 sheets)
    │
    └── convencionales/
        ├── 01_pdfs/
        ├── 02_csv/
        ├── 03_reportes/
        └── 04_consolidados/
```

## Development Commands

### Running the Dashboard

```bash
# From project root
streamlit run main.py
# Dashboard available at http://localhost:8501
```

### Automatic Stations Pipeline (7 days)

```bash
cd PIPELINE/automaticas

# Option 1: Full pipeline (download + process)
python ejecutar_pipeline_auto.py

# Option 2: Skip download (PDFs already exist)
python ejecutar_pipeline_auto.py --skip-download

# Option 3: Only processing steps (steps 3-4)
python ejecutar_pipeline_auto.py --solo-procesar

# Manual execution (step by step):
# 1. Download PDFs
python descargar_reportes.py

# 2. Extract data (run from DATA/automaticas/02_csv/)
cd ../../DATA/automaticas/02_csv
python ../../../PIPELINE/compartido/extractor_pdf.py
# When prompted: tipo_red = "automatica"

# 3. Process and calculate availability
python ../../../PIPELINE/automaticas/01_procesamiento.py

# 4. Consolidate with historical
python ../../../PIPELINE/automaticas/02_postproceso.py
```

### Conventional Stations Pipeline (30/90/180 days)

```bash
cd PIPELINE/convencionales

# Option 1: Full pipeline
python ejecutar_pipeline_conv.py

# Option 2: With custom period
python ejecutar_pipeline_conv.py --dias 90

# Option 3: Skip download
python ejecutar_pipeline_conv.py --skip-download

# Manual execution (step by step):
# 1. Download PDFs
python descargar_reportes.py

# 2. Extract data (run from DATA/convencionales/02_csv/)
cd ../../DATA/convencionales/02_csv
python ../../../PIPELINE/compartido/extractor_pdf.py
# When prompted: tipo_red = "convencional"

# 3. Process and calculate availability
python ../../../PIPELINE/convencionales/01_procesamiento.py

# 4. Consolidate with historical
python ../../../PIPELINE/convencionales/02_postproceso.py
```

### Installing Dependencies

```bash
# Dashboard dependencies (from root)
pip install -r requirements.txt

# Pipeline dependencies (if needed separately)
pip install selenium pdfplumber pandas openpyxl xlsxwriter
```

## Architecture

### Pipeline Differences: Automáticas vs Convencionales

| Aspect | Automáticas | Convencionales |
|--------|-------------|----------------|
| **Period** | 7 days (Friday-Friday) | 30/90/180 days |
| **Frequency Correction** | Uses `variables_frecuencia.xlsx` to fix PDF errors | Uses PDF data directly (no correction) |
| **Sensor Mapping** | Hardcoded dictionaries in script | Excel: `variables-instrumento-convencionales.xlsx` |
| **Expected Data Calculation** | `minuto: 6×24×7`, `horario: 24×7`, `diario: 7` | Uses PDF values directly |
| **Output File** | `reporte_disponibilidad_consolidado.xlsx` | `reporte_disponibilidad_consolidado_convencional.xlsx` |

### Shared Component: PDF Extraction

**Script:** `PIPELINE/compartido/extractor_pdf.py`

- **Serves both types** of stations (asks user for `tipo_red`)
- Auto-detects PDF source directory based on `tipo_red`:
  - `automatica` → `DATA/automaticas/01_pdfs/`
  - `convencional` → `DATA/convencionales/01_pdfs/`
- Outputs CSVs to: `DATA/{tipo_red}s/02_csv/`
- Extracts two tables:
  - "Tabla de Disponibilidad de Datos" → `disponibilidad_{tipo_red}_DDMM_DDMM.csv`
  - "Tabla de Fallas en Sensores" → `fallas_{tipo_red}_DDMM_DDMM.csv`
- Text normalization handles UTF-8/latin1 encoding issues
- Extracts DZ number from filename: `Reporte_DZ_N.pdf`

### Automatic Stations Pipeline

**Stage 1: Download** (`descargar_reportes.py`)
- Uses Selenium to automate SISMOP web interface (http://172.25.150.27:8050/)
- Iterates through 13 DZs
- Date logic: Reports cover Friday-to-Thursday but require Friday-to-Friday selection in SISMOP
- Downloads to: `DATA/automaticas/01_pdfs/`

**Stage 2: Processing** (`01_procesamiento.py`)
- **Critical feature:** Corrects PDF errors using `variables_frecuencia.xlsx`
- The PDF often miscalculates "Datos Esperados" - this Excel provides correct frequencies per (DZ, Estacion, Variable)
- Recalculates expected data counts:
  - `minuto`: 6 × 24 × 7 = 1008 (for 7 days)
  - `horario`: 24 × 7 = 168
  - `diario`: 7
- Subtracts 1 from `Datos_flag_C` (PDF counts starting hour incorrectly)
- Classifies variables into sensor types using hardcoded dictionaries (s_temp, s_humre, s_prec, etc.)
- Aggregates by:
  - **Station** (average of all variables)
  - **Equipment** (average by sensor type)
  - **Variable** (individual variable performance)
- Outputs 3-sheet Excel: "POR ESTACION", "POR EQUIPAMIENTO", "POR VARIABLE"
- Excludes operational variables: `N_BATERIA`, `N_TEMP_INT_TRANS`

**Stage 3: Consolidation** (`02_postproceso.py`)
- Compares current report with previous report
- Tracks incident states with 5-day tolerance:
  - **Sin incidencia**: Availability ≥ 80%, no prior issues
  - **Nueva**: First occurrence below 80%
  - **Recurrente**: "Nueva" incident persisting > 5 days
  - **Solucionado**: Previously had incident, now ≥ 80%
- Preserves `comentario` and `f_inci` (incident date) fields
- Outputs 4-sheet Excel: "POR ESTACION" (consolidated), "Indicadores" (metrics), "POR EQUIPAMIENTO", "POR VARIABLE"

### Conventional Stations Pipeline

**Differences from Automatic:**

1. **No frequency correction:** Uses PDF "Datos Esperados" directly (no `variables_frecuencia.xlsx`)
2. **Period detection:** Auto-calculates `nro_dias` from input dates
3. **Sensor mapping:** Reads from `variables-instrumento-convencionales.xlsx` instead of hardcoded dictionaries
   - Excel must have columns: `Variable`, `Instrumento`
   - Creates dynamic mapping: `mapeo_instrumento = dict(zip(Variable, Instrumento))`
4. **Output file:** `reporte_disponibilidad_consolidado_convencional.xlsx`

### Dashboard Architecture

**Entry Point**: `main.py`
- Streamlit-based single-page application
- Configuration loaded from `config.py` (paths, thresholds, color schemes)
- Modular design using `modules/` package

**Module Organization:**
- `modules/file_handler.py`: Excel loading with case-insensitive column validation
- `modules/data_processor.py`: Data transformations, filtering, alert priority classification
- `modules/chart_builder.py`: Plotly chart generation (13+ visualization types)
- `modules/ui_components.py`: Reusable UI elements (metric cards, alert badges)

**Alert Priority Logic:**
- **ALTA**: Availability < 30% OR incident "Recurrente"
- **MEDIA**: Availability 30-79% AND incident "Nueva"
- **BAJA**: Paralyzed stations (> 2 years inactive)

**Data Flow:**
```
DATA/{tipo}/04_consolidados/*.xlsx → file_handler → data_processor → [chart_builder, ui_components] → Streamlit UI
```

## Important Technical Details

### SISMOP Integration
- System URL: `http://172.25.150.27:8050/` (internal network only)
- Selenium timeouts:
  - Automáticas: 30s data loading, 60s PDF generation
  - Convencionales: 90s data loading, 180s PDF generation
- Date picker uses dynamic IDs, accessed via `placeholder` attribute
- Chrome WebDriver required (chromedriver in PATH)

### Frequency Calculations (Automáticas Only)
The `variables_frecuencia.xlsx` file is **critical for correct availability calculations**. The PDF often miscalculates expected data counts. This Excel file maps each (DZ, Estacion, Variable) tuple to its actual measurement frequency.

Without this correction, stations can show >100% availability (impossible).

### Availability Threshold
**80%** is the operational threshold across the entire system. Below this triggers incident classification.

### 5-Day Tolerance Rule
Incidents marked "Nueva" upgrade to "Recurrente" after 5 days. This allows reasonable time for troubleshooting before escalation.

### Date Selection Logic (Automáticas)
Weekly monitoring reports cover Friday-to-Thursday (7 days actual), but SISMOP requires Friday-to-Friday selection (8 days in UI). The download script handles this automatically via `fecha_fin + 1 día` logic.

### Sensor Variable Mapping

**Automáticas:** Uses hardcoded dictionaries (lines 22-137 in `01_procesamiento.py`):
- Each sensor type (e.g., `s_temp`, `s_prec`) contains `observado` and `calculado` variable lists
- Enables aggregation by equipment type

**Convencionales:** Uses Excel mapping (`variables-instrumento-convencionales.xlsx`):
- Dynamic lookup: `mapeo_instrumento.get(variable, None)`
- More flexible for stations with varying instrument configurations

### Auto-Detection of Period (Convencionales)

Script `01_procesamiento.py` automatically calculates `nro_dias`:
1. Extracts dates from CSV filename: `disponibilidad_convencional_0210_1003.csv`
2. Prompts user for year
3. Calculates: `nro_dias = (fecha_fin - fecha_inicio).days + 1`
4. Works for any period: 30, 31, 90, 180 days

### Excel Column Validation
Dashboard uses case-insensitive column matching to handle inconsistent capitalization from different report sources. See `file_handler.py:normalize_columns()`.

### Git Workflow
- Main branch: `main`
- Commit convention: Descriptive messages with "Co-Authored-By: Claude Sonnet 4.5"

## Common Issues & Solutions

### Issue: "No se encontró el archivo variables_frecuencia.xlsx"
- **Cause:** Script looking in wrong directory
- **Solution:** File must be in `PIPELINE/automaticas/config/variables_frecuencia.xlsx`

### Issue: "No se encontraron archivos PDF"
- **Cause:** PDFs in wrong directory or wrong tipo_red
- **Solution:**
  - Automáticas: PDFs must be in `DATA/automaticas/01_pdfs/`
  - Convencionales: PDFs must be in `DATA/convencionales/01_pdfs/`

### Issue: Availability > 100%
- **Cause:** PDF has incorrect "Datos Esperados"
- **Solution:**
  - For automáticas: Update `variables_frecuencia.xlsx`
  - For convencionales: Normal behavior (no correction applied)

### Issue: CSVs generated in wrong location
- **Cause:** Running extractor from wrong directory
- **Solution:** The extractor auto-detects output dir based on `tipo_red`, but ensure script is run with correct working directory

## Deployment Notes

### For Production on Work PC

1. **Directory Setup:**
   ```bash
   # Clone/copy project to work PC
   cd C:\SENAMHI\Dashboard-Operatividad
   ```

2. **Install Dependencies:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Scheduled Tasks (Windows Task Scheduler):**
   - **Automáticas:** Run `PIPELINE/automaticas/ejecutar_pipeline_auto.py` every Friday at 8 AM
   - **Convencionales:** Run `PIPELINE/convencionales/ejecutar_pipeline_conv.py` first day of month

4. **Dashboard Auto-Start:**
   ```batch
   @echo off
   cd C:\SENAMHI\Dashboard-Operatividad
   venv\Scripts\activate
   streamlit run main.py --server.port 8501
   ```

5. **Data Management:**
   - Keep PDFs for 30 days in `01_pdfs/`
   - Archive CSVs monthly from `02_csv/`
   - Preserve all consolidated reports in `04_consolidados/` for historical trend analysis

## Dependencies

**Dashboard** (root `requirements.txt`):
- streamlit
- pandas, numpy
- plotly
- openpyxl

**Pipeline:**
- selenium (≥4.15.0) - PDF download automation
- pdfplumber (≥0.10.0) - PDF data extraction
- pandas (≥2.0.0) - Data processing
- openpyxl, xlsxwriter (≥3.1.0) - Excel I/O
