-- Migration 2025/05/14 19:34:20
CREATE SCHEMA IF NOT EXISTS "downtime_panda";

CREATE TABLE IF NOT EXISTS "downtime_panda"."servizio" (
        id BIGINT PRIMARY KEY,
        nome VARCHAR(64),
        uri VARCHAR(255)
    );