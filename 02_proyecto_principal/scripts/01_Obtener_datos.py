import requests
import json
import os
import time
import csv
from datetime import datetime
import isodate

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(script_dir, ".."))

keys_path = os.path.join(base_dir, "keys.txt")
info_videos = os.path.join(base_dir, "data", "info_videos_raw.csv")
info_canal = os.path.join(base_dir, "data", "info_canales_raw.csv")

print(base_dir)

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

API_KEY = config.get('YOUTUBE_API_KEY')

def hacer_peticion(url, params, max_retries=3):
    """
    Realiza una petición GET con reintentos en caso de error.
    
    Args:
        url (str): La URL de la API.
        params (dict): Parámetros de la consulta.
        max_retries (int): Número máximo de intentos.
    
    Returns:
        dict or None: El JSON de la respuesta si es exitosa, None si falla tras reintentos.
    """
    for intento in range(1, max_retries + 1):
        try:
            respuesta = requests.get(url, params=params)
            respuesta.raise_for_status()  # Lanza excepción si el código HTTP no es 200
            return respuesta.json()       # Si llegó aquí, todo bien
        except requests.exceptions.RequestException as e:
            print(f"Intento {intento} falló: {e}")
            if intento < max_retries:
                print(f"Esperando 5 segundos antes de reintentar...")
                time.sleep(5)
            else:
                print(f"Fallo después de {max_retries} intentos.")
                return None

HANDLE = ["@Monitorfantasma", "@hugoxchugox", "@ElRobotdePlaton", "@DiloNomas", "@lahistoriade...1209"]

detalles_videos = []
detalles_canal = []
timestamp_canal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
for handle in HANDLE:
    params = {
        "part" : "contentDetails,statistics,snippet",
        "forHandle": handle,
        "key": API_KEY
    }

    channel_url = "https://www.googleapis.com/youtube/v3/channels"

    respuesta = hacer_peticion(channel_url, params = params)

    if respuesta is None:
        print(f"Error crítico: no se pudo obtener datos del canal {handle} después de reintentos.")
        exit(1)

    if not respuesta.get("items"):
        print("El canal no existe o no tiene datos públicos.")
        exit(1)

    uploads_playlist_id = respuesta["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    #print(uploads_playlist_id)

    detalle_canal = {}
    detalle_canal["timestamp_canal"] = timestamp_canal
    detalle_canal["title"] = respuesta["items"][0]["snippet"]["title"]
    detalle_canal["subscriberCount"] = respuesta["items"][0]["statistics"]["subscriberCount"]
    detalle_canal["videoCount"] = respuesta["items"][0]["statistics"]["videoCount"]
    detalle_canal["viewCount"] = respuesta["items"][0]["statistics"]["viewCount"]

    detalles_canal.append(detalle_canal)

    video_id_lista = []
    next_page_token = None

    while True:

        faltantes = 400 - len(video_id_lista)

        if faltantes <= 0:
            break

        result_a_llamar = min(faltantes, 50)

        params_videos = {
            "part": "snippet",
            "playlistId": uploads_playlist_id,
            "maxResults": result_a_llamar,
            "key": API_KEY
        }
        if next_page_token:
            params_videos["pageToken"] = next_page_token
        
        lista_videos_url = "https://www.googleapis.com/youtube/v3/playlistItems"

        
        lista_videos_data = hacer_peticion(lista_videos_url, params = params_videos)

        if lista_videos_data is None:
            print("Error crítico: no se pudo obtener la página después de reintentos.")
            break

        try:
            items = lista_videos_data["items"]
        except KeyError:
            print("La respuesta no contiene 'items'. Estructura inesperada:")
            print(lista_videos_data)
            break
        
        for item in items:
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_id_lista.append(video_id)

        next_page_token = lista_videos_data.get("nextPageToken")
        if not next_page_token or len(video_id_lista) == 400:
            break

    #print(f"Total videos: {len(video_id_lista)}")
    #print(video_id_lista)

    timestamp_extraccion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    for inicio in range(0, len(video_id_lista), 50):
        bloque = video_id_lista[inicio:inicio+50]
        ids_str = ",".join(bloque)

        params_metricas = {
            "part": "contentDetails,snippet,statistics",
            "id": ids_str,
            "key": API_KEY
        }

        metricas_url = "https://www.googleapis.com/youtube/v3/videos"

        lista_metricas_url = hacer_peticion(metricas_url, params=params_metricas)

        if "items" not in lista_metricas_url:
            print("Advertencia: respuesta sin items", lista_metricas_url)
            continue
        
        for item in lista_metricas_url["items"]:
            detalle_por_video = {}
            detalle_por_video["timestamp"] = timestamp_extraccion
            detalle_por_video["channelTitle"] = item["snippet"].get("channelTitle", None)
            detalle_por_video["id"] = item.get("id", None)
            detalle_por_video["publishedAt"] = item["snippet"].get("publishedAt", None)
            detalle_por_video["title"] = item["snippet"].get("title", None)
            detalle_por_video["viewCount"] = item["statistics"].get("viewCount", 0)
            detalle_por_video["likeCount"] = item["statistics"].get("likeCount", 0)
            detalle_por_video["commentCount"] = item["statistics"].get("commentCount", 0)
            detalle_por_video["duration"] = item["contentDetails"].get("duration", None)

            if detalle_por_video["duration"]:
                try:
                    duracion_segundos = isodate.parse_duration(detalle_por_video["duration"]).total_seconds()
                except:
                    duracion_segundos = 0
            else:
                duracion_segundos = 0

            if duracion_segundos >= 300:
            
                detalles_videos.append(detalle_por_video)

    #print(detalles_videos)
    time.sleep(1)

campos = ["timestamp", "channelTitle","id","publishedAt", "title", "viewCount", "likeCount", "commentCount", "duration"]

with open(info_videos, 'w', newline='', encoding='utf-8') as archivo:
    writer = csv.DictWriter(archivo, fieldnames=campos)
    writer.writeheader()           # escribe la fila de encabezados
    writer.writerows(detalles_videos)   # escribe todas las filas de una vez

campos_canal = ["timestamp_canal", "title","subscriberCount", "videoCount", "viewCount"]

archivo_canal_existe = os.path.isfile(info_canal) and os.path.getsize(info_canal)

with open(info_canal, 'a', newline='', encoding='utf-8') as archivo_canal:
    writer = csv.DictWriter(archivo_canal, fieldnames=campos_canal)
    if not archivo_canal_existe:
        writer.writeheader()           # escribe la fila de encabezados
    writer.writerows(detalles_canal)   # escribe todas las filas de una vez