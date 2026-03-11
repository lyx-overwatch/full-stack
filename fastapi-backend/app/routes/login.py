from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import BaseModel
from sqlmodel import Session
from app.utils.index import create_api_response, decrypt_password
from app.controllers.login import register_controller, login_controller
from app.database import get_session
from loguru import logger

router = APIRouter()

class UserCredentials(BaseModel):
    email: str
    password: str

SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/register")
async def register(credentials: UserCredentials, session: SessionDep):  

    email = credentials.email
    password_input = credentials.password

    if not email or not password_input:
        logger.error('Missing email or password')
        return create_api_response(msg="Missing email or password", code=500)

    decrypted = decrypt_password(password_input)

    if decrypted:
        password = decrypted
        try:
             result = await register_controller(email=email, password=password, session=session)
             return create_api_response(msg="Registration successful")
        except Exception as e:
             logger.error(f"Error during registration: {e}")
             return create_api_response(msg="Registration failed", code=500)
    else:
        logger.error('Decryption failed')
        return create_api_response(msg="Decryption failed", code=500)

@router.post("/login")
async def login(credentials: UserCredentials, session: SessionDep):

    email = credentials.email
    password_input = credentials.password

    if not email or not password_input:
        return create_api_response(msg="Missing email or password", code=500)

    decrypted = decrypt_password(password_input)

    if decrypted:
        password = decrypted
    else:
        return create_api_response(msg="Decryption failed", code=500)

    result = await login_controller(email=email, password=password, session=session)

    if not result:
        return create_api_response(msg="Invalid email or password", code=500)

    return create_api_response(msg="Login successful")
