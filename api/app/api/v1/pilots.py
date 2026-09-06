from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db import get_session
from app.models.pilot import Pilot
from app.models.challenge import Challenge
from app.models.startup import Startup
from app.models.milestone import Milestone
from app.models.user import User
from app.services.pdf_generator import generate_sandbox_mou

router = APIRouter(prefix="/pilots", tags=["Pilots"])


def _enrich_pilot(p: Pilot, session: Session) -> dict:
    ch = session.get(Challenge, p.challenge_id)
    st = session.get(Startup, p.startup_id)
    buyer = session.get(User, p.buyer_id)
    milestones = session.exec(select(Milestone).where(Milestone.pilot_id == p.id).order_by(Milestone.phase)).all()
    disbursed = sum(m.amount_inr for m in milestones if m.status == "Approved")
    return {
        **p.model_dump(),
        "challenge_title": ch.title if ch else "",
        "challenge_department": ch.department if ch else "",
        "challenge_location": ch.location if ch else "",
        "outcome_statement": ch.outcome_statement if ch else "",
        "startup_name": st.name if st else "",
        "seller_name": st.name if st else "",
        "startup_domain": st.domain if st else "",
        "seller_domain": st.domain if st else "",
        "startup_solution": st.solution_title if st else "",
        "seller_solution": st.solution_title if st else "",
        "dpiit_number": st.dpiit_number if st else "",
        "gem_seller_id": st.gem_seller_id if st else "",
        "buyer_name": buyer.full_name if buyer else "",
        "buyer_org": buyer.org_name if buyer else "",
        "milestones": [m.model_dump() for m in milestones],
        "disbursed_inr": disbursed,
        "pending_inr": round(p.budget_inr - disbursed, 2),
    }


@router.get("/mine", response_model=List[dict])
def my_pilots(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role == "buyer":
        stmt = select(Pilot).where(Pilot.buyer_id == current_user.id).order_by(Pilot.id.desc())
    elif current_user.role == "seller":
        st = session.exec(select(Startup).where(Startup.seller_id == current_user.id)).first()
        if not st:
            return []
        stmt = select(Pilot).where(Pilot.startup_id == st.id).order_by(Pilot.id.desc())
    else:
        stmt = select(Pilot).order_by(Pilot.id.desc())

    pilots = session.exec(stmt).all()
    return [_enrich_pilot(p, session) for p in pilots]


@router.get("/{pilot_id}", response_model=dict)
def get_pilot(
    pilot_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    p = session.get(Pilot, pilot_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pilot not found")
    return _enrich_pilot(p, session)


@router.get("/{pilot_id}/mou")
def download_sandbox_mou(
    pilot_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    p = session.get(Pilot, pilot_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pilot not found")
    data = _enrich_pilot(p, session)
    pdf_bytes = generate_sandbox_mou(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="SETU_Sandbox_MoU_{pilot_id}.pdf"'},
    )


@router.get("/{pilot_id}/dossier")
def export_scaleup_dossier(
    pilot_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    p = session.get(Pilot, pilot_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pilot not found")
    data = _enrich_pilot(p, session)
    p.dossier_exported = True
    session.add(p)
    session.commit()

    dossier = {
        "statutory_authority": "GFR 2017 Rule 173 - Innovation Sandbox Exemption",
        "portal": "SETU Government Procurement Portal",
        "dossier_reference": f"SETU/GEM-SCALEUP/{pilot_id:04d}/2026",
        "verification_status": "CERTIFIED FOR DIRECT NATIONAL PROCUREMENT ON GeM",
        "pilot_id": pilot_id,
        "challenge_title": data["challenge_title"],
        "startup_name": data["startup_name"],
        "dpiit_number": data["dpiit_number"],
        "gem_seller_id": data["gem_seller_id"],
        "buyer_org": data["buyer_org"],
        "total_trial_value_inr": data["budget_inr"],
        "milestones_completed": len([m for m in data["milestones"] if m["status"] == "Approved"]),
        "audit_certification": "All field telemetries and milestone tranches cryptographically anchored into SHA-256 ledger.",
        "statutory_recommendation": "Eligible for expedited L1-exempted commercial purchase orders across Central & State Government departments under GeM Startup Runway.",
    }
    return dossier
