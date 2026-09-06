import unittest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.db import get_session
from app.main import app
from app.models.challenge import Challenge, ChallengeStatus
from app.models.pilot import Milestone, MilestoneStatus, Pilot, PilotStatus
from app.models.startup import Startup


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        # Create a shared in-memory SQLite test database with StaticPool
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

        # Seed initial test data
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
                startup_id="civicportal-saas",
                name="CivicPortal App",
                title="Citizen Grievance Crowdsourcing Web Application",
                description="Mobile web dashboard for citizens to report waterlogging.",
                solution_overview="Web form and photo upload portal with municipal ticket assignment.",
                trl=3,
                compliance=0.55,
                capacity=0.45,
                dpiit_registered=False,
                sector="Civic Software",
            )
            session.add_all([s1, s2])
            session.commit()

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_create_and_list_challenges(self):
        payload = {
            "title": "Automated Urban Drainage Blockage Detection (Ward 14, PMC)",
            "outcome_statement": "Real-time acoustic sensing for drain clog detection.",
            "budget_ceiling": 300000.0,
            "status": "Published",
        }
        res = self.client.post("/api/v1/challenges", json=payload)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["title"], payload["title"])
        self.assertEqual(data["status"], "Published")
        c_id = data["id"]

        list_res = self.client.get("/api/v1/challenges")
        self.assertEqual(list_res.status_code, 200)
        challenges = list_res.json()
        self.assertTrue(any(c["id"] == c_id for c in challenges))

    def test_match_challenge_startups(self):
        # Create challenge
        c_res = self.client.post(
            "/api/v1/challenges",
            json={
                "title": "Urban Drainage Blockage Telemetry",
                "outcome_statement": "Acoustic sewer sensors and ultrasonic drainage flow monitoring.",
                "budget_ceiling": 300000.0,
            },
        )
        c_id = c_res.json()["id"]

        # Run matcher
        match_res = self.client.post(f"/api/v1/challenges/{c_id}/match")
        self.assertEqual(match_res.status_code, 200)
        data = match_res.json()

        self.assertEqual(data["challenge_id"], c_id)
        self.assertEqual(data["total_candidates_evaluated"], 2)
        matches = data["matches"]
        self.assertGreater(len(matches), 0)

        # HydroSense AI must be #1
        top_match = matches[0]
        self.assertEqual(top_match["startup_id"], "hydrosense-ai")
        self.assertGreater(top_match["composite_score"], 0.70)
        self.assertTrue(any("TRL-7" in r for r in top_match["reason_codes"]))
        self.assertTrue(any("DPIIT" in r for r in top_match["reason_codes"]))

    def test_pilot_creation_and_mou_streaming(self):
        # Create challenge
        c_res = self.client.post(
            "/api/v1/challenges",
            json={
                "title": "Drainage Telemetry Sandbox",
                "outcome_statement": "IoT ultrasonic drain monitoring",
                "budget_ceiling": 300000.0,
            },
        )
        c_id = c_res.json()["id"]

        # Initialize Pilot
        pilot_res = self.client.post(
            "/api/v1/pilots",
            json={
                "challenge_id": c_id,
                "startup_id": "hydrosense-ai",
            },
        )
        self.assertEqual(pilot_res.status_code, 201)
        pilot_data = pilot_res.json()
        p_id = pilot_data["pilot"]["id"]
        self.assertEqual(len(pilot_data["milestones"]), 3)

        # Download MoU PDF
        mou_res = self.client.get(f"/api/v1/pilots/{p_id}/mou")
        self.assertEqual(mou_res.status_code, 200)
        self.assertEqual(mou_res.headers["content-type"], "application/pdf")
        self.assertTrue(mou_res.content.startswith(b"%PDF"))

    def test_milestone_verification_and_audit_integrity(self):
        # Setup challenge and pilot
        c_res = self.client.post(
            "/api/v1/challenges",
            json={
                "title": "PMC Silt Telemetry Pilot",
                "outcome_statement": "Real-time silt monitoring",
                "budget_ceiling": 300000.0,
            },
        )
        c_id = c_res.json()["id"]

        pilot_res = self.client.post(
            "/api/v1/pilots",
            json={
                "challenge_id": c_id,
                "startup_id": "hydrosense-ai",
            },
        )
        p_id = pilot_res.json()["pilot"]["id"]

        # 1. Submit evidence for Milestone 1
        ev_res = self.client.post(
            f"/api/v1/pilots/{p_id}/milestones/1/evidence",
            json={"evidence_url": "https://storage.pmc.gov.in/evidence/m1_telemetry.pdf"},
        )
        self.assertEqual(ev_res.status_code, 200)
        self.assertEqual(ev_res.json()["milestone"]["status"], "Submitted")

        # 2. Verify Milestone 1
        ver_res = self.client.post(
            f"/api/v1/pilots/{p_id}/milestones/1/verify",
            json={"approved": True, "remarks": "Hardware telemetry calibrated"},
        )
        self.assertEqual(ver_res.status_code, 200)
        ver_data = ver_res.json()
        self.assertEqual(ver_data["status"], "VERIFIED")
        self.assertEqual(ver_data["milestone"]["status"], "Approved")
        self.assertEqual(ver_data["pilot_status"], "InProgress")
        self.assertGreater(ver_data["escrow_disbursement_inr"], 0)

        # 3. Check audit chain integrity
        audit_res = self.client.get(f"/api/v1/audit/{p_id}/verify")
        self.assertEqual(audit_res.status_code, 200)
        audit_data = audit_res.json()
        self.assertTrue(audit_data["tamper_evident"])
        self.assertEqual(audit_data["status"], "VERIFIED")
        self.assertGreaterEqual(audit_data["blocks_verified"], 3)

        # 4. Check GeM Dossier export
        dossier_res = self.client.get(f"/api/v1/pilots/{p_id}/dossier")
        self.assertEqual(dossier_res.status_code, 200)
        dossier = dossier_res.json()
        self.assertEqual(dossier["dossier_type"], "GeM_STARTUP_RUNWAY_DIRECT_PROCUREMENT_DOSSIER")
        self.assertEqual(dossier["startup_profile"]["startup_id"], "hydrosense-ai")


if __name__ == "__main__":
    unittest.main()
