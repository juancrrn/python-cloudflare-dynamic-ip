import json
import logging
from logging.handlers import RotatingFileHandler
from typing import TypedDict, NotRequired

import requests

from config.config import CLOUDFLARE_ZONES, LOGGING_LEVEL, LAST_IP_FILE, CURRENT_IP_API, LOG_FILE

logger = logging.getLogger(__name__)

# Force IPv4
requests.packages.urllib3.util.connection.HAS_IPV6 = False

CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"


class CloudflareDnsRecord(TypedDict):
    id: NotRequired[str]
    name: str
    proxied: NotRequired[bool]


class CloudflareDnsZone(TypedDict):
    id: str
    name: str
    token: str
    records: list[CloudflareDnsRecord]


def cloudflare_api_get_zone_records(zone_id: str, token: str) -> list[dict]:
    """
    See: https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/list/
    """
    url = f"{CLOUDFLARE_API_URL}/zones/{zone_id}/dns_records"

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    response = requests.get(url=url, headers=headers)

    response.raise_for_status()

    return response.json()["result"]


def cloudflare_api_update_zone_record(zone_id: str, record_id: str, record: dict, token: str) -> None:
    """
    See: https://developers.cloudflare.com/api/resources/dns/subresources/records/methods/update/
    """
    url = f"{CLOUDFLARE_API_URL}/zones/{zone_id}/dns_records/{record_id}"

    headers = {
        "Authorization": "Bearer {}".format(token),
        "Content-Type": "application/json"
    }

    response = requests.put(url=url, data=json.dumps(record), headers=headers)

    response.raise_for_status()


def get_last_ip() -> str | None:
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
    ip = requests.get(CURRENT_IP_API).text.rstrip()

    logger.info("Current IP: {}".format(ip))

    return ip


def get_zone_records(zone: CloudflareDnsZone) -> list[CloudflareDnsRecord]:
    logger.info("Getting Cloudflare records for zone: {}".format(zone["name"]))

    cloudflare_records = cloudflare_api_get_zone_records(zone["id"], zone["token"])

    enriched_records = []

    for record in zone["records"]:
        cloudflare_record = next((r for r in cloudflare_records if r["name"] == record["name"]), None)

        if not cloudflare_record:
            logger.error("Record {} not found in Cloudflare zone {}. Skipping record"
                         .format(record["name"], zone["name"]))
            continue

        enriched_records.append({
            "id": cloudflare_record["id"],
            "name": cloudflare_record["name"],
            "proxied": cloudflare_record.get("proxied", False)
        })

    return enriched_records


def process_record(record: CloudflareDnsRecord, zone: CloudflareDnsZone, new_ip: str) -> None:
    logger.info("Updating record {} in zone {}".format(record["name"], zone["name"]))

    data = {
        "type": "A",
        "name": record["name"],
        "content": new_ip,
        "ttl": 1,  # Automatic
        "proxied": record["proxied"]
    }

    try:
        cloudflare_api_update_zone_record(zone["id"], record["id"], data, zone["token"])
        logger.info("Record {} updated successfully".format(record["name"]))
    except requests.HTTPError as e:
        logger.error("Failed to update record {}: {}".format(record["name"], e))


def process_zone(zone: CloudflareDnsZone, ip: str) -> bool:
    logger.info("Processing zone: {}".format(zone["name"]))

    records = get_zone_records(zone)

    success = True

    for record in records:
        try:
            process_record(record, zone, ip)
        except Exception as e:
            success = False
            logger.error("Error processing record {} in zone {}: {}".format(record["name"], zone["name"], e))

    return success


def run() -> None:
    logger.info("Running...")

    last_ip = get_last_ip()
    current_ip = get_current_ip()

    if current_ip == last_ip:
        logger.info("IP has not changed. Exiting...")
        return

    success = True

    for zone in CLOUDFLARE_ZONES:
        if not process_zone(zone, current_ip):
            success = False

    if success:
        update_last_ip(current_ip)
    else:
        logger.error("One or more zones failed to update. Last IP not updated. Will try again next time.")

    logger.info("Finished processing zones. Exiting...")


def set_up_logging() -> None:
    global logger

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    handler = RotatingFileHandler(filename=LOG_FILE, mode="a", maxBytes=209 * 90, backupCount=2)
    handler.setFormatter(formatter)
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)


if __name__ == "__main__":
    set_up_logging()

    run()
