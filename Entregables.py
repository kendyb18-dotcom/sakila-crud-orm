import os
import urllib.parse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

print("Inicializando generación de gráficos de auditoría analítica...")

OUTPUT_DIR = r"C:\DC"
os.makedirs(OUTPUT_DIR, exist_ok=True)

USER = "root"
PASSWORD = urllib.parse.quote_plus("Contasena aqui") #Poner contraseña de MySQL en URL encoding
HOST = "127.0.0.1"
PORT = "3306"
DATABASE = "sakila"

#Crear Carpeta en disco C:/DC si no existe

engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")

# --- GRÁFICO 1: RESPALDO ASOCIADO A LA CONSULTA 15 ---
print(" -> Extrayendo datos según Consulta 15 (Promedio de duración por clasificación)...")
query_c15 = "SELECT rating, AVG(length) AS Duracion_Promedio FROM film GROUP BY rating ORDER BY Duracion_Promedio DESC;"
df_c15 = pd.read_sql(query_c15, con=engine)

plt.figure(figsize=(8, 4.5))
sns.barplot(data=df_c15, x='rating', y='Duracion_Promedio', hue='rating', palette="plasma", legend=False)
plt.title("Consulta 15: Promedio de Duración por Clasificación (Rating)")
plt.xlabel("Clasificación de Contenido (Rating)")
plt.ylabel("Duración Promedio (Minutos)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "1_campana_gauss_notas.png"), dpi=300)
plt.close()

# --- GRÁFICO 2: RESPALDO ASOCIADO A LA CONSULTA 8 ---
print(" -> Extrayendo datos según Consulta 8 (Cantidad de películas por categoría)...")
query_c8 = """
    SELECT c.name AS Categoria, COUNT(*) AS Total 
    FROM category c 
    INNER JOIN film_category fc ON c.category_id = fc.category_id 
    GROUP BY c.name 
    ORDER BY Total DESC;
"""
df_c8 = pd.read_sql(query_c8, con=engine)

plt.figure(figsize=(9, 5))
sns.barplot(data=df_c8, x='Total', y='Categoria', hue='Categoria', palette="viridis", legend=False)
plt.title("Consulta 8: Volumen Total de Películas por Categoría Cinematográfica")
plt.xlabel("Cantidad de Títulos Disponibles")
plt.ylabel("Género / Categoría")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "4_scatter_clicks_notas.png"), dpi=300)
plt.close()

print(f"Los outputs gráficos se han depositado directamente en:\n   {OUTPUT_DIR}")