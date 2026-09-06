from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Startup(SQLModel, table=True):
    __tablename__ = "startups"

    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: Optional[int] = Field(default=None, foreign_key="users.id", unique=True, index=True)
    name: str = Field(index=True)
    domain: str = Field(default="")
    solution_title: str = Field(default="")
    description: str = Field(default="")
    trl_level: int = Field(default=7)  # 1 to 9
    dpiit_certified: bool = Field(default=True)
    dpiit_number: Optional[str] = Field(default="DIPP12345")
    gem_seller_id: Optional[str] = Field(default=None, index=True)
    is_gem_verified: bool = Field(default=True)
    gem_rating: Optional[float] = Field(default=4.8)
    financial_capacity_score: float = Field(default=0.85)  # 0.0 - 1.0
    state: str = Field(default="Maharashtra")
    website: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
