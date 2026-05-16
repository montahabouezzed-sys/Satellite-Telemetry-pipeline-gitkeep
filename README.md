# Satellite-Telemetry-pipeline-gitkeep

# End-to-End NOAA APT Signal & Telemetry Data Pipeline

## 🎯 Project Goal
The objective of this project is to build an automated, production-grade data pipeline that bridges physical Radio Frequency (RF) engineering with scalable Software/Data Engineering. 

The pipeline ingests raw, real-world Automatic Picture Transmission (APT) analog audio signals from orbiting NOAA Weather Satellites (NOAA-15, 18, 19), processes the signal using digital signal processing (DSP) algorithms, extracts time-series satellite health telemetry, and structures it into a high-performance relational database using advanced SQL.

This project demonstrates an architectural solution for processing sovereign aerospace and satellite communication data locally without relying on proprietary, closed-source cloud ecosystems.

---

## Project Structure

```text
satcom-telemetry-pipeline/
│
├── config/                  
│   └── database.conf        # SECURED (Decoupled configuration parameters)
│
├── data/                    
│   ├── processed/           # POPULATED (1.8 MB binary spectrum array file)
│   └── raw/                 # POPULATED (17 MB pristine satellite audio file)
│
├── database/                
│   ├── schema.sql           # STABLE (Idempotent schema definitions)
│   └── views.sql            # STABLE (Advanced view analysis scripts)
│
├── docs/
│   └── assets/              # READY (Target folder for visual asset plots)
│
├── src/                     
│   ├── ingestion.py         # Automated ingestion worker
│   ├── dsp_engine.py        # Vectorized FFT signal analysis engine
│   └── db_pipeline.py       # Decoupled database connection executor
│
├── tests/                   
│   └── test_dsp.py          # VERIFIED (Automated algorithmic test panel)
│
├── .gitkeep    
└── requirements.txt
```


## 🏗️ System Architecture
```text
[Raw NOAA .WAV / IQ] ──> [Python Ingestion Engine] ──> [DSP Engine (FFT / Hilbert)]
│
▼
[Advanced Relational SQL] <── [SQLAlchemy Pipe] <── [Telemetry Feature Extraction]
```

1. **Ingestion Layer:** Automated fetching of raw radio observation recordings from open-source satellite ground-station networks (SatNOGS / NOAA public archives).
2. **DSP & Mathematics Engine:** Leveraging Fourier Analysis and Analytic Signal transforms to calculate instantaneous power and carrier-to-noise anomalies.
3. **Data Engineering Pipe:** Extrapolating continuous time-stamped system arrays into highly structured data structures.
4. **Database Analytics Layer:** Injecting processed features into a relational database optimized with indexing and analytical window functions for tracking hardware degradation over time.

---

## 🛠️ Technical Requirements & Stack

### Core Technologies
*   **Language:** Python 3.10+ (Data Ingestion, Analytical Computing, Database Pipe)
*   **Database:** PostgreSQL / TimescaleDB (Relational Time-Series Analytics)
*   **ORMs & Drivers:** `SQLAlchemy`, `psycopg2`

### Scientific & Data Frameworks
*   `SciPy` (Digital Signal Processing, Filter design, Hilbert Transforms)
*   `NumPy` (High-performance vectorized array mathematical operations)
*   `Pandas` (Data mutation, cleaning, and preparation)

### Mathematical Prerequisites Implemented
*   **Fast Fourier Transform (FFT):** Transitioning time-domain radio data to the frequency-domain to isolate the 2400Hz subcarrier frequency and calculate real-time SNR.
*   **Analytic Signal Generation:** Applying the Hilbert Transform to compute instantaneous amplitude envelopes, neutralizing phase dependencies in signal degradation.

---

## 📊 Database Design & Analytics
The repository implements a structured star-schema optimized for time-series data analysis. It contains strict primary/foreign key constraints, transactional controls, and specialized analytical views designed to isolate satellite degradation indicators.

*   `dim_satellites`: Tracks active/inactive orbital assets, NORAD identifiers, and orbital mechanics configurations.
*   `fact_satellite_telemetry`: Stores millions of individual time-series logs capturing signal voltage variance, SNR values, and carrier-lock statuses.

---

## 🚀 How to Run and Test This Project

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Initialize the database schema: `psql -U user -d database -f database/schema.sql`
4. Execute the pipeline: `python src/db_pipeline.py --input data/raw/sample_noaa.wav`
