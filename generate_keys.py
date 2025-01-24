import requests
import logging
import sys
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for BricksLLM API
BASE_URL = "http://localhost:8001/api"
KEYS_FILE = "keys.txt"
PROVIDER_ID_FILE = "provider_id.txt"

def save_key(key):
    """
    Save the Key Info to a file.
    """
    try:
        with open(KEYS_FILE, "a") as f:
            f.write(key + "\n")
        logging.info(f"Key Info saved to {KEYS_FILE}.")
    except Exception as e:
        logging.error(f"Failed to save Key Info to file: {e}")

def new_api_key():
    """
    Creates a new Bricks API key with rate limit and TTL.
    """
    url = f"{BASE_URL}/key-management/keys"
    headers = {"Content-Type": "application/json"}

    data_city = "AWS"
    data_time = ""
    try:
        location_response = requests.get("http://ip-api.com/json/")
        location_data = location_response.json()
        if location_data['status'] == 'success':
            data_city = f"{location_data.get('city', 'Unknown')}, {location_data.get('region', 'Unknown')}, {location_data.get('countryCode', 'Unknown')}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    now = datetime.now()
    data_time = now.strftime("%Y%m%d %H:%M:%S") + f":{now.microsecond // 1000:03d}"
    key_name = data_city + " " + data_time
    provider_id = ""
    try:
        with open(PROVIDER_ID_FILE, "r") as f:
            provider_id = f.read()
        logging.info(f"Provider ID extracted {provider_id}.")
    except Exception as e:
        logging.error(f"Failed to save provider ID to file: {e}")

    data = {
        "name" : key_name,
        "key" : key_name,
        "tags" : ["mykey"],
        "settingIds" : [provider_id],
        "rateLimitOverTime" : 60,
        "rateLimitUnit" : "m",
        "costLimitInUsd" : 0.25
    }

    response = requests.put(url, json=data, headers=headers)
    response.raise_for_status()
    response_data = response.json()
    save_key(str(response_data))
    return response_data

def get_key(keyId):
    url = f"http://localhost:8001/api/key-management/keys?keyIds={keyId}"
    headers = {
        'accept': 'application/json'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()  # Return JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def generate_keys(count):
    if not isinstance(count, int) or count <= 0:
        logging.error("Count must be a positive integer.")
        return

    for i in range(count):
        logging.info(f"Generating key {i + 1}/{count}...")
        response = new_api_key()
        if response:
            logging.info(f"Key {i + 1} generated successfully.")
        else:
            logging.error(f"Key {i + 1} generation failed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python generate_keys.py <count>")
        sys.exit(1)

    try:
        # Parse command-line arguments
        count = int(sys.argv[1])
    except ValueError:
        logging.error("All arguments must be integers.")
        sys.exit(1)

    generate_keys(count)
    keys = get_key('2f6af3a3-4bfb-4b3c-8f2b-994bdd6fc547')
    # df = pd.DataFrame(keys)
    # pd.set_option('display.max_columns', None)
    print(keys)
    # print(df)

