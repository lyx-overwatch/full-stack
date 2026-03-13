
from app.models.user import User
from app.models.refresh_token import RefreshToken
from sqlmodel import Session, select
from loguru import logger
import bcrypt
from datetime import datetime
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    hash_token,
    REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE,
    AUTH_USER_INVALID_CODE,
)

def get_password_hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

async def register_controller(email: str, password: str, session: Session) -> User | None:
    try:
        existing_user = session.exec(select(User).where(User.email == email)).first()
        if existing_user:
            raise ValueError("User with this email already exists")
        hashed_password = get_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise e

async def login_controller(email: str, password: str, session: Session) -> User | None:
    existing_user = session.exec(select(User).where(User.email == email)).first()
    try:
        if existing_user and verify_password(password, existing_user.password.encode('utf-8')):
            access_token = create_access_token({"sub": existing_user.email, "uid": existing_user.id})
            refresh_token = create_refresh_token({"sub": existing_user.email, "uid": existing_user.id})
            refresh_payload, _, _ = verify_refresh_token(refresh_token)
            if not refresh_payload:
                return create_api_response(msg="Failed to issue refresh token", code=500)

            refresh_record = RefreshToken(
                user_id=existing_user.id,
                jti=refresh_payload["jti"],
                token_hash=hash_token(refresh_token),
                expires_at=datetime.utcfromtimestamp(refresh_payload["exp"]),
            )
            session.add(refresh_record)
            session.commit()

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "email": existing_user.email,
                "uuid": existing_user.id,
            }, 'Login successful', 200
        return None, "Invalid email or password", 500
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise e

async def refresh_controller(refresh_token: str, session: Session) -> tuple:
    try:
        token_payload, err_code, err_msg = verify_refresh_token(refresh_token)

        if not token_payload:
            return None, err_msg, err_code or REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, 401

        uid = token_payload.get("uid")
        email = token_payload.get("sub")
        jti = token_payload.get("jti")

        if not uid or not email or not jti:
            return None, "Invalid refresh token payload", REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, 401

        refresh_record = session.exec(
            select(RefreshToken).where(
                RefreshToken.jti == jti,
                RefreshToken.user_id == uid,
                RefreshToken.revoked_at == None,
            )
        ).first()

        if not refresh_record:
            return None, "Refresh token has been revoked", REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, 401

        if refresh_record.expires_at <= datetime.utcnow():
            return None, "Invalid or expired refresh token", REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, 401

        if refresh_record.token_hash != hash_token(refresh_token):
            return None, "Invalid refresh token", REFRESH_TOKEN_INVALID_OR_EXPIRED_CODE, 401

        user = session.exec(select(User).where(User.id == uid)).first()
        if not user:
            return None, "User not found or session invalid", AUTH_USER_INVALID_CODE, 401

        access_token = create_access_token({"sub": user.email, "uid": user.id})
        refresh_token = create_refresh_token({"sub": user.email, "uid": user.id})

        refresh_record.revoked_at = datetime.utcnow()
        new_refresh_payload, _, _ = verify_refresh_token(refresh_token)

        if not new_refresh_payload:
            return None, "Failed to rotate refresh token", 500, 500

        new_refresh_record = RefreshToken(
            user_id=user.id,
            jti=new_refresh_payload["jti"],
            token_hash=hash_token(refresh_token),
            expires_at=datetime.utcfromtimestamp(new_refresh_payload["exp"]),
        )
        session.add(new_refresh_record)
        session.commit()

        return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "email": user.email,
                "uuid": user.id,
                }, 'token refreshed', 200, 200
    except Exception as e:
        logger.error(f"Error during token refresh: {e}")
        raise e

async def logout_controller(user_id: str, session: Session) -> tuple:
    try:
        active_tokens = session.exec(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at == None,
            )
        ).all()

        revoked_count = 0
        now = datetime.utcnow()
        for token in active_tokens:
            token.revoked_at = now
            revoked_count += 1

        session.commit()

        return {
            "uid": user_id,
            "revoked_refresh_tokens": revoked_count
        }, "Logout successful"

    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise e