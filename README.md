Sistema de Selección de Materias UASD

Descripción
Este proyecto automatiza el proceso de búsqueda y procesamiento de datos relacionados con la selección de materias y cursos en la UASD (Universidad Autónoma de Santo Domingo). Utiliza una combinación de Selenium, requests, y BeautifulSoup para capturar información dinámica de la página oficial y generar resultados procesados.

Características Principales
Captura Dinámica de Datos:

Usa Selenium para interactuar con la página de selección de materias y capturar tablas dinámicas.
Detecta automáticamente cambios en la interfaz web.
Procesamiento de Materias y Cursos:

Busca las URLs de cada materia y curso desde un repositorio JSON público.
Obtiene y analiza datos adicionales, como tipos de horarios y detalles de cada curso.
Generación de Resultados Procesados:

Los datos capturados se consolidan en un HTML dinámico con filtros y funcionalidades avanzadas.
Los resultados incluyen:
Materia y curso.
URLs correspondientes.
Tipos de horario extraídos.
Interfaz Gráfica (GUI):

Ofrece una ventana sencilla para facilitar la interacción con el sistema.
Incluye un botón para finalizar el programa y abrir hipervínculos relevantes.
Optimización del Rendimiento:

Implementa caché para evitar solicitudes repetitivas al repositorio.
Utiliza procesamiento paralelo para acelerar la búsqueda y el análisis.
Tecnologías Utilizadas
Python: Lenguaje principal.
Selenium: Captura dinámica de datos web.
Requests: Solicitudes HTTP para obtener datos JSON.
BeautifulSoup: Análisis y extracción de datos HTML.
Tkinter: Creación de la interfaz gráfica.
Concurrent Futures: Procesamiento paralelo para mejorar el rendimiento.
Cómo Funciona
Inicio del Programa:

El navegador Selenium se abre y el sistema espera hasta que el usuario navegue a la página de referencia correcta.
Captura de Datos:

El programa detecta y captura las tablas dinámicas que contienen información sobre materias y cursos.
Procesamiento:

Cada materia/curso se procesa para buscar su URL asociada en un repositorio público.
Se descarga el HTML correspondiente y se extraen los horarios disponibles.
Resultados:

Los datos procesados se muestran en la consola y en un HTML dinámico accesible desde una pestaña del navegador.
Interfaz Gráfica:

Permite finalizar la ejecución del programa con un solo clic y acceder a enlaces relevantes.

Requisitos Previos
Python 3.8+: Asegúrate de tener Python instalado en tu sistema.
Dependencias:
Selenium
Requests
BeautifulSoup
Navegador Chrome: Instalado y compatible con la versión del controlador (ChromeDriver).

Ejemplo de Uso

Ejecuta el programa.
Navega al portal oficial de la UASD y selecciona la página de proyección de cursos.
Observa cómo el sistema captura los datos automáticamente.
Consulta los resultados procesados en la consola o en la pestaña dinámica generada.
Contribuciones
