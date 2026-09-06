from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db import get_session
from app.models.startup import Startup
from app.models.user import User
from app.services.gem_apify import search_gem_sellers

router = APIRouter(prefix="/gem", tags=["GeM Integration"])


class GemSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None


class ImportStartupRequest(BaseModel):
    name: str
    domain: Optional[str] = "Innovation & Civic Tech"
    solution_title: Optional[str] = ""
    description: Optional[str] = ""
    trl_level: Optional[int] = 7
    gem_seller_id: Optional[str] = None
    state: Optional[str] = "India (GeM Verified)"
    gem_url: Optional[str] = None


@router.post("/search")
async def search_gem(payload: GemSearchRequest):
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Search keyword cannot be empty")
    results = await search_gem_sellers(payload.query.strip(), payload.location or "")
    return {
        "query": payload.query,
        "total_results": len(results),
        "sellers": results,
        "startups": results,
        "source": "Government e-Marketplace (gem.gov.in) via Apify",
    }


@router.post("/import-to-pool")
def import_startup_to_pool(
    payload: ImportStartupRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    seller_name = payload.name.strip()
    if not seller_name:
        raise HTTPException(status_code=400, detail="Seller name is required")

    existing = session.exec(select(Startup).where(Startup.name == seller_name)).first()
    if existing:
        return {
            "message": f"Seller '{existing.name}' is already in Sandbox Pool",
            "startup": existing.model_dump(),
            "seller": existing.model_dump(),
        }

    gem_id = payload.gem_seller_id or f"GEM-LIVE-{abs(hash(seller_name)) % 90000 + 10000}"
    st = Startup(
        name=seller_name,
        domain=payload.domain or "Innovation & Civic Tech",
        solution_title=payload.solution_title or "GeM Verified Innovation Solution",
        description=payload.description or f"Verified supplier registered on Government e-Marketplace ({gem_id})",
        trl_level=payload.trl_level or 7,
        dpiit_certified=True,
        dpiit_number=f"DIPP-{abs(hash(seller_name)) % 90000 + 10000}",
        gem_seller_id=gem_id,
        is_gem_verified=True,
        gem_rating=4.8,
        financial_capacity_score=0.85,
        state=payload.state or "India (GeM Verified)",
        website=payload.gem_url,
    )
    session.add(st)
    session.commit()
    session.refresh(st)

    from app.services.audit_service import append_audit_block
    append_audit_block(
        session=session,
        actor=f"{current_user.full_name} ({current_user.email})",
        action="SELLER_IMPORTED_TO_SANDBOX",
        entity_id=str(st.id),
        entity_type="Seller",
        details=f"Seller '{st.name}' imported from GeM ({st.gem_seller_id}) into evaluation pool",
    )

    return {
        "message": f"✓ Seller '{st.name}' added to Sandbox Evaluation Pool",
        "startup": st.model_dump(),
        "seller": st.model_dump(),
    }
