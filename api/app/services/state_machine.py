from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Union
from sqlmodel import Session, select

from app.core.audit_chain import calculate_audit_hash
from app.models.audit import AuditLog
from app.models.challenge import Challenge, ChallengeStatus

GENESIS_HASH: str = "0" * 64

# Valid state machine lifecycle graph for procurement
VALID_TRANSITIONS: Dict[str, List[str]] = {
    ChallengeStatus.DRAFT.value: [ChallengeStatus.PUBLISHED.value],
    ChallengeStatus.PUBLISHED.value: [ChallengeStatus.MATCHING.value],
    ChallengeStatus.MATCHING.value: [ChallengeStatus.PROPOSALS_OPEN.value],
    ChallengeStatus.PROPOSALS_OPEN.value: [ChallengeStatus.EVALUATION.value],
    ChallengeStatus.EVALUATION.value: [ChallengeStatus.PILOT_APPROVED.value],
    ChallengeStatus.PILOT_APPROVED.value: [ChallengeStatus.MOU_SIGNED.value],
    ChallengeStatus.MOU_SIGNED.value: [ChallengeStatus.IN_PROGRESS.value],
    ChallengeStatus.IN_PROGRESS.value: [ChallengeStatus.MILESTONE_REVIEW.value],
    ChallengeStatus.MILESTONE_REVIEW.value: [
        ChallengeStatus.IN_PROGRESS.value,
        ChallengeStatus.SCALE_UP_RECOMMENDED.value,
        ChallengeStatus.CLOSED.value,
    ],
    ChallengeStatus.SCALE_UP_RECOMMENDED.value: [ChallengeStatus.CLOSED.value],
    ChallengeStatus.CLOSED.value: [],
}


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal procurement lifecycle transition is requested."""

    def __init__(self, current_state: str, target_state: str, message: Optional[str] = None):
        msg = (
            message
            or f"Invalid transition from '{current_state}' to '{target_state}'. "
            f"Allowed transitions: {VALID_TRANSITIONS.get(current_state, [])}"
        )
        super().__init__(msg)
        self.current_state = current_state
        self.target_state = target_state


def validate_transition(current_state: str, target_state: str) -> bool:
    """
    Checks if a transition between two states is valid according to the procurement lifecycle.
    """
    allowed_states = VALID_TRANSITIONS.get(current_state, [])
    return target_state in allowed_states


def get_latest_audit_hash(session: Session) -> str:
    """
    Retrieves the most recent audit hash from the database.
    Returns GENESIS_HASH if no records exist yet.
    """
    statement = select(AuditLog).order_by(AuditLog.id.desc()).limit(1)
    latest_log = session.exec(statement).first()
    if latest_log and latest_log.curr_hash:
        return latest_log.curr_hash
    return GENESIS_HASH


def transition_challenge_state(
    session: Session,
    challenge: Challenge,
    target_state: Union[str, ChallengeStatus],
    actor_id: str,
) -> Tuple[Challenge, AuditLog]:
    """
    Executes a state transition for a challenge entity and appends an immutable,
    cryptographically-linked audit log entry to the audit chain.
    """
    target_val = target_state.value if isinstance(target_state, ChallengeStatus) else str(target_state)
    current_val = challenge.status

    if not validate_transition(current_val, target_val):
        raise InvalidStateTransitionError(current_state=current_val, target_state=target_val)

    # 1. Fetch previous hash in chain
    prev_hash = get_latest_audit_hash(session)

    # 2. Prepare timestamp and audit action
    now = datetime.now(timezone.utc)
    action = f"CHALLENGE_TRANSITION:{current_val}->{target_val}"
    entity_id = f"challenge:{challenge.id if challenge.id is not None else 'transient'}"

    # 3. Calculate tamper-evident current hash
    curr_hash = calculate_audit_hash(
        prev_hash=prev_hash,
        actor_id=actor_id,
        action=action,
        entity_id=entity_id,
        timestamp=now,
    )

    # 4. Create and persist audit record
    audit_entry = AuditLog(
        actor=actor_id,
        action=action,
        entity_id=entity_id,
        prev_hash=prev_hash,
        curr_hash=curr_hash,
        timestamp=now,
    )

    # 5. Mutate challenge state
    challenge.status = target_val

    session.add(challenge)
    session.add(audit_entry)
    session.commit()
    session.refresh(challenge)
    session.refresh(audit_entry)

    return challenge, audit_entry
