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
- [x] **Fase 3: Almacenamiento** — Carga en SQL con actualización incremental
- [x] **Fase 4: Visualización** — Dashboard en Power BI
- [ ] **Fase 5: Automatización** — Automatización con Task Scheduler

## Tecnologías
- **Lenguaje:** Python (vía Anaconda)
- **Editor:** Jupyter Notebook → VS Code
- **Librerías:** `requests`, `isodate`, `pandas`, `os`, `time`, `datetime`, `psycopg2`
- **Base de datos:** PostgreSQL, DBeaver
- **Visualización:** Power BI Desktop
- **Diseño:** Canva (fondos de páginas del dashboard)
- **API:** YouTube Data API v3

## Estructura del proyecto
```
proyecto-metrics-youtube/
│
│── 02_proyecto_principal/    
│   ├── data/
│   │   ├── info_videos_raw.csv         # Data cruda extraída por videos
│   │   ├── info_canales_raw.csv        # Data cruda extraída por canal
│   │   ├── info_videos_clean.csv       # Data procesada por videos
│   │   ├── info_canales_clean.csv      # Data procesada por canal
│   │
│   ├── scripts/
│   │   ├── 01_obtener_datos.ipynb      # Script de extracción Fase 1
│   │   ├── 02_Notebook_De_Pruebas.ipynb   # Borrador de pruebas
│   │   ├── 03_Procesamiento_datos.ipynb   # Script de limpieza de datos Fase 2
│   │   ├── 04_Carga_datos_Postgres.ipynb  # Script de carga de datos Fase 3
│   │ 
│   ├── sql/
│   │   ├── schema.sql                  # Creación de tablas, tipos de datos e índices
│   │   ├── views.sql                   # Lógica de negocio centralizada en 3 vistas
│   │
│   ├── dashboard/
│   │   └── youtube_niche_analyzer.pbix # Dashboard Power BI Fase 4
│   │
│   └── keys.txt                        # API keys (excluido via .gitignore)
│
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

## Almacenamiento de datos (Fase 3)
En este punto se decidió estandarizar los nombres de las columnas a snake_case

## Dashboard (Fase 4)
El dashboard responde 7 preguntas de negocio distribuidas en 4 páginas:

- **Página 1 — Vista General del Nicho:** Tabla comparativa de canales con suscriptores, vistas, engagement rate y ratio views/suscriptores. KPIs del nicho completo con indicadores de crecimiento MoM y YoY.
- **Página 2 — Rendimiento de Contenido:** Scatter plot views vs likes por video con tamaño de burbuja dinámico (comentarios, engagement o duración). Identifica videos virales y outliers.
- **Página 3 — Tendencias Temporales:** Evolución mensual de vistas y videos publicados. Crecimiento de suscriptores por canal desde el inicio del pipeline.
- **Página 4 — Calendario de Publicación:** Heatmap de días y horas cruzado con rendimiento o actividad. Identifica los momentos de mayor impacto por canal.

Todas las páginas incluyen tooltips personalizados y navegación entre páginas.

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
- Hasta la fase 1, no se contempla una extracción automatizada de datos lo suficientemente grande para armar una serie de tiempo. Esto se resolverá en la fase 5.

### Fase 2:
#### Decisiones de diseño
- duration original eliminada — duration_seconds suficiente para análisis y visualización.
- Transformaciones en Pandas, no en Power Query — Power BI queda solo para DAX y time intelligence.
- nombre_dia con diccionario manual — independiente del locale del sistema
- IQR aplicado a nivel de nicho (global), no por canal.
- canal se acumula por ejecución — cada fila es una snapshot con timestamp_canal.
- Extracción incremental delegada a Fase 3 — el pipeline actual extrae histórico completo.

#### Limitaciones
- Limitación documentada en código: alta dispersión entre canales hace el IQR global imperfecto; IQR por canal descartado por muestra insuficiente en La Historia De... (29 videos). Revisar en P2

### Fase 3:
#### Decisiones de diseño
- Motor elegido: PostgreSQL sobre SQLite — alineación con stack de mercado y portabilidad futura.
- Para la tabla videos: id de videos como PRIMARY KEY natural — inmutable, generado por YouTube.
- Para la tabla canal_snapshots: Surrogate SERIAL como PK en canal_snapshots — evita fragilidad de PK compuesta por colisión de timestamps.
- Índice compuesto sobre (channel_title, dia_semana, hora) en tabla videos — optimiza queries de la Página 4 del dashboard (heatmap).
- Validaciones automáticas en el script de carga — conteo por canal, rango de fechas, nulos en columnas críticas.
- Parser unificado de keys.txt entre Fase 1 y Fase 3 — configuración centralizada.
- Encoding utf-8-sig en to_csv Fase 2 y read_csv Fase 3 — resuelve corrupción de caracteres especiales en español.
- Tabla videos queda como snapshot más reciente, cada vez que se llame a la API esta tabla mostrará solo la información más reciente - ON CONFLICT ... DO UPDATE.
- Tabla canales guarda historico, para esto se agrega ADD CONSTRAINT unique_canal_snapshot UNIQUE (tiempo_extraccion, channel_title) - ON CONFLICT (tiempo_extraccion, channel_title) DO NOTHING.

    **Vistas creadas:**
- evolucion_mensual_canal — responde pregunta 5 (evolución mensual de suscriptores, videos y vistas por canal usando DATE_TRUNC sobre canal_snapshots)
- momento_despegue — responde pregunta 6 (detecta incremento semanal de métricas usando LAG y CTE sobre canal_snapshots)
- frecuencia_publicacion_crecimiento — responde pregunta 9 (cruza frecuencia de publicación de videos con crecimiento de suscriptores usando JOIN entre videos y canal_snapshots)


#### Limitaciones
- Se descarta la implementación de NLP para responder a las preguntas 3 y 10:

        Pregunta 3: ¿Hay palabras en los títulos que se repiten en los videos más exitosos?

        Pregunta 10: ¿Qué temas o formatos tienen alta demanda (engagement) pero poca oferta (pocos videos)

- Esta limitación responde al costo de implementar NLP versus su utilidad para mi objetivo profesional, considerando que implementarlo podría tomarme en este momento un mes. Se reserva la implementación de este feature para una próxima iteración de este MVP

- Las vistas usan datos desde el inicio del proyecto — no hay historia pre-Fase 1 en canal_snapshots

### Fase 4:
#### Decisiones de diseño
- Modelo de datos centralizado en Dim_Canal — tabla de dimensión dinámica generada desde videos via Power Query. Si se agregan canales, aparecen automáticamente al refrescar.
- Tabla Calendario DAX con jerarquía año/mes/día en español — base para time intelligence en todas las páginas.
- fecha_publicacion como columna DATE derivada en Power Query — resuelve la incompatibilidad entre TIMESTAMPTZ de PostgreSQL y la tabla Calendario. published_at se preserva en la base de datos para no perder el dato original.
- Tamaño de burbuja dinámico en scatter (Página 2) y métrica dinámica en heatmap (Página 4) implementados con el patrón: tabla desconectada → medida SWITCH → visual con formato condicional. Field Parameters nativos de Power BI no aceptan medidas dinámicas en el campo Size del scatter ni en formato condicional.
- Heatmap implementado con Matrix + formato condicional por gradiente — sin dependencias de visuals externos de AppSource.
- Indicadores de crecimiento MoM/YoY en KPIs con lógica de filtros explícita via ISFILTERED:

    | Año | Mes | Comportamiento |
    |-----|-----|----------------|
    | ✗ | ✗ | Mensaje guía al usuario |
    | ✓ | ✗ | Crecimiento total del año vs. año anterior |
    | ✗ | ✓ | Mensaje guía al usuario |
    | ✓ | ✓ | MoM + YoY del mes seleccionado |

- Avg Engagement Rate expresado en puntos porcentuales (pp) en los indicadores de crecimiento — más preciso que crecimiento relativo para comparar porcentajes.
- Identidad visual: paleta `#F5F5F5` / `#FFFFFF` / `#CC0000` / `#1C1C1C`, fondos diseñados en Canva, rojo reservado como acento en formato condicional y gradientes.

#### Limitaciones
- **Clave de relación basada en string:** El modelo usa channel_title (TEXT) como clave de relación entre todas las tablas. La solución correcta es un canal_id entero como clave surrogate. Pendiente para P2. Mitigación actual: channel_title se normaliza desde la YouTube Data API y no ha variado en ninguna extracción del MVP.

- **Historial insuficiente en canal_snapshots:** La tabla tiene solo 2 snapshots por canal (abril y mayo 2026) por ejecución manual del pipeline. Los indicadores de crecimiento de suscriptores y vistas del canal comparan dos puntos, no una tendencia. Se resuelve automáticamente en Fase 5 con la automatización del pipeline.

---
*Proyecto personal de aprendizaje como parte de la transición de Data Analyst
hacia roles técnicos de datos. Desarrollado con método incremental:
primero que funcione, luego refactorizar.*