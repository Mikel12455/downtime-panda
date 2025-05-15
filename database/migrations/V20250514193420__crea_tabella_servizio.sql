-- Migration 2025/05/14 19:34:20
CREATE SCHEMA IF NOT EXISTS `downtime_panda`;

CREATE TABLE IF NOT EXISTS `downtime_panda`.`service` (
        `id` BIGINT PRIMARY KEY,
        `name` VARCHAR(64),
        `uri` VARCHAR(255)
    );