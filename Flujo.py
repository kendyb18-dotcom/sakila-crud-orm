import os
import urllib.parse
import importlib
import numpy as np

# Carga dinámica adaptada para solventar el espacio en el nombre de 'Data Sakila.py'
data_sakila_module = importlib.import_module("Data Sakila")
DbContext = data_sakila_module.DbContext
FilmModel = data_sakila_module.FilmModel
FilmEntity = data_sakila_module.FilmEntity

QUERIES_REPOSITORIO = [
    ("CONSULTA 1: Cantidad total de películas", "SELECT COUNT(*) AS Total_Peliculas FROM film;"),
    ("CONSULTA 2: Películas con duración mayor a 120 minutos", "SELECT title, length FROM film WHERE length > 120 ORDER BY length DESC;"),
    ("CONSULTA 3: Actores ordenados por apellido", "SELECT actor_id, first_name, last_name FROM actor ORDER BY last_name;"),
    ("CONSULTA 4: Cantidad de películas por clasificación", "SELECT rating, COUNT(*) AS Cantidad FROM film GROUP BY rating;"),
    ("CONSULTA 5: Top 10 películas más largas", "SELECT title, length FROM film ORDER BY length DESC LIMIT 10;"),
    ("CONSULTA 6: Clientes con sus direcciones", "SELECT c.first_name, c.last_name, a.address FROM customer c INNER JOIN address a ON c.address_id = a.address_id;"),
    ("CONSULTA 7: Películas y categorías", "SELECT f.title, cat.name AS Categoria FROM film f INNER JOIN film_category fc ON f.film_id = fc.film_id INNER JOIN category cat ON fc.category_id = cat.category_id;"),
    ("CONSULTA 8: Cantidad de películas por categoría", "SELECT c.name AS Categoria, COUNT(*) AS Total FROM category c INNER JOIN film_category fc ON c.category_id = fc.category_id GROUP BY c.name ORDER BY Total DESC;"),
    ("CONSULTA 9: Ingresos por cliente", "SELECT customer_id, SUM(amount) AS Total_Gastado FROM payment GROUP BY customer_id ORDER BY Total_Gastado DESC;"),
    ("CONSULTA 10: Clientes que han gastado más de $100", "SELECT customer_id, SUM(amount) AS Total FROM payment GROUP BY customer_id HAVING SUM(amount) > 100;"),
    ("CONSULTA 11: Cantidad de alquileres por mes", "SELECT MONTH(rental_date) AS Mes, COUNT(*) AS Alquileres FROM rental GROUP BY MONTH(rental_date) ORDER BY Mes;"),
    ("CONSULTA 12: Actores y cantidad de películas", "SELECT a.actor_id, a.first_name, a.last_name, COUNT(fa.film_id) AS Total_Peliculas FROM actor a INNER JOIN film_actor fa ON a.actor_id = fa.actor_id GROUP BY a.actor_id, a.first_name, a.last_name ORDER BY Total_Peliculas DESC;"),
    ("CONSULTA 13: Películas nunca alquiladas", "SELECT DISTINCT f.title FROM film f LEFT JOIN inventory i ON f.film_id = i.film_id LEFT JOIN rental r ON i.inventory_id = r.inventory_id WHERE r.rental_id IS NULL;"),
    ("CONSULTA 14: Países y cantidad de ciudades", "SELECT co.country, COUNT(ci.city_id) AS Total_Ciudades FROM country co LEFT JOIN city ci ON co.country_id = ci.country_id GROUP BY co.country ORDER BY Total_Ciudades DESC;"),
    ("CONSULTA 15: Promedio de duración por clasificación", "SELECT rating, AVG(length) AS Duracion_Promedio FROM film GROUP BY rating ORDER BY Duracion_Promedio DESC;")
]

class SakilaMVCController:
    def __init__(self, db_context, output_dir):
        self.context = db_context
        self.model = FilmModel(db_context)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def calcular_metricas_descriptivas(self):
        print("\n📊 [MÉTRICAS DESCRIPTIVAS FUNDAMENTALES - PROCESAMIENTO NATIVO]")
        films = self.model.read_all()
        lengths = [f.length for f in films if f.length]
        costs = [f.replacement_cost for f in films if f.replacement_cost]
        
        if not lengths:
            print("[ALERTA] Listas vacías. Cargue datos previos antes de computar métricas.")
            return

        media_len = np.mean(lengths)
        rango_len = np.ptp(lengths)
        std_len = np.std(lengths)
        var_len = np.var(lengths)
        
        cov_matrix = np.cov(lengths, costs)
        covarianza_val = cov_matrix[0, 1] if cov_matrix.shape == (2,2) else 0.0

        print(f" -> Dimensión Duración de Películas (length):")
        print(f"    - Media Aritmética: {media_len:.2f} min")
        print(f"    - Rango Dinámico: {rango_len:.2f} min")
        print(f"    - Desviación Estándar: {std_len:.2f}")
        print(f"    - Varianza Poblacional: {var_len:.2f}")
        print(f" -> Relación Multivariada Lineal:")
        print(f"    - Covarianza [Duración vs Costo Reemplazo]: {covarianza_val:.4f}")

    def ejecutar_auditoria_oficial(self):
        print("\n🔍 [AUDITORÍA] Inicializando secuencia de las 15 consultas del reporte...")
        for index, (titulo, sql) in enumerate(QUERIES_REPOSITORIO, start=1):
            print(f"\n----------------------------------------------------------------------")
            print(f"▶️ {titulo}")
            try:
                rows = self.context.execute_query(sql)
                print("   [EVIDENCIA DE CORRIDA]:")
                for row in rows[:4]:
                    print(f"     {row}")
                if len(rows) > 4:
                    print(f"     ... ({len(rows) - 4} registros adicionales omitidos en vista previa)")
            except Exception as e:
                print(f"   ❌ [ERROR EN SENTENCIA RELACIONAL]: {str(e)}")

    def desplegar_menu_consola(self):
        while True:
            print("\n==================================================================")
            print("🖥️  SISTEMA ORM PROPIO - GRUPO PETER NAUR (FACULTAD DE CIENCIAS - UASD)")
            print("==================================================================")
            print("1. Calcular Métricas Descriptivas Fundamentales (Fase I)")
            print("2. Correr Repositorio de las 15 Consultas Oficiales de Auditoría")
            print("3. Ejecutar Caso de Uso CRUD Completo (Inserción de Película)")
            print("4. Serializar Modelos a Archivos de Intercambio (CSV / JSON)")
            print("5. Salir")
            print("==================================================================")
            opcion = input("Seleccione una opción del flujo operativo: ")

            if opcion == "1":
                self.calcular_metricas_descriptivas()
            elif opcion == "2":
                self.ejecutar_auditoria_oficial()
            elif opcion == "3":
                print("\n⚙️ [CRUD] Insertando registro de prueba con el ORM propio...")
                nueva_peli = FilmEntity(title="PETER NAUR REPORTE FINAL 2026", description="ORM Propio Basado en POO", 
                                        release_year=2026, rental_rate=4.99, 1gth=135, replacement_cost=21.99)
                self.model.create(nueva_peli)
                print("⚙️ [CRUD] Éxito. Entidad mapeada e insertada. Actualizando list<object>...")
                self.model.read_all()
            elif opcion == "4":
                csv_path = os.path.join(self.output_dir, "sakila_films.csv")
                json_path = os.path.join(self.output_dir, "sakila_films.json")
                self.model.export_to_csv(csv_path)
                self.model.export_to_json(json_path)
                print(f"💾 [MODEL COMPLIANCE] Archivos exportados de forma segura a:\n   {self.output_dir}")
            elif opcion == "5":
                print("[CONTROLLER] Finalizando ciclo de vida de la aplicación. Desconexión exitosa.")
                break
            else:
                print("[ALERTA] Selección errónea. Intente nuevamente.")

if __name__ == "__main__":
    USER = "root"
    PASSWORD = urllib.parse.quote_plus("Contrasena aqui") #Poner contraseña de MySQL en URL encoding
    HOST = "127.0.0.1"
    PORT = "3306"
    DATABASE = "sakila"
    
    OUTPUT_FOLDER = r"C:\DC"
    CONN_STRING = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
    
    context = DbContext(CONN_STRING)
    controller = SakilaMVCController(context, OUTPUT_FOLDER)
    controller.desplegar_menu_consola()
