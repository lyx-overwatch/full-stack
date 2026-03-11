import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class RefreshToken(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    user_id: str = Field(index=True, max_length=64)
    jti: str = Field(index=True, unique=True, max_length=64)
    token_hash: str = Field(index=True, unique=True, max_length=64)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = Field(default=None)
