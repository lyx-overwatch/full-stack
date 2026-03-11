from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from loguru import logger 
from dotenv import load_dotenv

load_dotenv()

def create_api_response(data=None, msg="Success", code=200) -> JSONResponse:
    content = jsonable_encoder({"code": code, "data": data, "msg": msg})
    return JSONResponse(status_code=code, content=content)

import os
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


def load_private_key():
    key_str = os.getenv("RSA_PRIVATE_KEY")
    if not key_str:
        logger.error("RSA_PRIVATE_KEY environment variable is not set.")
        return None
    try:
        formatted_key = key_str.strip()
        return serialization.load_pem_private_key(
            formatted_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
    except ValueError as ve:
        logger.error(f"ValueError while loading private key: {ve}")
    except Exception as e:
        logger.error(f"Unexpected error loading private key: {e}")
    return None

private_key = load_private_key()

def decrypt_password(encrypted_password_b64):
    """
    Helper function to decrypt password using the private key.
    Expects a base64 encoded string from the frontend.
    """
    
    if not private_key:
        logger.error("RSA private key not configured or invalid, cannot decrypt password")
        return None

    try:
        # Decode the base64 string to get the encrypted bytes
        encrypted_bytes = base64.b64decode(encrypted_password_b64.encode('utf-8'))
        logger.debug(f"Encrypted bytes: {encrypted_bytes.hex()}")

        # Decrypt properly using the bytes with PKCS1v15 padding
        decrypted_data = private_key.decrypt(
            encrypted_bytes,
            padding.PKCS1v15()
        )

        try:
            return decrypted_data.decode('utf-8')
        except UnicodeDecodeError as e:
            logger.error(f"Decrypted data is not valid UTF-8: {e}. Raw data: {decrypted_data.hex()}")
            return None

    except ValueError as ve:
        logger.error(f"ValueError during decryption: {ve}")
    except Exception as e:
        logger.error(f"Unexpected error during decryption: {e}")
    return None


  