-- Vista 1 — Evolución mensual del canal (pregunta 5)

CREATE OR REPLACE VIEW evolucion_mensual_canal AS
SELECT
    DATE_TRUNC('month', tiempo_extraccion) AS mes,
    channel_title AS nombre_canal,
    MAX(subscriber_count) AS seguidores_mes,
    MAX(video_count) AS videos_mes,
    MAX(view_count) AS vistas_mes
FROM canal_snapshots
GROUP BY DATE_TRUNC('month', tiempo_extraccion), channel_title;

-- Vista 2 — Momento del despegue (pregunta 6)

CREATE OR REPLACE VIEW momento_despegue AS
WITH max_semana AS (
SELECT
    DATE_TRUNC('week', tiempo_extraccion) AS semana,
    channel_title,
    MAX(subscriber_count) AS seguidores_semana,
    MAX(video_count) AS videos_semana,
    MAX(view_count) AS vistas_semana
FROM canal_snapshots
GROUP BY DATE_TRUNC('week', tiempo_extraccion), channel_title 
)
SELECT
    semana,
    channel_title AS nombre_canal,
    LAG(seguidores_semana, 1, NULL) OVER(PARTITION BY channel_title ORDER BY semana) AS suscriptores_semama_anterior,
    seguidores_semana - LAG(seguidores_semana, 1, NULL) OVER(PARTITION BY channel_title ORDER BY semana) AS diferencia_seguidores_semanal,
    LAG(videos_semana, 1, NULL) OVER(PARTITION BY channel_title ORDER BY semana) AS videos_semama_anterior,
    videos_semana - LAG(videos_semana, 1, NULL) OVER(PARTITION BY channel_title ORDER BY semana) AS diferencia_videos_semanal,
    LAG(vistas_semana, 1, NULL) OVER(PARTITION BY channel_title ORDER BY semana) AS vistas_semama_anterior,
    vistas_semana - LAG(vistas_semana, 1, NULL) OVER(PARTITION BY channel_title ORDER BY semana) AS diferencia_vistas_semanal
FROM max_semana;

-- Vista 3 — Frecuencia de publicación vs crecimiento (pregunta 9)

CREATE OR REPLACE VIEW frecuencia_publicacion_crecimiento AS
WITH conteo_videos_canal AS (
SELECT
    DATE_TRUNC('week', published_at) AS semana_video,
    channel_title,
    COUNT(published_at) AS cantidad_videos
FROM videos
GROUP BY channel_title, DATE_TRUNC('week', published_at)
),
crecimiento_canal AS (
SELECT
    DATE_TRUNC('week', tiempo_extraccion) AS semana_canal,
    channel_title,
    MAX(subscriber_count) AS seguidores_semana
FROM canal_snapshots
GROUP BY channel_title, DATE_TRUNC('week', tiempo_extraccion)
)
SELECT
    a.channel_title,
    a.cantidad_videos,
    b.semana_canal,
    b.seguidores_semana,
    LAG(b.seguidores_semana, 1, NULL) OVER(PARTITION BY b.channel_title ORDER BY b.semana_canal) AS suscriptores_semama_anterior,
    b.seguidores_semana - LAG(b.seguidores_semana, 1, NULL) OVER(PARTITION BY b.channel_title ORDER BY b.semana_canal) AS diferencia_seguidores_semanal
FROM conteo_videos_canal a
JOIN crecimiento_canal b ON a.channel_title = b.channel_title AND a.semana_video = b.semana_canal;