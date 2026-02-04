#!/usr/bin/env python3
"""
consolidar_disponibilidad_xlsxwriter.py

Comparación entre reporte_anterior (con f_inci/estado_inci/comentario) y
reporte_nuevo (sin esas columnas). Genera:
 - Excel output con 4 hojas: "POR ESTACION", "Indicadores", "POR EQUIPAMIENTO" y "POR VARIABLE" 
   (usa xlsxwriter para formato).
 - Resumen en consola.

Reglas implementadas:
 - Clave: (DZ, Estacion)
 - Clasificación de var_disp según disponibilidad numérica.
 - Estados: 'Sin incidencia', 'Nueva', 'Recurrente', 'Solucionado' (se conservan comentarios/f_inci según reglas).
 - Tolerancia 5 días aplicada solo a prev estado == 'Nueva'.
 - Todas las estaciones (union) aparecen en el consolidado.
 - Se copian hojas adicionales del reporte nuevo: POR EQUIPAMIENTO y POR VARIABLE
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

SHEET_NAME = "POR ESTACION"
SHEET_EQUIPAMIENTO = "POR EQUIPAMIENTO"
SHEET_VARIABLE = "POR VARIABLE"
OUTFILE = "reporte_disponibilidad_consolidado.xlsx"

def clean_input_path(s: str) -> str:
    return s.strip().strip('"').strip("'")

def clasificar_var_disp_num(p):
    try:
        if pd.isna(p):
            return "No recibido en el período"
        p = float(p)
    except Exception:
        return "No recibido en el período"
    if p > 100:
        return "Más del 100%"
    if p >= 80:
        return "Normal (≥ 80%)"
    if p >= 30:
        return "Problemas de disponibilidad (≥ 30%)"
    if p > 0:
        return "Problemas de disponibilidad (< 30%)"
    if p == 0:
        return "No recibido en el período"
    return "No recibido en el período"

def safe_read(path, sheet_name=SHEET_NAME):
    return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")

def input_date_ddmmyyyy(prompt):
    while True:
        s = input(prompt).strip()
        try:
            return datetime.strptime(s, "%d/%m/%Y").date()
        except Exception:
            print("Formato incorrecto. Use dd/mm/YYYY. Intente otra vez.")

# ----- Entradas -----
ruta_prev = clean_input_path(input("Ruta archivo reporte anterior (xlsx): ").strip())
ruta_act = clean_input_path(input("Ruta archivo reporte nuevo (xlsx): ").strip())
print("\n--- FECHA DE REFERENCIA ---")
print("Esta es la fecha de corte o última fecha de los datos a monitorear.")
print("Representa 'hoy' o el momento actual del análisis.")
print("Ejemplo: Si estás analizando datos hasta el 06/11/2025, esa es tu fecha de referencia.\n")
fecha_ref = input_date_ddmmyyyy("Fecha de referencia (dd/mm/YYYY): ")

p_prev = Path(ruta_prev)
p_act = Path(ruta_act)
if not p_prev.exists():
    raise FileNotFoundError(f"No existe archivo anterior: {p_prev.resolve()}")
if not p_act.exists():
    raise FileNotFoundError(f"No existe archivo actual: {p_act.resolve()}")

# ----- Carga -----
df_prev = safe_read(p_prev, SHEET_NAME)
df_act = safe_read(p_act, SHEET_NAME)

# Leer hojas adicionales del reporte nuevo
df_equipamiento = None
df_variable = None

try:
    df_equipamiento = safe_read(p_act, SHEET_EQUIPAMIENTO)
    print(f"✓ Hoja '{SHEET_EQUIPAMIENTO}' cargada ({len(df_equipamiento)} filas)")
except Exception as e:
    print(f"⚠ No se pudo cargar la hoja '{SHEET_EQUIPAMIENTO}': {e}")

try:
    df_variable = safe_read(p_act, SHEET_VARIABLE)
    print(f"✓ Hoja '{SHEET_VARIABLE}' cargada ({len(df_variable)} filas)")
except Exception as e:
    print(f"⚠ No se pudo cargar la hoja '{SHEET_VARIABLE}': {e}")

# Normalizar nombres columnas y asegurar existencia
for df in (df_prev, df_act):
    df.rename(columns=lambda x: x.strip() if isinstance(x, str) else x, inplace=True)

# Columnas esperadas
for c in ["DZ", "Estacion", "disponibilidad", "var_disp"]:
    if c not in df_act.columns:
        df_act[c] = np.nan
    if c not in df_prev.columns:
        df_prev[c] = np.nan

# Columnas extras en prev
for c in ["f_inci", "estado_inci", "comentario"]:
    if c not in df_prev.columns:
        df_prev[c] = pd.NA

# Normalizar tipos y limpiar strings
df_act["DZ"] = df_act["DZ"].astype(pd.Int64Dtype())
df_prev["DZ"] = df_prev["DZ"].astype(pd.Int64Dtype())
df_act["Estacion"] = df_act["Estacion"].astype(str).str.strip()
df_prev["Estacion"] = df_prev["Estacion"].astype(str).str.strip()

# Normalizar fechas en prev
if "f_inci" in df_prev.columns:
    df_prev["f_inci"] = pd.to_datetime(df_prev["f_inci"], errors="coerce").dt.date

# Clasificar var_disp en caso falte o sea inconsistente: preferir disponibilidad numérica si var_disp no está bien
df_act["disponibilidad"] = pd.to_numeric(df_act["disponibilidad"], errors="coerce")
df_prev["disponibilidad"] = pd.to_numeric(df_prev["disponibilidad"], errors="coerce")

df_act["var_disp_cls"] = df_act["disponibilidad"].apply(clasificar_var_disp_num)
df_prev["var_disp_cls"] = df_prev["disponibilidad"].apply(clasificar_var_disp_num)

# Renombrar columnas preparadas para merge
df_act_proc = df_act[["DZ", "Estacion", "disponibilidad", "var_disp_cls"]].rename(
    columns={"disponibilidad": "disponibilidad_act", "var_disp_cls": "var_disp_act"})
df_prev_proc = df_prev[["DZ", "Estacion", "disponibilidad", "var_disp_cls", "f_inci", "estado_inci", "comentario"]].rename(
    columns={"disponibilidad": "disponibilidad_prev", "var_disp_cls": "var_disp_prev"})

# Merge outer por (DZ, Estacion)
merged = pd.merge(df_act_proc, df_prev_proc, how="outer", on=["DZ", "Estacion"], indicator=True)

# Función para determinar estado según reglas finales
def determinar_estado(row, fecha_ref):
    # obtener variables
    var_act = row.get("var_disp_act")
    var_prev = row.get("var_disp_prev")
    estado_prev = row.get("estado_inci")
    f_inci_prev = row.get("f_inci")
    merge_flag = row.get("_merge")

    # Normalizar strings
    if isinstance(var_act, float) and np.isnan(var_act):
        var_act = None
    if isinstance(var_prev, float) and np.isnan(var_prev):
        var_prev = None
    if pd.isna(estado_prev):
        estado_prev = None

    # helpers
    def is_incidence(var):  # var is one of categories
        return var is not None and var != "Normal (≥ 80%)"

    # Caso: solo en previo (no aparece en nuevo)
    if merge_flag == "right_only":
        # conservar estado_prev (si existe), sino mantener como 'Sin incidencia' o 'Inactivo'
        return {
            "estado_inci": estado_prev if estado_prev is not None else "Sin incidencia",
            "f_inci": f_inci_prev,
            "comentario": row.get("comentario")
        }

    # Caso: solo en actual (nueva estación en lista actual)
    if merge_flag == "left_only":
        if var_act is None:
            return {"estado_inci": "Sin incidencia", "f_inci": pd.NaT, "comentario": pd.NA}
        if is_incidence(var_act):
            # si hay incidencia y no estaba antes -> Nueva (analista pone f_inci)
            return {"estado_inci": "Nueva", "f_inci": pd.NaT, "comentario": pd.NA}
        else:
            return {"estado_inci": "Sin incidencia", "f_inci": pd.NaT, "comentario": pd.NA}

    # Caso: en ambos
    # si var_act es None, tratar como 0 (No recibido)
    if var_act is None:
        var_act = "No recibido en el período"

    if not is_incidence(var_act):  # actual Normal
        # si antes tenía incidencia -> Solucionado
        if estado_prev in ("Nueva", "Recurrente"):
            return {"estado_inci": "Solucionado", "f_inci": f_inci_prev, "comentario": row.get("comentario")}
        else:
            # conservar comentario anterior si existe
            return {"estado_inci": "Sin incidencia", "f_inci": pd.NaT, "comentario": row.get("comentario")}

    else:
        # actual tiene incidencia
        if estado_prev in (None, "Sin incidencia"):
            # antes no tenía -> Nueva
            return {"estado_inci": "Nueva", "f_inci": pd.NaT, "comentario": pd.NA}
        if estado_prev in ("Nueva", "Recurrente"):
            # aplicar tolerancia si prev fue Nueva
            if estado_prev == "Nueva":
                if isinstance(f_inci_prev, (datetime, )):
                    f_inci_prev_date = f_inci_prev.date()
                else:
                    f_inci_prev_date = f_inci_prev  # already date or None
                # Verificar si es None o pd.NaT
                if f_inci_prev_date is None or pd.isna(f_inci_prev_date):
                    # no fecha previa: mantener Recurrente (no hay dato para evaluar)
                    return {"estado_inci": "Recurrente", "f_inci": f_inci_prev, "comentario": row.get("comentario")}
                # si han pasado >5 días desde f_inci_prev y sigue con problema -> Recurrente
                if (fecha_ref - f_inci_prev_date) > timedelta(days=5):
                    return {"estado_inci": "Recurrente", "f_inci": f_inci_prev, "comentario": row.get("comentario")}
                else:
                    # aún dentro de tolerancia -> mantener Nueva
                    return {"estado_inci": "Nueva", "f_inci": f_inci_prev, "comentario": row.get("comentario")}
            else:
                # prev era Recurrente -> mantener Recurrente
                return {"estado_inci": "Recurrente", "f_inci": f_inci_prev, "comentario": row.get("comentario")}
        # Otros casos fallback
        return {"estado_inci": "Nueva", "f_inci": pd.NaT, "comentario": pd.NA}

# Aplicar determinación
res_list = []
for _, row in merged.iterrows():
    r = determinar_estado(row, fecha_ref)
    res = {
        "DZ": row.get("DZ"),
        "Estacion": row.get("Estacion"),
        "disponibilidad": row.get("disponibilidad_act") if row.get("_merge") in ("both", "left_only") else 0.0,
        "var_disp": row.get("var_disp_act") if row.get("_merge") in ("both", "left_only") and pd.notna(row.get("var_disp_act")) else row.get("var_disp_prev"),
        "f_inci": r["f_inci"],
        "estado_inci": r["estado_inci"],
        "comentario": r["comentario"],
        "fuente": "ambos" if row.get("_merge")=="both" else ("actual" if row.get("_merge")=="left_only" else "anterior")
    }
    # asegurar var_disp clasificada (si quedó NaN)
    if pd.isna(res["var_disp"]):
        res["var_disp"] = clasificar_var_disp_num(res["disponibilidad"])
    res_list.append(res)

df_final = pd.DataFrame(res_list)

# Normalizar tipos y ordenar
df_final["DZ"] = df_final["DZ"].astype(pd.Int64Dtype())
df_final["Estacion"] = df_final["Estacion"].astype(str).str.strip()
df_final["disponibilidad"] = pd.to_numeric(df_final["disponibilidad"], errors="coerce").fillna(0.0).astype(float)
df_final = df_final.sort_values(by=["DZ", "Estacion"], ascending=[True, True]).reset_index(drop=True)

# Indicadores globales
total_est = len(df_final)
cnt_nueva = int((df_final["estado_inci"] == "Nueva").sum())
cnt_recurrente = int((df_final["estado_inci"] == "Recurrente").sum())
cnt_solucionado = int((df_final["estado_inci"] == "Solucionado").sum())
cnt_sin = int((df_final["estado_inci"] == "Sin incidencia").sum())
cnt_sin_datos = int((df_final["disponibilidad"] == 0).sum())
pct_ge80 = round((df_final["disponibilidad"] >= 80).sum() / max(total_est,1) * 100, 2)

# Indicadores por DZ
agg_dz = df_final.groupby("DZ").agg(
    estaciones=("Estacion", "count"),
    avg_disponibilidad=("disponibilidad", "mean"),
    pct_ge80=("disponibilidad", lambda s: round((s>=80).sum()/max(len(s),1)*100,2)),
    n_nueva=("estado_inci", lambda s: int((s=="Nueva").sum())),
    n_recurrente=("estado_inci", lambda s: int((s=="Recurrente").sum())),
    n_solucionado=("estado_inci", lambda s: int((s=="Solucionado").sum())),
    n_sin=("estado_inci", lambda s: int((s=="Sin incidencia").sum())),
    n_sin_datos=("disponibilidad", lambda s: int((s==0).sum()))
).reset_index()

# Exportar Excel con xlsxwriter y formatos por estado/var_disp
with pd.ExcelWriter(OUTFILE, engine="xlsxwriter", datetime_format="dd/mm/yyyy") as writer:
    # ===== Hoja 1: POR ESTACION (consolidada) =====
    df_final.to_excel(writer, sheet_name="POR ESTACION", index=False)
    workbook  = writer.book
    ws = writer.sheets["POR ESTACION"]

    # Encabezado manual para estética
    header_fmt = workbook.add_format({"bold": True, "align": "center"})
    for col_num, value in enumerate(df_final.columns.values):
        ws.write(0, col_num, value, header_fmt)

    # Formatos por estado_inci
    fmt_nueva = workbook.add_format({"bg_color": "#FFC7CE"})       # rojo claro
    fmt_recurrente = workbook.add_format({"bg_color": "#FFEB9C"})  # amarillo
    fmt_solucionado = workbook.add_format({"bg_color": "#C6EFCE"}) # verde claro
    fmt_sin = workbook.add_format({"bg_color": "#FFFFFF"})         # blanco

    # Aplicar formato condicional sobre columna 'estado_inci' (col index)
    col_idx_estado = list(df_final.columns).index("estado_inci")
    first_row = 2
    last_row = 1 + len(df_final)
    rng = f"{chr(65+col_idx_estado)}{first_row}:{chr(65+col_idx_estado)}{last_row}"
    ws.conditional_format(rng, {"type": "text",
                                "criteria": "containing",
                                "value": "Nueva",
                                "format": fmt_nueva})
    ws.conditional_format(rng, {"type": "text",
                                "criteria": "containing",
                                "value": "Recurrente",
                                "format": fmt_recurrente})
    ws.conditional_format(rng, {"type": "text",
                                "criteria": "containing",
                                "value": "Solucionado",
                                "format": fmt_solucionado})

    # Formato por var_disp (col)
    col_idx_var = list(df_final.columns).index("var_disp")
    rng_var = f"{chr(65+col_idx_var)}{first_row}:{chr(65+col_idx_var)}{last_row}"
    ws.conditional_format(rng_var, {"type": "text", "criteria": "containing", "value": "Más del 100%", "format": fmt_nueva})
    ws.conditional_format(rng_var, {"type": "text", "criteria": "containing", "value": "No recibido en el período", "format": fmt_nueva})
    ws.conditional_format(rng_var, {"type": "text", "criteria": "containing", "value": "Problemas de disponibilidad (< 30%)", "format": fmt_recurrente})
    ws.conditional_format(rng_var, {"type": "text", "criteria": "containing", "value": "Problemas de disponibilidad (≥ 30%)", "format": fmt_recurrente})
    ws.set_column(0, len(df_final.columns)-1, 18)

    # ===== Hoja 2: Indicadores =====
    sheet_ind = "Indicadores"
    agg_dz.to_excel(writer, sheet_name=sheet_ind, index=False, startrow=10)
    ws2 = writer.sheets[sheet_ind]
    # Totales globales
    resumen_tot = pd.DataFrame({
        "indicador": [
            "total_estaciones",
            "num_nueva",
            "num_recurrente",
            "num_solucionado",
            "num_sin_incidencia",
            "num_sin_datos",
            "pct_>=80"
        ],
        "valor": [
            total_est,
            cnt_nueva,
            cnt_recurrente,
            cnt_solucionado,
            cnt_sin,
            cnt_sin_datos,
            pct_ge80
        ]
    })
    resumen_tot.to_excel(writer, sheet_name=sheet_ind, index=False, startrow=0)
    
    # ===== Hoja 3: POR EQUIPAMIENTO (copia del reporte nuevo) =====
    if df_equipamiento is not None:
        df_equipamiento.to_excel(writer, sheet_name=SHEET_EQUIPAMIENTO, index=False)
        ws_equip = writer.sheets[SHEET_EQUIPAMIENTO]
        
        # Aplicar formato de encabezado
        for col_num, value in enumerate(df_equipamiento.columns.values):
            ws_equip.write(0, col_num, value, header_fmt)
        
        # Ajustar ancho de columnas
        ws_equip.set_column(0, len(df_equipamiento.columns)-1, 18)
        
        print(f"✓ Hoja '{SHEET_EQUIPAMIENTO}' agregada al archivo de salida")
    
    # ===== Hoja 4: POR VARIABLE (copia del reporte nuevo) =====
    if df_variable is not None:
        df_variable.to_excel(writer, sheet_name=SHEET_VARIABLE, index=False)
        ws_var = writer.sheets[SHEET_VARIABLE]
        
        # Aplicar formato de encabezado
        for col_num, value in enumerate(df_variable.columns.values):
            ws_var.write(0, col_num, value, header_fmt)
        
        # Ajustar ancho de columnas
        ws_var.set_column(0, len(df_variable.columns)-1, 18)
        
        print(f"✓ Hoja '{SHEET_VARIABLE}' agregada al archivo de salida")

# Salida en consola
print("\n---- Resumen (consolidado) ----")
print(f"Fecha referencia: {fecha_ref.strftime('%d/%m/%Y')}")
print(f"Total estaciones (union): {total_est}")
print(f"Disponibilidad >=80%: {pct_ge80}%")
print(f"Nuevas: {cnt_nueva}")
print(f"Recurrentes: {cnt_recurrente}")
print(f"Solucionadas: {cnt_solucionado}")
print(f"Sin incidencia: {cnt_sin}")
print(f"Sin datos (==0): {cnt_sin_datos}")
print("\nPrimeras filas de indicadores por DZ:")
print(agg_dz.head(20).to_string(index=False))
print(f"\nArchivo generado: {Path(OUTFILE).resolve()}")

# Mostrar resumen de hojas incluidas
print("\n---- Hojas incluidas en el archivo ----")
hojas_generadas = ["POR ESTACION (consolidada)", "Indicadores"]
if df_equipamiento is not None:
    hojas_generadas.append(SHEET_EQUIPAMIENTO)
if df_variable is not None:
    hojas_generadas.append(SHEET_VARIABLE)
for i, hoja in enumerate(hojas_generadas, 1):
    print(f"{i}. {hoja}")


"""
df_consolidado = pd.read_excel("Datos/0711_1311/reporte_disponibilidad_SGR_0711_1311.xlsx", sheet_name="POR ESTACION")
def clasificar(disponibilidad):
    if disponibilidad > 80:
        return "Operativa"
    elif 0 < disponibilidad <= 80:
        return "Parcialmente operativa"
    else:
        return "Inoperativa"

df_consolidado["EO"] = df_consolidado["disponibilidad"].apply(clasificar)
df_consolidado["EO"].value_counts()
"""