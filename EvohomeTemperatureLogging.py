import time
import logging
import configparser
import csv
from datetime import datetime
from evohomeclient import EvohomeClient

# ---------------- CONFIG ----------------
CONFIG_FILE = "config.ini"
CSV_FILE = "evohome_data.csv"
LOG_FILE = "evohome.log"

POLL_INTERVAL = 600        # seconds
BACKOFF_INTERVAL = 300     # seconds
# --------------------------------------


def setup_logging():
    handler = logging.FileHandler(LOG_FILE)
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    handler.flush = handler.stream.flush  # force immediate flush

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logging.info("Logger initialized")


def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    if "Evohome" not in config:
        raise RuntimeError("Missing [Evohome] section")

    return config["Evohome"]["Username"], config["Evohome"]["Password"]


def write_rows(rows):
    if not rows:
        return

    file_exists = False
    try:
        with open(CSV_FILE, "r"):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if not file_exists:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
        f.flush()  # <-- force flush to disk


def collect_temperatures(client):
    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for zone in client.temperatures():
        row = dict(zone)
        row["time"] = timestamp
        rows.append(row)

    return rows


def main():
    setup_logging()
    username, password = load_config()
    client = EvohomeClient(username, password)

    while True:
        try:
            rows = collect_temperatures(client)
            write_rows(rows)
            logging.info("Wrote %d rows", len(rows))
            time.sleep(POLL_INTERVAL)

        except Exception as e:
            logging.error("Error during polling: %s", e)
            time.sleep(BACKOFF_INTERVAL)


if __name__ == "__main__":
    main()
