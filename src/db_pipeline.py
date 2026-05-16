import os
import sys
from sqlalchemy import create_engine
from datetime import datetime, timezone

# Import the functional modules built in the previous phases
from ing2 import download_satellite_signal
from dsp_engine import analyze_satellite_signal

# DATABASE CONFIGURATION PARAMETERS
# Format: postgresql+psycopg2://<username>:<password>@<host>:<port>/<database_name>
# Adjust these strings to match local pgAdmin4 connection credentials
DB_USER = "postgres"
DB_PASS = " "  # <-- Change this to actual pgAdmin4 master password
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"  # Standard default database name in pgAdmin4


def get_db_engine():
    """
    Initializes a highly efficient, pooled SQLAlchemy connection engine
    linked to PostgreSQL server instance.
    """
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # pooling parameters keep connections open safely during bulk uploads
    return create_engine(connection_string, pool_pre_ping=True)


def run_end_to_end_pipeline():
    """
    Executes the complete Sovereign SatCom Data Pipeline sequence:
    Ingestion (Phase 1) -> DSP Engineering (Phase 2) -> Relational Storage (Phase 4)
    """
    print(f"[{datetime.now(timezone.utc).isoformat()}] PIPELINE_LAUNCHED: Initiating operational sequence.")

    # --- PHASE 1: DATA INGESTION ---
    # Downloads the binary recording to local file system disk array
    raw_file_path = download_satellite_signal()
    if not raw_file_path or not os.path.exists(raw_file_path):
        print("[CRITICAL] Pipeline stopped: Data ingestion phase failed.", file=sys.stderr)
        return

    # --- PHASE 2: DIGITAL SIGNAL PROCESSING ---
    # Parses the binary, processes vectorized FFT transformations, and extracts a DataFrame
    df_telemetry = analyze_satellite_signal(filename=os.path.basename(raw_file_path))
    if df_telemetry is None or df_telemetry.empty:
        print("[CRITICAL] Pipeline stopped: Matrix DSP processing phase failed.", file=sys.stderr)
        return

    # --- PHASE 4: DATABASE INJECTION ---
    print(f"[{datetime.now(timezone.utc).isoformat()}] STORAGE_STAGE: Connecting to PostgreSQL target server...")
    # --- PHASE 4: DATABASE INJECTION ---
    print(f"[{datetime.now(timezone.utc).isoformat()}] STORAGE_STAGE: Connecting to PostgreSQL target server...")


    try:
        engine = get_db_engine()

        # Wrapping the stream inside a secure contextual transaction block
        with engine.begin() as connection:
            print("Database transaction context opened. Injecting records...")

            df_telemetry.to_sql(
                name='fact_satellite_telemetry',
                con=connection,  # Pass the active transaction connection, NOT the bare engine
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )

        # Exiting the 'with' block automatically executes a COMMIT command across the connection pool
        print(
            f"[{datetime.now(timezone.utc).isoformat()}] PIPELINE_SUCCESS: Streamed and COMMITTED {len(df_telemetry)} records directly into PostgreSQL database.")

    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] PIPELINE_FATAL_STORAGE_ERROR: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    run_end_to_end_pipeline()
