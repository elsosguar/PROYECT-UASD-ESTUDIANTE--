# @Elsosguar
# UASD PROYECTO DE SELECCION DE ASIGNATURAS.

 
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
from selenium.common.exceptions import NoSuchWindowException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import tkinter as tk
from tkinter import messagebox
import webbrowser
import threading
import concurrent.futures
import os

cache_urls = {}

def buscar_url_por_materia_y_curso(materia, curso):
    """
    Busca la URL correspondiente a una materia y curso específicos desde un repositorio en línea.
    Optimizado con caché para evitar solicitudes repetidas.
    """
    clave = f"{materia}-{curso}"
    if clave in cache_urls:
        return cache_urls[clave]

    try:
        # Construir la URL dinámica para la materia
        base_url = "https://cdn.jsdelivr.net/gh/elsosguar/PROYECT-UASD-ESTUDIANTE--/materias/"
        url_json = f"{base_url}{materia}.json"

        # Descargar el archivo JSON desde la URL
        response = requests.get(url_json, timeout=5)  # Reducir timeout
        response.raise_for_status()
        datos = response.json()

        # Buscar la clave correspondiente al curso
        clave_a_buscar = f"{materia} {curso}"
        for clave, url in datos.items():
            if clave.startswith(clave_a_buscar):
                resultado = f"https://ssb.uasd.edu.do{url}" if url.startswith('/') else url
                cache_urls[clave] = resultado
                return resultado

        resultado = f"No se encontró el curso {curso} en la materia {materia}."
        cache_urls[clave] = resultado
        return resultado

    except Exception as e:
        resultado = f"Error al procesar los datos de la materia '{materia}': {e}"
        cache_urls[clave] = resultado
        return resultado
    
def obtener_html(url, driver):
    session = requests.Session()

    # Pasar las cookies de Selenium a requests
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    try:
        respuesta = session.get(url, timeout=10)
        respuesta.raise_for_status()
        print(f"HTML obtenido de {url}")
        return respuesta.text
    except requests.RequestException as e:
        print(f"Error al obtener HTML de {url}: {e}")
        return ""

def extraer_tipos_de_horario(html):
    """
    Extrae los enlaces de los tipos de horario de un HTML.

    Args:
        html (str): Contenido HTML de la página.

    Returns:
        list: Lista de enlaces encontrados para los tipos de horario.
    """
    soup = BeautifulSoup(html, "html.parser")
    horarios = []

    # Buscar "Tipos de Horario" y sus enlaces
    contenedor = soup.find("span", class_="fieldlabeltext", string="Tipos de Horario: ")
    if contenedor:
        # Solo capturar los enlaces directamente relacionados con "Tipos de Horario"
        for enlace in contenedor.find_next_siblings("a"):
            if "schd_in" in enlace["href"]:  # Asegurar que el enlace contiene 'schd_in'
                horarios.append(enlace["href"])
    else:
        print("No se encontró 'Tipos de Horario' en el HTML.")
    return horarios

def procesar_dato(dato, driver):
    """
    Procesa un único dato (materia y curso), busca su URL, obtiene el HTML y extrae horarios.
    """
    materia = dato["Materia"]
    curso = dato["Curso"]
    url = buscar_url_por_materia_y_curso(materia, curso)

    if url.startswith("http"):
        html = obtener_html(url, driver)
        horarios = extraer_tipos_de_horario(html)
    else:
        horarios = url

    return {
        "Materia": materia,
        "Curso": curso,
        "URL": url,
        "Tipos de Horario": horarios
    }

def procesar_datos_capturados(datos_capturados, driver):
    """
    Procesa los datos capturados utilizando procesamiento paralelo y busca las URLs correspondientes.
    """
    resultados = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futuros = {executor.submit(procesar_dato, dato, driver): dato for dato in datos_capturados}
        for futuro in concurrent.futures.as_completed(futuros):
            resultados.append(futuro.result())
    return resultados
 
def capturar_datos_materias(driver, url_referencia):
    """
    Espera indefinidamente hasta que el usuario navegue a la página de referencia,
    y detecta si los datos están disponibles. Si no encuentra datos, sigue buscando.
    """
    print(f"Esperando a que el usuario navegue a la página correcta: {url_referencia}")

    while True:
        try:
            # Verificar si el navegador sigue abierto
            if not driver.window_handles:
                print("No se detectaron pestañas abiertas. Esperando...")
                time.sleep(5)
                continue

            # Cambiar a la pestaña que contiene la URL de referencia
            for handle in driver.window_handles:
                driver.switch_to.window(handle)

                # Verificar si estamos en la página correcta
                if driver.current_url == url_referencia:
                    print("Pestaña correcta encontrada. Capturando datos...")

                    while True:
                        try:
                            # Intentar localizar la tabla de materias
                            tabla = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//table[contains(., 'Cursos en la Proyección')]"))
                            )
                            print("Tabla encontrada. Capturando datos...")

                            # Capturar las filas de la tabla
                            filas = tabla.find_elements(By.XPATH, ".//tr")[1:]  # Saltar encabezado
                            materias = []

                            for fila in filas:
                                columnas = fila.find_elements(By.XPATH, ".//td")
                                if len(columnas) >= 7:
                                    materia = {
                                        "Materia": columnas[0].text.strip(),
                                        "Curso": columnas[1].text.strip(),
                                        "Descripción": columnas[2].text.strip(),
                                        "Nivel": columnas[3].text.strip(),
                                        "Prioridad": columnas[4].text.strip(),
                                        "Créditos": columnas[5].text.strip(),
                                        "Electivo": columnas[6].text.strip(),
                                    }
                                    materias.append(materia)

                            if materias:
                                print("Datos capturados con éxito.")
                                return materias
                            else:
                                print("Datos aún no disponibles. Reintentando...")
                                time.sleep(5)  # Esperar antes de reintentar

                        except Exception:
                            print("La tabla aún no está disponible. Esperando...")
                            time.sleep(5)  # Esperar antes de reintentar

            # Si no estamos en la pestaña correcta, seguir esperando
            print("La URL de referencia no está abierta en ninguna pestaña. Reintentando...")
            time.sleep(5)  # Reducir la frecuencia de verificación

        except NoSuchWindowException:
            print("La ventana del navegador se cerró. Esperando a que el usuario la abra nuevamente...")
            time.sleep(5)
            continue

        except WebDriverException as e:
            # Manejar otros errores del navegador
            print(f"Error del navegador detectado. Reintentando... Error: {e}")
            time.sleep(5)
            continue

        except Exception as e:
            # Si ocurre otro error, seguir esperando
            print(f"Error inesperado. Reintentando... Error: {e}")
            time.sleep(5)
            continue

def integrar_con_selenium(driver):
    """
    Captura los datos dinámicamente, busca las URLs correspondientes en los archivos JSON,
    procesa los tipos de horario y muestra todo en una pestaña dinámica en la sesión de Selenium.
    """
    # Capturar los datos dinámicamente
    datos_capturados = capturar_datos_materias(driver)

    if not datos_capturados:
        print("No se capturaron datos. Verifica la página y vuelve a intentarlo.")
        return

    # Procesar y buscar URLs para las materias capturadas
    carpeta_json = "materias"
    resultados = procesar_datos_capturados(datos_capturados, driver, carpeta_json)

    # Mostrar resultados en consola
    for resultado in resultados:
        print(f"Materia: {resultado['Materia']}, Curso: {resultado['Curso']}")
        print(f"URL: {resultado['URL']}")
        if isinstance(resultado["Tipos de Horario"], list):
            print("  Tipos de Horario:")
            for horario in resultado["Tipos de Horario"]:
                print(f"    {horario}")
        else:
            print(f"  {resultado['Tipos de Horario']}")

    # Consolidar los datos de tipos de horario en un HTML dinámico
    html_consolidado = procesar_tipos_de_horario_y_extraer_tablas(resultados, driver)

    # Escapar el HTML para evitar problemas con caracteres especiales
    html_consolidado_escapado = urllib.parse.quote(html_consolidado)

    # Mostrar el HTML consolidado en una pestaña dinámica de Selenium
    driver.execute_script("window.open('');")  # Abre una nueva pestaña
    driver.switch_to.window(driver.window_handles[-1])  # Cambia a la nueva pestaña
    driver.get(f"data:text/html;charset=utf-8,{html_consolidado_escapado}")  # Muestra el HTML dinámico
    print("Resultados consolidados mostrados en una pestaña dinámica.")

def procesar_tipos_de_horario_y_extraer_tablas(resultados, driver):
    """
    Itera sobre las URLs de tipos de horario, extrae los datos de todas las secciones
    (nombre del curso, código, campus, método educativo, horario, y día) y los organiza en una tabla HTML con ordenamiento y filtros.

    Args:
        resultados (list): Lista de resultados con las URLs de tipos de horario.
        driver (webdriver): Instancia de Selenium WebDriver.

    Returns:
        str: Contenido HTML dinámico con formato mejorado, funcionalidad de ordenamiento y filtros.
    """
    # Listas para opciones únicas en los filtros
    cursos = set()
    codigos = set()
    campus = set()
    metodos = set()
    horarios = set()
    dias = set()

    # Extraer datos de cada resultado para construir la tabla y los filtros
    filas_html = ""
    for resultado in resultados:
        if isinstance(resultado["Tipos de Horario"], list):
            for horario in resultado["Tipos de Horario"]:
                url_completa = f"https://ssb.uasd.edu.do{horario}" if horario.startswith('/') else horario
                html = obtener_html(url_completa, driver)
                if html:
                    soup = BeautifulSoup(html, "html.parser")
                    secciones = soup.find_all("th", class_="ddtitle")
                    for seccion in secciones:
                        try:
                            nombre_curso = seccion.find("a").text.strip()
                            cursos.add(nombre_curso)
                        except AttributeError:
                            nombre_curso = "No disponible"

                        try:
                            codigo = nombre_curso.split(" - ")[1]
                            codigos.add(codigo)
                        except IndexError:
                            codigo = "No disponible"

                        try:
                            detalles = seccion.find_parent("tr").find_next_sibling("tr").find("td", class_="dddefault")
                            campus_text = detalles.find(string=lambda x: "Campus" in x).find_next("br").find_previous_sibling(string=True).strip()
                            campus.add(campus_text)
                        except AttributeError:
                            campus_text = "No disponible"

                        try:
                            metodo_educativo = detalles.find(string=lambda x: "Método Educativo" in x).find_next("br").find_previous_sibling(string=True).strip()
                            metodos.add(metodo_educativo)
                        except AttributeError:
                            metodo_educativo = "No disponible"

                        try:
                            tabla_horarios = detalles.find_next("table", class_="datadisplaytable")
                            filas_horarios = tabla_horarios.find_all("tr")[1:]
                            horarios_text = []
                            dias_text = []
                            for fila in filas_horarios:
                                celdas = fila.find_all("td")
                                if len(celdas) >= 3 and celdas[0].text.strip() == "Class":
                                    horarios_text.append(celdas[1].text.strip())
                                    dias_text.append(celdas[2].text.strip())
                            horarios.add(", ".join(horarios_text))
                            dias.add(", ".join(dias_text))
                        except AttributeError:
                            horarios_text = ["No disponible"]
                            dias_text = ["No disponible"]

                        filas_html += f"""
                        <tr>
                            <td>{nombre_curso}</td>
                            <td>{codigo}</td>
                            <td>{campus_text}</td>
                            <td>{metodo_educativo}</td>
                            <td>{', '.join(horarios_text)}</td>
                            <td>{', '.join(dias_text)}</td>
                        </tr>
                        """

    # Construir los filtros
    def construir_opciones(opciones):
        return "".join(f'<option value="{opcion}">{opcion}</option>' for opcion in sorted(opciones))

    # Construir el HTML final
    html_consolidado = f"""
    <html>
    <head>
        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid black;
                text-align: left;
                padding: 8px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            select {{
                width: 90%;
            }}
        </style>
        <script>
            function filterTable(columnIndex, filterValue) {{
                const table = document.getElementById("seccionesTable");
                const rows = table.tBodies[0].rows;
                for (let i = 0; i < rows.length; i++) {{
                    const cellValue = rows[i].cells[columnIndex].innerText;
                    rows[i].style.display = filterValue === "all" || cellValue.includes(filterValue) ? "" : "none";
                }}
            }}
        </script>
    </head>
    <body>
        <h1>Resumen de Secciones</h1>
        <table id="seccionesTable">
            <thead>
                <tr>
                    <th>Nombre del Curso<br>
                        <select onchange="filterTable(0, this.value)">
                            <option value="all">Todos</option>
                            {construir_opciones(cursos)}
                        </select>
                    </th>
                    <th>Código<br>
                        <select onchange="filterTable(1, this.value)">
                            <option value="all">Todos</option>
                            {construir_opciones(codigos)}
                        </select>
                    </th>
                    <th>Campus<br>
                        <select onchange="filterTable(2, this.value)">
                            <option value="all">Todos</option>
                            {construir_opciones(campus)}
                        </select>
                    </th>
                    <th>Método Educativo<br>
                        <select onchange="filterTable(3, this.value)">
                            <option value="all">Todos</option>
                            {construir_opciones(metodos)}
                        </select>
                    </th>
                    <th>Horario<br>
                        <select onchange="filterTable(4, this.value)">
                            <option value="all">Todos</option>
                            {construir_opciones(horarios)}
                        </select>
                    </th>
                    <th>Día<br>
                        <select onchange="filterTable(5, this.value)">
                            <option value="all">Todos</option>
                            {construir_opciones(dias)}
                        </select>
                    </th>
                </tr>
            </thead>
            <tbody>
                {filas_html}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html_consolidado

# Variable global para el driver de Selenium
driver = None

# Función para mostrar la interfaz gráfica
def mostrar_interfaz():
    ventana = tk.Tk()
    ventana.title("Mis Datos")
    ventana.geometry("300x200")
    
    # Etiquetas para mostrar datos
    nombre_label = tk.Label(ventana, text="UASD", font=("Arial", 15))
    nombre_label.pack(pady=10)

    titulo_label = tk.Label(ventana, text="--Selección de Materias--", font=("Arial", 12))
    titulo_label.pack(pady=10)
 
    # Botón para finalizar todo el programa
    def finalizar_programa():
        ventana.destroy()  # Cierra la ventana
        if driver is not None:  # Verifica si el driver de Selenium está activo
            try:
                driver.quit()  # Cierra el navegador
                print("Navegador cerrado.")
            except Exception as e:
                print(f"Error al cerrar el navegador: {e}")
        os._exit(0)  # Termina completamente el programa

    terminar_boton = tk.Button(ventana, text="Terminar programa", command=finalizar_programa)
    terminar_boton.pack(pady=10)

    # Función para abrir el hipervínculo
    def abrir_enlace():
        webbrowser.open("https://github.com/elsosguar")

    # Etiqueta como hipervínculo
    enlace = tk.Label(ventana, text="Elsosguar", font=("Arial", 12), fg="blue", cursor="hand2")
    enlace.pack(pady=10)
    enlace.bind("<Button-1>", lambda e: abrir_enlace())  # Evento para hacer clic

    # Mantener la ventana abierta
    ventana.mainloop()

# Función para ejecutar Selenium
 
# Crear hilos para ejecutar la interfaz y el script por separado
hilo_interfaz = threading.Thread(target=mostrar_interfaz)
 
# Iniciar los hilos
hilo_interfaz.start()
 
if __name__ == "__main__":
    # URL de referencia donde se encuentra la tabla de materias
    url_referencia = "https://ssb.uasd.edu.do/PROD/bwskfreg.P_AltPin"

    # Configurar Selenium
    driver = webdriver.Chrome()
    driver.get("https://uasd.edu.do/servicios/autoservicio/")  # Abrir el navegador con una página inicial genérica

    try:
        print(f"Navegador iniciado. Por favor, navega a la URL objetivo: {url_referencia}")

        # Capturar los datos dinámicamente desde la tabla
        datos_capturados = capturar_datos_materias(driver, url_referencia)

        if datos_capturados:
            print("Datos capturados con éxito. Procesando información...")

            # Procesar los datos capturados
            resultados = procesar_datos_capturados(datos_capturados, driver)

            # Mostrar resultados
            for resultado in resultados:
                print(f"Materia: {resultado['Materia']}, Curso: {resultado['Curso']}")
                print(f"URL: {resultado['URL']}")
                if isinstance(resultado["Tipos de Horario"], list):
                    print("  Tipos de Horario:")
                    for horario in resultado["Tipos de Horario"]:
                        print(f"    {horario}")
                else:
                    print(f"  {resultado['Tipos de Horario']}")

            # Consolidar los datos de tipos de horario en un HTML dinámico
            html_consolidado = procesar_tipos_de_horario_y_extraer_tablas(resultados, driver)
            html_consolidado_escapado = urllib.parse.quote(html_consolidado)

            # Mostrar el HTML consolidado en una pestaña dinámica de Selenium
            driver.execute_script("window.open('');")  # Abre una nueva pestaña
            driver.switch_to.window(driver.window_handles[-1])  # Cambia a la nueva pestaña
            driver.get(f"data:text/html;charset=utf-8,{html_consolidado_escapado}")  # Muestra el HTML dinámico
            print("Resultados consolidados mostrados en una pestaña dinámica.")

        else:
            print("No se encontraron datos. Verifica tu selección.")

    finally:
        root = tk.Tk()
        root.withdraw()  # Oculta la ventana principal de Tkinter
        messagebox.showinfo("Proceso FINALIZADO", "Presiona OK para cerrar la ventana.")