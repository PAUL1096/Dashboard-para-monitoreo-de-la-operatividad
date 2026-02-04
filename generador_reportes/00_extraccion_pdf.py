from pyparsing import col
import pdfplumber
import csv
import pandas as pd
import numpy as np
import re
import os
import glob
import csv
import unicodedata
import datetime
import locale


# Preguntar al usuario por el tipo de red
tipo_red = ''
while tipo_red not in ['automatica', 'convencional']:
    tipo_red = input("¿Qué red se procesará? (automatica/convencional): ").strip().lower()

# Establecer el locale en español (esto puede variar según el sistema operativo)
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Linux/Mac
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain')  # Windows
    except:
        print("No se pudo establecer el locale en español.")

fecha_inicio = input("Ingresa fecha inicio (dd/mm/yyyy): ").strip()
fecha_fin = input("Ingresa fecha fin (dd/mm/yyyy): ").strip()

# Lista de archivos PDF a procesar (puedes poner una carpeta o lista manual)
ruta_carpeta = "../automaticas_disp"
pdf_files = glob.glob(os.path.join(ruta_carpeta, "*.pdf"))

# CSV de salida
# fecha_inicio = '02/10/2025'
# fecha_fin = '08/10/2025'
dia_mes_inicio = fecha_inicio[:5].replace('/', '')
dia_mes_fin = fecha_fin[:5].replace('/', '')

# Creación de los nombres de los archivos resultantes
csv_disponibilidad = "disponibilidad" + '_' + tipo_red + '_' + dia_mes_inicio + '_' + dia_mes_fin + '.csv'
csv_fallas = "fallas" + '_' + tipo_red + '_' + dia_mes_inicio + '_' + dia_mes_fin + '.csv'

# --- Patrones ---
patron_estacion = re.compile(r"Estación:\s+(.+)", re.IGNORECASE)
patron_disponibilidad = re.compile(r"Tabla de Disponibilidad de Datos", re.IGNORECASE)
patron_fallas = re.compile(r"Tabla de Fallas en Sensores", re.IGNORECASE)
patron_dz = re.compile(r"Reporte_DZ_(\d+)\.pdf", re.IGNORECASE)

# --- Normalización / reparación de texto ---
def fix_text(s):
    if s is None:
        return s
    s = s.strip()
    if not s:
        return s
    s = s.replace("\ufeff", "")
    try:
        if "Ã" in s or "Â" in s:
            candidate = s.encode("latin1").decode("utf-8")
            if sum(1 for c in candidate if ord(c) > 127) >= sum(1 for c in s if ord(c) > 127):
                s = candidate
    except Exception:
        pass
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# --- Inicializar estructuras ---
rows_disponibilidad = []
rows_fallas = []

cols_disponibilidad = ["DZ", "Estacion", "Variable", "Datos_flag_C", "Datos_flag_M", "Datos_flag_SD", "Datos_esperados", "Operatividad"]
cols_fallas = ["DZ", "Estacion", "Sensor ID", "Nombre del Sensor", "Variables con Falla"]

# --- Procesar PDFs ---
for pdf_file in pdf_files:
    # extraer número DZ del nombre de archivo
    dz_match = patron_dz.search(os.path.basename(pdf_file))
    dz_value = dz_match.group(1) if dz_match else "NA"

    if not os.path.exists(pdf_file):
        print(f"Archivo no encontrado: {pdf_file}")
        continue

    with pdfplumber.open(pdf_file) as pdf:
        estacion_actual = None
        en_disponibilidad = False
        en_fallas = False

        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for raw_line in text.split("\n"):
                line = fix_text(raw_line)

                # detectar estación
                m_est = patron_estacion.search(line)
                if m_est:
                    estacion_actual = fix_text(m_est.group(1))
                    en_disponibilidad = False
                    en_fallas = False
                    continue

                # detectar inicio de tablas
                if patron_disponibilidad.search(line):
                    en_disponibilidad = True
                    en_fallas = False
                    continue
                if patron_fallas.search(line):
                    en_disponibilidad = False
                    en_fallas = True
                    continue

                # parsear disponibilidad
                if en_disponibilidad:
                    parts = line.split()
                    if len(parts) >= 6:
                        variable = fix_text(parts[0])
                        # filtrar filas basura
                        if variable in {"Variable", "Operatividad", "Sin"}:
                            continue
                        tail = parts[-5:]
                        datos_c, datos_m, datos_sd, datos_exp, oper = [fix_text(t) for t in tail]
                        rows_disponibilidad.append([
                            dz_value,
                            estacion_actual,
                            variable,
                            datos_c, datos_m, datos_sd, datos_exp, oper
                        ])

                # parsear fallas
                if en_fallas:
                    parts = line.split()
                    if len(parts) >= 3:
                        sensor_id = fix_text(parts[0])
                        variables = fix_text(parts[-1])
                        nombre_sensor = fix_text(" ".join(parts[1:-1])) if len(parts) > 2 else ""
                        rows_fallas.append([
                            dz_value,
                            estacion_actual,
                            sensor_id,
                            nombre_sensor,
                            variables
                        ])

# Guardar CSV con BOM
with open(csv_disponibilidad, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(cols_disponibilidad)
    writer.writerows(rows_disponibilidad)

with open(csv_fallas, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(cols_fallas)
    writer.writerows(rows_fallas)

print("Extracción completada:")
print(" -", csv_disponibilidad)
print(" -", csv_fallas)
