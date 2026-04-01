# YouTube Channel Intelligence Dashboard

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
- [ ] **Fase 2: Transformación** — Limpieza y normalización con Pandas
- [ ] **Fase 3: Almacenamiento** — Carga en SQL con actualización incremental
- [ ] **Fase 4: Visualización** — Dashboard en Power BI + automatización con Task Scheduler

## Tecnologías
- **Lenguaje:** Python (vía Anaconda)
- **Editor:** Jupyter Notebook → VS Code
- **Librerías:** `requests`, `isodate`, `pandas`, `sqlite3`
- **Visualización:** Power BI
- **API:** YouTube Data API v3

## Estructura del proyecto
```
proyecto-metrics-youtube/
│
│── 02_proyecto_principal/    
│   ├── scripts/
│   │   ├── 01_obtener_datos.ipynb   # Script de extracción Fase 1
│   │   ├── 02_Notebook_De_Pruebas.ipynb   # Borrador de pruebas
│   ├── info_videos_youtube_raw.csv  # Data cruda extraída por videos
│   ├── info_videos_youtube_raw.csv  # Data cruda extraída por canal   
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
---
*Proyecto personal de aprendizaje como parte de la transición de Data Analyst
hacia roles técnicos de datos. Desarrollado con método incremental:
primero que funcione, luego refactorizar.*