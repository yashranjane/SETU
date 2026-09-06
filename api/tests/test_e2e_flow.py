import os
import unittest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.audit_chain import calculate_audit_hash, verify_audit_log_integrity
from app.db import get_session
from app.main import app
from app.models.audit import AuditLog
from app.models.challenge import Challenge, ChallengeStatus
from app.models.pilot import Milestone, MilestoneStatus, Pilot, PilotStatus
from app.models.startup import Startup


class TestE2EIntegrationFlow(unittest.TestCase):
    """
    Comprehensive End-to-End Integration Test Suite simulating the full
    GFR 2017 Rule 173 procurement lifecycle from challenge posting to GeM Scale-Up.
    """

    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        SQLModel.metadata.create_all(self.engine)

        def override_get_session():
            with Session(self.engine, expire_on_commit=False) as session:
                yield session

        app.dependency_overrides[get_session] = override_get_session
        self.client = TestClient(app)

        with Session(self.engine, expire_on_commit=False) as session:
            s1 = Startup(
                startup_id="hydrosense-ai",
                name="HydroSense AI Pvt. Ltd.",
                title="IoT Ultrasonic Drainage Telemetry & Early Silt Detection",
                description="Autonomous ultrasonic sewer and stormwater acoustic telemetry sensors with solar edge gateways.",
                solution_overview="Non-invasive IoT acoustic nodes clamped onto manhole lids transmitting telemetry to GIS.",
                trl=7,
                compliance=0.98,
                capacity=0.92,
                dpiit_registered=True,
                sector="Water & Civic IoT",
            )
            s2 = Startup(
                startup_id="citydrain-mech",
                name="CityDrain Robotics",
                title="Robotic Desilting Rover & Pipeline Inspection Crawler",
                description="Remotely operated crawlers with high-torque mechanical augers for heavy silt extraction.",
                solution_overview="Tethered robotic crawlers designed for subsurface stormwater conduits.",
                trl=5,
                compliance=0.70,
                capacity=0.65,
                dpiit_registered=True,
                sector="Civic Robotics",
            )
            s3 = Startup(
                startup_id="civicportal-saas",
                name="CivicPortal App",
                title="Citizen Grievance Crowdsourcing Web Application",
                description="Mobile web dashboard for citizens to report waterlogging and overflowing drains.",
                solution_overview="Web form and photo upload portal with municipal ticket assignment.",
                trl=3,
                compliance=0.55,
                capacity=0.45,
                dpiit_registered=False,
                sector="Civic Software",
            )
            session.add_all([s1, s2, s3])
            session.commit()

            challenge = Challenge(
                id=1,
                title="Automated Urban Drainage Blockage Detection & Telemetry (Ward 14, Pune Municipal Corporation)",
                outcome_statement="Deployment of real-time non-invasive telemetry and AI acoustic/ultrasonic sensing to detect subsurface stormwater drain clogs and sewage overflow risks across critical flooding hotspots in Ward 14.",
                budget_ceiling=300000.0,
                status=ChallengeStatus.PUBLISHED,
            )
            session.add(challenge)
            session.commit()

            ts1 = datetime(2026, 9, 5, 12, 0, 0, tzinfo=timezone.utc)
            genesis_hash = calculate_audit_hash(
                prev_hash="0" * 64,
                actor_id="pmc_nodal_officer",
                action="CHALLENGE_PUBLISHED:ID_1",
                entity_id="challenge:1",
                timestamp=ts1,
            )
            audit_1 = AuditLog(
                actor="pmc_nodal_officer",
                action="CHALLENGE_PUBLISHED:ID_1",
                entity_id="challenge:1",
                prev_hash="0" * 64,
                curr_hash=genesis_hash,
                timestamp=ts1,
            )
            session.add(audit_1)

            pilot = Pilot(
                id=1,
                challenge_id=1,
                startup_id="hydrosense-ai",
                status=PilotStatus.IN_PROGRESS,
            )
            session.add(pilot)
            session.commit()

            m1 = Milestone(
                id=1,
                pilot_id=1,
                index=1,
                amount=60000.0,
                status=MilestoneStatus.SUBMITTED,
                evidence_url="https://telemetry.hydrosense.io/pmc-ward14/m1_installation_report.pdf",
            )
            m2 = Milestone(
                id=2,
                pilot_id=1,
                index=2,
                amount=150000.0,
                status=MilestoneStatus.PENDING,
            )
            m3 = Milestone(
                id=3,
                pilot_id=1,
                index=3,
                amount=90000.0,
                status=MilestoneStatus.PENDING,
            )
            session.add_all([m1, m2, m3])

            ts2 = datetime(2026, 9, 5, 12, 5, 0, tzinfo=timezone.utc)
            pilot_hash = calculate_audit_hash(
                prev_hash=genesis_hash,
                actor_id="pmc_nodal_officer",
                action="PILOT_APPROVED:Challenge_1->Startup_hydrosense-ai",
                entity_id="pilot:1",
                timestamp=ts2,
            )
            audit_2 = AuditLog(
                actor="pmc_nodal_officer",
                action="PILOT_APPROVED:Challenge_1->Startup_hydrosense-ai",
                entity_id="pilot:1",
                prev_hash=genesis_hash,
                curr_hash=pilot_hash,
                timestamp=ts2,
            )
            session.add(audit_2)
            session.commit()

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_complete_procurement_lifecycle_e2e(self):
        # 1. Assert GET /api/v1/challenges lists Ward 14 Pune MC challenge
        res_ch = self.client.get("/api/v1/challenges")
        self.assertEqual(res_ch.status_code, 200)
        challenges = res_ch.json()
        self.assertGreaterEqual(len(challenges), 1)
        ward14_ch = next((c for c in challenges if c["id"] == 1), None)
        self.assertIsNotNone(ward14_ch)
        self.assertIn("Ward 14", ward14_ch["title"])
        self.assertEqual(ward14_ch["budget_ceiling"], 300000.0)

        # 2. Assert POST /api/v1/challenges/1/match returns HydroSense AI as #1
        res_match = self.client.post("/api/v1/challenges/1/match")
        self.assertEqual(res_match.status_code, 200)
        match_data = res_match.json()
        self.assertEqual(match_data["challenge_id"], 1)
        self.assertEqual(match_data["total_candidates_evaluated"], 3)
        self.assertGreaterEqual(len(match_data["matches"]), 1)

        top_match = match_data["matches"][0]
        self.assertEqual(top_match["startup_id"], "hydrosense-ai")
        self.assertEqual(top_match["startup_name"], "HydroSense AI Pvt. Ltd.")
        self.assertGreater(top_match["composite_score"], 0.70)
        self.assertEqual(top_match["raw_trl"], 7)
        self.assertTrue(len(top_match["reason_codes"]) >= 3)
        self.assertTrue(any("TRL-7" in r for r in top_match["reason_codes"]))
        self.assertTrue(any("DPIIT" in r for r in top_match["reason_codes"]))

        # 3. Assert GET /api/v1/pilots/1/mou returns valid PDF bytes starting with b"%PDF"
        res_mou = self.client.get("/api/v1/pilots/1/mou")
        self.assertEqual(res_mou.status_code, 200)
        self.assertEqual(res_mou.headers["content-type"], "application/pdf")
        self.assertTrue(res_mou.content.startswith(b"%PDF"))
        self.assertGreater(len(res_mou.content), 500)

        # 4. Assert POST /api/v1/pilots/1/milestones/1/verify marks milestone verified and advances escrow
        res_ver = self.client.post(
            "/api/v1/pilots/1/milestones/1/verify",
            json={"approved": True, "remarks": "Hardware telemetry calibrated in Ward 14"},
        )
        self.assertEqual(res_ver.status_code, 200)
        ver_payload = res_ver.json()
        self.assertEqual(ver_payload["status"], "VERIFIED")
        self.assertEqual(ver_payload["milestone"]["status"], "Approved")
        self.assertEqual(ver_payload["escrow_disbursement_inr"], 60000.0)
        self.assertIsNotNone(ver_payload["audit_hash"])

        # 5. Assert GET /api/v1/audit/1/verify & /api/v1/audit/verify return tamper_evident: true
        res_audit_pilot = self.client.get("/api/v1/audit/1/verify")
        self.assertEqual(res_audit_pilot.status_code, 200)
        audit_pilot_data = res_audit_pilot.json()
        self.assertTrue(audit_pilot_data["tamper_evident"])
        self.assertEqual(audit_pilot_data["status"], "VERIFIED")
        self.assertGreaterEqual(audit_pilot_data["blocks_verified"], 3)

        res_audit_global = self.client.get("/api/v1/audit/verify")
        self.assertEqual(res_audit_global.status_code, 200)
        audit_global_data = res_audit_global.json()
        self.assertTrue(audit_global_data["tamper_evident"])
        self.assertEqual(audit_global_data["status"], "VERIFIED")

        # 6. Assert GET /api/v1/pilots/1/dossier returns valid GFR 2017 Rule 173 GeM dossier
        res_dossier = self.client.get("/api/v1/pilots/1/dossier")
        self.assertEqual(res_dossier.status_code, 200)
        dossier = res_dossier.json()
        self.assertEqual(dossier["dossier_type"], "GeM_STARTUP_RUNWAY_DIRECT_PROCUREMENT_DOSSIER")
        self.assertIn("GFR 2017 Rule 173", dossier["statutory_authority"])
        self.assertEqual(dossier["startup_profile"]["startup_id"], "hydrosense-ai")
        self.assertEqual(dossier["startup_profile"]["legal_name"], "HydroSense AI Pvt. Ltd.")
        self.assertTrue(dossier["audit_certification"]["chain_tamper_evident"])
        self.assertTrue(dossier["gem_startup_runway_recommendation"]["scale_up_multiplier_eligible"])


if __name__ == "__main__":
    unittest.main()
