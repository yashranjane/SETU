from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db import get_session
from app.models.audit import AuditBlock
from app.models.user import User
from app.services.audit_service import verify_chain

router = APIRouter(prefix="/audit", tags=["Audit Ledger"])


@router.get("/ledger", response_model=List[dict])
def get_ledger(session: Session = Depends(get_session)):
    blocks = session.exec(select(AuditBlock).order_by(AuditBlock.block_index.desc())).all()
    return [b.model_dump() for b in blocks]


@router.post("/verify", response_model=dict)
def run_audit_verification(session: Session = Depends(get_session)):
    """
    Step 4: Interactive verification of the SHA-256 parent-child cryptographic hash chain.
    """
    return verify_chain(session)
