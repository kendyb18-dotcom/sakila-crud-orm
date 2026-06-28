import os
import csv
import json
from sqlalchemy import create_engine, text

# =========================================================================
# GESTOR DE CONEXIONES CENTRALIZADO (DbContext)
# =========================================================================
class DbContext:
    """
    Componente centralizado de la arquitectura encargado de aislar el motor 
    relacional y gobernar las conexiones hacia el DBMS MySQL.
    """
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        print("[DbContext] Conexión inicializada con éxito con el esquema Sakila.")

    def execute_query(self, sql_string, params=None):
        with self.engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
            result = conn.execute(text(sql_string), params or {})
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
            if sql_string.strip().upper().startswith("SELECT"):
                return result.fetchall()
            return result

# =========================================================================
# CLASSES ENTITIES (Representación de tablas como objetos de código)
# =========================================================================
class FilmEntity:
    def __init__(self, film_id=None, title=None, description=None, release_year=None, 
                 rental_rate=None, length=None, replacement_cost=None, rating=None):
        self.film_id = film_id
        self.title = title
        self.description = description
        self.release_year = release_year
        self.rental_rate = rental_rate
        self.length = length
        self.replacement_cost = replacement_cost
        self.rating = rating

class CountryEntity:
    def __init__(self, country_id=None, country=None):
        self.country_id = country_id
        self.country = country

class CityEntity:
    def __init__(self, city_id=None, city=None, country_id=None):
        self.city_id = city_id
        self.city = city
        self.country_id = country_id

# =========================================================================
# MODULES MODELS (Manipulación de registros en colecciones indexadas)
# =========================================================================
class FilmModel:
    def __init__(self, db_context):
        self.context = db_context
        self.entities = []  # Estructura obligatoria: list<object>

    def create(self, film: FilmEntity):
        sql = """INSERT INTO film (title, description, release_year, rental_rate, length, replacement_cost, language_id) 
                 VALUES (:title, :description, :release_year, :rental_rate, :length, :replacement_cost, 1);"""
        self.context.execute_query(sql, {
            "title": film.title, "description": film.description,
            "release_year": film.release_year, "rental_rate": film.rental_rate,
            "length": film.length, "replacement_cost": film.replacement_cost
        })

    def read_all(self):
        self.entities.clear()
        sql = "SELECT film_id, title, description, release_year, rental_rate, length, replacement_cost, rating FROM film;"
        rows = self.context.execute_query(sql)
        for r in rows:
            self.entities.append(FilmEntity(r[0], r[1], r[2], r[3], float(r[4]) if r[4] else 0.0, r[5], float(r[6]) if r[6] else 0.0, r[7]))
        return self.entities

    def update(self, film_id, new_title, new_rate):
        sql = "UPDATE film SET title = :title, rental_rate = :rate WHERE film_id = :id;"
        self.context.execute_query(sql, {"title": new_title, "rate": new_rate, "id": film_id})

    def delete(self, film_id):
        sql = "DELETE FROM film WHERE film_id = :id;"
        self.context.execute_query(sql, {"id": film_id})

    # --- SERIALIZACIÓN E INTERCAMBIO DE FORMATOS (IO CORES) ---
    def export_to_csv(self, file_path):
        if not self.entities: self.read_all()
        with open(file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['film_id', 'title', 'rental_rate', 'length', 'replacement_cost', 'rating'])
            for e in self.entities:
                writer.writerow([e.film_id, e.title, e.rental_rate, e.length, e.replacement_cost, e.rating])

    def export_to_json(self, file_path):
        if not self.entities: self.read_all()
        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump([e.__dict__ for e in self.entities], f, indent=4, default=str)