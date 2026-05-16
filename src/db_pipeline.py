import os
import sys
import configparser
from sqlalchemy import create_engine
from datetime import datetime, timezone

# Import the functional pipeline modules
from ingestion import download_satellite_signal
from dsp_engine import analyze_satellite_signal


def get_project_root():
    """Resolves the absolute path to the project root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def get_db_engine():
    """
    Reads decoupled credentials from config/database.conf securely
    and initializes a pooled SQLAlchemy connection engine.
    """
    root_path = get_project_root()
    config_path = os.path.join(root_path, "config", "database.conf")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Critical configuration asset missing at: {config_path}")

    # Initialize native config parser engine
    config = configparser.ConfigParser()
    config.read(config_path)

    # Extract targeted parameter tokens safely
    try:
        user = config.get('postgresql', 'db_user')
        password = config.get('postgresql', 'db_pass')
        host = config.get('postgresql', 'db_host')
        port = config.get('postgresql', 'db_port')
        dbname = config.get('postgresql', 'db_name')
    except configparser.NoOptionError as e:
        raise ValueError(f"Database configuration parse failure: Missing key -> {str(e)}")

    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(connection_string, pool_pre_ping=True)


def run_end_to_end_pipeline():
    """
    Executes the integrated secure end-to-end pipeline pipeline.
    """
    print(f"[{datetime.now(timezone.utc).isoformat()}] PIPELINE_LAUNCHED: Operational execution sequence active.")

    raw_file_path = download_satellite_signal()
    if not raw_file_path or not os.path.exists(raw_file_path):
        print("[CRITICAL] Ingestion window failed.", file=sys.stderr)
        return

    df_telemetry = analyze_satellite_signal(filename=os.path.basename(raw_file_path))
    if df_telemetry is None or df_telemetry.empty:
        print("[CRITICAL] Processing array extraction failed.", file=sys.stderr)
        return

    print(f"[{datetime.now(timezone.utc).isoformat()}] STORAGE_STAGE: Establishing decoupled datalink protocol...")
    try:
        engine = get_db_engine()

        with engine.begin() as connection:
            print("Transactional workspace active. Uploading rows...")
            df_telemetry.to_sql(
                name='fact_satellite_telemetry',
                con=connection,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )

        print(
            f"[{datetime.now(timezone.utc).isoformat()}] PIPELINE_SUCCESS: Streamed and COMMITTED {len(df_telemetry)} records directly into PostgreSQL database.")

    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] PIPELINE_FATAL_STORAGE_ERROR: {str(e)}", file=sys.stderr)


if __name__ == "__main__":
    run_end_to_end_pipeline()
