import urllib
from sqlalchemy import create_engine, text

# Conexión al servidor (SIN especificar la base de datos OULAD)
server = r'DESKTOP-2DOU7M7\SQLEXPRESS'

params = urllib.parse.quote_plus(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server};'
    f'Trusted_Connection=yes;'
)

engine = create_engine(
    f'mssql+pyodbc:///?odbc_connect={params}'
)

def eliminar_base_datos():

    with engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as conn:

        # Verificar si existe
        existe = conn.execute(text("""
            SELECT COUNT(*)
            FROM sys.databases
            WHERE name = 'OULAD'
        """)).scalar()

        if existe:

            print("Eliminando conexiones activas...")

            conn.execute(text("""
                ALTER DATABASE OULAD
                SET SINGLE_USER
                WITH ROLLBACK IMMEDIATE
            """))

            print("Eliminando base de datos OULAD...")

            conn.execute(text("""
                DROP DATABASE OULAD
            """))

            print("✓ Base de datos OULAD eliminada correctamente.")

        else:
            print("⚠ La base de datos OULAD no existe.")

if __name__ == "__main__":
    eliminar_base_datos()