CREATE TABLE IF NOT EXISTS "videos" (
	"tiempo_extraccion" TIMESTAMP NOT NULL,
	"channel_title" TEXT NOT NULL,
	"id" TEXT NOT NULL,
	"published_at" TIMESTAMPTZ NOT NULL,
	"title" TEXT,
	"view_count" INTEGER,
	"like_count" INTEGER,
	"comment_count" INTEGER,
	"duration_seconds" INTEGER,
	"hora" INTEGER,
	"dia_semana" INTEGER,
	"nombre_dia" TEXT,
	"engagement_rate" NUMERIC,
	"tipo_video" TEXT,
	PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS idx_videos_channeltitle_dia_semana_hora ON "videos" ("channel_title", "dia_semana", "hora");

CREATE TABLE IF NOT EXISTS "canal_snapshots" (
	"id" SERIAL,
	"tiempo_extraccion" TIMESTAMP NOT NULL,
	"channel_title" TEXT NOT NULL,
	"subscriber_count" INTEGER,
	"video_count" INTEGER,
	"view_count" INTEGER,
	PRIMARY KEY ("id")
);

ALTER TABLE "canal_snapshots" 
ADD CONSTRAINT unique_canal_snapshot UNIQUE (tiempo_extraccion, channel_title);

=================================================

# Crear channels y poblarla

CREATE TABLE IF NOT EXISTS "channels" (
    "canal_id" SERIAL PRIMARY KEY,
    "channel_title" TEXT NOT NULL UNIQUE
);

INSERT INTO channels (channel_title)
SELECT DISTINCT channel_title FROM videos
UNION
SELECT DISTINCT channel_title FROM canal_snapshots
ON CONFLICT (channel_title) DO NOTHING;

=================================================

# Agregar canal_id FK a videos y canal_snapshots + backfill

-- videos
ALTER TABLE videos ADD COLUMN canal_id INTEGER;

UPDATE videos v
SET canal_id = c.canal_id
FROM channels c
WHERE v.channel_title = c.channel_title;

ALTER TABLE videos ALTER COLUMN canal_id SET NOT NULL;
ALTER TABLE videos
  ADD CONSTRAINT fk_videos_canal FOREIGN KEY (canal_id) REFERENCES channels(canal_id);

-- canal_snapshots
ALTER TABLE canal_snapshots ADD COLUMN canal_id INTEGER;

UPDATE canal_snapshots cs
SET canal_id = c.canal_id
FROM channels c
WHERE cs.channel_title = c.channel_title;

ALTER TABLE canal_snapshots ALTER COLUMN canal_id SET NOT NULL;
ALTER TABLE canal_snapshots
  ADD CONSTRAINT fk_canal_snapshots_canal FOREIGN KEY (canal_id) REFERENCES channels(canal_id);

