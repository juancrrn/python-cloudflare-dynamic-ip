import logging

"""
Cloudflare zones to update, including the zone ID, name, a token with write access, and the records to update.

Example:

CLOUDFLARE_ZONES = [
    {
        "id": "b23c8a2207674f7a97e52b73d723c8b0",    
        "name": "example.com",
        "token": "xxxxxxxxxxxxxxxxxxxx_xxxxxxxxx",
        "records": [
            {"name": "home.example.com"},
            {"name": "office.example.com"}
        ]
    }
]
"""
CLOUDFLARE_ZONES = [
    {
        "id": "{zone_id}",
        "name": "{zone_name}",
        "token": "{zone_token}",
        "records": [
            {"name": "{record_name}"}
        ]
    }
]

# Location of the cache and log files
LAST_IP_FILE = "./cloudflare-dynamic-ip-last.txt"
LOG_FILE = "./cloudflare-dynamic-ip.log"

# Log level (see https://docs.python.org/3/library/logging.html)
LOGGING_LEVEL = logging.INFO

# Where you get the external IP address, this endpoint must return an IP address in plain text
CURRENT_IP_API = "https://api.ipify.org"
