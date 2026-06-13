import pandas as pd
import os
import isodate

base_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))

info_videos = os.path.join(base_dir, "data", "info_videos_raw.csv")
info_canal = os.path.join(base_dir, "data", "info_canales_raw.csv")

# Convertir tipos
video = pd.read_csv(info_videos,  encoding="utf-8")
video["timestamp"] = pd.to_datetime(video["timestamp"], format="%Y-%m-%d %H:%M:%S")
video["publishedAt"] = pd.to_datetime(video["publishedAt"], utc=True)
video["duration_seconds"] = video["duration"].map(lambda x: isodate.parse_duration(x).total_seconds())
video["duration_seconds"] = video["duration_seconds"].astype(int)
video.drop("duration", axis=1, inplace=True)

video["hora"] = video["publishedAt"].dt.hour
video["dia_semana"] = video["publishedAt"].dt.dayofweek

dias = {
    0: "Lunes",
    1: "Martes", 
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
}

video["nombre_dia"] = video["dia_semana"].map(dias)

# Manejar nulos
video.dropna(subset=["publishedAt"], inplace=True)
video["viewCount"] = video["viewCount"].fillna(0)
video["likeCount"] = video["likeCount"].fillna(0)
video["commentCount"] = video["commentCount"].fillna(0)

# Calcular columnas derivadas

def safe_div(num, den):
    if den != 0:
        return num/den
    else:
        return 0

video["engagement_rate"] = video.apply(
    lambda x: safe_div(x["likeCount"] + x["commentCount"], x["viewCount"]), axis=1
)


# Clasificación por nicho (IQR global).
""" Limitación: alta dispersión entre canales — el concepto de "viral" 
varía significativamente por canal (min views: Dilo Nomas=2,005 vs 
La Historia De...=70,026). """
# IQR por canal descartado por muestra insuficiente (La Historia De...=29 videos).
# Revisar ambos enfoques en P2 con mayor volumen y más canales.

Q1_global = video["viewCount"].quantile(0.25)
Q3_global = video["viewCount"].quantile(0.75)
IQR_global = Q3_global - Q1_global

limite_inferior_global = Q1_global - 1.5 * IQR_global
limite_superior_global = Q3_global + 1.5 * IQR_global

video["tipo_video"] = "normal"

video.loc[video["viewCount"] > limite_superior_global, "tipo_video"] = "viral"
video.loc[video["viewCount"] < limite_inferior_global, "tipo_video"] = "bajo"


canal = pd.read_csv(info_canal)

canal["timestamp_canal"] = pd.to_datetime(canal["timestamp_canal"], format="%Y-%m-%d %H:%M:%S")


video.to_csv(os.path.join(base_dir, "data", "info_videos_clean.csv"), index=False, encoding='utf-8-sig')
canal.to_csv(os.path.join(base_dir, "data", "info_canales_clean.csv"), index=False, encoding='utf-8-sig')
