import unittest
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.audit_chain import verify_audit_log_integrity
from app.models.audit import AuditLog
from app.models.challenge import Challenge, ChallengeStatus
from app.models.pilot import Milestone, MilestoneStatus, Pilot, PilotStatus
from app.services.state_machine import (
    InvalidStateTransitionError,
    transition_challenge_state,
    validate_transition,
)


class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        SQLModel.metadata.create_all(self.engine)

    def test_lifecycle_progression(self):
        lifecycle = [
            ChallengeStatus.PUBLISHED,
            ChallengeStatus.MATCHING,
            ChallengeStatus.PROPOSALS_OPEN,
            ChallengeStatus.EVALUATION,
            ChallengeStatus.PILOT_APPROVED,
            ChallengeStatus.MOU_SIGNED,
            ChallengeStatus.IN_PROGRESS,
            ChallengeStatus.MILESTONE_REVIEW,
            ChallengeStatus.SCALE_UP_RECOMMENDED,
            ChallengeStatus.CLOSED,
        ]

        with Session(self.engine) as session:
            challenge = Challenge(
                title="AI Road Safety",
                outcome_statement="Detect potholes in real-time",
                budget_ceiling=1000000.0,
                status=ChallengeStatus.DRAFT.value,
            )
            session.add(challenge)
            session.commit()
            session.refresh(challenge)

            for target in lifecycle:
                challenge, audit = transition_challenge_state(
                    session=session,
                    challenge=challenge,
                    target_state=target,
                    actor_id="admin_user_1",
                )
                self.assertEqual(challenge.status, target.value)
                self.assertIsNotNone(audit.id)

            # Check all audit logs sequentially for tamper-proof integrity
            all_logs = session.exec(select(AuditLog).order_by(AuditLog.id.asc())).all()
            self.assertEqual(len(all_logs), len(lifecycle))
            self.assertTrue(verify_audit_log_integrity(all_logs))

    def test_invalid_transition_rejected(self):
        with Session(self.engine) as session:
            challenge = Challenge(
                title="Smart Metering",
                outcome_statement="Automated meter reading",
                budget_ceiling=500000.0,
                status=ChallengeStatus.DRAFT.value,
            )
            session.add(challenge)
            session.commit()
            session.refresh(challenge)

            # Direct jump from Draft to InProgress must fail
            with self.assertRaises(InvalidStateTransitionError):
                transition_challenge_state(
                    session=session,
                    challenge=challenge,
                    target_state=ChallengeStatus.IN_PROGRESS,
                    actor_id="hacker_1",
                )

            # Status should remain Draft
            session.refresh(challenge)
            self.assertEqual(challenge.status, ChallengeStatus.DRAFT.value)

    def test_pilot_and_milestones_creation(self):
        with Session(self.engine) as session:
            challenge = Challenge(
                title="Green Hydrogen Storage",
                outcome_statement="Nanomaterial storage tanks",
                budget_ceiling=2500000.0,
                status=ChallengeStatus.PILOT_APPROVED.value,
            )
            session.add(challenge)
            session.commit()
            session.refresh(challenge)

            pilot = Pilot(
                challenge_id=challenge.id,
                startup_id="startup_quantum_energy",
                mou_url="https://storage.setu.gov.in/mou/pilot_42.pdf",
                status=PilotStatus.PILOT_APPROVED.value,
            )
            session.add(pilot)
            session.commit()
            session.refresh(pilot)

            m1 = Milestone(
                pilot_id=pilot.id,
                index=1,
                amount=500000.0,
                evidence_url="https://storage.setu.gov.in/evidence/m1_prototype.pdf",
                status=MilestoneStatus.APPROVED.value,
            )
            m2 = Milestone(
                pilot_id=pilot.id,
                index=2,
                amount=1000000.0,
                status=MilestoneStatus.PENDING.value,
            )
            session.add(m1)
            session.add(m2)
            session.commit()

            milestones = session.exec(select(Milestone).where(Milestone.pilot_id == pilot.id)).all()
            self.assertEqual(len(milestones), 2)
            self.assertEqual(milestones[0].amount + milestones[1].amount, 1500000.0)


if __name__ == "__main__":
    unittest.main()
