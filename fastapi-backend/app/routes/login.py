from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import BaseModel
from sqlmodel import Session
from app.utils.index import create_api_response, decrypt_password
from app.controllers.login import register_controller, login_controller
from app.database import get_session

router = APIRouter()

class UserCredentials(BaseModel):
    email: str
    password: str

CommonDeps= Annotated[UserCredentials, Depends()]
SessionDep = Annotated[Session, Depends(get_session)]

@router.post("/register")
async def register(credentials: CommonDeps, session: SessionDep):

    email = credentials.email
    password_input = credentials.password

    if not email or not password_input:
        return create_api_response(msg="Missing email or password", code=500)

    decrypted = decrypt_password(password_input)

    if decrypted:
        password = decrypted
        result = await register_controller(email=email, password=password, session=session)
        if not result:
            return create_api_response(msg="User already exists", code=500)
        return create_api_response(msg="Registration successful")
    else:
        return create_api_response(msg="Decryption failed", code=500)


@router.post("/login")
async def login(credentials: CommonDeps, session: SessionDep):

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
