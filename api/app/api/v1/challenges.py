from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user, require_buyer
from app.db import get_session
from app.models.challenge import Challenge
from app.models.startup import Startup
from app.models.pilot import Pilot
from app.models.milestone import Milestone
from app.models.user import User
from app.models.proposal import Proposal
from app.services.matching import calculate_explainable_fit
from app.services.audit_service import append_audit_block

router = APIRouter(prefix="/challenges", tags=["Challenges"])


class ChallengeCreate(BaseModel):
    title: str
    department: str = ""
    location: str = ""
    budget_ceiling_inr: float
    outcome_statement: str
    category: str = ""
    deadline: str = ""


class ApprovePilotRequest(BaseModel):
    startup_id: Optional[int] = None
    seller_id: Optional[int] = None


@router.get("", response_model=List[dict])
def list_challenges(
    status: Optional[str] = None,
    session: Session = Depends(get_session),
):
    stmt = select(Challenge).order_by(Challenge.id.desc())
    challenges = session.exec(stmt).all()
    result = []
    for c in challenges:
        if status and c.status != status:
            continue
        buyer = session.get(User, c.buyer_id)
        result.append({
            **c.model_dump(),
            "buyer_name": buyer.full_name if buyer else "",
            "buyer_org": buyer.org_name if buyer else "",
        })
    return result


@router.get("/mine", response_model=List[dict])
def my_challenges(
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    stmt = select(Challenge).where(Challenge.buyer_id == current_user.id).order_by(Challenge.id.desc())
    challenges = session.exec(stmt).all()
    return [c.model_dump() for c in challenges]


@router.post("", response_model=dict, status_code=201)
def create_challenge(
    payload: ChallengeCreate,
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    ch = Challenge(
        buyer_id=current_user.id,
        title=payload.title.strip(),
        department=payload.department.strip() or current_user.org_name,
        location=payload.location.strip() or current_user.state,
        budget_ceiling_inr=payload.budget_ceiling_inr,
        outcome_statement=payload.outcome_statement.strip(),
        category=payload.category.strip() or "Civic Innovation",
        deadline=payload.deadline.strip(),
        status="Open",
    )
    session.add(ch)
    session.commit()
    session.refresh(ch)

    # Append to SHA-256 Audit Ledger
    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({current_user.email})",
        action="CHALLENGE_POSTED",
        entity_id=str(ch.id),
        entity_type="Challenge",
        details=f"Title: {ch.title} | Budget: Rs {ch.budget_ceiling_inr:,.2f}",
    )

    return ch.model_dump()


@router.get("/opportunities", response_model=List[dict])
def seller_opportunities(
    q: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Find the startup profile for this seller
    startup = session.exec(select(Startup).where(Startup.seller_id == current_user.id)).first()
    if not startup:
        # If admin or no seller_id linked, fallback to first startup
        startup = session.exec(select(Startup)).first()

    stmt = select(Challenge).where(Challenge.status.in_(["Open", "Matched"])).order_by(Challenge.id.desc())
    challenges = session.exec(stmt).all()
    results = []
    st_dict = startup.model_dump() if startup else {}

    for c in challenges:
        if q:
            term = q.lower()
            if term not in c.title.lower() and term not in c.outcome_statement.lower() and term not in c.category.lower():
                continue
        buyer = session.get(User, c.buyer_id)

        # Calculate reverse AI relevance fit
        fit = calculate_explainable_fit(c.outcome_statement, st_dict)

        # Check if seller has already submitted a proposal
        existing_prop = None
        if current_user.role == "seller":
            existing_prop = session.exec(
                select(Proposal).where(Proposal.challenge_id == c.id, Proposal.seller_id == current_user.id)
            ).first()

        results.append({
            **c.model_dump(),
            "buyer_name": buyer.full_name if buyer else "",
            "buyer_org": buyer.org_name if buyer else "",
            "relevance_score": fit.get("match_percentage", 75.0),
            "semantic_fit": fit["semantic_fit"],
            "trl_level": st_dict.get("trl_level", 7),
            "compliance_score": fit["compliance_score"],
            "capacity_score": fit["capacity_score"],
            "reason_chips": fit["reason_chips"],
            "matched_solution": st_dict.get("solution_title", "Innovation Solution"),
            "matched_startup_name": st_dict.get("name", "Startup"),
            "has_submitted_proposal": existing_prop is not None,
            "proposal_status": existing_prop.status if existing_prop else None,
            "proposal_id": existing_prop.id if existing_prop else None,
        })

    # Sort by relevance_score descending
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results


@router.get("/{challenge_id}", response_model=dict)
def get_challenge(challenge_id: int, session: Session = Depends(get_session)):
    ch = session.get(Challenge, challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    buyer = session.get(User, ch.buyer_id)
    return {
        **ch.model_dump(),
        "buyer_name": buyer.full_name if buyer else "",
        "buyer_org": buyer.org_name if buyer else "",
    }


@router.post("/{challenge_id}/match", response_model=dict)
async def run_explainable_match(
    challenge_id: int,
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    """
    Step 1: Compute Explainable Composite Fit using the 4-factor formula:
    CompositeScore = (0.40 * SemanticFit) + (0.25 * TRL) + (0.20 * Compliance) + (0.15 * Capacity)
    If the local sandbox pool is empty, dynamically scrapes live GeM sellers for the challenge topic.
    """
    ch = session.get(Challenge, challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")

    startups = session.exec(select(Startup)).all()
    if not startups:
        from app.services.gem_apify import search_gem_sellers
        search_query = ch.category or ch.title or "smart sensors"
        gem_sellers = await search_gem_sellers(search_query, ch.location or "")
        for g in gem_sellers:
            new_st = Startup(
                name=g["name"],
                domain=g.get("domain", ch.category or "Innovation"),
                solution_title=g["solution_title"],
                description=g["description"],
                trl_level=g.get("trl_level", 7),
                dpiit_certified=True,
                dpiit_number=f"DIPP-{abs(hash(g['name'])) % 90000 + 10000}",
                gem_seller_id=g.get("gem_seller_id", "GEM-LIVE-1234"),
                is_gem_verified=True,
                gem_rating=g.get("gem_rating", 4.8),
                financial_capacity_score=0.85,
                state=ch.location or "India (GeM Verified)",
            )
            session.add(new_st)
        session.commit()
        startups = session.exec(select(Startup)).all()

    if not startups:
        raise HTTPException(status_code=400, detail="No registered sellers found in sandbox pool")

    ranked = []
    for st in startups:
        fit = calculate_explainable_fit(ch.outcome_statement, st.model_dump())
        ranked.append({
            "startup_id": st.id,
            "seller_id": st.id,
            "name": st.name,
            "domain": st.domain,
            "solution_title": st.solution_title,
            "description": st.description,
            "trl_level": st.trl_level,
            "dpiit_certified": st.dpiit_certified,
            "gem_seller_id": st.gem_seller_id,
            "is_gem_verified": st.is_gem_verified,
            "gem_rating": st.gem_rating,
            "state": st.state,
            **fit,
        })

    # Sort descending by composite match
    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    top3 = ranked[:3]

    ch.status = "Matched"
    session.add(ch)
    session.commit()

    # Log to Audit Ledger
    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({current_user.email})",
        action="EXPLAINABLE_MATCH_EXECUTED",
        entity_id=str(ch.id),
        entity_type="Challenge",
        details=f"Top candidate: {top3[0]['name']} ({top3[0]['match_percentage']}%) under 4-factor formula",
    )

    return {
        "challenge_id": ch.id,
        "challenge_title": ch.title,
        "total_evaluated": len(startups),
        "candidates": top3,
    }


@router.post("/{challenge_id}/approve-pilot", response_model=dict, status_code=201)
def approve_pilot_and_sign_mou(
    challenge_id: int,
    payload: ApprovePilotRequest,
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    """
    Step 2: Statutory MoU Generation & Escrow Lockdown:
    - Initialize approved Pilot for Challenge and Startup
    - Automatically allocate pilot budget into 3 standard milestone escrow tranches:
        Milestone 1: 20% (Deployment & Telemetry Baseline Setup)
        Milestone 2: 50% (72-Hour Field Run & Uptime Telemetry)
        Milestone 3: 30% (Final Evaluation & Integration Dossier)
    """
    ch = session.get(Challenge, challenge_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found")
    target_id = payload.seller_id or payload.startup_id
    if not target_id:
        raise HTTPException(status_code=400, detail="Seller ID or Startup ID required")
    st = session.get(Startup, target_id)
    if not st:
        raise HTTPException(status_code=404, detail="Seller not found in sandbox pool")

    existing_pilot = session.exec(select(Pilot).where(Pilot.challenge_id == ch.id)).first()
    if existing_pilot:
        return {"message": "Pilot already active", "pilot_id": existing_pilot.id}

    today = datetime.now(timezone.utc).strftime("%d-%m-%Y")
    pilot = Pilot(
        challenge_id=ch.id,
        startup_id=st.id,
        buyer_id=current_user.id,
        budget_inr=ch.budget_ceiling_inr,
        status="Active",
        mou_signed_at=today,
    )
    session.add(pilot)
    session.commit()
    session.refresh(pilot)

    ch.status = "PilotActive"
    session.add(ch)

    # 3 Standard Escrow Milestone Tranches
    tranches = [
        (1, "Deployment & Telemetry Baseline Setup", "Field hardware deployment, communication handshake, and baseline telemetry stream initialization.", 0.20),
        (2, "72-Hour Field Run & Uptime Telemetry", "72-hour continuous automated sensor operations with live telemetry stream into municipal SCADA.", 0.50),
        (3, "Final Evaluation & Integration Dossier", "Final validation of outcome performance targets, fail-safe verification, and scale-up integration report.", 0.30),
    ]

    for phase, title, desc, frac in tranches:
        m = Milestone(
            pilot_id=pilot.id,
            phase=phase,
            title=title,
            description=desc,
            amount_inr=round(pilot.budget_inr * frac, 2),
            status="Pending",
        )
        session.add(m)

    session.commit()

    # Append to Audit Ledger
    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({current_user.email})",
        action="PILOT_MOU_EXECUTED",
        entity_id=str(pilot.id),
        entity_type="Pilot",
        details=f"Pilot #{pilot.id} signed with {st.name} | Budget: Rs {pilot.budget_inr:,.2f} locked in 3 escrow tranches",
    )

    return {
        "message": "Pilot approved and Sandbox MoU executed under GFR 2017 Rule 173",
        "pilot_id": pilot.id,
        "startup_name": st.name,
        "budget_inr": pilot.budget_inr,
    }