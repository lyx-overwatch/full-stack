import uuid
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: uuid.UUID | None = Field(default=lambda: uuid.uuid4().hex, primary_key=True)
    email: str = Field(max_length=100)
    password: str = Field(max_length=256)

