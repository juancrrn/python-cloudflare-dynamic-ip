# Cloudflare DNS Record IP Retrieval Functions

This document describes the new functions added to retrieve the current IP address from Cloudflare DNS records.

## Functions

### `get_ip_from_cloudflare_record(zone_id, record_name, api_token)`

Retrieves the current IP address from a specific Cloudflare DNS A record.

**Parameters:**
- `zone_id` (str): The Cloudflare zone ID
- `record_name` (str): The DNS record name (e.g., 'example.com' or 'subdomain.example.com')
- `api_token` (str): The Cloudflare API token with Zone:Read permissions

**Returns:**
- `str | None`: The IP address from the DNS record, or None if not found or error occurred

**Example:**
```python
from cloudflare_dynamic_ip import get_ip_from_cloudflare_record

zone_id = "your_zone_id_here"
record_name = "example.com"
api_token = "your_api_token_here"

ip = get_ip_from_cloudflare_record(zone_id, record_name, api_token)
if ip:
    print(f"Current IP for {record_name}: {ip}")
else:
    print("Failed to retrieve IP")
```

### `get_ip_from_existing_record(record_config)`

Retrieves the current IP address using the existing configuration format from `CLOUDFLARE_RECORDS`.

**Parameters:**
- `record_config` (dict): Record configuration with keys:
  - `id`: record ID
  - `zone_id`: zone ID  
  - `name`: record name

**Returns:**
- `str | None`: The IP address from the DNS record, or None if not found or error occurred

**Example:**
```python
from cloudflare_dynamic_ip import get_ip_from_existing_record
from config.config import CLOUDFLARE_RECORDS

# Use the first configured record
if CLOUDFLARE_RECORDS:
    record_config = CLOUDFLARE_RECORDS[0]
    ip = get_ip_from_existing_record(record_config)
    if ip:
        print(f"Current IP: {ip}")
```

## Setup Requirements

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Cloudflare credentials:**
   - Copy `config/config.sample.py` to `config/config.py`
   - Add your Cloudflare zone ID, API token, and record details

3. **API Token Permissions:**
   Your Cloudflare API token needs at least:
   - Zone:Read permissions for the zones you want to query

## Usage Examples

### Basic Usage
```python
# Direct usage with parameters
ip = get_ip_from_cloudflare_record("zone_id", "example.com", "api_token")

# Using existing configuration
from config.config import CLOUDFLARE_RECORDS
ip = get_ip_from_existing_record(CLOUDFLARE_RECORDS[0])
```

### Error Handling
```python
ip = get_ip_from_cloudflare_record(zone_id, record_name, api_token)
if ip is None:
    print("Failed to retrieve IP - check logs for details")
else:
    print(f"Retrieved IP: {ip}")
```

### Integration with Existing Code
```python
# Compare current external IP with DNS record IP
current_external_ip = get_current_ip()  # existing function
dns_record_ip = get_ip_from_existing_record(record_config)

if current_external_ip != dns_record_ip:
    print("IP addresses don't match - update needed")
    # Proceed with update logic
```

## Testing

Run the test script to verify the functions work correctly:
```bash
python test_get_ip.py
```

Run the example script to see the functions in action:
```bash
python example_get_ip.py
```

## Error Handling

The functions include comprehensive error handling:
- Invalid API tokens
- Non-existent zones or records
- Network connectivity issues
- Missing configuration

All errors are logged using the existing logging configuration.

## Enhanced run() Function

The main `run()` function has been enhanced to use these IP retrieval functions for more intelligent update detection:

### New Behavior:
1. **Dual IP Checking**: Compares current IP against both:
   - Last saved IP (existing behavior)
   - Current DNS record IP (new functionality)

2. **Selective Updates**: Only updates records that actually need updating:
   - Checks each DNS record individually
   - Skips records that already have the correct IP
   - Reduces unnecessary API calls

3. **Update Verification**: After each update:
   - Re-checks the DNS record to verify the update succeeded
   - Logs verification results
   - Provides better error detection

4. **Enhanced Logging**: Provides detailed information about:
   - Which records need updating and why
   - Verification results for each update
   - Summary of actions taken

### Update Triggers:
The script will update DNS records if **either** condition is true:
- Current external IP ≠ last saved IP, **OR**
- Current external IP ≠ any DNS record IP

### Benefits:
- **Reduced API Usage**: Fewer unnecessary update calls
- **Better Accuracy**: Handles corrupted/missing last IP files
- **Fault Tolerance**: Continues with other records if one fails
- **Verification**: Confirms updates were successful
- **Detailed Monitoring**: Better logging for troubleshooting

## Integration Notes

These functions integrate seamlessly with the existing codebase:
- Use the same logging configuration
- Compatible with existing `CLOUDFLARE_ZONES` and `CLOUDFLARE_RECORDS` configuration
- Follow the same error handling patterns
- Use the official Cloudflare Python SDK for reliable API access
- Enhanced `run()` function maintains backward compatibility