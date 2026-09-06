from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Vendor(SQLModel, table=True):
    __tablename__ = "vendors"

    id: Optional[int] = Field(default=None, primary_key=True)
    seller_id: int = Field(foreign_key="users.id", unique=True, index=True)
    company_name: str = Field(default="")
    gem_seller_id: Optional[str] = Field(default=None, index=True)
    category: str = Field(default="")
    description: str = Field(default="")
    gstin: Optional[str] = Field(default=None)
    state: str = Field(default="")
    experience_years: int = Field(default=0)
    website: Optional[str] = Field(default=None)
    is_gem_verified: bool = Field(default=False)
    gem_rating: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
