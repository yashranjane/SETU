from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.auth import require_admin
from app.db import get_session
from app.models.challenge import Challenge
from app.models.startup import Startup
from app.models.pilot import Pilot
from app.models.audit import AuditBlock
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def admin_stats(
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    buyers = len(session.exec(select(User).where(User.role == "buyer")).all())
    sellers = len(session.exec(select(User).where(User.role == "seller")).all())
    challenges = len(session.exec(select(Challenge)).all())
    pilots = len(session.exec(select(Pilot)).all())
    startups = len(session.exec(select(Startup)).all())
    audit_blocks = len(session.exec(select(AuditBlock)).all())
    return {
        "buyers": buyers,
        "sellers": sellers,
        "challenges": challenges,
        "pilots": pilots,
        "startups": startups,
        "audit_blocks": audit_blocks,
    }
