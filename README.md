# YouTube Niche Analyzer (MVP)

End-to-end data pipeline that extracts YouTube channel metrics,
transforms them, stores them in SQL, and visualizes them in Power BI.
Learning project built as part of a transition toward technical data roles.

## Goal
Analyze the performance of 5 channels in the Peruvian cultural/political niche
to answer real business questions:
- **Who dominates the niche?** Channel comparison by subscribers, views, engagement, and conversion.
- **Which videos drive the most impact?** Identify outliers and high-performance patterns.
- **Is the channel growing, stagnant, or declining?** Monthly evolution of activity and audience.
- **When is the best time to publish?** Performance and activity distribution by day and hour.

## Channels analyzed
- [@Monitorfantasma](https://www.youtube.com/@Monitorfantasma) — Essay/Philosophy
- [@hugoxchugox](https://www.youtube.com/@hugoxchugox) — History/Documentary
- [@ElRobotdePlaton](https://www.youtube.com/@ElRobotdePlaton) — Science/Critical Analysis
- [@DiloNomas](https://www.youtube.com/@DiloNomas) — Chronicle/Society
- [@lahistoriade...1209](https://www.youtube.com/@lahistoriade...1209) — Peruvian historical documentaries

## Development Plan
- [x] **Phase 1: Extraction** — YouTube API, pagination, error handling, shorts filtering
- [x] **Phase 2: Transformation** — Cleaning and normalization with Pandas
- [x] **Phase 3: Storage** — SQL loading with incremental updates
- [x] **Phase 4: Visualization** — Power BI dashboard
- [x] **Phase 5: Automation** — Automated pipeline with Task Scheduler and logging

## Tech Stack
- **Language:** Python (via Anaconda)
- **Editor:** Jupyter Notebook → VS Code
- **Libraries:** `requests`, `isodate`, `pandas`, `os`, `time`, `datetime`, `psycopg2`, `logging`, `subprocess`
- **Database:** PostgreSQL, DBeaver
- **Visualization:** Power BI Desktop
- **Design:** Canva (dashboard page backgrounds)
- **API:** YouTube Data API v3
- **Automation:** Windows Task Scheduler

## Project Structure
```
proyecto-metrics-youtube/
│
│── 02_proyecto_principal/
│   ├── run_pipeline.py             # Orchestrator — single entry point for automation
│   │
│   ├── data/
│   │   ├── info_videos_raw.csv         # Raw data extracted per video
│   │   ├── info_canales_raw.csv        # Raw data extracted per channel
│   │   ├── info_videos_clean.csv       # Processed data per video
│   │   └── info_canales_clean.csv      # Processed data per channel
│   │
│   ├── scripts/
│   │   ├── 01_Obtener_datos.py         # Extraction via YouTube API v3 (Phase 1)
│   │   ├── 02_Procesamiento_datos.py   # Transformation with Pandas (Phase 2)
│   │   ├── 03_Carga_datos_Postgres.py  # Load to PostgreSQL (Phase 3)
│   │   ├── 01_Obtener_datos.ipynb      # Original extraction notebook
│   │   ├── 02_Notebook_De_Pruebas.ipynb   # Testing draft
│   │   ├── 03_Procesamiento_datos.ipynb   # Original transformation notebook
│   │   └── 04_Carga_datos_Postgres.ipynb  # Original loading notebook
│   │
│   ├── sql/
│   │   ├── schema.sql                  # Table creation, data types, and indexes
│   │   └── views.sql                   # Business logic centralized in 3 views
│   │
│   ├── dashboards/
│   │   └── youtube_niche_analyzer.pbix # Power BI dashboard (Phase 4)
│   │
│   ├── logs/                           # Execution logs (excluded via .gitignore)
│   │   └── pipeline.log
│   │
│   └── keys.txt                        # API keys and credentials (excluded via .gitignore)
│
├── .gitignore
└── README.md
```

## Data Extracted (Phase 1)
For each channel, the 400 most recent videos are extracted (excluding shorts
and videos under 5 minutes) with the following metrics:
`timestamp`, `channelTitle`, `id`, `publishedAt`, `title`, `viewCount`, `likeCount`,
`commentCount`, `duration`

Channel-level information is also extracted:
`title`, `subscriberCount`, `videoCount`, `viewCount`

## Cleaned Data (Phase 2)
Video-level metrics:
`timestamp`, `channelTitle`, `id`, `publishedAt`, `title`, `viewCount`, `likeCount`, `commentCount`, `duration_seconds`, `hora`, `dia_semana`, `nombre_dia`, `engagement_rate`, `tipo_video`

Channel-level metrics:
`timestamp_canal`, `title`, `subscriberCount`, `videoCount`, `viewCount`

## Data Storage (Phase 3)
At this point, it was decided to standardize column names to snake_case.

## Dashboard (Phase 4)
The dashboard answers 7 business questions across 4 pages:

- **Page 1 — Niche Overview:** Comparative channel table with subscribers, views, engagement rate, and views/subscribers ratio. Niche-wide KPIs with MoM and YoY growth indicators.
- **Page 2 — Content Performance:** Views vs. likes scatter plot per video with dynamic bubble size (comments, engagement, or duration). Identifies viral videos and outliers.
- **Page 3 — Time Trends:** Monthly evolution of views and videos published. Subscriber growth per channel since the pipeline's start.
- **Page 4 — Publishing Calendar:** Day/hour heatmap cross-referenced with performance or activity. Identifies peak-impact windows per channel.

All pages include custom tooltips and page-to-page navigation.

## Design Decisions and Limitations

### Phase 1:
#### Design Decisions
- Endpoint: playlistItems + videos.list instead of search.list. 50x more quota-efficient — 80 units vs. 4,000 for 5 channels.
- Video limit: 400 per channel, prioritizing the most recent. Videos from 2019-2023 remain available, but date filtering is delegated to Power BI, not the pipeline.
- Short-content filter: 300-second threshold to exclude shorts and teasers. Static for now — Phase 2 will evaluate complementing it with IQR-based outlier detection.
- Error handling: retry with 3 attempts and 5 seconds between attempts. On failure, the script saves what it has and moves on to the next channel.
- Security: API key stored in a .txt file excluded via .gitignore. Lesson learned the hard way — Jupyter outputs get embedded in the .ipynb and pushed to GitHub.
- Two separate CSVs: info_videos_youtube_raw.csv for per-video metrics and info_canales_raw.csv for aggregated channel data. This split mirrors the future SQL table structure.

#### Limitations
- El Robot de Platón has shorts massively mixed into its uploads playlist — of 400 extracted IDs, only 117 pass the filter. It's the smallest sample in the analysis.
- La Historia de... has only 29 real public videos. Analytically valid due to its high average views, but with limited volume for statistical patterns.
- YouTube doesn't distinguish shorts from regular videos in playlistItems — the duration filter is the only mechanism available without access to private endpoints.
- publishedAt includes a timezone in ISO 8601 format — requires parsing in Phase 2 before it can be used for time-based analysis.
- As of Phase 1, there isn't yet a large enough automated data extraction history to build a proper time series. This gets resolved in Phase 5.

### Phase 2:
#### Design Decisions
- Original duration column dropped — duration_seconds is sufficient for analysis and visualization.
- Transformations done in Pandas, not Power Query — Power BI is reserved for DAX and time intelligence only.
- nombre_dia built from a manual dictionary — independent of the system's locale.
- IQR applied at the niche level (global), not per channel.
- channel data accumulates per run — each row is a snapshot with timestamp_canal.
- Incremental extraction delegated to Phase 3 — the current pipeline extracts full history each time.

#### Limitations
- Documented limitation in code: high dispersion across channels makes the global IQR imperfect; per-channel IQR was dropped due to insufficient sample size for La Historia De... (29 videos). To revisit in P2.

### Phase 3:
#### Design Decisions
- Engine chosen: PostgreSQL over SQLite — aligns with market-standard stack and future portability.
- For the videos table: video id as a natural PRIMARY KEY — immutable, generated by YouTube.
- For the canal_snapshots table: surrogate SERIAL as PK — avoids fragility from a composite PK colliding on timestamps.
- Composite index on (channel_title, dia_semana, hora) in the videos table — optimizes queries for the dashboard's Page 4 (heatmap).
- Automated validations in the loading script — per-channel counts, date range checks, nulls in critical columns.
- Unified keys.txt parser shared between Phase 1 and Phase 3 — centralized configuration.
- utf-8-sig encoding in Phase 2's to_csv and Phase 3's read_csv — resolves special-character corruption in Spanish text.
- The videos table holds the most recent snapshot only — each time the API is called, this table shows only the latest info via ON CONFLICT ... DO UPDATE.
- The canales table keeps historical records, enforced by ADD CONSTRAINT unique_canal_snapshot UNIQUE (tiempo_extraccion, channel_title) — ON CONFLICT (tiempo_extraccion, channel_title) DO NOTHING.

    **Views created:**
- evolucion_mensual_canal — answers question 5 (monthly evolution of subscribers, videos, and views per channel using DATE_TRUNC over canal_snapshots)
- momento_despegue — answers question 6 (detects weekly metric increases using LAG and a CTE over canal_snapshots)
- frecuencia_publicacion_crecimiento — answers question 9 (cross-references publishing frequency with subscriber growth using a JOIN between videos and canal_snapshots)

#### Limitations
- NLP implementation was dropped for questions 3 and 10:

        Question 3: Are there recurring words in the titles of the most successful videos?

        Question 10: Which topics or formats have high demand (engagement) but low supply (few videos)?

- This limitation reflects the cost of implementing NLP versus its value for my professional goal, given that implementing it would currently take about a month. This feature is reserved for a future iteration of this MVP.
- The views use data from the project's start date only — there's no pre-Phase-1 history in canal_snapshots.

### Phase 4:
#### Design Decisions
- Data model centralized around Dim_Canal — a dynamic dimension table generated from videos via Power Query. If channels are added, they appear automatically on refresh.
- DAX Calendar table with a year/month/day hierarchy in Spanish — the base for time intelligence across all pages.
- fecha_publicacion as a derived DATE column in Power Query — resolves the incompatibility between PostgreSQL's TIMESTAMPTZ and the Calendar table. published_at is preserved in the database to avoid losing the original value.
- Dynamic bubble size in the scatter plot (Page 2) and dynamic metric in the heatmap (Page 4) implemented with the pattern: disconnected table → SWITCH measure → visual with conditional formatting. Power BI's native Field Parameters don't support dynamic measures in the scatter plot's Size field or in conditional formatting.
- Heatmap implemented with a Matrix + gradient conditional formatting — no dependency on external AppSource visuals.
- MoM/YoY growth indicators in the KPIs with explicit filter logic via ISFILTERED:

    | Year | Month | Behavior |
    |-----|-----|----------------|
    | ✗ | ✗ | Guidance message shown to user |
    | ✓ | ✗ | Total year-over-year growth |
    | ✗ | ✓ | Guidance message shown to user |
    | ✓ | ✓ | MoM + YoY for the selected month |

- Avg Engagement Rate expressed in percentage points (pp) in growth indicators — more accurate than relative growth for comparing percentages.
- Visual identity: palette `#F5F5F5` / `#FFFFFF` / `#CC0000` / `#1C1C1C`, backgrounds designed in Canva, red reserved as an accent in conditional formatting and gradients.

#### Limitations
- **String-based relationship key:** The model uses channel_title (TEXT) as the relationship key across all tables. The correct solution would be an integer canal_id as a surrogate key. Pending for P2. Current mitigation: channel_title is normalized from the YouTube Data API and hasn't changed across any extraction in the MVP.
- **Insufficient history in canal_snapshots:** The table has only 2 snapshots per channel (April and May 2026) due to manual pipeline runs. Subscriber and view growth indicators compare two points, not a trend. This gets resolved automatically in Phase 5 through pipeline automation.

### Phase 5:
#### Design Decisions

**Conditioning scripts from previous phases**
- Converted notebooks to `.py` scripts — notebooks were useful for interactive exploration; production code lives in `.py` files. A prerequisite for any automation outside Jupyter.
- Base paths using `__file__` instead of `os.getcwd()` — `os.getcwd()` depends on the working directory of the process invoking the script, which in Task Scheduler is not the project folder. `__file__` anchors paths to the script's physical location, regardless of where it's invoked from.
- Fixed the channel API call: direct `requests.get()` replaced with `hacer_peticion()` — the original call had no retries, leaving a non-resilient failure point in unattended execution.
- Empty DataFrame validation before connecting to PostgreSQL — if extraction or transformation fails silently and produces CSVs with no rows, `executemany()` doesn't raise an error and the pipeline would report success without having inserted anything. Validated with `video.empty` / `canal.empty` before opening the connection, with `exit(1)` if detected.
- PostgreSQL session wrapped in `try/finally` — guarantees cursor and connection closure on any exit path, including those ending in `exit(1)` inside `except` blocks.

**Orchestration and automation**
- Single orchestrator `run_pipeline.py` as the entry point — runs the 3 scripts in order as subprocesses via `subprocess.run()`. If a step fails (exit code != 0), the chain stops without attempting the following steps. Task Scheduler points only to this file.
- `sys.executable` instead of `"python"` — ensures the orchestrator uses the same Python installation (Anaconda) the scripts were tested with, without relying on Task Scheduler's environment PATH.
- Logging with `RotatingFileHandler` in `logs/pipeline.log` — persistent logging with size-based rotation (2MB, 5 backups). Every line includes a timestamp, severity level, and message. Simultaneous console output for monitoring during manual tests. The `logs/` folder is excluded from the repository via `.gitignore`.
- Visual separator between runs in the log — a blank line written directly to the file before each execution block, since the logger can't write empty lines without a timestamp.
- Task Scheduler configured with a weekly trigger (Saturdays at 10:30) + active network condition + "run as soon as possible if a scheduled start was missed" — if the laptop was off at the scheduled time, the pipeline runs as soon as the machine is available with an internet connection.

#### Limitations
- **Visible CMD window during execution:** Task Scheduler with "Run only when user is logged on" briefly shows a CMD window while the pipeline runs (~1 minute). Removing it requires "Run whether user is logged on or not," which introduces unnecessary permission complexity for personal use.
- **No failure notifications:** if the pipeline fails on a Saturday, it's only detectable by manually checking `logs/pipeline.log`. There's no failure alert mechanism. Acceptable for a personal MVP; in a real production setting this would be solved with an alerting system (email, Slack, etc.).
- **Dependent on local machine availability:** the pipeline requires the laptop to be on and connected to the internet. There's no server or cloud instance guaranteeing availability. A local-architecture limitation — partially mitigated by the "run as soon as possible" condition.

---
*Personal learning project as part of a transition from Data Analyst
toward technical data roles. Built with an incremental approach:
make it work first, then refactor.*