from fastapi import FastAPI, HTTPException
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64
import logging
import generate_keys
import json

app = FastAPI()
KEYS_FILE = "keys.txt"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_200_key():
    var = 0
    while var < 5:
        try:
            with open(KEYS_FILE, "r") as f:
                line = f.read()
                print(line)
                data = json.loads(line.strip())
                key =  generate_keys.get_key(data['keyID'])[0]
                if key['revoked'] != "False":
                    return key['key']
        except Exception as e:
            logging.error(f"Failed to saveget keye: {e}")
        var += 1

def encrypt(text: str) -> dict:
    iv = os.urandom(12)  # GCM standard IV size is 12 bytes
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(text.encode("utf-8")) + encryptor.finalize()
    auth_tag = encryptor.tag
    return {
        "encryptedData": base64.b64encode(encrypted_data).decode("utf-8"),
        "iv": base64.b64encode(iv).decode("utf-8"),
        "authTag": base64.b64encode(auth_tag).decode("utf-8"),
    }

@app.get("/get-api-key")
def get_api_key():
    key = get_200_key()

    return {"test": "test"}
