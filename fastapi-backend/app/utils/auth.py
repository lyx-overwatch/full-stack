import os
import hashlib
import uuid
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User

load_dotenv()

ACCESS_TOKEN_EXPIRED_CODE = 40101
ACCESS_TOKEN_INVALID_CODE = 40102
AUTH_USER_INVALID_CODE = 40103
REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE = 40104


def _create_token(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "token_type": token_type})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm="HS256")
    return encoded_jwt

def create_access_token(data: dict, expires_delta: timedelta = None):
    if not expires_delta:
        access_token_expire_hours = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))
        expires_delta = timedelta(hours=access_token_expire_hours)
        # expires_delta = timedelta(seconds=10)
    return _create_token(data=data, expires_delta=expires_delta, token_type="access")


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    payload = data.copy()
    payload.setdefault("jti", uuid.uuid4().hex)
    if not expires_delta:
        refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        expires_delta = timedelta(days=refresh_token_expire_days)
    return _create_token(data=payload, expires_delta=expires_delta, token_type="refresh")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token(token: str, expected_token_type: str):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        token_type = payload.get("token_type")
        if token_type != expected_token_type:
            logger.warning(
                f"Token type mismatch. Expected: {expected_token_type}, got: {token_type}"
            )
            if expected_token_type == "access":
                return None, ACCESS_TOKEN_INVALID_CODE, "Invalid access token"
            return None, REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, "Invalid refresh token"
        return payload, None, None
    except ExpiredSignatureError:
        logger.warning("Token has expired")
        if expected_token_type == "access":
            return None, ACCESS_TOKEN_EXPIRED_CODE, "Access token expired"
        return None, REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, "Invalid or expired refresh token"
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        if expected_token_type == "access":
            return None, ACCESS_TOKEN_INVALID_CODE, "Invalid access token"
        return None, REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, "Invalid or expired refresh token"

def verify_access_token(token: str):
    return verify_token(token=token, expected_token_type="access")


def verify_refresh_token(token: str):
    return verify_token(token=token, expected_token_type="refresh")

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session),
):
    """获取当前用户依赖项"""
    token = credentials.credentials
    payload, err_code, err_msg = verify_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": err_code, "msg": err_msg},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    uid = payload.get("uid")
    if uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": ACCESS_TOKEN_INVALID_CODE, "msg": "Invalid access token"},
        )

    user = session.exec(select(User).where(User.id == uid)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": AUTH_USER_INVALID_CODE, "msg": "User not found or session invalid"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"uid": user.id, "email": user.email, "payload": payload}

