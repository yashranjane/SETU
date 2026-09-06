import unittest
from app.services.matcher import (
    compute_semantic_similarity,
    evaluate_startup_fit,
    normalize_trl,
    rank_startups_for_challenge,
)
from app.services.pdf_generator import generate_mou_pdf


class TestMatcherAndPDF(unittest.TestCase):
    def test_normalize_trl(self):
        self.assertAlmostEqual(normalize_trl(9), 1.0, places=4)
        self.assertAlmostEqual(normalize_trl(1), 1.0 / 9.0, places=4)
        self.assertAlmostEqual(normalize_trl(0), 0.0, places=4)
        self.assertAlmostEqual(normalize_trl(4.5), 0.5, places=4)

    def test_composite_scoring_weight_distribution(self):
        challenge = {
            "title": "Real-time AI Pothole Detection",
            "outcome_statement": "Automated road distress mapping and classification",
        }
        startup = {
            "id": "st_001",
            "name": "RoadAI Vision",
            "title": "Real-time AI Pothole Detection",
            "description": "Automated road distress mapping and classification",
            "trl": 9,
            "compliance": 1.0,
            "capacity": 1.0,
        }

        result = evaluate_startup_fit(challenge, startup)

        # Expected formula: 0.40*Semantic + 0.25*TRL + 0.20*Compliance + 0.15*Capacity
        sem = result["semantic_fit"]
        trl = result["trl_score"]
        comp = result["compliance_score"]
        cap = result["capacity_score"]

        expected_composite = round((0.40 * sem) + (0.25 * trl) + (0.20 * comp) + (0.15 * cap), 4)
        self.assertEqual(result["composite_score"], expected_composite)

        # Verify breakdown components
        breakdown = result["breakdown"]
        self.assertAlmostEqual(breakdown["semantic_contribution"], 0.40 * sem, places=4)
        self.assertAlmostEqual(breakdown["trl_contribution"], 0.25 * trl, places=4)
        self.assertAlmostEqual(breakdown["compliance_contribution"], 0.20 * comp, places=4)
        self.assertAlmostEqual(breakdown["capacity_contribution"], 0.15 * cap, places=4)

    def test_reason_codes_generation(self):
        challenge = {
            "title": "Drone Forest Fire Monitoring",
            "outcome_statement": "Thermal camera early fire alert system",
        }
        high_startup = {
            "id": "st_high",
            "name": "AeroThermal Labs",
            "title": "Drone Forest Fire Monitoring",
            "description": "Thermal camera early fire alert system for forest reserves",
            "trl": 8,
            "compliance": 0.95,
            "capacity": 0.90,
        }
        result = evaluate_startup_fit(challenge, high_startup)
        codes = result["reason_codes"]

        self.assertTrue(any("High Semantic Fit" in c for c in codes))
        self.assertTrue(any("TRL-8 Field Tested" in c for c in codes))
        self.assertTrue(any("DPIIT Certified under GFR 173" in c for c in codes))
        self.assertTrue(any("High Deployment" in c for c in codes))

    def test_rank_startups_for_challenge(self):
        challenge = {
            "title": "Smart Solar Inverter Telemetry",
            "outcome_statement": "IoT edge sensor monitoring for grid solar plants",
        }
        startups = [
            {
                "id": "s1",
                "name": "Unrelated Fashion Tech",
                "title": "Online apparel store",
                "description": "E-commerce platform for clothing",
                "trl": 2,
                "compliance": 0.5,
                "capacity": 0.5,
            },
            {
                "id": "s2",
                "name": "SolarEdge IoT",
                "title": "Smart Solar Inverter Telemetry",
                "description": "IoT edge sensor monitoring for grid solar plants",
                "trl": 8,
                "compliance": 1.0,
                "capacity": 0.9,
            },
            {
                "id": "s3",
                "name": "General Clean Energy",
                "title": "Solar panel cleaning robotics",
                "description": "Robotic cleaning for solar panels",
                "trl": 6,
                "compliance": 0.8,
                "capacity": 0.7,
            },
        ]

        ranked = rank_startups_for_challenge(challenge, startups, top_k=3)
        self.assertEqual(len(ranked), 3)
        self.assertEqual(ranked[0]["startup_id"], "s2")
        self.assertGreater(ranked[0]["composite_score"], ranked[1]["composite_score"])
        self.assertGreater(ranked[1]["composite_score"], ranked[2]["composite_score"])

    def test_generate_mou_pdf(self):
        pilot_data = {
            "pilot_id": "MH-SETU-2026-PILOT-099",
            "execution_date": "05 September 2026",
            "department_name": "Public Works Department, Govt of Maharashtra",
            "challenge_title": "AI Pothole & Distress Assessment System",
            "budget_amount": "30,00,000/-",
            "startup_name": "RoadVision AI Pvt. Ltd.",
            "solution_summary": "Edge camera devices for continuous pavement quality analysis.",
            "pilot_duration": "90 Days",
            "nodal_officer_name": "Dr. S. K. Deshmukh",
            "nodal_officer_title": "Superintending Engineer & Nodal Officer",
            "signatory_name": "Vikram Adve",
            "signatory_title": "Managing Director",
            "milestones": [
                {
                    "index": 1,
                    "scope": "Telemetry hardware setup on 50 municipal buses",
                    "amount": "6,00,000/- (20%)",
                    "evidence": "Hardware installation report and telemetry ingestion logs",
                },
                {
                    "index": 2,
                    "scope": "Live corridor scanning across 200km road network",
                    "amount": "15,00,000/- (50%)",
                    "evidence": "Geotagged pothole dataset & verification certificate",
                },
                {
                    "index": 3,
                    "scope": "Final accuracy validation and scale-up handbook",
                    "amount": "9,00,000/- (30%)",
                    "evidence": "Third-party audit report and final presentation",
                },
            ],
        }

        pdf_bytes = generate_mou_pdf(pilot_data)

        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 100)
        # Check standard PDF magic header
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
