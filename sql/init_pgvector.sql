CREATE EXTENSION IF NOT EXISTS vector;

-- Staging table for raw match events
CREATE TABLE IF NOT EXISTS raw_match_events (
    id VARCHAR(64) PRIMARY KEY,
    match_id BIGINT NOT NULL,
    event_index INT,
    period INT,
    timestamp TIME,
    minute INT,
    second INT,
    event_type VARCHAR(50),
    player_name VARCHAR(100),
    team_name VARCHAR(100),
    location_x FLOAT,
    location_y FLOAT,
    pass_end_location_x FLOAT,
    pass_end_location_y FLOAT,
    raw_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);