from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str = Field(default="")
    password_hash: str
    role: str = Field(default="buyer", index=True)
    org_name: str = Field(default="")
    state: str = Field(default="")
    phone: str = Field(default="")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
