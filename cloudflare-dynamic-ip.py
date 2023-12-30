import json
import logging

import requests

from config.config import CLOUDFLARE_ZONES, LOGGING_LEVEL, LAST_IP_FILE, CURRENT_IP_API, CLOUDFLARE_RECORDS, \
    LOG_FILE

logger = logging.getLogger(__name__)


def update_record(record: dict, current_ip: str) -> bool:
    zone = CLOUDFLARE_ZONES[record["zone_id"]]

    logger.info("Updating record: {} in zone: {}".format(record["name"], zone["name"]))

    data = {
        "type": "A",
        "name": record["name"],
        "content": current_ip,
        "ttl": 1,  # Automatic
        "proxied": record["proxied"]
    }

    headers = {
        "Authorization": "Bearer {}".format(zone["token"]),
        "Content-Type": "application/json"
    }

    # See:  https://api.cloudflare.com/#dns-records-for-a-zone-update-dns-record
    url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}".format(zone["id"], record["id"])

    response = requests.put(url=url, data=json.dumps(data), headers=headers)

    if "success" in response.json() and response.json()["success"]:
        logger.info("Record updated successfully")

        return True

    logger.error("Failed to update record")

    return False


def get_last_ip() -> str|None:
    ip = None

    try:
        with open(LAST_IP_FILE, "r") as file:
            ip = file.readline()
    except:
        pass

    logger.info("Last IP: {}".format(ip))

    return ip


def update_last_ip(ip: str) -> None:
    logger.info("Saving current IP...")

    with open(LAST_IP_FILE, "w") as file:
        file.write(ip)
        file.close()

    logger.info("Current IP saved")


def get_current_ip() -> str:
    ip = requests.get(CURRENT_IP_API).text

    logger.info("Current IP: {}".format(ip))

    return ip


def run() -> None:
    logger.info("Running...")

    last_ip = get_last_ip()
    current_ip = get_current_ip()

    if current_ip == last_ip:
        logger.info("IP has not changed. Exiting...")

        return

    any_failures = False

    for record in CLOUDFLARE_RECORDS:
        result = update_record(record, current_ip)

        if not result:
            any_failures = True
            break

    if not any_failures:
        update_last_ip(current_ip)

        logger.info("All records updated successfully. Exiting...")
    else:
        logger.error("Failed to update some records. Exiting...")


def set_up_logging() -> None:
    global logger

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.FileHandler(LOG_FILE, mode="a")
    handler.setFormatter(formatter)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)


if __name__ == "__main__":
    set_up_logging()

    run()
