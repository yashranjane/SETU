from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.auth import get_current_user, require_buyer
from app.db import get_session
from app.models.requirement import Requirement
from app.models.user import User

router = APIRouter(prefix="/requirements", tags=["Requirements"])


class RequirementCreate(BaseModel):
    title: str
    department: str = ""
    location: str = ""
    budget_inr: float
    description: str
    category: str = ""
    deadline: str = ""


class RequirementUpdate(BaseModel):
    status: str


@router.get("", response_model=List[dict])
def list_requirements(
    status: Optional[str] = None,
    category: Optional[str] = None,
    session: Session = Depends(get_session),
):
    reqs = session.exec(select(Requirement).order_by(Requirement.id.desc())).all()
    result = []
    for r in reqs:
        if status and r.status != status:
            continue
        if category and category.lower() not in r.category.lower():
            continue
        buyer = session.get(User, r.buyer_id)
        result.append({
            **r.model_dump(),
            "buyer_name": buyer.full_name if buyer else "",
            "buyer_org": buyer.org_name if buyer else "",
        })
    return result


@router.get("/mine", response_model=List[dict])
def my_requirements(
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    stmt = select(Requirement).where(Requirement.buyer_id == current_user.id).order_by(Requirement.id.desc())
    reqs = session.exec(stmt).all()
    return [r.model_dump() for r in reqs]


@router.post("", response_model=dict, status_code=201)
def create_requirement(
    payload: RequirementCreate,
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    req = Requirement(
        buyer_id=current_user.id,
        title=payload.title.strip(),
        department=payload.department.strip(),
        location=payload.location.strip(),
        budget_inr=payload.budget_inr,
        description=payload.description.strip(),
        category=payload.category.strip(),
        deadline=payload.deadline.strip(),
        status="Open",
    )
    session.add(req)
    session.commit()
    session.refresh(req)
    return req.model_dump()


@router.get("/{req_id}", response_model=dict)
def get_requirement(req_id: int, session: Session = Depends(get_session)):
    req = session.get(Requirement, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    buyer = session.get(User, req.buyer_id)
    return {
        **req.model_dump(),
        "buyer_name": buyer.full_name if buyer else "",
        "buyer_org": buyer.org_name if buyer else "",
        "buyer_state": buyer.state if buyer else "",
    }


@router.patch("/{req_id}/status")
def update_status(
    req_id: int,
    payload: RequirementUpdate,
    current_user: User = Depends(require_buyer),
    session: Session = Depends(get_session),
):
    req = session.get(Requirement, req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    if req.buyer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not your requirement")
    req.status = payload.status
    session.add(req)
    session.commit()
    return {"message": "Status updated", "status": req.status}
