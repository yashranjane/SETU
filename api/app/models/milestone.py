from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class Milestone(SQLModel, table=True):
    __tablename__ = "sandbox_milestones"

    id: Optional[int] = Field(default=None, primary_key=True)
    pilot_id: int = Field(foreign_key="pilots.id", index=True)
    phase: int  # 1 (20%), 2 (50%), 3 (30%)
    title: str = Field(default="")
    description: str = Field(default="")
    amount_inr: float = Field(default=0.0)
    proof_url: Optional[str] = Field(default=None)
    proof_video_url: Optional[str] = Field(default=None)
    proof_type: Optional[str] = Field(default="url")  # url, video, both
    proof_notes: Optional[str] = Field(default=None)
    status: str = Field(default="Pending", index=True)  # Pending, ProofSubmitted, Approved
    approved_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
