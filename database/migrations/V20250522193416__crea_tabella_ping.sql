-- Migration 2025/05/22 19:34:16
CREATE TABLE IF NOT EXISTS downtime_panda.ping (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_id BIGINT,
    pinged_at TIMESTAMPTZ,
    http_response SMALLINT,
    CONSTRAINT service_fk
        FOREIGN KEY(service_id)
            REFERENCES downtime_panda.service(id)
);
