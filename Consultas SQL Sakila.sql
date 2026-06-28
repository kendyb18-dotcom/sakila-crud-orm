/* =========================================================================
   UNIVERSIDAD AUTÓNOMA DE SANTO DOMINGO (UASD)
   FACULTAD DE CIENCIAS - MAESTRÍA EN DATA SCIENCE & AI
   ASIGNATURA: CIENCIA DE DATOS I
   EQUIPO: PETER NAUR (Johanna Joaquín, Kendy Báez, Lennen Santos Mejía)
   ========================================================================= */

USE sakila;

-- =========================================================================
-- OPTIMIZACIÓN DE INTEGRIDAD E INYECCIÓN DE CALIDAD (DDL)
-- =========================================================================

-- Forzar restricciones únicas para mitigar registros huérfanos o duplicados
ALTER TABLE country ADD CONSTRAINT unique_country UNIQUE (country);
ALTER TABLE city ADD CONSTRAINT unique_city_country UNIQUE (city, country_id);
ALTER TABLE film ADD CONSTRAINT unique_film_title UNIQUE (title, release_year);


-- =========================================================================
-- REPOSITORIO DE SENTENCIAS SQL (SCRIPT ANALÍTICO COMPLETO)
-- =========================================================================

-- CONSULTA 1: Cantidad total de películas
SELECT COUNT(*) AS Total_Peliculas FROM film;[cite: 4]

-- CONSULTA 2: Películas con duración mayor a 120 minutos
SELECT title, length FROM film WHERE length > 120 ORDER BY length DESC;[cite: 4]

-- CONSULTA 3: Actores ordenados por apellido[cite: 4]
SELECT actor_id, first_name, last_name FROM actor ORDER BY last_name;[cite: 4]

-- CONSULTA 4: Cantidad de películas por clasificación[cite: 4]
SELECT rating, COUNT(*) AS Cantidad FROM film GROUP BY rating;[cite: 4]

-- CONSULTA 5: Top 10 películas más largas[cite: 4]
SELECT title, length FROM film ORDER BY length DESC LIMIT 10;[cite: 4]

-- CONSULTA 6: Clientes con sus direcciones[cite: 4]
SELECT c.first_name, c.last_name, a.address
FROM customer c
INNER JOIN address a ON c.address_id = a.address_id;[cite: 4]

-- CONSULTA 7: Películas y categorías[cite: 4]
SELECT f.title, cat.name AS Categoria
FROM film f
INNER JOIN film_category fc ON f.film_id = fc.film_id
INNER JOIN category cat ON fc.category_id = cat.category_id;[cite: 4]

-- CONSULTA 8: Cantidad de películas por categoría[cite: 4]
SELECT c.name AS Categoria, COUNT(*) AS Total
FROM category c
INNER JOIN film_category fc ON c.category_id = fc.category_id
GROUP BY c.name
ORDER BY Total DESC;[cite: 4]

-- CONSULTA 9: Ingresos por cliente[cite: 4]
SELECT customer_id, SUM(amount) AS Total_Gastado
FROM payment
GROUP BY customer_id
ORDER BY Total_Gastado DESC;[cite: 4]

-- CONSULTA 10: Clientes que han gastado más de $100[cite: 4]
SELECT customer_id, SUM(amount) AS Total
FROM payment
GROUP BY customer_id
HAVING SUM(amount) > 100;[cite: 4]

-- CONSULTA 11: Cantidad de alquileres por mes[cite: 4]
SELECT MONTH(rental_date) AS Mes, COUNT(*) AS Alquileres
FROM rental
GROUP BY MONTH(rental_date)
ORDER BY Mes;[cite: 4]

-- CONSULTA 12: Actores y cantidad de películas[cite: 4]
SELECT a.actor_id, a.first_name, a.last_name, COUNT(fa.film_id) AS Total_Peliculas
FROM actor a
INNER JOIN film_actor fa ON a.actor_id = fa.actor_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY Total_Peliculas DESC;[cite: 4]

-- CONSULTA 13: Películas nunca alquiladas[cite: 4]
SELECT DISTINCT f.title
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
WHERE r.rental_id IS NULL;[cite: 4]

-- CONSULTA 14: Países y cantidad de ciudades[cite: 4]
SELECT co.country, COUNT(ci.city_id) AS Total_Ciudades
FROM country co
LEFT JOIN city ci ON co.country_id = ci.country_id
GROUP BY co.country
ORDER BY Total_Ciudades DESC;[cite: 4]

-- CONSULTA 15: Promedio de duración por clasificación[cite: 4]
SELECT rating, AVG(length) AS Duracion_Promedio
FROM film
GROUP BY rating
ORDER BY Duracion_Promedio DESC;[cite: 4]