import os
import time
import csv
import logging
import configparser
from datetime import datetime
from evohomeclient import EvohomeClient

# ==================================================
# CONFIG
# ==================================================
CSV_FILE = "evohome_data.csv"
LOG_FILE = "evohome.log"

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "600"))     # seconds
RUN_ONCE = os.getenv("RUN_ONCE", "false").lower() == "true"
# --------------------------------------------------


def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logging.getLogger().addHandler(logging.StreamHandler())


def load_credentials():
    # Priority: ENV → config.ini
    user = os.getenv("EVOHOME_USERNAME")
    pwd = os.getenv("EVOHOME_PASSWORD")

    if user and pwd:
        return user, pwd

    config = configparser.ConfigParser()
    config.read("config.ini")

    if "Evohome" not in config:
        raise RuntimeError("Missing Evohome credentials")

    return config["Evohome"]["Username"], config["Evohome"]["Password"]


def write_rows(rows):
    if not rows:
        return

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
        data = dict(zone)
        data["time"] = timestamp
        rows.append(data)

    return rows


def main():
    setup_logging()
    user, pwd = load_credentials()

    logging.info("Starting Evohome logger")
    client = EvohomeClient(user, pwd)

    while True:
        try:
            rows = collect_temperatures(client)
            write_rows(rows)
            logging.info("Logged %d rows", len(rows))
        except Exception as e:
            logging.exception("Error during polling: %s", e)

        if RUN_ONCE:
            break

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
