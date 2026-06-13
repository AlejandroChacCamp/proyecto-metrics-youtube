# Importación de librerías
import pandas as pd
import os
import psycopg2

# Construcción de rutas de archivos
base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))

keys_path = os.path.join(base_dir, "keys.txt")
info_videos = os.path.join(base_dir, "data", "info_videos_clean.csv")
info_canal = os.path.join(base_dir, "data", "info_canales_clean.csv")

# Lectura de los archivos CSV con Pandas
video = pd.read_csv(info_videos, encoding='utf-8-sig')
canal = pd.read_csv(info_canal, encoding='utf-8-sig')

# Termina el proceso si los dataframes viene vacío antes de abrir la conexión con la BD
if video.empty:
    print("ERROR: info_videos_clean.csv no tiene filas. Posible fallo silencioso en pasos anteriores.")
    exit(1)

if canal.empty:
    print("ERROR: info_canales_clean.csv no tiene filas. Posible fallo silencioso en pasos anteriores.")
    exit(1)

# Renombrar columnas de los DataFrames para que coincidan con el snake_case de la BD
video = video.rename(columns={'timestamp': 'tiempo_extraccion', 'channelTitle': 'channel_title','publishedAt': 'published_at', 'viewCount': 'view_count','likeCount': 'like_count', 'commentCount': 'comment_count'})

canal = canal.rename(columns={'timestamp_canal': 'tiempo_extraccion','title': 'channel_title','subscriberCount': 'subscriber_count','videoCount': 'video_count','viewCount': 'view_count'})

# Lectura del archivo de configuración keys.txt
config = {}
with open(keys_path, "r") as file:
    for linea in file:
        linea = linea.strip()
        if not linea or linea.startswith('#'): 
            continue
        if '=' in linea:
            clave, valor = linea.split('=', 1)
            config[clave.strip()] = valor.strip()

HOST = config.get('HOST')
PORT = config.get('PORT')
DATABASE = config.get('DATABASE')
DB_USER = config.get('DB_USER')
DB_PASSWORD = config.get('DB_PASSWORD')

# Conexión a PostgreSQL
try:
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        database=DATABASE,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    print("Conexión a PostgreSQL establecida correctamente.")
except psycopg2.Error as e:
    print(f"Error al conectar a PostgreSQL: {e}")
    exit(1)  # Finaliza el programa con código de error

# Transformación del DataFrame video a lista de tuplas
# Paso 1: convertir el DataFrame a un array de NumPy
array_videos = video.to_numpy()

# Paso 2: crear una lista vacía donde guardaremos las tuplas
datos_videos = []

# Paso 3: recorrer cada fila del array
for fila in array_videos:
    # Paso 4: convertir la fila (que es como una lista) en una tupla
    tupla_fila = tuple(fila)
    # Paso 5: agregar esa tupla a la lista
    datos_videos.append(tupla_fila)

# Preparación e inserción de datos en la tabla videos
insert_videos = """
    INSERT INTO videos 
    (tiempo_extraccion, channel_title, id, published_at, title, view_count, like_count, comment_count, duration_seconds, hora, dia_semana, nombre_dia, engagement_rate, tipo_video)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        view_count = EXCLUDED.view_count,
        like_count = EXCLUDED.like_count,
        comment_count = EXCLUDED.comment_count,
        engagement_rate = EXCLUDED.engagement_rate,
        tipo_video = EXCLUDED.tipo_video;
"""

# 3. Ejecutar la inserción para todas las filas y Confirmar los cambios
try:
    cur.executemany(insert_videos, datos_videos)
    conn.commit()
    print("Inserción completada exitosamente.")
except psycopg2.Error as e:
    print(f"Error durante la inserción: {e}")
    conn.rollback()  # deshace los cambios
    exit(1)

# VALIDACIONES DE CALIDAD SOBRE LOS DATOS

print("=== INICIO DE VALIDACIONES - TABLA VIDEOS ===\n")

# --------------------------------------------------
# 1. Cantidad de filas por canal
# --------------------------------------------------
print("1. Cantidad de videos por canal:")
cur.execute("""
    SELECT channel_title, COUNT(*) AS cantidad_videos
    FROM videos
    GROUP BY channel_title
    ORDER BY cantidad_videos DESC;
""")
rows = cur.fetchall()
if rows:
    for row in rows[:10]:
        print(f"Canal: {row[0]} - Videos: {row[1]}")
    if len(rows) > 10:
        print(f"... y {len(rows)-10} canales más.")
else:
    print("No hay datos en la tabla.")
print()

# --------------------------------------------------
# 2. Rango de fechas de publicación
# --------------------------------------------------
print("2. Rango de fechas de published_at:")
cur.execute("""
    SELECT MIN(published_at) AS fecha_minima, MAX(published_at) AS fecha_maxima
    FROM videos;
""")
row = cur.fetchone()
fecha_min, fecha_max = row
if fecha_min and fecha_max:
    print(f"Fecha más antigua: {fecha_min}")
    print(f"Fecha más reciente: {fecha_max}")
else:
    print("Tabla vacía.")
print()

# --------------------------------------------------
# 3. Verificar nulos en columnas críticas de videos
# --------------------------------------------------
print("3. Filas con nulos en channel_title, tiempo_extraccion o published_at (videos):")
cur.execute("""
    SELECT channel_title, tiempo_extraccion, published_at
    FROM videos
    WHERE channel_title IS NULL OR tiempo_extraccion IS NULL OR published_at IS NULL;
""")
rows = cur.fetchall()
if rows:
    print(f"{len(rows)} filas con nulos:")
    for row in rows[:5]:
        print(f"channel_title={row[0]}, tiempo_extraccion={row[1]}, published_at={row[2]}")
    if len(rows) > 5:
        print(f"... y {len(rows)-5} filas más.")
else:
    print("No se encontraron nulos en esas columnas.")
print()

print("\n=== FIN DE VALIDACIONES - TABLA VIDEOS ===")

# Transformación del DataFrame canal a lista de tuplas
array_canal = canal.to_numpy()

datos_canal = []

for fila_canal in array_canal:
    tupla_fila_canal = tuple(fila_canal)
    datos_canal.append(tupla_fila_canal)

# Inserción en la tabla canal_snapshots
insert_canales = """
    INSERT INTO canal_snapshots 
    (tiempo_extraccion, channel_title, subscriber_count, video_count, view_count)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (tiempo_extraccion, channel_title) DO NOTHING;
"""

try:
    cur.executemany(insert_canales, datos_canal)
    conn.commit()
    print("Inserción completada exitosamente.")
except psycopg2.Error as e:
    print(f"Error durante la inserción: {e}")
    conn.rollback()  # deshace los cambios
    exit(1)

# VALIDACIONES DE CALIDAD SOBRE LOS DATOS

print("=== INICIO DE VALIDACIONES - TABLA CANAL_SNAPSHOTS ===\n")

# --------------------------------------------------
# 1. Cantidad de snapshots por canal
# --------------------------------------------------
print("1. Cantidad de snapshots históricos por canal:")
cur.execute("""
    SELECT channel_title, COUNT(*) AS cantidad_snapshots
    FROM canal_snapshots
    GROUP BY channel_title
    ORDER BY cantidad_snapshots DESC;
""")
rows = cur.fetchall()
if rows:
    for row in rows[:10]:
        print(f"Canal: {row[0]} - Snapshots: {row[1]}")
    if len(rows) > 10:
        print(f"... y {len(rows)-10} canales más.")
else:
    print("No hay datos en la tabla.")
print()

# --------------------------------------------------
# 2. Verificar nulos en columnas críticas de canal_snapshots
# --------------------------------------------------
print("2. Filas con nulos en channel_title o tiempo_extraccion:")
cur.execute("""
    SELECT channel_title, tiempo_extraccion
    FROM canal_snapshots
    WHERE channel_title IS NULL OR tiempo_extraccion IS NULL;
""")
rows = cur.fetchall()
if rows:
    print(f"{len(rows)} filas con nulos:")
    for row in rows[:5]:
        print(f"      channel_title={row[0]}, tiempo_extraccion={row[1]}")
    if len(rows) > 5:
        print(f"... y {len(rows)-5} filas más.")
else:
    print("No se encontraron nulos en esas columnas.")
print()

print("\n=== FIN DE VALIDACIONES - TABLA CANAL_SNAPSHOTS ===")

# Cierre de la conexión
cur.close()
conn.close()


