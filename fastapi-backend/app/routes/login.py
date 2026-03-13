from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel
from sqlmodel import Session, select
from app.utils.index import create_api_response, decrypt_password
from app.utils.auth import get_current_user
from app.controllers.login import register_controller, login_controller, refresh_controller, logout_controller
from app.database import get_session
from app.models.user import User
from app.models.refresh_token import RefreshToken
from loguru import logger

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

class UserCredentials(BaseModel):
    email: str
    password: str

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

    data,msg,code = await login_controller(email=email, password=password, session=session)

    if not data:
        return create_api_response(msg="Invalid email or password", code=500)

    return create_api_response(
        data=data,
        msg=msg,
        code=code
    )

class RefreshTokenPayload(BaseModel):
    refresh_token: str

@router.post("/refresh")
async def refresh_access_token(payload: RefreshTokenPayload, session: SessionDep):
    data,msg,code,http_status_code = await refresh_controller(payload.refresh_token, session)

    return create_api_response(
        data=data,
        msg=msg,
        code=code,
        http_status_code=http_status_code
    )


@router.post("/logout")
async def logout(current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    data, msg = await logout_controller(current_user["uid"], session)

    return create_api_response(
        data=data,
        msg=msg,
    )
