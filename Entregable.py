import os
import sys
import urllib.parse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis, ttest_ind
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine, text

# ==========================================
# 1. CONFIGURACIÓN GENERAL
# ==========================================
SERVER = r'DESKTOP-2DOU7M7\SQLEXPRESS'
DATABASE = 'OULAD'
RUTA_CSV = r'C:\data' # Cambia esto si tus CSV están en otra ruta

# ==========================================
# 2. CREACIÓN DE BASE DE DATOS (MASTER)
# ==========================================
print("=== FASE 1: VERIFICACIÓN/CREACIÓN DE BASE DE DATOS ===")

params_master = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"Trusted_Connection=yes;"
)

engine_master = create_engine(f"mssql+pyodbc:///?odbc_connect={params_master}")

with engine_master.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
    existe_bd = conn.execute(text(f"""
        SELECT COUNT(*) FROM sys.databases WHERE name = '{DATABASE}'
    """)).scalar()

    if existe_bd:
        print(f"✓ Base de datos '{DATABASE}' ya existe.")
    else:
        print(f"⚠ Base de datos '{DATABASE}' no existe. Creando...")
        conn.execute(text(f"CREATE DATABASE {DATABASE}"))
        print(f"✓ Base de datos '{DATABASE}' creada exitosamente.")

# ==========================================
# 3. CONEXIÓN A LA BASE DE DATOS 'OULAD'
# ==========================================
params_db = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"Trusted_Connection=yes;"
)

# fast_executemany=True es crucial para que pandas inserte rápido en SQL Server
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params_db}", fast_executemany=True)

# ==========================================
# 4. CREACIÓN DE TABLAS Y RESTRICCIONES (DDL)
# ==========================================
print("\n=== FASE 2: VERIFICACIÓN/CREACIÓN DE ESTRUCTURAS (DDL) ===")

tablas = {
    "courses": """
        CREATE TABLE courses(
            code_module VARCHAR(10) NOT NULL,
            code_presentation VARCHAR(10) NOT NULL,
            module_presentation_length INT
        )
    """,
    "assessments": """
        CREATE TABLE assessments(
            id_assessment INT NOT NULL,
            code_module VARCHAR(10),
            code_presentation VARCHAR(10),
            assessment_type VARCHAR(20),
            date INT,
            weight FLOAT
        )
    """,
    "studentInfo": """
        CREATE TABLE studentInfo(
            code_module VARCHAR(10) NOT NULL,
            code_presentation VARCHAR(10) NOT NULL,
            id_student BIGINT NOT NULL,
            gender VARCHAR(10),
            region VARCHAR(100),
            highest_education VARCHAR(100),
            imd_band VARCHAR(50),
            age_band VARCHAR(50),
            num_of_prev_attempts INT,
            studied_credits INT,
            disability VARCHAR(10),
            final_result VARCHAR(50)
        )
    """,
    "studentRegistration": """
        CREATE TABLE studentRegistration(
            code_module VARCHAR(10),
            code_presentation VARCHAR(10),
            id_student BIGINT,
            date_registration INT,
            date_unregistration INT
        )
    """,
    "studentAssessment": """
        CREATE TABLE studentAssessment(
            id_assessment INT,
            id_student BIGINT,
            date_submitted INT,
            is_banked INT,
            score FLOAT
        )
    """,
    "studentVle": """
        CREATE TABLE studentVle(
            code_module VARCHAR(10),
            code_presentation VARCHAR(10),
            id_student BIGINT,
            id_site INT,
            date INT,
            sum_click INT
        )
    """,
    "vle": """
        CREATE TABLE vle(
            id_site INT NOT NULL,
            code_module VARCHAR(10) NOT NULL,
            code_presentation VARCHAR(10) NOT NULL,
            activity_type VARCHAR(100),
            week_from INT,
            week_to INT
        )
    """
}

primary_keys = [
    ("PK_courses", """ALTER TABLE courses ADD CONSTRAINT PK_courses PRIMARY KEY (code_module, code_presentation)"""),
    ("PK_assessments", """ALTER TABLE assessments ADD CONSTRAINT PK_assessments PRIMARY KEY (id_assessment)"""),
    ("PK_studentInfo", """ALTER TABLE studentInfo ADD CONSTRAINT PK_studentInfo PRIMARY KEY (id_student, code_module, code_presentation)"""),
    ("PK_vle", """ALTER TABLE vle ADD CONSTRAINT PK_vle PRIMARY KEY (id_site, code_module, code_presentation)""")
]

foreign_keys = [
    ("FK_assessments_courses", """ALTER TABLE assessments ADD CONSTRAINT FK_assessments_courses FOREIGN KEY (code_module, code_presentation) REFERENCES courses(code_module, code_presentation)"""),
    ("FK_studentInfo_courses", """ALTER TABLE studentInfo ADD CONSTRAINT FK_studentInfo_courses FOREIGN KEY (code_module, code_presentation) REFERENCES courses(code_module, code_presentation)""")
]

with engine.begin() as conn:
    for nombre_tabla, ddl in tablas.items():
        existe = conn.execute(text(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{nombre_tabla}'")).scalar()
        if existe:
            print(f"  [-] Tabla {nombre_tabla} ya existe.")
        else:
            conn.execute(text(ddl))
            print(f"  [+] Tabla {nombre_tabla} creada.")

    for nombre_pk, sql_pk in primary_keys:
        existe = conn.execute(text(f"SELECT COUNT(*) FROM sys.key_constraints WHERE name = '{nombre_pk}'")).scalar()
        if not existe:
            conn.execute(text(sql_pk))
            print(f"  [+] PK {nombre_pk} creada.")

    for nombre_fk, sql_fk in foreign_keys:
        existe = conn.execute(text(f"SELECT COUNT(*) FROM sys.foreign_keys WHERE name = '{nombre_fk}'")).scalar()
        if not existe:
            conn.execute(text(sql_fk))
            print(f"  [+] FK {nombre_fk} creada.")

    # CREACIÓN DE LA VISTA
    vista_sql = """
        CREATE OR ALTER VIEW dbo.vw_FullDomain_Assess_VLE AS
        SELECT
            sa.id_student,
            a.code_module,
            a.code_presentation,
            a.assessment_type,
            sa.score,
            SUM(sv.sum_click) AS total_clicks
        FROM studentAssessment sa
        INNER JOIN assessments a
            ON sa.id_assessment = a.id_assessment
        LEFT JOIN studentVle sv
            ON sa.id_student = sv.id_student
            AND a.code_module = sv.code_module
            AND a.code_presentation = sv.code_presentation
        GROUP BY
            sa.id_student,
            a.code_module,
            a.code_presentation,
            a.assessment_type,
            sa.score;
    """
    conn.execute(text(vista_sql))
    print("  [+] Vista 'vw_FullDomain_Assess_VLE' verificada/creada.")

# ==========================================
# 5. FUNCIONES ETL
# ==========================================
def extraer_y_limpiar(ruta_csv):
    print(f"  -> Extrayendo y limpiando: {os.path.basename(ruta_csv)}...")
    df = pd.read_csv(ruta_csv)
    
    df.dropna(how='all', inplace=True)
    
    if 'score' in df.columns:
        df['score'] = df['score'].fillna(0)
        
    return df

def cargar_datos(df, nombre_tabla):
    num_registros = len(df)
    print(f"  -> Iniciando carga en '{nombre_tabla}' ({num_registros} registros detectados)...")
    
    lote = 200000 
    
    for i in range(0, num_registros, lote):
        lote_df = df.iloc[i:i+lote]
        lote_df.to_sql(nombre_tabla, con=engine, if_exists='append', index=False)
        
        registros_procesados = min(i + lote, num_registros)
        porcentaje = (registros_procesados / num_registros) * 100
        
        longitud_barra = 40
        bloques_llenos = int((porcentaje / 100) * longitud_barra)
        barra = '█' * bloques_llenos + '-' * (longitud_barra - bloques_llenos)
        
        sys.stdout.write(f"\r     [{barra}] {porcentaje:.1f}% ({registros_procesados}/{num_registros})")
        sys.stdout.flush()
        
    print(f"\n  ✓ ¡'{nombre_tabla}' cargada exitosamente!\n")
    return num_registros

# ==========================================
# 6. ORQUESTADOR PIPELINE
# ==========================================
def ejecutar_pipeline():
    print("\n=== FASE 3: INICIANDO PIPELINE ETL (CARGA DE DATOS) ===")
    
    archivos_tablas = {
        'courses.csv': 'courses',
        'vle.csv': 'vle',
        'assessments.csv': 'assessments',
        'studentInfo.csv': 'studentInfo',
        'studentAssessment.csv': 'studentAssessment',
        'studentVle.csv': 'studentVle',
        'studentRegistration.csv': 'studentRegistration'
    }
    
    total_registros_insertados = 0

    for archivo, tabla in archivos_tablas.items():
        try:
            ruta_completa = os.path.join(RUTA_CSV, archivo)
            if os.path.exists(ruta_completa):
                df_limpio = extraer_y_limpiar(ruta_completa)
                registros = cargar_datos(df_limpio, tabla)
                total_registros_insertados += registros
            else:
                print(f"  [⚠] ADVERTENCIA: No se encontró el archivo '{archivo}' en {RUTA_CSV}\n")
                
        except Exception as e:
            print(f"  [✖] ERROR: Falló el procesamiento de {archivo}. Detalle: {e}\n")

    print("=====================================================")
    print(f"🎉 PIPELINE FINALIZADO. Total de registros cargados: {total_registros_insertados}")
    print("=====================================================")

# ==========================================
# 7. ANÁLISIS DE DATOS Y MACHINE LEARNING
# ==========================================
def ejecutar_analisis():
    print("\n=== FASE 4: ANÁLISIS DE DATOS Y MACHINE LEARNING ===")
    try:
        # Extraer el FullDomain (Usando TOP 100,000 para optimizar el EDA)
        print("Extrayendo datos de la vista 'vw_FullDomain_Assess_VLE'...")
        query = "SELECT TOP 100000 * FROM vw_FullDomain_Assess_VLE ORDER BY NEWID()"
        df = pd.read_sql(query, engine)
        
        print(f"Total de registros a graficar/analizar: {len(df)}")
        
        # 1. Campana de Gauss, Asimetría y Curtosis
        print("Generando Gráfico: Distribución de Calificaciones...")
        plt.figure(figsize=(8, 5))
        sns.histplot(df['score'].dropna(), kde=True, color='blue', bins=20) 
        plt.title('Distribución de Calificaciones (Scores)')
        plt.show(block=False)

        print(f"Asimetría (Skewness): {skew(df['score'].dropna()):.4f}")
        print(f"Curtosis (Kurtosis): {kurtosis(df['score'].dropna()):.4f}")

        # 2. Boxplot y Dispersión
        # Filtramos nulos de score y assessment_type para evitar errores
        df_graficos = df.dropna(subset=['assessment_type', 'score']).copy()
        df_graficos['total_clicks'] = df_graficos['total_clicks'].fillna(0)

        print("Generando Gráfico: Boxplot de Clicks...")
        plt.figure(figsize=(8, 5))
        sns.boxplot(x='assessment_type', y='total_clicks', data=df_graficos)
        plt.title('Boxplot: Clicks en VLE por Tipo de Evaluación')
        plt.show(block=False)

        print("Generando Gráfico: Dispersión...")
        plt.figure(figsize=(8, 5))
        sns.scatterplot(x='total_clicks', y='score', data=df_graficos, alpha=0.5)
        plt.title('Dispersión: Total de Clicks vs Calificación')
        plt.show(block=False)

        # 3. Matriz de Correlación
        print("Generando Matriz de Correlación...")
        plt.figure(figsize=(6, 4))
        matriz_corr = df_graficos[['score', 'total_clicks']].corr()
        sns.heatmap(matriz_corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Matriz de Correlación')
        plt.show(block=False)

        # 4. Creación de Campo Ordinal y Tabla Pivot
        print("\nGenerando Campo Ordinal y Tabla Pivot...")
        # Convierte las notas continuas en 3 categorías ordinales (Bajo, Medio, Alto)
        df_graficos['score_ordinal'] = pd.qcut(df_graficos['score'], q=3, labels=[1, 2, 3]) 
        
        pivot_df = pd.pivot_table(df_graficos, values='total_clicks', index='assessment_type', columns='score_ordinal', aggfunc='mean')
        
        print("\n--- Tabla Pivot (Promedio de Clicks por Tipo de Evaluación y Nivel de Nota) ---")
        print(pivot_df)
        print("-------------------------------------------------------------------------\n")

        # 5. Pruebas de Hipótesis (T-test)
        print("Ejecutando Prueba de Hipótesis (T-test)...")
        media_clicks = df_graficos['total_clicks'].median()
        grupo_alto = df_graficos[df_graficos['total_clicks'] >= media_clicks]['score']
        grupo_bajo = df_graficos[df_graficos['total_clicks'] < media_clicks]['score']

        t_stat, p_val = ttest_ind(grupo_alto, grupo_bajo)
        print(f"Estadístico T: {t_stat:.2f}")
        print(f"P-value: {p_val}")

        # 6. Modelo de Machine Learning y Matriz de Confusión
        print("\nEntrenando Modelo de Regresión Logística...")
        df_modelo = df_graficos.copy()
        df_modelo['aprueba'] = (df_modelo['score'] >= 60).astype(int)

        X = df_modelo[['total_clicks']]
        y = df_modelo['aprueba']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        modelo = LogisticRegression()
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)

        print("Generando Matriz de Confusión...")
        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Reprueba', 'Aprueba'])
        disp.plot(cmap='Blues')
        plt.title('Matriz de Confusión')
        plt.show() # Este último plt.show() bloquea la ejecución hasta que cierres las ventanas
        
    except Exception as e:
        print(f"\n[✖] ERROR en el análisis: {e}")
        print("Asegúrate de que la vista 'vw_FullDomain_Assess_VLE' haya sido creada en SQL Server.")

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == '__main__':
    # 1. Ejecutar el ETL
    ejecutar_pipeline()
    
    # 2. Ejecutar el Análisis
    ejecutar_analisis()