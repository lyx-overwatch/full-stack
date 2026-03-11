from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def create_api_response(data=None, msg="Success", code=200) -> JSONResponse:
    content = jsonable_encoder({"code": code, "data": data, "msg": msg})
    return JSONResponse(status_code=code, content=content)

import os
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5

def load_private_key():
    key_str = os.getenv("RSA_PRIVATE_KEY")
    if not key_str:
        return None
    try:
        return RSA.import_key(key_str.replace('\\n', '\n'))
    except Exception as e:
        print(f"Error loading private key: {e}")
        return None

private_key = load_private_key()


def decrypt_password(encrypted_password_b64):
    """
    Helper function to decrypt password using the private key.
    Expects a base64 encoded string from the frontend.
    """
    if not private_key:
        # current_app.logger.error("RSA private key not configured or invalid, cannot decrypt password")
        return None

    try:
        # Decode the base64 string to get the encrypted bytes
        encrypted_bytes = base64.b64decode(encrypted_password_b64)
        
        cipher = Cipher_PKCS1_v1_5.new(private_key)
        sentinel = object()
        # Decrypt properly using the bytes
        decrypted_data = cipher.decrypt(encrypted_bytes, sentinel)
        
        if decrypted_data is sentinel:
            return None
            
        return decrypted_data.decode('utf-8')
    except Exception as e:
        # current_app.logger.error(f"Password decryption failed (using plaintext fallback): {str(e)}")
        return None