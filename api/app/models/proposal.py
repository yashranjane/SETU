from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Proposal(SQLModel, table=True):
    __tablename__ = "proposals"

    id: Optional[int] = Field(default=None, primary_key=True)
    challenge_id: int = Field(index=True)
    seller_id: int = Field(foreign_key="users.id", index=True)
    startup_id: Optional[int] = Field(default=None, index=True)
    relevance_score: float = Field(default=0.0)
    pitch_text: str = Field(default="")
    proposed_budget_inr: float = Field(default=0.0)
    timeline_days: int = Field(default=30)
    status: str = Field(default="Submitted", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

