import os
import sys
import requests
from datetime import datetime, timezone

# architecting the absolute URL string so it is explicit and clear of truncation errors
URL_PROTOCOL = "https://"
URL_HOST = "raw.githubusercontent.com"
URL_PATH = "/martinber/noaa-apt/master/test/test_11025hz.wav"

# compiling the full path string dynamically at runtime
SAMPLE_SIGNAL_URL = f"{URL_PROTOCOL}{URL_HOST}{URL_PATH}"
DEFAULT_TARGET_FILENAME = "test_11025hz.wav"

def get_project_root():
    """
    Dynamically resolves the absolute path to the project root directory.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def initialize_data_registry():
    """
    Ensures the data directory structure exists matching the repository architecture.
    """
    root_path = get_project_root()
    raw_data_dir = os.path.join(root_path, "data", "raw")
    os.makedirs(raw_data_dir, exist_ok=True)
    return raw_data_dir


def verify_wav_header(file_path):
    """
    Data Integrity Step: Verifies if the downloaded file has a valid RIFF/WAVE header.
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(12)
            # A valid WAV file must start with RIFF and contain the WAVE format indicator
            if header[0:4] == b'RIFF' and header[8:12] == b'WAVE':
                return True
            else:
                # Print out what was actually downloaded to catch hidden HTML/Text errors
                print(f"[ERROR] Invalid WAV Header. First 12 bytes read as text: {header}")
                return False
    except Exception as e:
        print(f"[ERROR] Failed to read file header: {str(e)}")
        return False


def download_satellite_signal(url=SAMPLE_SIGNAL_URL, filename=DEFAULT_TARGET_FILENAME):
    """
    Streams a raw analog satellite audio signal using the requests engine,
    logs network execution windows, and writes clean binary data to disk.
    """
    target_dir = initialize_data_registry()
    destination_path = os.path.join(target_dir, filename)

    print(f"[{datetime.now(timezone.utc).isoformat()}] INGESTION_START: Streaming binary data from GitHub storage...")
    print(f"Source URL: {url}")
    print(f"Target Path: {destination_path}")

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        # Open network stream over HTTP/HTTPS with stream=True for large binaries
        with requests.get(url, headers=headers, stream=True, timeout=15) as r:
            r.raise_for_status()  # Automatically throws an exception if the file isn't found

            content_length = r.headers.get('content-length')
            if content_length:
                print(f"Payload Size: {round(int(content_length) / (1024 * 1024), 2)} MB")

            # Stream chunks to local storage disk file in binary write mode ('wb')
            with open(destination_path, 'wb') as local_file:
                for chunk in r.iter_content(chunk_size=512 * 1024):  # 512KB chunks
                    if chunk:
                        local_file.write(chunk)

        # Post-download validation check
        if verify_wav_header(destination_path):
            print(
                f"[{datetime.now(timezone.utc).isoformat()}] INGESTION_SUCCESS: Pristine binary compiled and validated.")
            return destination_path
        else:
            print(
                f"[{datetime.now(timezone.utc).isoformat()}] INGESTION_FAILED: Integrity check failed. Corrupted payload.")
            return None

    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] INGESTION_CRITICAL_FAILURE: {str(e)}", file=sys.stderr)
        return None


if __name__ == "__main__":
    downloaded_file = download_satellite_signal()
    if downloaded_file:
        print(f"Module verify check: Valid binary written -> {os.path.exists(downloaded_file)}")
