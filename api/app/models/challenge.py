from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Challenge(SQLModel, table=True):
    __tablename__ = "challenges"

    id: Optional[int] = Field(default=None, primary_key=True)
    buyer_id: int = Field(foreign_key="users.id", index=True)
    title: str = Field(index=True)
    department: str = Field(default="")
    location: str = Field(default="")
    budget_ceiling_inr: float = Field(default=0.0)
    outcome_statement: str = Field(default="")
    category: str = Field(default="")
    deadline: str = Field(default="")
    status: str = Field(default="Open", index=True)  # Open, Matched, PilotActive, Completed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
