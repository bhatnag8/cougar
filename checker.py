from fastapi import FastAPI, HTTPException
from cryptography.fernet import Fernet
import os
import hashlib
import base64
import logging
import generate_keys
import json
from dotenv import load_dotenv

KEYS_FILE = "keys.txt"

def keys_status():
    with open(KEYS_FILE, "r") as f:
        while 1:
            line = f.readline()  # Read one line and strip any leading/trailing whitespace
            if not line:
                break
            line = line.strip()
            try:
                corrected_line = (
                    line.replace("'", '"')
                        .replace("True", "true")
                        .replace("False", "false")
                        .replace("None", "null")
                )
                data = json.loads(corrected_line)
                key = generate_keys.get_key(data['keyId'])
                filtered = {
                    k: (key[k][:8] + "*****" + key[k][-12:] if k in ['key', 'keyId'] else key[k])
                    for k in ['name', 'keyId', 'revoked', 'key', 'costLimitInUsdOverTime']
                    if k in key
                }
                with open("keys_status.txt", "a") as g:
                    g.write(str(filtered) + "\n")
            except json.JSONDecodeError as json_error:
                logging.error(f"Invalid JSON format in file: {json_error}")


# Encrypt the file using Fernet
def encrypt_file(file_path, encryption_key):
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()  # Read file contents

        # Encrypt the file data
        fernet = Fernet(encryption_key)
        encrypted_data = fernet.encrypt(file_data)

        # Overwrite the file with encrypted content
        with open(file_path, "wb") as f:
            f.write(encrypted_data)

        print(f"File {file_path} encrypted successfully.")
    except Exception as e:
        logging.error(f"Error during file encryption: {e}")

if __name__ == "__main__":
    keys_status()
    word = os.getenv("FERNET_WORD")
    hashed_word = hashlib.sha256(word.encode()).digest()
    encryption_key = base64.urlsafe_b64encode(hashed_word[:32])
    if encryption_key is None:
            logging.error("Environment variable 'FERNET_KEY' is not set.")
    else:
        try:
            encryption_key = encryption_key
            encrypt_file("keys_status.txt", encryption_key)
        except Exception as e:
            logging.error(f"Failed to encrypt the file: {e}")
