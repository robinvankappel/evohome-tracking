import os
import time
import csv
import logging
import configparser
from datetime import datetime
from evohomeclient import EvohomeClient
IS_GITHUB = os.getenv("GITHUB_ACTIONS") == "true"

# ================= CONFIG =================
CONFIG_FILE = "config.ini"
CSV_FILE = "evohome_data.csv"
LOG_FILE = "evohome.log"

POLL_INTERVAL = 600        # seconds
BACKOFF_INTERVAL = 300     # seconds
# ========================================


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    # Force immediate write to disk
    for handler in logging.getLogger().handlers:
        handler.flush = handler.stream.flush


def load_config():
    # Prefer environment variables (GitHub Actions)
    user = os.getenv("EVOHOME_USERNAME")
    pwd = os.getenv("EVOHOME_PASSWORD")

    if user and pwd:
        return user, pwd

    # Fallback to local config file
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    if "Evohome" not in config:
        raise RuntimeError("Missing [Evohome] section in config.ini")

    return config["Evohome"]["Username"], config["Evohome"]["Password"]


def write_rows(rows):
    if not rows:
        return

    os.makedirs(os.path.dirname(CSV_FILE) or ".", exist_ok=True)

    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
        f.flush()


def collect_temperatures(client):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []

    for zone in client.temperatures():
        row = dict(zone)
        row["time"] = timestamp
        rows.append(row)

    return rows

def main():
    setup_logging()
    username, password = load_config()
    client = EvohomeClient(username, password)

    if IS_GITHUB:
        # One-shot run for GitHub Actions
        rows = collect_temperatures(client)
        write_rows(rows)
        logging.info("Single run completed (GitHub Actions)")
        return

    # Local mode: continuous logging
    while True:
        try:
            rows = collect_temperatures(client)
            write_rows(rows)
            logging.info("Logged %d rows", len(rows))
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            logging.error("Error during polling: %s", e)
            time.sleep(BACKOFF_INTERVAL)

if __name__ == "__main__":
    main()
