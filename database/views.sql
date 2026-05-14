CREATE OR REPLACE VIEW view_satellite_signal_analytics AS
SELECT 
    timestamp,
    satellite_id,
    snr_db,
    carrier_lock,
    
    -- 1. Window Function: Calculate a 3-row rolling average SNR to smooth out signal noise
    ROUND(AVG(snr_db) OVER (
        PARTITION BY satellite_id 
        ORDER BY timestamp 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_snr_avg,
    
    -- 2. Window Function: Identify historical peak voltage fluctuations across the pass duration
    ROUND(MAX(peak_voltage) OVER (
        PARTITION BY satellite_id 
        ORDER BY timestamp
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ), 4) AS session_peak_voltage_ceiling,
    
    -- 3. Analytical Lead Function: Predict structural signal status changes ahead of time
    LEAD(carrier_lock, 1) OVER (
        PARTITION BY satellite_id 
        ORDER BY timestamp
    ) AS next_frame_carrier_lock_prediction

FROM fact_satellite_telemetry;

