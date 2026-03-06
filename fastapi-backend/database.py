import os
from sqlmodel import create_engine
from typing import Generator

db_url = os.getenv("DATABASE_URL")

engine = create_engine(db_url)

def get_session() -> Generator:
    with Session(engine) as session:
        yield session