from app.models.user import User
from sqlmodel import Session, select
from loguru import logger
import bcrypt

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
            return existing_user
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise e