-- 1. Dimension Table: Stores metadata about specific physical satellites
CREATE TABLE dim_satellites (
    satellite_id VARCHAR(50) PRIMARY KEY,
    norad_id INT UNIQUE NOT NULL,
    constellation VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('ACTIVE', 'DECOMMISSIONED', 'SPARE'))
);

-- 2. Fact Table: Stores the time-series signal telemetry extracted by the DSP engine
CREATE TABLE fact_satellite_telemetry (
    telemetry_id BIGSERIAL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    satellite_id VARCHAR(50) NOT NULL,
    signal_strength_dbm NUMERIC(6,2) NOT NULL,
    snr_db NUMERIC(5,2) NOT NULL,
    carrier_lock BOOLEAN NOT NULL,
    peak_voltage NUMERIC(6,4) NOT NULL,
    
    -- Enforce data integrity through relational constraints
    PRIMARY KEY (telemetry_id),
    CONSTRAINT fk_satellite FOREIGN KEY (satellite_id) REFERENCES dim_satellites(satellite_id) ON DELETE RESTRICT
);

-- 3. Operational Indexing: Speeds up time-range queries on historical telemetry logs
CREATE INDEX idx_telemetry_timestamp ON fact_satellite_telemetry (timestamp DESC);
CREATE INDEX idx_telemetry_sat_id ON fact_satellite_telemetry (satellite_id);

-- 4. Seed Dimension Data: Populate metadata for the satellite used in our pipeline
INSERT INTO dim_satellites (satellite_id, norad_id, constellation, status)
VALUES ('NOAA-19', 33591, 'POES (Polar Operational Environmental Satellites)', 'ACTIVE')
ON CONFLICT (satellite_id) DO NOTHING;

