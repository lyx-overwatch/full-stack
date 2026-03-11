from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel
from sqlmodel import Session, select
from app.utils.index import create_api_response, decrypt_password
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user,
    hash_token,
    REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE,
    AUTH_USER_INVALID_CODE,
)
from app.controllers.login import register_controller, login_controller
from app.database import get_session
from app.models.user import User
from app.models.refresh_token import RefreshToken
from loguru import logger

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

class UserCredentials(BaseModel):
    email: str
    password: str


class RefreshTokenPayload(BaseModel):
    refresh_token: str

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

    access_token = create_access_token({"sub": result.email, "uid": result.id})
    refresh_token = create_refresh_token({"sub": result.email, "uid": result.id})
    refresh_payload, _, _ = verify_refresh_token(refresh_token)
    if not refresh_payload:
        return create_api_response(msg="Failed to issue refresh token", code=500)

    refresh_record = RefreshToken(
        user_id=result.id,
        jti=refresh_payload["jti"],
        token_hash=hash_token(refresh_token),
        expires_at=datetime.utcfromtimestamp(refresh_payload["exp"]),
    )
    session.add(refresh_record)
    session.commit()

    return create_api_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "email": result.email,
            "uuid": result.id,
        },
        msg="Login successful",
    )


@router.post("/refresh")
async def refresh_access_token(payload: RefreshTokenPayload, session: SessionDep):
    token_payload, err_code, err_msg = verify_refresh_token(payload.refresh_token)
    if not token_payload:
        return create_api_response(
            msg=err_msg,
            code=err_code or REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE,
            http_status_code=401,
        )

    uid = token_payload.get("uid")
    email = token_payload.get("sub")
    jti = token_payload.get("jti")

    if not uid or not email or not jti:
        return create_api_response(
            msg="Invalid refresh token payload",
            code=REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE,
            http_status_code=401,
        )

    refresh_record = session.exec(
        select(RefreshToken).where(
            RefreshToken.jti == jti,
            RefreshToken.user_id == uid,
            RefreshToken.revoked_at == None,
        )
    ).first()

    if not refresh_record:
        return create_api_response(
            msg="Refresh token has been revoked",
            code=REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE,
            http_status_code=401,
        )

    if refresh_record.expires_at <= datetime.utcnow():
        return create_api_response(
            msg="Invalid or expired refresh token",
            code=REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE,
            http_status_code=401,
        )

    if refresh_record.token_hash != hash_token(payload.refresh_token):
        return create_api_response(
            msg="Invalid refresh token",
            code=REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE,
            http_status_code=401,
        )

    user = session.exec(select(User).where(User.id == uid)).first()
    if not user:
        return create_api_response(
            msg="User not found or session invalid",
            code=AUTH_USER_INVALID_CODE,
            http_status_code=401,
        )

    access_token = create_access_token({"sub": user.email, "uid": user.id})
    refresh_token = create_refresh_token({"sub": user.email, "uid": user.id})

    refresh_record.revoked_at = datetime.utcnow()
    new_refresh_payload, _, _ = verify_refresh_token(refresh_token)
    if not new_refresh_payload:
        return create_api_response(msg="Failed to rotate refresh token", code=500)

    new_refresh_record = RefreshToken(
        user_id=user.id,
        jti=new_refresh_payload["jti"],
        token_hash=hash_token(refresh_token),
        expires_at=datetime.utcfromtimestamp(new_refresh_payload["exp"]),
    )
    session.add(new_refresh_record)
    session.commit()

    return create_api_response(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "email": user.email,
            "uuid": user.id,
        },
        msg="Token refreshed",
    )


@router.post("/logout")
async def logout(current_user: Annotated[dict, Depends(get_current_user)], session: SessionDep):
    active_tokens = session.exec(
        select(RefreshToken).where(
            RefreshToken.user_id == current_user["uid"],
            RefreshToken.revoked_at == None,
        )
    ).all()

    revoked_count = 0
    now = datetime.utcnow()
    for token in active_tokens:
        token.revoked_at = now
        revoked_count += 1

    session.commit()

    return create_api_response(
        data={"uid": current_user["uid"], "revoked_refresh_tokens": revoked_count},
        msg="Logout successful",
    )
