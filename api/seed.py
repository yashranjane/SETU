import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app.models  # noqa: F401
from app.db import engine
from sqlmodel import SQLModel, Session, select
from app.models.user import User
from app.models.startup import Startup
from app.models.challenge import Challenge
from app.models.pilot import Pilot
from app.models.milestone import Milestone
from app.core.auth import hash_password
from app.services.audit_service import append_audit_block

reset_requested = (
    "--reset" in sys.argv
    or os.getenv("RESET_DB", "").lower() in ("true", "1", "yes")
)

if reset_requested:
    print("  [RESET] Dropping all existing tables to restore clean baseline...")
    SQLModel.metadata.drop_all(engine)

# Ensure tables exist
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    existing_user = session.exec(select(User)).first()
    if existing_user and not reset_requested:
        print("  Database already contains data. Preserving all records.")
        sys.exit(0)

    print("  Seeding initial clean data (Stormwater challenge baseline)...")

with Session(engine) as session:
    # 1. Admin
    admin = User(
        email="admin@setu.gov.in",
        full_name="Portal Administrator",
        password_hash=hash_password("Admin@123!"),
        role="admin",
        org_name="SETU Public Procurement Cell",
        state="Delhi",
        phone="011-23456789",
        is_active=True,
    )
    session.add(admin)

    # 2. Buyer (Pune Municipal Corp)
    buyer = User(
        email="buyer@pune.gov.in",
        full_name="Suresh Patil",
        password_hash=hash_password("Buyer@123!"),
        role="buyer",
        org_name="Pune Municipal Corporation",
        state="Maharashtra",
        phone="+91 98230 11223",
        is_active=True,
    )
    session.add(buyer)

    # 3. Seller (Rajputana Electronics)
    seller = User(
        email="seller@rajputana.in",
        full_name="Vikram Singh",
        password_hash=hash_password("Seller@123!"),
        role="seller",
        org_name="Rajputana Electronics Pvt Ltd",
        state="Maharashtra",
        phone="+91 98290 55443",
        is_active=True,
    )
    session.add(seller)
    session.commit()
    session.refresh(buyer)
    session.refresh(seller)

    # 4. Seller Profile (DPIIT & GeM Verified)
    seller_profile = Startup(
        seller_id=seller.id,
        name="Rajputana Electronics Pvt Ltd",
        domain="IoT & Environmental Telemetry",
        solution_title="JalDrishti - Autonomous Ultrasonic Water Level & Flood Warning Sonde",
        description="Indigenous micro-RTU with integrated 4G telemetry and LoRaWAN fallback, certified IP68 for stormwater drains and automated flood warning under CPCB/CWC standards.",
        trl_level=8,
        dpiit_certified=True,
        dpiit_number="DIPP-94821",
        gem_seller_id="GEM-LIVE-78419",
        is_gem_verified=True,
        gem_rating=4.9,
        financial_capacity_score=0.88,
        state="Maharashtra",
        website="https://rajputana.in",
    )
    session.add(seller_profile)

    # 5. Verified GeM Suppliers in Sandbox Pool
    gem_seller_1 = Startup(
        name="Asteria Aerospace Limited",
        domain="IoT & Environmental Telemetry",
        solution_title="A200-XT Autonomous Surveillance & Aerial Drain Inspection Drone",
        description="DGCA type-certified micro-UAV system with fail-safe automated landing and real-time aerial sensor telemetry into municipal disaster control centers.",
        trl_level=8,
        dpiit_certified=True,
        dpiit_number="DIPP-11245",
        gem_seller_id="GEM-LIVE-11245",
        is_gem_verified=True,
        gem_rating=4.8,
        financial_capacity_score=0.92,
        state="Karnataka",
        website="https://mkp.gem.gov.in",
    )
    gem_seller_2 = Startup(
        name="CBAI Technologies Private Limited",
        domain="IoT & Environmental Telemetry",
        solution_title="UAS Model-T Airborne Sensor & Flow Rate Telemetry Pod",
        description="High-endurance multi-rotor drone equipped with optical flow sensors and real-time telemetry streaming for water level and disaster monitoring.",
        trl_level=7,
        dpiit_certified=True,
        dpiit_number="DIPP-60041",
        gem_seller_id="GEM-LIVE-60041",
        is_gem_verified=True,
        gem_rating=4.7,
        financial_capacity_score=0.80,
        state="Maharashtra",
        website="https://mkp.gem.gov.in",
    )
    session.add(gem_seller_1)
    session.add(gem_seller_2)

    # 6. Sample Outcome Challenge (Public Buyer Sandbox)
    challenge = Challenge(
        buyer_id=buyer.id,
        title="Automated Real-Time Stormwater Drain Telemetry & Urban Flood Warning",
        department="Drainage & Disaster Management Cell",
        location="Pune, Maharashtra",
        budget_ceiling_inr=1500000.0,
        outcome_statement="Deploy non-contact telemetry sensing units across 20 vulnerable stormwater arterial drains capable of transmitting water levels every 60 seconds with 99.5% uptime during monsoon deluge, alerting disaster management dashboard before overflow.",
        category="IoT & Environmental Telemetry",
        status="Open",
    )
    session.add(challenge)
    session.commit()

    # Genesis block for the tamper-evident audit ledger
    append_audit_block(
        session=session,
        actor="System",
        action="GENESIS_LEDGER_INITIALIZED",
        entity_id="0",
        entity_type="System",
        details="SETU GFR 2017 Rule 173 Tamper-Evident Ledger initialized with verified GeM & DPIIT innovation pool.",
    )

    print("  [OK] Admin login:  admin@setu.gov.in  / Admin@123! (or admin/admin)")
    print("  [OK] Buyer login:  buyer@pune.gov.in  / Buyer@123! (or buyer/buyer)")
    print("  [OK] Seller login: seller@rajputana.in / Seller@123! (or seller/seller)")
    print("  [OK] Working Model Initialized: 1 Challenge, 3 Verified GeM/DPIIT Sellers ready for AI evaluation.")

print("Database reset: Working model initialized and ready for live user interaction.")
