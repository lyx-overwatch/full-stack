import os
from sqlmodel import create_engine, Session
from typing import Generator
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise RuntimeError("环境变量 DATABASE_URL 未设置，请在 .env 或系统环境中配置。")

engine = create_engine(db_url)

def get_session() -> Generator:
    with Session(engine) as session:
        yield session