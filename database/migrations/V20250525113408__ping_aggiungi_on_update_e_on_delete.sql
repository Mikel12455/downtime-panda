-- Migration 2025/05/25 11:34:08
ALTER TABLE downtime_panda.ping
DROP CONSTRAINT service_fk;

ALTER TABLE downtime_panda.ping
ADD CONSTRAINT service_fk
FOREIGN KEY (service_id)
    REFERENCES downtime_panda.service(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;
