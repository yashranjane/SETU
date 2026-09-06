from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel


class AuditBlock(SQLModel, table=True):
    __tablename__ = "audit_ledger"

    id: Optional[int] = Field(default=None, primary_key=True)
    block_index: int = Field(index=True)
    prev_hash: str = Field(index=True)
    block_hash: str = Field(unique=True, index=True)
    actor: str = Field(default="")
    action: str = Field(default="")
    entity_id: str = Field(default="")
    entity_type: str = Field(default="")
    details: str = Field(default="")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
