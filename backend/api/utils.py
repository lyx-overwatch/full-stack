from flask import jsonify, url_for, current_app

class APIException(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

def generate_sitemap(app):
    links = ['/admin/']
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            if "/admin/" not in url:
                links.append(url)

    links_html = "".join(["<li><a href='" + y + "'>" + y + "</a></li>" for y in links])
    return """
        <div style="text-align: center;">
        <img style="max-height: 80px" src='https://storage.googleapis.com/breathecode/boilerplates/rigo-baby.jpeg' />
        <h1>Rigo welcomes you to your API!!</h1>
        <p>API HOST: <script>document.write('<input style="padding: 5px; width: 300px" type="text" value="'+window.location.href+'" />');</script></p>
        <p>Start working on your project by following the <a href="https://start.4geeksacademy.com/starters/react-flask" target="_blank">Quick Start</a></p>
        <p>Remember to specify a real endpoint path like: </p>
        <ul style="text-align: left;">"""+links_html+"</ul></div>"

def APIResponse(data=None, msg="Success", code=200):
    return jsonify({
        "code": code,
        "data": data,
        "msg": msg
    }), code

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
        current_app.logger.error("RSA private key not configured or invalid, cannot decrypt password")
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
        current_app.logger.error(f"Password decryption failed (using plaintext fallback): {str(e)}")
        return None