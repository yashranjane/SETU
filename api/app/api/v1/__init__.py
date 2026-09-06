from fastapi import APIRouter
from app.api.v1 import auth, challenges, startups, pilots, milestones, audit, gem, admin, proposals

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router)
api_v1_router.include_router(challenges.router)
api_v1_router.include_router(startups.router, prefix="/startups", tags=["Startups"])
api_v1_router.include_router(startups.router, prefix="/sellers", tags=["Sellers"])
api_v1_router.include_router(proposals.router)
api_v1_router.include_router(pilots.router)
api_v1_router.include_router(milestones.router)
api_v1_router.include_router(audit.router)
api_v1_router.include_router(gem.router)
api_v1_router.include_router(admin.router)


__all__ = ["api_v1_router"]
