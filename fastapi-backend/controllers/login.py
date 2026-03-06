from models.User import User
from sqlmodel import Session, select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def register_controller(email: str, password: str, session: Session) -> User | None:
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        return None

    hashed_password = get_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

async def login_controller(email: str, password: str, session: Session) -> User | None:
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user and verify_password(password, existing_user.password):
        return existing_user
    return None