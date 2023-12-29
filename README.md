# Python script to manage dynamic IP addresses in Cloudflare DNS

Can be scheduled to run periodically using Cron jobs.

## Introduction

Use this script as a template for managing dynamic IP addresses in Cloudflare DNS using API v4.

Documentation about updating a DNS record through Cloudflare API v4 is available here: https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-update-dns-record.

## Installation

1. Generate a token for the Cloudflare API. For mor details, see https://developers.cloudflare.com/fundamentals/api/get-started/create-token/.

2. Verify the token:

```shell
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type:application/json"
```

2. Get your DNS zone's ID from your dashboard. For more details, see https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/.

3. Get your DNS record's details using the API:

    - Only records of type `A` (IPv4) are supported by this script.

```shell
curl -X GET "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records" \
     -H "Authorization: Bearer {token}"
```

5. Copy the `config/config.sample.py` file to `config/config.py` and fill in the required information.

6. Install the required Python packages:

```shell
pip install -r requirements.txt
```

7. Test the script:

```shell
python cloudflare-dynamic-ip.py
```

It should generate a log file called `cloudflare-dynamic-ip.log` in the same directory.

## Usage

Run the script:

```shell
python cloudflare-dynamic-ip.py
```

## Cron

If you want to run the script programatically, you can use Cron jobs:

```console
# crontab -e
```

And add, for example:

```shell
0,14,29,44 * * * * /path/to/python /path/to/cloudflare-dynamic-ip.py
```
