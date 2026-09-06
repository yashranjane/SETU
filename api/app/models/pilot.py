from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Pilot(SQLModel, table=True):
    __tablename__ = "pilots"

    id: Optional[int] = Field(default=None, primary_key=True)
    challenge_id: int = Field(foreign_key="challenges.id", index=True)
    startup_id: int = Field(foreign_key="startups.id", index=True)
    buyer_id: int = Field(foreign_key="users.id", index=True)
    budget_inr: float = Field(default=0.0)
    status: str = Field(default="Active", index=True)  # Active, ScaleUpRecommended, Completed, Terminated
    mou_signed_at: str = Field(default="")
    dossier_exported: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
