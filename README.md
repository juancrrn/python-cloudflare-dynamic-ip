# Python script to manage dynamic IP addresses in Cloudflare DNS

Can be scheduled to run periodically using Cron jobs.

## Introduction

Use this script as a template for managing dynamic IP addresses in Cloudflare DNS using API v4.

Only A (IPv4) records are supported, but you can easily extend it to support other types of records.

See also:
- [Cloudflare API | DNS › Records › Overwrite DNS Record](https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-update-dns-record.)

## Requirements

- A custom domain name or subdomain, like `example.com` or `sub.example.com`.
- A Cloudflare account. The free plan is enough.
- One or more DNS records of type A (IPv4) set up in your Cloudflare DNS zone.
- Python 3, with modules `python3-pip`, `requests` and `python3-venv` (optional).
- A virtual environment (optional, but recommended).

## Installation

### Cloudflare setup

1. Generate a token for the Cloudflare API following the steps in [Create API token · Cloudflare Fundamentals docs](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/).

2. Verify the token:

```shell
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type:application/json"
```

You should see a JSON result with a message similar to "This API Token is valid and active".

3. Get the ID of your DNS zone by accessing your Cloudflare Dashboard and following the steps in [Find account and zone IDs · Cloudflare Fundamentals docs](https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/).

4. Save both the token and your zone's ID for the next steps.

### Python setup

1. A Python virtual environment is recommended, but you can skip this step if you install the dependencies globally. To 
create and activate a virtual environment, run:

```shell
python3 -m venv .venv

source .venv/bin/activate
```

2. Install the required Python packages:

```shell
pip install -r requirements.txt
```

3. Copy the `config/config.sample.py` file to `config/config.py` and fill in the required information, including the
token, the zone ID and the DNS records you want to manage.

### Test run

1. Run the script:

```shell
python cloudflare-dynamic-ip.py
```

2. A log file called `cloudflare-dynamic-ip.log` should appear in the same directory.

3. Check the log file for any errors or messages. If everything is set up correctly, you should see a message indicating
that the DNS records were updated successfully.

## Usage

Once the setup has been completed and the script has been tested, you just need to run it to update your DNS records 
with the current public IP address of your server.

```shell
python cloudflare-dynamic-ip.py
```

## Cron

If you want to run the script periodically, you can use Cron jobs:

```shell
crontab -e
```

And add, e.g.:

```
@reboot /path/to/.venv/bin/python /path/to/cloudflare-dynamic-ip.py
0 0,12 * * * /path/to/.venv/bin/python /path/to/cloudflare-dynamic-ip.py
```

This Cron configuration will run the script at reboot and every day at 00:00 and 12:00.
