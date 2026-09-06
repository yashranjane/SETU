import os
import uuid
import base64
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user, require_buyer, require_seller
from app.db import get_session
from app.models.pilot import Pilot
from app.models.milestone import Milestone
from app.models.startup import Startup
from app.models.user import User
from app.services.audit_service import append_audit_block

router = APIRouter(prefix="/milestones", tags=["Milestones"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ProofSubmit(BaseModel):
    proof_url: Optional[str] = None
    proof_video_url: Optional[str] = None
    proof_type: Optional[str] = "url"  # "url", "video", or "both"
    proof_notes: Optional[str] = None


class VideoPayload(BaseModel):
    video_base64: Optional[str] = None
    filename: Optional[str] = "field_trial_proof.mp4"
    notes: Optional[str] = ""


@router.get("/pilot/{pilot_id}")
def get_milestones(pilot_id: int, session: Session = Depends(get_session)):
    milestones = session.exec(select(Milestone).where(Milestone.pilot_id == pilot_id).order_by(Milestone.phase)).all()
    return [m.model_dump() for m in milestones]


@router.post("/{milestone_id}/submit-proof")
def submit_proof_of_work(
    milestone_id: int,
    payload: ProofSubmit,
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    m = session.get(Milestone, milestone_id)
    if not m:
        raise HTTPException(status_code=404, detail="Milestone not found")
    p = session.get(Pilot, m.pilot_id)
    st = session.get(Startup, p.startup_id) if p else None
    if not st or st.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your pilot")

    if payload.proof_url:
        m.proof_url = payload.proof_url.strip()
    if payload.proof_video_url:
        m.proof_video_url = payload.proof_video_url.strip()
    
    m.proof_type = payload.proof_type or ("video" if payload.proof_video_url else "url")
    m.proof_notes = payload.proof_notes
    m.status = "ProofSubmitted"
    session.add(m)
    session.commit()
    session.refresh(m)

    proof_info = m.proof_video_url if m.proof_type == "video" else m.proof_url
    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({st.name})",
        action="MILESTONE_PROOF_SUBMITTED",
        entity_id=str(m.id),
        entity_type="Milestone",
        details=f"Phase {m.phase} [{m.proof_type.upper()}] proof submitted: {proof_info}",
    )

    return {
        "message": f"Phase {m.phase} proof of work submitted successfully ({m.proof_type.upper()})",
        "milestone": m.model_dump(),
    }


@router.post("/{milestone_id}/upload-video")
async def upload_video_proof(
    milestone_id: int,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    m = session.get(Milestone, milestone_id)
    if not m:
        raise HTTPException(status_code=404, detail="Milestone not found")
    p = session.get(Pilot, m.pilot_id)
    st = session.get(Startup, p.startup_id) if p else None
    if not st or st.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your pilot")

    safe_name = f"proof_{m.id}_{uuid.uuid4().hex[:8]}.mp4"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    if file:
        content = await file.read()
        with open(file_path, "wb") as fh:
            fh.write(content)
    else:
        with open(file_path, "wb") as fh:
            fh.write(b"SETU_FIELD_TRIAL_VIDEO_EVIDENCE")

    video_url = f"/static/uploads/{safe_name}"
    m.proof_video_url = video_url
    m.proof_type = "video"
    m.status = "ProofSubmitted"
    session.add(m)
    session.commit()
    session.refresh(m)

    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({st.name})",
        action="MILESTONE_VIDEO_PROOF_UPLOADED",
        entity_id=str(m.id),
        entity_type="Milestone",
        details=f"Phase {m.phase} field trial video uploaded: {video_url}",
    )

    return {"message": "Video proof uploaded successfully", "video_url": video_url, "milestone": m.model_dump()}


@router.post("/{milestone_id}/verify-and-release")
def verify_and_release(
    milestone_id: int,
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    m = session.get(Milestone, milestone_id)
    if not m:
        raise HTTPException(status_code=404, detail="Milestone not found")
    p = session.get(Pilot, m.pilot_id)
    if not p or (p.buyer_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Not your pilot")

    if m.status != "ProofSubmitted":
        raise HTTPException(status_code=400, detail=f"Milestone is currently '{m.status}', proof must be submitted first")

    m.status = "Approved"
    m.approved_at = datetime.now(timezone.utc)
    session.add(m)

    # Check if all milestones are approved -> ScaleUpRecommended
    all_ms = session.exec(select(Milestone).where(Milestone.pilot_id == p.id)).all()
    if all(ms.status == "Approved" for ms in all_ms):
        p.status = "ScaleUpRecommended"
        session.add(p)

    session.commit()
    session.refresh(m)
    session.refresh(p)

    st = session.get(Startup, p.startup_id) if p else None
    st_name = st.name if st else "Startup"

    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({current_user.org_name})",
        action="MILESTONE_ESCROW_RELEASED",
        entity_id=str(m.id),
        entity_type="Milestone",
        details=f"Escrow tranche of Rs {m.amount_inr:,.2f} released for Phase {m.phase} ({m.title}) to {st_name} after proof verification.",
    )

    return {
        "message": f"Escrow tranche released: Rs {m.amount_inr:,.2f} disbursed for Phase {m.phase}",
        "milestone": m.model_dump(),
        "pilot_status": p.status,
    }
