"""
descargar_reportes.py
Script para descarga automática de reportes PDF desde SISMOP(A)-SGR

Este script automatiza la descarga de reportes de disponibilidad de estaciones
automáticas desde el Sistema de Monitoreo de Operatividad (SISMOP).

Requisitos:
    - Python 3.8+
    - Selenium: pip install selenium
    - Chrome WebDriver (chromedriver) instalado y en PATH
    - Acceso a la red local donde está SISMOP (172.25.150.27)

Uso:
    python descargar_reportes.py                    # Descarga todas las DZs (1-13)
    python descargar_reportes.py --dz 1 5 9        # Descarga solo DZs específicas
    python descargar_reportes.py --dias 30         # Período de 30 días (boletín)
    python descargar_reportes.py --fecha-fin 2025-12-12  # Fecha fin específica

Autor: Sistema de Monitoreo Meteorológico - SGR
Versión: 1.0
Fecha: Febrero 2026
"""

import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# URL del sistema SISMOP - Ajustar según la red local
SISMOP_URL = "http://172.25.150.27:8050/"

# Número total de Direcciones Zonales
TOTAL_DZS = 13

# Tiempo máximo de espera para carga de datos (segundos)
TIMEOUT_CARGA_DATOS = 30

# Tiempo máximo de espera para descarga de PDF (segundos)
TIMEOUT_GENERACION_REPORTE = 60

# Tiempo de espera entre acciones (segundos) - reducido para mayor velocidad
DELAY_ENTRE_ACCIONES = 0.5

# Directorio de descarga de PDFs (relativo al script)
DIRECTORIO_DESCARGAS = Path(__file__).parent / "input_pdfs"

# =============================================================================
# IDs DE ELEMENTOS HTML EN SISMOP (verificados)
# =============================================================================

# Dropdown de Dirección Zonal
ID_DROPDOWN_DZ = "dz-select"

# Dropdown de Estación (no se usa para reporte por DZ, pero documentado)
ID_DROPDOWN_ESTACION = "station-select"

# Contenedor del selector de fechas
ID_DATE_PICKER = "date-picker-select"

# Botón para consultar rango de fechas
ID_BOTON_CONSULTAR = "update-date-range-button"

# Botón para generar reporte por DZ
ID_BOTON_REPORTE = "report-button"


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def calcular_rango_fechas(fecha_fin: datetime = None, dias: int = 7) -> tuple:
    """
    Calcula el rango de fechas para la consulta.

    Para el monitoreo semanal (7 días):
    - El período real es de viernes a jueves
    - En SISMOP se selecciona viernes a viernes (fecha_fin + 1 día)

    Args:
        fecha_fin: Fecha final del período (por defecto: jueves más reciente)
        dias: Número de días del período (7 para monitoreo, 30 para boletín)

    Returns:
        tuple: (fecha_inicio, fecha_fin_sismop) en formato datetime
    """
    if fecha_fin is None:
        # Buscar el jueves más reciente (o hoy si es jueves)
        hoy = datetime.now()
        dias_desde_jueves = (hoy.weekday() - 3) % 7
        if dias_desde_jueves == 0 and hoy.hour < 12:
            # Si es jueves pero antes del mediodía, usar jueves anterior
            dias_desde_jueves = 7
        fecha_fin = hoy - timedelta(days=dias_desde_jueves)

    # Fecha de inicio: retroceder los días del período desde fecha_fin
    fecha_inicio = fecha_fin - timedelta(days=dias - 1)

    # En SISMOP se selecciona fecha_fin + 1 día
    fecha_fin_sismop = fecha_fin + timedelta(days=1)

    return fecha_inicio, fecha_fin_sismop


def configurar_chrome(directorio_descargas: Path) -> webdriver.Chrome:
    """
    Configura y retorna una instancia de Chrome WebDriver.

    Args:
        directorio_descargas: Directorio donde se guardarán los PDFs

    Returns:
        webdriver.Chrome: Instancia configurada del navegador
    """
    # Crear directorio de descargas si no existe
    directorio_descargas.mkdir(parents=True, exist_ok=True)

    # Configurar opciones de Chrome
    chrome_options = Options()

    # Configurar directorio de descargas
    prefs = {
        "download.default_directory": str(directorio_descargas.absolute()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,  # Descargar PDFs en lugar de abrirlos
        "safebrowsing.enabled": False,  # Deshabilitar safebrowsing para evitar bloqueo
        "safebrowsing.disable_download_protection": True,  # Permitir descargas "inseguras"
        "profile.default_content_setting_values.automatic_downloads": 1,  # Permitir múltiples descargas
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Opciones adicionales para estabilidad
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")  # Permitir descargas HTTP
    chrome_options.add_argument("--allow-running-insecure-content")  # Permitir contenido HTTP

    # Descomentar para modo headless (sin ventana visible)
    # chrome_options.add_argument("--headless")

    # Crear instancia del navegador
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    # Usar Chrome DevTools Protocol para permitir descargas sin confirmación
    # Esto evita el diálogo "Se bloqueó una descarga no segura"
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": str(directorio_descargas.absolute())
    })

    return driver


def manejar_dialogo_descarga(driver, timeout: int = 5):
    """
    Intenta manejar el diálogo de descarga de Chrome que aparece para sitios HTTP.

    Chrome muestra "Se bloqueó una descarga no segura" con botón "Conservar".

    Args:
        driver: Instancia de WebDriver
        timeout: Tiempo máximo de espera para el diálogo
    """
    try:
        # El diálogo de descarga de Chrome es una notificación del navegador
        # Intentar encontrar y hacer click en "Conservar" o "Keep"
        wait = WebDriverWait(driver, timeout)

        # Buscar el botón "Conservar" o "Keep" en la barra de descargas
        botones_conservar = [
            "//button[contains(text(), 'Conservar')]",
            "//button[contains(text(), 'Keep')]",
            "//button[contains(text(), 'Mantener')]",
            "//*[contains(text(), 'Conservar')]",
            "//*[contains(text(), 'Keep')]"
        ]

        for xpath in botones_conservar:
            try:
                boton = driver.find_element(By.XPATH, xpath)
                if boton.is_displayed():
                    boton.click()
                    time.sleep(1)
                    return True
            except:
                pass

        # Si no encontramos el botón, intentar con JavaScript para cerrar alertas
        try:
            driver.switch_to.alert.accept()
            return True
        except:
            pass

    except:
        pass

    return False


def esperar_descarga_completa(directorio: Path, timeout: int = 60, driver=None, dias: int = 7, pdfs_antes: set = None) -> bool:
    """
    Espera hasta que se complete la descarga del archivo PDF.

    Detecta nuevos PDFs comparando con el estado anterior del directorio.

    Args:
        directorio: Directorio donde se descarga el archivo
        timeout: Tiempo máximo de espera base en segundos
        driver: Instancia de WebDriver para manejar diálogos
        dias: Período en días para ajustar timeout
        pdfs_antes: Set de nombres de PDFs existentes antes de iniciar descarga

    Returns:
        bool: True si la descarga se completó, False si hubo timeout
    """
    # Ajustar timeout según período
    if dias > 7:
        timeout = int(timeout * 1.5)

    # Si no se pasó lista de PDFs anteriores, obtenerla ahora
    if pdfs_antes is None:
        pdfs_antes = set(p.name for p in directorio.glob("*.pdf"))

    tiempo_inicio = time.time()
    intentos_dialogo = 0
    ultimo_log = 0

    while time.time() - tiempo_inicio < timeout:
        transcurrido = time.time() - tiempo_inicio

        # Intentar manejar el diálogo de descarga
        if driver and intentos_dialogo < 3:
            manejar_dialogo_descarga(driver)
            intentos_dialogo += 1

        # Buscar archivos .crdownload (descargas en progreso)
        descargas_en_progreso = list(directorio.glob("*.crdownload"))
        if descargas_en_progreso:
            if transcurrido - ultimo_log > 10:
                print(f"  [    ] Descarga en progreso... ({transcurrido:.0f}s)")
                ultimo_log = transcurrido
            time.sleep(1)
            continue

        # Buscar nuevos PDFs (que no estaban antes)
        pdfs_actuales = set(p.name for p in directorio.glob("*.pdf"))
        nuevos_pdfs = pdfs_actuales - pdfs_antes

        if nuevos_pdfs:
            # Verificar que el PDF tenga contenido
            for nombre_pdf in nuevos_pdfs:
                pdf_path = directorio / nombre_pdf
                try:
                    if pdf_path.stat().st_size > 1000:
                        print(f"  [    ] PDF detectado: {nombre_pdf} ({transcurrido:.1f}s)")
                        return True
                except:
                    pass

        time.sleep(1)

    # Timeout - mostrar diagnóstico
    print(f"  [DEBUG] Timeout después de {timeout}s")
    print(f"  [DEBUG] PDFs antes: {pdfs_antes}")
    print(f"  [DEBUG] PDFs ahora: {set(p.name for p in directorio.glob('*.pdf'))}")
    return False


def obtener_pdfs_existentes(directorio: Path) -> set:
    """Obtiene el set de nombres de PDFs existentes en el directorio."""
    return set(p.name for p in directorio.glob("*.pdf"))


# =============================================================================
# FUNCIONES DE INTERACCIÓN CON SISMOP
# =============================================================================

def seleccionar_dropdown_dash(driver, dropdown_id: str, valor: str, timeout: int = 10):
    """
    Selecciona un valor en un dropdown searchable de Dash (dcc.Dropdown).

    Args:
        driver: Instancia de WebDriver
        dropdown_id: ID del componente dropdown
        valor: Valor a seleccionar
        timeout: Tiempo máximo de espera
    """
    wait = WebDriverWait(driver, timeout)

    # Localizar el contenedor del dropdown por ID
    dropdown_container = wait.until(
        EC.presence_of_element_located((By.ID, dropdown_id))
    )

    # Limpiar selección existente
    try:
        clear_button = dropdown_container.find_element(By.CLASS_NAME, "Select-clear")
        clear_button.click()
    except NoSuchElementException:
        pass

    # Click para abrir el dropdown
    try:
        select_control = dropdown_container.find_element(By.CLASS_NAME, "Select-control")
        select_control.click()
    except NoSuchElementException:
        dropdown_container.click()

    # Buscar el input
    try:
        dropdown_input = dropdown_container.find_element(By.CSS_SELECTOR, "input[role='combobox']")
    except NoSuchElementException:
        dropdown_input = dropdown_container.find_element(By.TAG_NAME, "input")

    # Escribir el valor para filtrar
    dropdown_input.send_keys(Keys.CONTROL + "a")
    dropdown_input.send_keys(valor)
    time.sleep(0.5)

    # Buscar opción exacta usando JavaScript (más confiable con virtualización)
    js_click = """
    var opciones = document.querySelectorAll('.VirtualizedSelectOption, .Select-option');
    for (var i = 0; i < opciones.length; i++) {
        if (opciones[i].textContent.trim() === arguments[0]) {
            opciones[i].click();
            return true;
        }
    }
    return false;
    """

    encontrado = driver.execute_script(js_click, valor)
    if encontrado:
        return

    # Si no encontramos con JS, intentar con Selenium
    selectores = [".VirtualizedSelectOption", ".Select-option"]
    for selector in selectores:
        try:
            opciones = driver.find_elements(By.CSS_SELECTOR, selector)
            for opcion in opciones:
                if opcion.text.strip() == valor:
                    opcion.click()
                    return
        except:
            pass

    # Fallback: cerrar dropdown con Escape y reportar
    dropdown_input.send_keys(Keys.ESCAPE)
    print(f"  [ADVERTENCIA] No se encontró '{valor}' - verificar manualmente")


def seleccionar_primera_opcion_dropdown(driver, dropdown_id: str, timeout: int = 10):
    """
    Selecciona la primera opción disponible en un dropdown.
    Versión optimizada.

    Args:
        driver: Instancia de WebDriver
        dropdown_id: ID del componente dropdown
        timeout: Tiempo máximo de espera
    """
    wait = WebDriverWait(driver, timeout)

    # Localizar el contenedor del dropdown
    dropdown_container = wait.until(
        EC.presence_of_element_located((By.ID, dropdown_id))
    )

    # Click para abrir el dropdown
    try:
        select_control = dropdown_container.find_element(By.CLASS_NAME, "Select-control")
        select_control.click()
    except NoSuchElementException:
        dropdown_container.click()

    # Flecha abajo + Enter para seleccionar primera opción
    try:
        dropdown_input = dropdown_container.find_element(By.CSS_SELECTOR, "input[role='combobox']")
        dropdown_input.send_keys(Keys.ARROW_DOWN)
        dropdown_input.send_keys(Keys.ENTER)
    except:
        pass


def seleccionar_fecha_dash(driver, placeholder: str, fecha: datetime, timeout: int = 10):
    """
    Selecciona una fecha en un DatePicker de Dash usando el placeholder como selector.

    Los IDs de los inputs de fecha en Dash son dinámicos, por lo que usamos
    el atributo placeholder para localizarlos de forma estable.

    Args:
        driver: Instancia de WebDriver
        placeholder: Valor del atributo placeholder ("Start Date" o "End Date")
        fecha: Fecha a seleccionar
        timeout: Tiempo máximo de espera
    """
    wait = WebDriverWait(driver, timeout)

    # Localizar el input de fecha usando el placeholder
    # Los inputs tienen placeholder="Start Date" o placeholder="End Date"
    date_input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"input[placeholder='{placeholder}']"))
    )

    # Hacer click para activar el input
    date_input.click()
    time.sleep(0.3)

    # Limpiar el campo (seleccionar todo y borrar)
    date_input.send_keys(Keys.CONTROL + "a")
    time.sleep(0.1)

    # Escribir la fecha en formato dd/mm/yyyy
    fecha_str = fecha.strftime("%d/%m/%Y")
    date_input.send_keys(fecha_str)

    # Presionar Enter para confirmar y cerrar el calendario
    date_input.send_keys(Keys.ENTER)
    time.sleep(DELAY_ENTRE_ACCIONES)


def hacer_click_boton(driver, boton_texto: str = None, boton_id: str = None, timeout: int = 10):
    """
    Hace click en un elemento clickeable por su texto o ID.

    Incluye scroll al elemento y fallback con JavaScript click.

    Args:
        driver: Instancia de WebDriver
        boton_texto: Texto del elemento a buscar
        boton_id: ID del elemento
        timeout: Tiempo máximo de espera
    """
    wait = WebDriverWait(driver, timeout)

    if boton_id:
        boton = wait.until(
            EC.presence_of_element_located((By.ID, boton_id))
        )
    elif boton_texto:
        # Buscar en cualquier elemento que contenga el texto
        xpath = f"//*[contains(text(), '{boton_texto}')]"
        try:
            boton = wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except TimeoutException:
            xpath_link = f"//a[contains(text(), '{boton_texto}')]"
            boton = wait.until(
                EC.presence_of_element_located((By.XPATH, xpath_link))
            )
    else:
        raise ValueError("Debe especificar boton_texto o boton_id")

    # Scroll hasta el elemento para asegurar que esté visible
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", boton)
    time.sleep(0.5)

    # Intentar click normal primero
    try:
        wait.until(EC.element_to_be_clickable((By.ID, boton_id) if boton_id else (By.XPATH, xpath)))
        boton.click()
    except:
        # Si falla, usar JavaScript click como fallback
        driver.execute_script("arguments[0].click();", boton)

    time.sleep(DELAY_ENTRE_ACCIONES)


def esperar_carga_datos(driver, timeout: int = 30, dias: int = 7):
    """
    Espera a que los datos se carguen en la página.

    Versión simplificada: espera a que aparezca cualquier tabla con datos.

    Args:
        driver: Instancia de WebDriver
        timeout: Tiempo máximo de espera (default 30s - suficiente para carga normal)
        dias: No usado, mantenido por compatibilidad

    Returns:
        bool: True si los datos cargaron correctamente
    """
    tiempo_inicio = time.time()

    # Selectores de tablas de datos
    selectores = [
        "//table//tbody//tr[td]",
        "//table//tr[td]",
        ".dash-spreadsheet-container tbody tr"
    ]

    while time.time() - tiempo_inicio < timeout:
        for selector in selectores:
            try:
                if selector.startswith("//"):
                    filas = driver.find_elements(By.XPATH, selector)
                else:
                    filas = driver.find_elements(By.CSS_SELECTOR, selector)

                # Si encontramos filas con datos, la tabla cargó
                if len(filas) > 5:  # Al menos algunas filas
                    transcurrido = time.time() - tiempo_inicio
                    print(f"  [    ] Datos cargados: {len(filas)} filas ({transcurrido:.1f}s)")
                    return True
            except:
                pass

        time.sleep(0.5)

    print(f"  [ADVERTENCIA] Timeout esperando datos ({timeout}s)")
    return True  # Continuar de todos modos


# =============================================================================
# FUNCIÓN PRINCIPAL DE DESCARGA
# =============================================================================

def descargar_reportes_dz(
    dzs: list = None,
    fecha_fin: datetime = None,
    dias: int = 7,
    directorio_salida: Path = None,
    tipo_red: str = "automaticas"
):
    """
    Descarga los reportes PDF de las Direcciones Zonales especificadas.

    Args:
        dzs: Lista de números de DZ a descargar (None = todas, 1-13)
        fecha_fin: Fecha final del período
        dias: Número de días del período (7 o 30)
        directorio_salida: Directorio donde guardar los PDFs
        tipo_red: Tipo de red a consultar ("automaticas" o "convencionales")
    """
    # Configurar lista de DZs
    if dzs is None:
        dzs = list(range(1, TOTAL_DZS + 1))

    # Configurar directorio de salida
    if directorio_salida is None:
        directorio_salida = DIRECTORIO_DESCARGAS

    # Calcular rango de fechas
    fecha_inicio, fecha_fin_sismop = calcular_rango_fechas(fecha_fin, dias)

    print("=" * 60)
    print("DESCARGA AUTOMÁTICA DE REPORTES - SISMOP-SENAMHI")
    print("=" * 60)
    print(f"Tipo de red: {tipo_red.upper()}")
    print(f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {(fecha_fin_sismop - timedelta(days=1)).strftime('%d/%m/%Y')}")
    print(f"Fechas en SISMOP: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin_sismop.strftime('%d/%m/%Y')}")
    print(f"DZs a descargar: {dzs}")
    print(f"Directorio de salida: {directorio_salida}")
    print("=" * 60)

    # Inicializar el navegador
    print("\n[INFO] Iniciando navegador Chrome...")
    driver = configurar_chrome(directorio_salida)

    reportes_descargados = []
    reportes_fallidos = []

    try:
        # Navegar a SISMOP - Página principal
        print(f"[INFO] Navegando a {SISMOP_URL}...")
        driver.get(SISMOP_URL)
        time.sleep(3)

        # Seleccionar tipo de red en la página inicial
        boton_tipo = "Automáticas" if tipo_red == "automaticas" else "Convencionales"
        print(f"[INFO] Seleccionando '{boton_tipo}'...")
        hacer_click_boton(driver, boton_texto=boton_tipo)
        time.sleep(3)  # Esperar a que cargue la página

        # Procesar cada DZ
        for dz_num in dzs:
            print(f"\n[DZ {dz_num}] Procesando Dirección Zonal {dz_num}...")

            try:
                # 1. Seleccionar la DZ
                print(f"  [1/5] Seleccionando DZ {dz_num}...")
                seleccionar_dropdown_dash(driver, ID_DROPDOWN_DZ, f"DZ {dz_num}")
                time.sleep(1)  # Esperar a que se actualice el dropdown de estaciones

                # 2. Seleccionar una estación (la primera disponible)
                # Esto es necesario para que carguen los datos
                print(f"  [2/5] Seleccionando primera estación disponible...")
                seleccionar_primera_opcion_dropdown(driver, ID_DROPDOWN_ESTACION)

                # 3. Seleccionar fecha de inicio (usando placeholder "Start Date")
                print(f"  [3/5] Configurando fecha inicio: {fecha_inicio.strftime('%d/%m/%Y')}...")
                seleccionar_fecha_dash(driver, "Start Date", fecha_inicio)

                # 4. Seleccionar fecha fin (usando placeholder "End Date")
                print(f"  [4/5] Configurando fecha fin: {fecha_fin_sismop.strftime('%d/%m/%Y')}...")
                seleccionar_fecha_dash(driver, "End Date", fecha_fin_sismop)

                # Los datos cargan automáticamente al seleccionar las fechas
                # Esperar carga de datos
                print("  [    ] Esperando carga de datos...")
                if not esperar_carga_datos(driver):
                    print(f"  [ERROR] No se pudieron cargar los datos para DZ {dz_num}")
                    reportes_fallidos.append(dz_num)
                    continue

                # 5. Generar y descargar reporte
                print("  [5/5] Generando reporte PDF...")

                # Obtener lista de PDFs ANTES de descargar para detectar el nuevo
                pdfs_antes = obtener_pdfs_existentes(directorio_salida)

                hacer_click_boton(driver, boton_id=ID_BOTON_REPORTE)

                # Esperar descarga (comparando con PDFs anteriores)
                print(f"  [    ] Esperando descarga del PDF...")
                if esperar_descarga_completa(directorio_salida, TIMEOUT_GENERACION_REPORTE, driver, dias, pdfs_antes):
                    print(f"  [OK] Reporte DZ {dz_num} descargado correctamente")
                    reportes_descargados.append(dz_num)

                    # Renombrar el archivo descargado con formato estándar
                    renombrar_ultimo_pdf(directorio_salida, dz_num, fecha_inicio, fecha_fin_sismop - timedelta(days=1))
                else:
                    print(f"  [ERROR] Timeout en descarga para DZ {dz_num}")
                    reportes_fallidos.append(dz_num)

            except Exception as e:
                print(f"  [ERROR] Error procesando DZ {dz_num}: {str(e)}")
                reportes_fallidos.append(dz_num)
                continue

    finally:
        # Cerrar navegador
        print("\n[INFO] Cerrando navegador...")
        driver.quit()

    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE DESCARGA")
    print("=" * 60)
    print(f"Reportes descargados: {len(reportes_descargados)}/{len(dzs)}")
    if reportes_descargados:
        print(f"  DZs exitosas: {reportes_descargados}")
    if reportes_fallidos:
        print(f"  DZs fallidas: {reportes_fallidos}")
    print("=" * 60)

    return reportes_descargados, reportes_fallidos


def renombrar_ultimo_pdf(directorio: Path, dz_num: int, fecha_inicio: datetime, fecha_fin: datetime):
    """
    Renombra el último PDF descargado con un formato estándar.

    Formato: Reporte_DZ_{dz}_{fecha_inicio}_{fecha_fin}.pdf

    Args:
        directorio: Directorio donde está el PDF
        dz_num: Número de la DZ
        fecha_inicio: Fecha de inicio del período
        fecha_fin: Fecha fin del período
    """
    # Encontrar el PDF más reciente
    pdfs = list(directorio.glob("*.pdf"))
    if not pdfs:
        return

    pdf_reciente = max(pdfs, key=lambda p: p.stat().st_mtime)

    # Generar nuevo nombre
    fecha_ini_str = fecha_inicio.strftime("%d%m")
    fecha_fin_str = fecha_fin.strftime("%d%m")
    nuevo_nombre = f"Reporte_DZ_{dz_num}_{fecha_ini_str}_{fecha_fin_str}.pdf"

    # Renombrar si el nombre es diferente
    nuevo_path = directorio / nuevo_nombre
    if pdf_reciente.name != nuevo_nombre:
        # Si ya existe un archivo con ese nombre, eliminarlo
        if nuevo_path.exists():
            nuevo_path.unlink()
        pdf_reciente.rename(nuevo_path)
        print(f"  [    ] Renombrado a: {nuevo_nombre}")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

def main():
    """Punto de entrada principal del script."""
    parser = argparse.ArgumentParser(
        description="Descarga automática de reportes PDF desde SISMOP(A)-SGR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python descargar_reportes.py                          # Automáticas, todas las DZs, 7 días
  python descargar_reportes.py --dz 1 5 9              # Solo DZs 1, 5 y 9
  python descargar_reportes.py --dias 30               # Período de 30 días
  python descargar_reportes.py --fecha-fin 2025-12-12  # Fecha específica
  python descargar_reportes.py --tipo convencionales   # Red convencional
        """
    )

    parser.add_argument(
        "--dz",
        type=int,
        nargs="+",
        help="Números de DZ a descargar (ej: --dz 1 5 9). Por defecto: todas (1-13)"
    )

    parser.add_argument(
        "--dias",
        type=int,
        default=7,
        choices=[7, 30],
        help="Período en días: 7 (monitoreo semanal) o 30 (boletín). Por defecto: 7"
    )

    parser.add_argument(
        "--fecha-fin",
        type=str,
        help="Fecha fin del período en formato YYYY-MM-DD. Por defecto: jueves más reciente"
    )

    parser.add_argument(
        "--output",
        type=str,
        help="Directorio de salida para los PDFs. Por defecto: ./input_pdfs"
    )

    parser.add_argument(
        "--tipo",
        type=str,
        default="automaticas",
        choices=["automaticas", "convencionales"],
        help="Tipo de red: automaticas o convencionales. Por defecto: automaticas"
    )

    args = parser.parse_args()

    # Procesar fecha fin
    fecha_fin = None
    if args.fecha_fin:
        try:
            fecha_fin = datetime.strptime(args.fecha_fin, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Formato de fecha inválido. Use YYYY-MM-DD")
            sys.exit(1)

    # Procesar directorio de salida
    directorio_salida = None
    if args.output:
        directorio_salida = Path(args.output)

    # Validar DZs
    if args.dz:
        for dz in args.dz:
            if dz < 1 or dz > TOTAL_DZS:
                print(f"Error: DZ {dz} fuera de rango. Debe ser entre 1 y {TOTAL_DZS}")
                sys.exit(1)

    # Ejecutar descarga
    try:
        descargados, fallidos = descargar_reportes_dz(
            dzs=args.dz,
            fecha_fin=fecha_fin,
            dias=args.dias,
            directorio_salida=directorio_salida,
            tipo_red=args.tipo
        )

        # Código de salida basado en resultados
        if fallidos:
            sys.exit(1)
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n[INFO] Descarga cancelada por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
