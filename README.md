=========================================================================
   UNIVERSIDAD AUTÓNOMA DE SANTO DOMINGO (UASD)
   FACULTAD DE CIENCIAS - MAESTRÍA EN DATA SCIENCE & AI
   ASIGNATURA: CIENCIA DE DATOS I - GRUPO PETER NAUR
=========================================================================

GUÍA DE DESPLIEGUE Y AJUSTES DE COMPATIBILIDAD MULTI-PC

Este instructivo detalla el orden secuencial para ejecutar el proyecto y 
especifica las modificaciones obligatorias que se deben realizar en el 
código fuente para que los scripts funcionen en computadoras distintas 
a la de desarrollo original (cambios de rutas y credenciales de MySQL).

-------------------------------------------------------------------------
SECCIÓN CRÍTICA: AJUSTES PREVIOS ANTES DE CORRER LOS ARCHIVOS .PY
-------------------------------------------------------------------------
Para evitar errores de conexión ("Access Denied") o fallos de rutas 
inexistentes ("FileNotFoundError"), abra los archivos en su editor de 
código (VS Code, PyCharm, etc.) y modifique los siguientes parámetros:

1. En el archivo "Flujo.py":
   * Ubique la línea donde se definen las credenciales del servidor:
     **PASSWORD = urllib.parse.quote_plus("admin")**
     --> Reemplace "admin" por la contraseña de SU servidor MySQL local.
   * Ubique la línea donde se define la ruta de salida de datos:
     **OUTPUT_FOLDER = r"C:\Users\lenne\OneDrive\Desktop\..."**
     --> Cambie esa dirección completa por una ruta válida de SU computadora 
         donde desee que se guarden los archivos indexados .csv y .json.

2. En el archivo "Entregables.py":
   * Ubique la línea de definición del directorio de outputs gráficos:
    **OUTPUT_DIR = r"C:\Users\lenne\OneDrive\Desktop\..."**
     --> Modifique esta ruta absoluta por la carpeta de su PC donde quiere 
         que el script deposite las imágenes PNG generadas de las gráficas.
   * Ubique la línea de credenciales del servidor:
     PASSWORD = urllib.parse.quote_plus("admin")
     --> Cambie "admin" por la contraseña correspondiente a su motor MySQL local.

-------------------------------------------------------------------------
Paso 1: Configuración de la Base de Datos en MySQL Workbench
-------------------------------------------------------------------------
Antes de levantar la aplicación en Python, es obligatorio asegurar la 
consistencia del catálogo relacional.

1. Abre MySQL Workbench e ingresa a tu instancia relacional local.
2. Abre y ejecuta el script completo llamado "Consultas SQL Sakila.sql".
3. Este script aplicará de manera automática las restricciones de 
   integridad únicas (DDL) sobre las tablas core para mitigar la duplicidad 
   de registros huérfanos antes de la ingesta de datos:

   USE sakila;
   ALTER TABLE country ADD CONSTRAINT unique_country UNIQUE (country);
   ALTER TABLE city ADD CONSTRAINT unique_city_country UNIQUE (city, country_id);
   ALTER TABLE film ADD CONSTRAINT unique_film_title UNIQUE (title, release_year);

-------------------------------------------------------------------------
Paso 2: Instalación de Dependencias Técnicas
-------------------------------------------------------------------------
Asegúrese de contar con las librerías necesarias ejecutando el siguiente 
comando en su terminal, consola o símbolo del sistema (cmd):

pip install sqlalchemy pymysql pandas matplotlib seaborn numpy

-------------------------------------------------------------------------
Paso 3: Lanzar la Capa de Control Interactiva ("Flujo.py")
-------------------------------------------------------------------------
Este archivo orquesta la navegación de todo el sistema a través de menús 
interactivos desplegados en la consola.

1. Abre tu terminal en la carpeta física donde guardaste los archivos.
2. Corre el script principal con el siguiente comando:
   
   python Flujo.py

3. El sistema llamará dinámicamente a "Data Sakila.py" para establecer 
   la conexión segura mediante la clase DbContext utilizando tus credenciales.

4. Funciones Operativas del Menú de Consola:
   * Opción 1: Calcula en tiempo real las métricas descriptivas y de 
     relación lineal (como la covarianza) usando procesamiento nativo 
     en memoria sin librerías externas de persistencia.
   * Opción 2: Corre de forma automática e indexada las 15 consultas 
     analíticas de auditoría oficial, mostrando sus resultados directos 
     en la pantalla como evidencia técnica de la corrida.
   * Opción 3: Ejecuta un caso de uso CRUD inyectando una nueva entidad 
     de película mapeada dentro de la base de datos relacional.
   * Opción 4: Convierte y serializa las colecciones list<object> en 
     archivos planos de intercambio listos para el negocio en formatos 
     estándar .csv y .json en la carpeta local que configuraste.

-------------------------------------------------------------------------
Paso 4: Generar el Respaldo Gráfico Avanzado ("Entregables.py")
-------------------------------------------------------------------------
Una vez ejecutada la auditoría del menú, corre el módulo gráfico 
especializado para producir las figuras de densidad científica requeridas 
para el informe escrito final:

1. En tu terminal, ejecuta el script analítico visual:

   python Entregables.py

2. El script extraerá automáticamente las tendencias agregadas de la 
   base de datos (como el promedio de duración por clasificación de la 
   Consulta 15 y el volumen por categorías de la Consulta 8) utilizando 
   queries nativos conectados a tu motor local ajustado.
3. Las imágenes de alta definición se guardarán de manera directa en la 
   ruta física de outputs que adaptaste en el inicio de esta guía.

=========================================================================
Fin del Instructivo Operativo y de Compartibilidad - 2026
=========================================================================
