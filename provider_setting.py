import requests
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base URL for BricksLLM API
BASE_URL = "http://localhost:8001/api"
PROVIDER_ID_FILE = "provider_id.txt"

def save_provider_id(provider_id):
    """
    Save the provider ID to a file.
    """
    try:
        with open(PROVIDER_ID_FILE, "w") as f:
            f.write(provider_id)
        logging.info(f"Provider ID saved to {PROVIDER_ID_FILE}.")
    except Exception as e:
        logging.error(f"Failed to save provider ID to file: {e}")

def new_provider_setting(key):
    """
    Creates or updates provider settings for OpenAI.
    """
    if not key:
        logging.error("API key cannot be empty.")
        return

    url = f"{BASE_URL}/provider-settings"
    headers = {"Content-Type": "application/json"}
    data = {
       "provider": "openai",
        "setting": {
            "apikey": key
        }
    }

    try:
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()

        # Extract the ID from the response JSON
        response_data = response.json()
        provider_id = response_data.get("id")

        if provider_id:
            save_provider_id(provider_id)
            logging.info(f"Provider setting updated successfully. ID: {provider_id}")
        else:
            logging.warning("Response did not contain an 'id' field.")

    except requests.RequestException as e:
        logging.error(f"Failed to update provider setting: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python provider_setting.py <apikey>")
        sys.exit(1)

    api_key = sys.argv[1]
    new_provider_setting(api_key)
