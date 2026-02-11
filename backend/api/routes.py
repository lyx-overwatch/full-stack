"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import request, Blueprint
from flask import current_app
from api.models import db, User
from api.utils import APIResponse, decrypt_password
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)

@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return APIResponse(data=response_body), 200

@api.route('/register', methods=['POST'])
def register():
    try:
        email = request.json.get("email", None)
        password_input = request.json.get("password", None)

        if not email or not password_input:
            return APIResponse(msg="Missing email or password"), 400

        decrypted = decrypt_password(password_input)
        print(f"Debug Register - Decrypted password: {decrypted}")
        if decrypted:
            # If decryption succeeds, use the decrypted password
            password = decrypted
        else:
            # If decryption fails (e.g. invalid base64, wrong length), 
            # assume it's a plaintext password and log a warning
            current_app.logger.error("Password decryption failed or plaintext password provided. Using original input.")
            return APIResponse(msg="Decryption failed", code=500)

        user = User.query.filter_by(email=email).first()
        if user:
            return APIResponse(msg="User already exists", code=400)

        user = User(email=email, password=generate_password_hash(password), is_active=True)
        db.session.add(user)
        db.session.commit()

        register_return_data= {
            "user": user.serialize()
        }

        return APIResponse(data=register_return_data, msg="User created successfully", code=200 )
    except Exception as e:
        db.session.rollback()
        # 在服务端打印或记录详细错误，方便排查
        current_app.logger.error(f"Error in register: {str(e)}")
        # 返回通用的错误信息给前端，隐藏技术细节
        return APIResponse(msg="Internal server error, please try again later", code=500)

@api.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get("email", None)
        password_input = request.json.get("password", None)

        # DEBUG: 打印前端传来的数据
        current_app.logger.error(f"Debug - Login Attempt: email='{email}', password_input len='{len(str(password_input)) if password_input else 0}'")

        # Try to decrypt the password
        decrypted = decrypt_password(password_input)
        print(f"Debug Login - Decrypted password: {decrypted}")
        if decrypted:
            current_app.logger.error("Debug - Password successfully decrypted")
            password = decrypted
        else:
            current_app.logger.error("Debug - Password decryption failed or assume plaintext")
            password = password_input

        user = User.query.filter_by(email=email).first()
        
        if not user:
            current_app.logger.error("Debug - Error: User not found in DB")
        else:
            current_app.logger.error(f"Debug - User found: {user.email}")
            # DEBUG: 查看密码验证结果
            print(f"Debug - Stored hashed password: {user.password} - {password}")
            is_valid = check_password_hash(user.password, password)
            current_app.logger.error(f"Debug - Password check result: {is_valid}")

        if not user or not check_password_hash(user.password, password):
            return APIResponse(msg="Bad email or password", code=401)

        access_token = create_access_token(identity=email)
        login_return_data= APIResponse({
            "access_token": access_token,
            "userid": user.id
        }, msg="Login successful")
        return login_return_data
    except Exception as e:
        # 在服务端打印或记录详细错误
        current_app.logger.error(f"Error in login: {str(e)}")
        # 返回通用的错误信息
        return APIResponse(msg="Internal server error, please try again later", code=500)
