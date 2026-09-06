from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session, select

from app.core.auth import get_current_user
from app.db import get_session
from app.models.contract import Contract
from app.models.milestone import Milestone
from app.models.requirement import Requirement
from app.models.user import User
from app.models.vendor import Vendor
from app.services.pdf_generator import generate_contract_pdf

router = APIRouter(prefix="/contracts", tags=["Contracts"])


def _enrich(c: Contract, session: Session) -> dict:
    req = session.get(Requirement, c.requirement_id)
    vendor = session.get(Vendor, c.vendor_id)
    buyer = session.get(User, c.buyer_id)
    seller = session.get(User, vendor.seller_id) if vendor else None
    milestones = session.exec(
        select(Milestone).where(Milestone.contract_id == c.id).order_by(Milestone.phase)
    ).all()
    disbursed = sum(m.amount_inr for m in milestones if m.status == "PaymentReleased")
    return {
        **c.model_dump(),
        "requirement_title": req.title if req else "",
        "requirement_description": req.description if req else "",
        "requirement_department": req.department if req else "",
        "requirement_location": req.location if req else "",
        "company_name": vendor.company_name if vendor else "",
        "gem_seller_id": vendor.gem_seller_id if vendor else "",
        "seller_name": seller.full_name if seller else "",
        "seller_email": seller.email if seller else "",
        "seller_phone": seller.phone if seller else "",
        "buyer_name": buyer.full_name if buyer else "",
        "buyer_org": buyer.org_name if buyer else "",
        "buyer_email": buyer.email if buyer else "",
        "milestones": [m.model_dump() for m in milestones],
        "disbursed_inr": disbursed,
        "pending_inr": round(c.total_value_inr - disbursed, 2),
    }


@router.get("/mine", response_model=List[dict])
def my_contracts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if current_user.role == "buyer":
        stmt = select(Contract).where(Contract.buyer_id == current_user.id).order_by(Contract.id.desc())
    elif current_user.role == "seller":
        vendor = session.exec(select(Vendor).where(Vendor.seller_id == current_user.id)).first()
        if not vendor:
            return []
        stmt = select(Contract).where(Contract.vendor_id == vendor.id).order_by(Contract.id.desc())
    else:
        stmt = select(Contract).order_by(Contract.id.desc())
    contracts = session.exec(stmt).all()
    return [_enrich(c, session) for c in contracts]


@router.get("/{contract_id}", response_model=dict)
def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    c = session.get(Contract, contract_id)
    if not c:
        raise HTTPException(status_code=404, detail="Contract not found")
    vendor = session.get(Vendor, c.vendor_id)
    if current_user.role not in ("admin",):
        is_buyer = c.buyer_id == current_user.id
        is_seller = vendor and vendor.seller_id == current_user.id
        if not (is_buyer or is_seller):
            raise HTTPException(status_code=403, detail="Access denied")
    return _enrich(c, session)


@router.get("/{contract_id}/mou")
def download_mou(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    c = session.get(Contract, contract_id)
    if not c:
        raise HTTPException(status_code=404, detail="Contract not found")
    data = _enrich(c, session)
    pdf_bytes = generate_contract_pdf(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="contract_{contract_id}.pdf"'},
    )
