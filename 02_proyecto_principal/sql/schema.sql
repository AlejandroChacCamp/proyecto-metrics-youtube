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