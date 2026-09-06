from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user, require_seller
from app.db import get_session
from app.models.startup import Startup
from app.models.user import User

router = APIRouter(tags=["Startups & Sellers"])


class StartupUpsert(BaseModel):
    name: str
    domain: str = ""
    solution_title: str = ""
    description: str = ""
    trl_level: int = 7
    dpiit_certified: bool = True
    dpiit_number: Optional[str] = "DIPP12345"
    gem_seller_id: Optional[str] = None
    is_gem_verified: bool = True
    gem_rating: Optional[float] = 4.8
    financial_capacity_score: float = 0.85
    state: str = "Maharashtra"
    website: Optional[str] = None


@router.get("", response_model=List[dict])
def list_startups(session: Session = Depends(get_session)):
    startups = session.exec(select(Startup)).all()
    return [s.model_dump() for s in startups]


@router.get("/profile/me")
def my_startup_profile(
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    st = session.exec(select(Startup).where(Startup.seller_id == current_user.id)).first()
    if not st:
        return None
    return st.model_dump()


@router.post("/profile", response_model=dict, status_code=201)
def upsert_startup_profile(
    payload: StartupUpsert,
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    existing = session.exec(select(Startup).where(Startup.seller_id == current_user.id)).first()
    if existing:
        for k, v in payload.model_dump(exclude_none=False).items():
            setattr(existing, k, v)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing.model_dump()

    st = Startup(seller_id=current_user.id, **payload.model_dump())
    session.add(st)
    session.commit()
    session.refresh(st)
    return st.model_dump()


@router.get("/{startup_id}", response_model=dict)
def get_startup(startup_id: int, session: Session = Depends(get_session)):
    st = session.get(Startup, startup_id)
    if not st:
        raise HTTPException(status_code=404, detail="Startup not found")
    return st.model_dump()
