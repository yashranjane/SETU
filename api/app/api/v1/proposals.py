from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user, require_buyer, require_seller
from app.db import get_session
from app.models.challenge import Challenge
from app.models.startup import Startup
from app.models.pilot import Pilot
from app.models.milestone import Milestone
from app.models.proposal import Proposal
from app.models.user import User
from app.services.matching import calculate_explainable_fit
from app.services.audit_service import append_audit_block

router = APIRouter(prefix="/proposals", tags=["Proposals"])


class ProposalSubmit(BaseModel):
    challenge_id: int
    pitch_text: str
    proposed_budget_inr: Optional[float] = 0.0
    timeline_days: Optional[int] = 30


@router.post("", response_model=dict, status_code=201)
def submit_proposal(
    payload: ProposalSubmit,
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    startup = session.exec(select(Startup).where(Startup.seller_id == current_user.id)).first()
    if not startup:
        raise HTTPException(status_code=400, detail="Complete your startup company profile first")

    challenge = session.get(Challenge, payload.challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if challenge.status not in ("Open", "Matched"):
        raise HTTPException(status_code=400, detail="Challenge is no longer accepting proposals")

    # Check for duplicate
    existing = session.exec(
        select(Proposal).where(
            Proposal.challenge_id == payload.challenge_id,
            Proposal.seller_id == current_user.id,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="You have already submitted a proposal for this challenge")

    # Calculate current AI fit score
    fit = calculate_explainable_fit(challenge.outcome_statement, startup.model_dump())
    rel_score = fit.get("match_percentage", 75.0)

    budget = payload.proposed_budget_inr if payload.proposed_budget_inr and payload.proposed_budget_inr > 0 else challenge.budget_ceiling_inr

    proposal = Proposal(
        challenge_id=challenge.id,
        seller_id=current_user.id,
        startup_id=startup.id,
        relevance_score=rel_score,
        pitch_text=payload.pitch_text.strip(),
        proposed_budget_inr=budget,
        timeline_days=payload.timeline_days or 30,
        status="Submitted",
    )
    session.add(proposal)
    session.commit()
    session.refresh(proposal)

    # Append to SHA-256 Audit Ledger
    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({startup.name})",
        action="STARTUP_PROPOSAL_SUBMITTED",
        entity_id=str(proposal.id),
        entity_type="Proposal",
        details=f"Technical pitch submitted for Challenge #{challenge.id} | AI Relevance: {rel_score}% | Budget: Rs {budget:,.2f}",
    )

    return {
        "message": "Proposal submitted successfully to buyer!",
        "id": proposal.id,
        "proposal_id": proposal.id,
        "relevance_score": rel_score,
        "startup_name": startup.name,
        "proposed_budget_inr": proposal.proposed_budget_inr,
        "timeline_days": proposal.timeline_days,
        "status": proposal.status,
    }


@router.get("/notifications", response_model=List[dict])
def buyer_proposal_notifications(
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    if current_user.role == "admin":
        my_challenges = session.exec(select(Challenge)).all()
    else:
        my_challenges = session.exec(select(Challenge).where(Challenge.buyer_id == current_user.id)).all()

    ch_ids = [c.id for c in my_challenges]
    if not ch_ids:
        return []

    proposals = session.exec(
        select(Proposal).where(Proposal.challenge_id.in_(ch_ids)).order_by(Proposal.id.desc())
    ).all()

    results = []
    for p in proposals:
        ch = session.get(Challenge, p.challenge_id)
        st = session.get(Startup, p.startup_id) if p.startup_id else None
        seller = session.get(User, p.seller_id) if p.seller_id else None
        results.append({
            **p.model_dump(),
            "challenge_title": ch.title if ch else "",
            "challenge_department": ch.department if ch else "",
            "challenge_budget": ch.budget_ceiling_inr if ch else 0,
            "startup_name": st.name if st else (seller.full_name if seller else "Startup"),
            "solution_title": st.solution_title if st else "Innovation Solution",
            "domain": st.domain if st else "",
            "trl_level": st.trl_level if st else 7,
            "is_gem_verified": st.is_gem_verified if st else True,
            "dpiit_certified": st.dpiit_certified if st else True,
            "gem_seller_id": st.gem_seller_id if st else "",
            "seller_email": seller.email if seller else "",
        })
    return results


@router.get("/challenge/{challenge_id}", response_model=List[dict])
def proposals_for_challenge(
    challenge_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    ch = session.get(Challenge, challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")

    proposals = session.exec(select(Proposal).where(Proposal.challenge_id == challenge_id)).all()
    results = []
    for p in proposals:
        st = session.get(Startup, p.startup_id) if p.startup_id else None
        seller = session.get(User, p.seller_id) if p.seller_id else None
        results.append({
            **p.model_dump(),
            "startup_name": st.name if st else (seller.full_name if seller else "Startup"),
            "solution_title": st.solution_title if st else "",
            "trl_level": st.trl_level if st else 7,
            "gem_seller_id": st.gem_seller_id if st else "",
        })
    return results


@router.get("/mine", response_model=List[dict])
def my_proposals(
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    proposals = session.exec(select(Proposal).where(Proposal.seller_id == current_user.id).order_by(Proposal.id.desc())).all()
    results = []
    for p in proposals:
        ch = session.get(Challenge, p.challenge_id)
        results.append({
            **p.model_dump(),
            "challenge_title": ch.title if ch else "",
            "challenge_department": ch.department if ch else "",
            "challenge_location": ch.location if ch else "",
        })
    return results


@router.post("/{proposal_id}/accept-and-pilot", status_code=201)
def accept_proposal_and_start_pilot(
    proposal_id: int,
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    prop = session.get(Proposal, proposal_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")
    ch = session.get(Challenge, prop.challenge_id)
    if not ch or (ch.buyer_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Not your challenge")

    existing_pilot = session.exec(select(Pilot).where(Pilot.challenge_id == ch.id)).first()
    if existing_pilot:
        raise HTTPException(status_code=400, detail=f"Pilot #{existing_pilot.id} is already active for this challenge")

    prop.status = "Accepted"
    session.add(prop)

    other_props = session.exec(select(Proposal).where(Proposal.challenge_id == ch.id, Proposal.id != proposal_id)).all()
    for op in other_props:
        op.status = "Rejected"
        session.add(op)

    ch.status = "PilotActive"
    session.add(ch)

    pilot_budget = prop.proposed_budget_inr if prop.proposed_budget_inr > 0 else ch.budget_ceiling_inr
    today_str = datetime.now(timezone.utc).strftime("%d-%m-%Y")

    pilot = Pilot(
        challenge_id=ch.id,
        startup_id=prop.startup_id,
        buyer_id=current_user.id,
        budget_inr=pilot_budget,
        status="Active",
        mou_signed_at=today_str,
    )
    session.add(pilot)
    session.commit()
    session.refresh(pilot)

    phases = [
        ("Deployment & Telemetry Baseline Setup", "Field hardware deployment, communication handshake, and baseline telemetry stream initialization.", 0.20),
        ("72-Hour Field Run & Uptime Telemetry", "72-hour continuous automated sensor operations with live telemetry stream into municipal SCADA.", 0.50),
        ("Final Evaluation & Integration Dossier", "Final validation of outcome performance targets, fail-safe verification, and scale-up integration report.", 0.30),
    ]

    for i, (title, desc, frac) in enumerate(phases, start=1):
        m = Milestone(
            pilot_id=pilot.id,
            phase=i,
            title=title,
            description=desc,
            amount_inr=round(pilot.budget_inr * frac, 2),
            status="Pending",
        )
        session.add(m)
    session.commit()

    st = session.get(Startup, prop.startup_id) if prop.startup_id else None
    st_name = st.name if st else "Startup"

    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({current_user.org_name})",
        action="PILOT_MOU_EXECUTED",
        entity_id=str(pilot.id),
        entity_type="Pilot",
        details=f"Statutory GFR Rule 173 MoU executed with {st_name} via Proposal #{prop.id} | Budget: Rs {pilot.budget_inr:,.2f} locked in 3 escrow tranches.",
    )

    return {
        "message": f"Proposal accepted! Pilot #{pilot.id} created and Rs {pilot.budget_inr:,.2f} ring-fenced in escrow.",
        "pilot_id": pilot.id,
    }
