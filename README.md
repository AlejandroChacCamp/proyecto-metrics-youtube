# YouTube Niche Analyzer (MVP)

Pipeline de datos end to end que extrae métricas de canales de YouTube,
las transforma, almacena en SQL y visualiza en Power BI.
Proyecto de aprendizaje para la transición hacia roles técnicos de datos.

## Objetivo
Analizar el rendimiento de 5 canales del nicho cultural/político peruano
para responder preguntas de negocio reales: ¿qué tipo de contenido genera
más engagement? ¿qué duración funciona mejor? ¿quién domina el nicho y por qué?

## Canales analizados
- [@Monitorfantasma](https://www.youtube.com/@Monitorfantasma) — Ensayo/Filosofía
- [@hugoxchugox](https://www.youtube.com/@hugoxchugox) — Historia/Documental
- [@ElRobotdePlaton](https://www.youtube.com/@ElRobotdePlaton) — Ciencia/Análisis crítico
- [@DiloNomas](https://www.youtube.com/@DiloNomas) — Crónica/Sociedad
- [@lahistoriade...1209](https://www.youtube.com/@lahistoriade...1209) — Documentales históricos peruanos

## Plan de Desarrollo
- [x] **Fase 1: Extracción** — YouTube API, paginación, manejo de errores, filtro de shorts
- [x] **Fase 2: Transformación** — Limpieza y normalización con Pandas
- [ ] **Fase 3: Almacenamiento** — Carga en SQL con actualización incremental
- [ ] **Fase 4: Visualización** — Dashboard en Power BI + automatización con Task Scheduler

## Tecnologías
- **Lenguaje:** Python (vía Anaconda)
- **Editor:** Jupyter Notebook → VS Code
- **Librerías:** `requests`, `isodate`, `pandas`, `sqlite3`, `os`, `time`, `datetime`
- **Visualización:** Power BI
- **API:** YouTube Data API v3

## Estructura del proyecto
```
proyecto-metrics-youtube/
│
│── 02_proyecto_principal/    
│   ├── data/
│   │   ├── info_videos_raw.csv  # Data cruda extraída por videos
│   │   ├── info_canales_raw.csv  # Data cruda extraída por canal
│   │   ├── info_videos_clean.csv  # Data procesada por videos
│   │   ├── info_canales_clean.csv  # Data procesa por canal
│   │
│   ├── scripts/
│   │   ├── 01_obtener_datos.ipynb   # Script de extracción Fase 1
│   │   ├── 02_Notebook_De_Pruebas.ipynb   # Borrador de pruebas
│   │   ├── 03_Procesamiento_datos.ipynb   # Script de limpieza de datos Fase 2
│   │
│   └── keys.txt                   # API keys (excluido via .gitignore)
│── .gitignore
│
└── README.md
```

## Datos extraídos (Fase 1)
Por cada canal se extraen los 400 videos más recientes (excluyendo shorts
y videos menores a 5 minutos) con las siguientes métricas:
`timestamp`, `channelTitle`, `id`, `publishedAt`, `title`, `viewCount`, `likeCount`,
`commentCount`, `duration`

También se extraen la información de cada canal:
`title`, `subscriberCount`, `videoCount`, `viewCount`

## Datos limpiados (Fase 2)
métricas por videos:
`timestamp`, `channelTitle`, `id`, `publishedAt`, `title`, `viewCount`, `likeCount`, `commentCount`, `duration_seconds`, `hora`, `dia_semana`, `nombre_dia`, `engagement_rate`, `tipo_video`

métricas por canal:
`timestamp_canal`, `title`, `subscriberCount`, `videoCount`, `viewCount`

## Decisiones de diseño y limitaciones

### Fase 1:
#### Decisiones de diseño
- Endpoint: playlistItems + videos.list en lugar de search.list. 50x más eficiente en cuota — 80 unidades vs 4,000 para 5 canales.
- Límite de videos: 400 por canal priorizando los más recientes. Videos de 2019-2023 quedan disponibles pero el filtro de fecha se delega a Power BI, no al pipeline.
- Filtro de contenido corto: umbral de 300 segundos para excluir shorts y teasers. Estático por ahora — en Fase 2 se evaluará complementarlo con detección de outliers con IQR.
- Manejo de errores: retry con 3 intentos y 5 segundos entre intentos. Si falla, el script guarda lo que tiene y continúa con el siguiente canal.
- Seguridad: API key en archivo .txt excluido via .gitignore. Lección aprendida en vivo — los outputs de Jupyter se incrustan en el .ipynb y se suben a GitHub.
- Dos CSVs separados: info_videos_youtube_raw.csv para métricas por video e info_canales_raw.csv para datos agregados del canal. Separación que refleja la futura estructura de tablas en SQL.

#### Limitaciones
- El Robot de Platón tiene shorts masivamente mezclados en su playlist de uploads — de 400 IDs extraídos solo 117 superan el filtro. Es la muestra más pequeña del análisis.
- La Historia de... tiene solo 29 videos públicos reales. Canal válido analíticamente por su alto promedio de views, pero con volumen limitado para patrones estadísticos.
- YouTube no distingue shorts de videos en playlistItems — el filtro de duración es el único mecanismo disponible sin acceso a endpoints privados.
- publishedAt incluye timezone en formato ISO 8601 — requiere parsing en Fase 2 antes de poder usarse para análisis temporal.
- Hasta la fase 1, no se contempla una extracción automatizada de datos lo suficientemente grande para armar una serie de tiempo. Esto se resolverá en la fase 4.

### Fase 2:
#### Decisiones de diseño
- duration original eliminada — duration_seconds suficiente para análisis y visualización
- Transformaciones en Pandas, no en Power Query — Power BI queda solo para DAX y time intelligence
- nombre_dia con diccionario manual — independiente del locale del sistema
- IQR aplicado a nivel de nicho (global), no por canal
- canal se acumula por ejecución — cada fila es una snapshot con timestamp_canal
- Extracción incremental delegada a Fase 3 — el pipeline actual extrae histórico completo

#### Limitaciones
- Limitación documentada en código: alta dispersión entre canales hace el IQR global imperfecto; IQR por canal descartado por muestra insuficiente en La Historia De... (29 videos). Revisar en P2

---
*Proyecto personal de aprendizaje como parte de la transición de Data Analyst
hacia roles técnicos de datos. Desarrollado con método incremental:
primero que funcione, luego refactorizar.*