from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user, require_seller
from app.db import get_session
from app.models.vendor import Vendor
from app.models.user import User

router = APIRouter(prefix="/vendors", tags=["Vendors"])


class VendorUpsert(BaseModel):
    company_name: str
    gem_seller_id: Optional[str] = None
    category: str = ""
    description: str = ""
    gstin: Optional[str] = None
    state: str = ""
    experience_years: int = 0
    website: Optional[str] = None
    is_gem_verified: bool = False
    gem_rating: Optional[float] = None


@router.get("", response_model=List[dict])
def list_vendors(
    category: Optional[str] = None,
    state: Optional[str] = None,
    session: Session = Depends(get_session),
):
    vendors = session.exec(select(Vendor)).all()
    result = []
    for v in vendors:
        if category and category.lower() not in v.category.lower():
            continue
        if state and state.lower() not in v.state.lower():
            continue
        seller = session.get(User, v.seller_id)
        result.append({
            **v.model_dump(),
            "seller_name": seller.full_name if seller else "",
            "seller_email": seller.email if seller else "",
        })
    return result


@router.get("/profile/me")
def my_vendor_profile(
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    v = session.exec(select(Vendor).where(Vendor.seller_id == current_user.id)).first()
    if not v:
        return None
    return v.model_dump()


@router.post("/profile", response_model=dict, status_code=201)
def upsert_vendor_profile(
    payload: VendorUpsert,
    current_user: User = Depends(require_seller),
    session: Session = Depends(get_session),
):
    existing = session.exec(select(Vendor).where(Vendor.seller_id == current_user.id)).first()
    if existing:
        for k, val in payload.model_dump(exclude_none=False).items():
            setattr(existing, k, val)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing.model_dump()
    v = Vendor(seller_id=current_user.id, **payload.model_dump())
    session.add(v)
    session.commit()
    session.refresh(v)
    return v.model_dump()


@router.get("/{vendor_id}", response_model=dict)
def get_vendor(vendor_id: int, session: Session = Depends(get_session)):
    v = session.get(Vendor, vendor_id)
    if not v:
        raise HTTPException(status_code=404, detail="Vendor not found")
    seller = session.get(User, v.seller_id)
    return {
        **v.model_dump(),
        "seller_name": seller.full_name if seller else "",
        "seller_email": seller.email if seller else "",
        "seller_phone": seller.phone if seller else "",
    }
