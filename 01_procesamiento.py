import pandas as pd
import numpy as np

import os
import re
from datetime import datetime
import locale

from os import getcwd
from os import listdir
from sys import exit
import datetime
import calendar


# -------------------------------------------------------------- #
# ---------------------------- FUNCIONES ----------------------- #
# -------------------------------------------------------------- #


# Diccionario de sensores y variables
s_temp = {
    'observado': ['N_AIRTEMP_INST','N_AIRTEMP','N_AIRTEMP_00M','N_AIRTEMP_10M','N_AIRTEMP_20M','N_AIRTEMP_30M','N_AIRTEMP_40M','N_AIRTEMP_50M','N_AIRTEMP_60M'],
    'calculado': ['N_MAXAT','N_MINAT','N_MAXATH','N_MINATH']
}

s_humre = {
    'observado': ['N_HUMEDAD', 'N_HUMEDAD_INST'],
    'calculado': ['N_MAXRH','N_MINRH','N_MAXRHH','N_MINRHH','N_PTO_ROCIO'],
}

s_prec = {
    'observado': ['N_LLUVIA','N_INT_LLUVIA','N_INT_2_LLUVIA','N_LLUVIA_2','N_RAIN_10M','N_RAIN_2_10M','N_RAIN_00M','N_RAIN_20M','N_RAIN_30M','N_RAIN_40M','N_RAIN_50M'],
    'calculado': ['N_DAYRAIN','N_DAYRAIN_2']
}

s_dir_viento = {
    'observado': ['N_DIRVIENTO','N_DIRVIENTO_INST','N_DIRVIENTO_02M','N_DIRRACHA','N_DIRRACHA_H'],
    'calculado': ['N_MAXDIRVIENTO','N_MAXDIRVIENTO_D','N_MAXDIRVIENTO_H','N_MAXDIRVIENTO_02M','N_DEVSTDH']
}

s_vel_viento = {
    'observado': ['N_VELVIENTO','N_VELVIENTO_INST','N_VELVIENTO_02M', 'N_RACHA', 'N_RACHAH'],
    'calculado': ['N_MAXVELVIENTO','N_MAXVELVIENTO_H','N_MAXVELVIENTO_D','N_MAXVELVIENTO_02M']
}

s_presion = {
    'observado': ['N_PRESATM','N_PRESATM_INST'],
    'calculado': ['N_MAXPRESATMH','N_MINPRESATMH', 'N_MAXPRESATMD','N_MINPRESATMD']
}

s_rad_solar = {
    'observado': ['N_RADSOLAR','N_RADSOLAR_INST','N_RADSOLARHR',],
    'calculado': ['N_RADSOLAR_TOT', 'N_RADSOLAR_TOT_NET', 'N_ENERSOLAR24H', 'N_ENERSOL_ACU1H', 'N_ENERSOLAR1H', 'N_HS101']
}

s_rad_uv = {
    'observado': ['N_IND_UV','N_RAUV_A_INST','N_RAUV_A_PROM','N_RAUV_BE_INST','N_RAUV_BE_PROM'],
    'calculado': []
}

s_nivel = {
    'observado': ['N_NIVELAGUA','N_NIVELMEDIO','N_NIV_INST_10','N_NIV_INST_20','N_NIV_INST_30','N_NIV_INST_40','N_NIV_INST_50','N_NIVEL_INST_H','N_NIVMEDH','N_NIVELAGUA_10M','N_NIV_INST_00','N_NIVEL_INST_RADAR','N_NIVELAGUAH','N_VEL_AGUA_10M'],
    'calculado': ['N_MAXNIVEL','N_MINNIVEL','N_MAXNIVELH','N_MINNIVELH']
}

s_humhoja = {
    'observado': ['N_HOJAHUMED'],
    'calculado': []
}

s_humsuelo = {
    'observado': ['N_SUELOHUMED'],
    'calculado': []
}

s_temsuelo = {
    'observado': ['N_SOILTEMP','N_SOILTEMP_INST']
}

s_radiometrico = {
    'observado': ['N_RS003','N_RS004','N_RS005','N_RS006','N_RS007','N_RS008','N_RS009','N_RS010','N_RS011','N_RS012','N_RS013','N_TM014'],
    'calculado': []
}

s_nieve = {
    'observado': ['N_PT003','N_PT004','N_PT005','N_PT006'],
    'calculado': []
}

s_evapo = {
    'observado': ['N_EVAPO_HORARIA','N_EVAPO_INST_H'],
    'calculado': ['N_MAXEVAPOH','N_MINEVAPOH']
}

s_cal_agua = {
    'observado': ['N_COND','N_OXIGENO','N_PHH','N_TURBH','N_WTEMP','N_COND_INST'],
    'calculado': []
}

s_temp_ifr = {
    'observado': ['N_TEMP_IR_SUPERF_HIELO','N_TEMP_NETRAD_K','N_TEMP_TERMIS_SENSOR_IR'],
    'calculado': ['N_TEMP_IR_SUPERF_HIELO_MAX','N_TEMP_IR_SUPERF_HIELO_MIN']
}

s_ref_sue = {
    'observado': ['N_VOLAG_INST_H','N_VOLAG_PROM']
}

s_caudal = {
    'observado': ['N_CAUDAL', 'N_CAUDAL_10M'],
    'calculado': ['N_CAUDAL_D', 'N_CAUDAL_MAX_D', 'N_CAUDAL_MIN_D']
}


sensores = {
    's_temp': s_temp,
    's_humre': s_humre,
    's_prec': s_prec,
    's_dir_viento': s_dir_viento,
    's_vel_viento': s_vel_viento,
    's_presion': s_presion,
    's_rad_solar': s_rad_solar,
    's_rad_uv': s_rad_uv,
    's_nivel': s_nivel,
    's_humhoja': s_humhoja,
    's_humsuelo': s_humsuelo,
    's_temsuelo': s_temsuelo,
    's_radiometrico': s_radiometrico,
    's_nieve': s_nieve,
    's_evapo': s_evapo,
    's_cal_agua': s_cal_agua,
    's_temp_ifr': s_temp_ifr,
    's_ref_sue': s_ref_sue,
    's_caudal': s_caudal

}

# Función para clasificar cada variable
def clasificar_variable(variable):
    for sensor, tipos in sensores.items():
        for tipo, lista_variables in tipos.items():
            if variable in lista_variables:
                return sensor, tipo
    return None, None  # Si no se encuentra en ningún diccionario

# Función para calculo de los datos esperados
def calcular_esperado(frecuencia):
    return {
        'minuto': 6*24*nro_dias,
        'horario': 24*nro_dias,
        # 'horario*2': 2*24*nro_dias,
        'diario': nro_dias,
        # 'diario*2': 2*nro_dias
    }.get(frecuencia, np.nan)

# Función para clasificar la estación en base a su disponibilidad
def clasificar_disponibilidad(disponibilidad):
    """
    Clasifica una estación según su porcentaje de disponibilidad.

    Parámetros:
    - disponibilidad: float o None, porcentaje de disponibilidad (0 a 100+)

    Retorna:
    - str, categoría de disponibilidad
    """
    if disponibilidad is None or disponibilidad == 0:
        return 'No recibido en el período'
    elif disponibilidad > 100:
        return 'Más del 100%'
    elif disponibilidad >= 80:
        return 'Normal (≥ 80%)'
    elif disponibilidad >= 30:
        return 'Problemas de disponibilidad (≥ 30%)'
    else:
        return 'Problemas de disponibilidad (< 30%)'
    
# -------------------------------------------------------------- #
# ------------------- PROCESAMIENTO INICIAL -------------------- #
# -------------------------------------------------------------- #
archivos = os.listdir()
archivos_disponibilidad = [
    archivo for archivo in archivos 
    if archivo.startswith('disponibilidad_') and archivo.endswith('.csv')
]

# Apertura del archivo de disponibilidad
reporte_sgr = pd.read_csv(archivos_disponibilidad[0])
# Quitamos los parametros operacionales
parametros_operacionales = ["N_BATERIA", "N_TEMP_INT_TRANS"]
reporte_sgr = reporte_sgr[~reporte_sgr["Variable"].isin(parametros_operacionales)]
# Escogemos las columnas objetivo
reporte_sgr = reporte_sgr[['DZ', 'Estacion', 'Variable', 'Datos_flag_C', 'Datos_flag_M', 'Datos_flag_SD']]
# Apertura del archivo de frecuencias correctas
var_frecuencia = pd.read_excel('variables_frecuencia.xlsx', sheet_name='frecuencias')

# Unir df1 con df2 usando merge, en las columnas comunes
reporte_correcto = reporte_sgr.merge(
    var_frecuencia[['DZ', 'Estacion', 'Variable', 'Frecuencia']],
    on=['DZ', 'Estacion', 'Variable'],
    how='left'
)

# Seteo del número de días a analizar
nro_dias = 7

# Calculo de los datos esperados en base a la frecuencia de medición
reporte_correcto['Datos_esperados'] = reporte_correcto['Frecuencia'].apply(lambda f: calcular_esperado(f))
# Se quita una unidad ya que se contabiliza un dato más debido a que la selección inicia con una dato
# (00 horas) que no corresponde al periodo seleccionado, debe de comenzar en la hora 1 del día y no 0
reporte_correcto['Datos_flag_C'] = reporte_correcto['Datos_flag_C'].apply(
    lambda x: x - 1 if x > 1 else x
)

# -------------------------------------------------------------- #
# DISPONIBILIDAD POR VARIABLE
# Calculo de la disponibilidad de datos por variable
disponibilidad_variable = reporte_correcto.copy()
disponibilidad_variable['disponibilidad'] = round((disponibilidad_variable['Datos_flag_C'] / disponibilidad_variable['Datos_esperados']) * 100, 2)
disponibilidad_variable["var_disp"] = disponibilidad_variable["disponibilidad"].apply(clasificar_disponibilidad)
disponibilidad_variable = disponibilidad_variable[['DZ', 'Estacion', 'Variable', 'Frecuencia', 'Datos_flag_C', 
                                                   'Datos_flag_M', 'Datos_flag_SD', 'Datos_esperados', 'disponibilidad', 'var_disp']]
disponibilidad_variable[['Sensor', 'Tipo']] = disponibilidad_variable['Variable'].apply(
    lambda v: pd.Series(clasificar_variable(v))
)
disponibilidad_variable.drop('Tipo', axis=1, inplace=True)
disponibilidad_variable.sort_values(by = ["DZ", "Estacion", "Sensor", "Variable"], ascending=True, inplace=True)
disponibilidad_variable = disponibilidad_variable[['DZ', 'Estacion', 'Sensor', 'Variable', 'Frecuencia', 'Datos_flag_C',
                                                   'Datos_flag_M', 'Datos_flag_SD', 'Datos_esperados', 'disponibilidad', 'var_disp']]

# -------------------------------------------------------------- #
# DISPONIBILIDAD POR EQUIPAMIENTO
# Aplicar la función a la columna 'Variable'
disp_variable = disponibilidad_variable[['DZ', 'Estacion', 'Variable', 'disponibilidad']].copy()
disp_variable[['Sensor', 'Tipo']] = disp_variable['Variable'].apply(
    lambda v: pd.Series(clasificar_variable(v))
)
# Calculo de la disponibilidad por equipamiento
disponibilidad_equipamiento = disp_variable.groupby(["DZ", "Estacion", "Sensor"]).agg({
    'disponibilidad': 'mean'
}).reset_index()
disponibilidad_equipamiento["var_disp"] = disponibilidad_equipamiento["disponibilidad"].apply(clasificar_disponibilidad)

# -------------------------------------------------------------- #
# DISPONIBILIDAD POR ESTACION
# Calculo de la disponibilidad por estación
disponibilidad_estacion = disp_variable.groupby(["DZ", "Estacion"]).agg({
    'disponibilidad': lambda x: round(x.mean(), 2)
}).reset_index()
disponibilidad_estacion["var_disp"] = disponibilidad_estacion["disponibilidad"].apply(clasificar_disponibilidad)




# ALERTAS POR DISPONIBILIDAD DE ESTACION
# Paso 1: Clasificar la disponibilidad (ya tienes tu función clasificar_disponibilidad)
disponibilidad_estacion["var_disp"] = disponibilidad_estacion["disponibilidad"].apply(clasificar_disponibilidad)
# Paso 2: Agrupar y contar por categoría de disponibilidad
conteo_por_categoria = disponibilidad_estacion.groupby("var_disp").size().reset_index(name='Conteo')
print(conteo_por_categoria)

# Paso 3: Alertar las estaciones según categoría de disponibilidad
# Alerta para "Problemas de disponibilidad (≥ 30%)"
media_disponibilidad = disponibilidad_estacion[disponibilidad_estacion["var_disp"] == "Problemas de disponibilidad (≥ 30%)"]
if not media_disponibilidad.empty:
    print("\n🚨 Estaciones con PROBLEMAS DE DISPONIBILIDAD (≥ 30%):")
    for idx, row in media_disponibilidad.iterrows():
        print(f" - DZ: {row['DZ']} | Estación: {row['Estacion']} ({row['disponibilidad']}%)")
else:
    print("\n✅ No hay estaciones con problemas de disponibilidad (≥ 30%).")

# Alerta para "Problemas de disponibilidad (< 30%)"
baja_disponibilidad = disponibilidad_estacion[disponibilidad_estacion["var_disp"] == "Problemas de disponibilidad (< 30%)"]
if not baja_disponibilidad.empty:
    print("\n🚨 Estaciones con PROBLEMAS DE DISPONIBILIDAD (< 30%):")
    for idx, row in baja_disponibilidad.iterrows():
        print(f" - DZ: {row['DZ']} | Estación: {row['Estacion']} ({row['disponibilidad']}%)")
else:
    print("\n✅ No hay estaciones con problemas de disponibilidad (< 30%).")

# Alerta para "No recibido en el período"
sin_disponibilidad = disponibilidad_estacion[disponibilidad_estacion["var_disp"] == "No recibido en el período"]
if not sin_disponibilidad.empty:
    print("\n🚨 Estaciones SIN DISPONIBILIDAD en el período:")
    for idx, row in sin_disponibilidad.iterrows():
        print(f" - DZ: {row['DZ']} | Estación: {row['Estacion']} ({row['disponibilidad']}%)")
else:
    print("\n✅ No hay estaciones sin disponibilidad en el período.")


# si no se cuenta con el paquete
# pip install xlsxwriter
# Extraemos los datos de las fechas del nombre del archivo
nombre_file = archivos_disponibilidad[0]
partes = nombre_file.replace('.csv', '').split('_')
# Tomar los últimos dos elementos y unirlos con "_"
rango_fechas = '_'.join(partes[-2:])
# Creación del nombre de archivo
archivo_salida = f"reporte_disponibilidad_{rango_fechas}.xlsx"

# Crear un archivo Excel con múltiples hojas
with pd.ExcelWriter(archivo_salida, engine='xlsxwriter') as writer:
    disponibilidad_estacion.to_excel(writer, sheet_name='POR ESTACION', index=False)
    disponibilidad_equipamiento.to_excel(writer, sheet_name='POR EQUIPAMIENTO', index=False)
    disponibilidad_variable.to_excel(writer, sheet_name='POR VARIABLE', index=False)


"""
# Número de estaciones
df_limpio = reporte_sgr.drop_duplicates(subset=["DZ", "Estacion"])
conteo_estaciones = df_limpio.groupby("DZ")["Estacion"].nunique().reset_index(name="Conteo")
nro_estaciones = conteo_estaciones["Conteo"].sum()
print(f'La cantidad de estaciones dentro del archivo son:')
print(nro_estaciones)
print('El detalles por DZ es el siguiente')
print(conteo_estaciones)
"""


"""
# Constantes
columnas_obj = ['DZ', 'Estacion', 'Variable', 'Datos_flag_C', 'Datos_esperados', 'Operatividad', 'Sensor', 'Tipo']

def inferir_frecuencia_por_datos(c, m, esperado_hora, esperado_diario):
    total = c + m
    if total > esperado_hora:
        return 'minuto'
    elif total > esperado_diario:
        return 'hora'
    else:
        return 'diario'

def calcular_esperado(frecuencia, esperado_minuto, esperado_hora, esperado_diario):
    return {
        'minuto': esperado_minuto,
        'hora': esperado_hora,
        'diario': esperado_diario
    }.get(frecuencia, np.nan)


# Cetear el número de días del análisis
nro_dias = 7
esperado_minuto = 12 * 24 * nro_dias
esperado_hora = 24 * nro_dias
esperado_diario = nro_dias

reporte_sgr['Datos_flag_C'] = pd.to_numeric(reporte_sgr['Datos_flag_C'], errors='coerce')
reporte_sgr['Datos_flag_M'] = pd.to_numeric(reporte_sgr['Datos_flag_M'], errors='coerce')
reporte_sgr['Frecuencia'] = reporte_sgr.apply(
    lambda row: inferir_frecuencia_por_datos(row['Datos_flag_C'], row['Datos_flag_M'], 
                                             esperado_hora, esperado_diario),
                                             axis=1
)
reporte_sgr['Datos_esperados_cogd'] = reporte_sgr['Frecuencia'].apply(
        lambda f: calcular_esperado(f, esperado_minuto, esperado_hora, esperado_diario)
)
reporte_sgr['Operatividad_cogd'] = round(
        (reporte_sgr['Datos_flag_C'] / reporte_sgr['Datos_esperados_cogd']) * 100, 2
)
reporte_sgr["diff_op"] = reporte_sgr['Operatividad'] - reporte_sgr['Operatividad_cogd']


ab = reporte_sgr[['DZ', 'Estacion', 'Variable', 'Operatividad', 'Frecuencia', 'Operatividad_cogd', 'diff_op']]
ab.to_excel('estaciones_variables.xlsx', index=False)

# --- Lógica principal ---
incongruencias = reporte_sgr[reporte_sgr["Operatividad"] > 100].copy()

if not incongruencias.empty:
    esperado_hora = 24 * nro_dias
    esperado_diario = nro_dias

    # Asegurar numéricos
    incongruencias['Datos_flag_C'] = pd.to_numeric(incongruencias['Datos_flag_C'], errors='coerce')
    incongruencias['Datos_flag_M'] = pd.to_numeric(incongruencias['Datos_flag_M'], errors='coerce')

    # Inferir frecuencia
    incongruencias['Frecuencia'] = incongruencias.apply(
        lambda row: inferir_frecuencia_por_datos(row['Datos_flag_C'], row['Datos_flag_M'], 
                                                 esperado_hora, esperado_diario),
        axis=1
    )

    # Calcular esperados y operatividad corregida
    incongruencias['Datos_esperados_cogd'] = incongruencias['Frecuencia'].apply(
        lambda f: calcular_esperado(f, esperado_hora, esperado_diario)
    )
    incongruencias['Operatividad_cogd'] = round(
        (incongruencias['Datos_flag_C'] / incongruencias['Datos_esperados_cogd']) * 100, 2
    )

    # Subset final
    resultado_prueba = incongruencias[columnas_obj].copy()
    resultado_prueba['Etiqueta'] = 'corregido'

    # Restantes sin modificar
    sin_cambios = reporte_sgr[~(reporte_sgr["Operatividad"] > 100)].copy()
    sin_cambios = sin_cambios[columnas_obj]
    sin_cambios['Etiqueta'] = None

    # Combinar
    resultado_final = pd.concat([sin_cambios, resultado_prueba], ignore_index=True)
    resultado_final.sort_values(by=["DZ", "Estacion"], ascending=True, inplace=True)
    print("✅ Impresión del resultado con modificaciones.")

else:
    resultado_final = reporte_sgr[columnas_obj].copy()
    resultado_final['Etiqueta'] = None
    print("✅ Impresión del resultado sin modificaciones.")


"""
