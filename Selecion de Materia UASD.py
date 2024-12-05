from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup  # Importación necesaria para analizar el HTML


def iniciar_conexion(url):
    """Inicia el navegador y abre la URL especificada."""
    driver = webdriver.Chrome()
    driver.get(url)
    return driver

def procesar_formulario1(driver, semestre):
    """Completa el primer formulario seleccionando el semestre y enviándolo."""
    try:
        # Seleccionar semestre
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "term_input_id"))
        )
        select = Select(select_element)
        select.select_by_value(semestre)

        # Clic en el botón Enviar
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Enviar')]"))
        )
        submit_button.click()
    except Exception as e:
        print(f"Error en el formulario 1: {e}")

def procesar_formulario2(driver, materia):
    """Completa el segundo formulario seleccionando una materia y extrayendo las URLs con sus nombres."""
    try:
        # Esperar que cargue el segundo formulario
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "sel_subj")))

        # Seleccionar materia
        subject_select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "subj_id"))
        )
        subject_select = Select(subject_select_element)
        subject_select.select_by_value(materia)

        # Clic en el botón Obtener cursos
        obtener_cursos_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Obtener cursos')]"))
        )

        # Intentar clic normal y forzado
        try:
            obtener_cursos_button.click()
        except:
            driver.execute_script("arguments[0].click();", obtener_cursos_button)

        # Esperar la carga de la página y capturar el HTML resultante
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html_resultante = driver.page_source

        # Usar BeautifulSoup para extraer las URLs y nombres
        soup = BeautifulSoup(html_resultante, 'html.parser')
        resultados = {}
        for td in soup.find_all('td', class_='nttitle'):
            enlace = td.find('a')
            if enlace and enlace['href']:
                url = enlace['href']
                nombre = enlace.text.strip()
                resultados[nombre] = url
        
        # Imprimir en formato JSON
        for nombre, url in resultados.items():
            print(f'"{nombre}" : "{url}"')

    except Exception as e:
        print(f"Error en el formulario 2: {e}")


def main():
    url = "https://ssb.uasd.edu.do/PROD/bwckctlg.p_disp_dyn_ctlg"
    semestre = "202510"  # Primer Semestre 2025
    materia = "ADM"  # Administración

    # Paso 1: Iniciar conexión
    driver = iniciar_conexion(url)

    try:
        # Paso 2: Procesar el primer formulario
        procesar_formulario1(driver, semestre)

        # Paso 3: Procesar el segundo formulario y capturar el HTML resultante
        html_resultante = procesar_formulario2(driver, materia)

        # Mostrar el HTML resultante
        if html_resultante:
            print(html_resultante)

    finally:
        # Cerrar el navegador
        driver.quit()

if __name__ == "__main__":
    main()
