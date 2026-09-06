from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Contract(SQLModel, table=True):
    __tablename__ = "contracts"

    id: Optional[int] = Field(default=None, primary_key=True)
    requirement_id: int = Field(foreign_key="requirements.id", index=True)
    vendor_id: int = Field(foreign_key="vendors.id", index=True)
    buyer_id: int = Field(foreign_key="users.id", index=True)
    proposal_id: int = Field(foreign_key="proposals.id", unique=True, index=True)
    total_value_inr: float = Field(default=0.0)
    start_date: str = Field(default="")
    end_date: str = Field(default="")
    status: str = Field(default="Active", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
