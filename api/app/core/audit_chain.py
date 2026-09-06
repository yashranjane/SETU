import hashlib
from datetime import datetime
from typing import Any, List, Union


def format_canonical_timestamp(ts: Union[str, datetime]) -> str:
    """
    Produces a canonical, deterministic string representation of a timestamp
    regardless of whether it is passed as a string or datetime object.
    """
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    # If already a string, normalize if it contains ISO T
    ts_str = str(ts).replace("T", " ")
    # Strip timezone suffix if present for database normalization
    if "+" in ts_str:
        ts_str = ts_str.split("+")[0]
    if "Z" in ts_str:
        ts_str = ts_str.rstrip("Z")
    return ts_str.strip()


def calculate_audit_hash(
    prev_hash: str,
    actor_id: str,
    action: str,
    entity_id: str,
    timestamp: Union[str, datetime],
) -> str:
    """
    Calculates a SHA-256 hash for an audit log entry.
    Ensures deterministic ordering of canonical fields.
    """
    timestamp_str = format_canonical_timestamp(timestamp)
    payload = f"{prev_hash}|{actor_id}|{action}|{entity_id}|{timestamp_str}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def verify_audit_log_integrity(logs: List[Any]) -> bool:
    """
    Sequentially validates parent-child hash integrity across an audit log sequence.
    Returns True if all parent-child links and calculated hashes are authentic, False otherwise.
    """
    if not logs:
        return True

    for i, log in enumerate(logs):
        if isinstance(log, dict):
            actor = str(log.get("actor") or log.get("actor_id") or "")
            action = str(log.get("action", ""))
            entity_id = str(log.get("entity_id", ""))
            prev_hash = str(log.get("prev_hash", ""))
            curr_hash = str(log.get("curr_hash", ""))
            timestamp = log.get("timestamp")
        else:
            actor = str(getattr(log, "actor", getattr(log, "actor_id", "")))
            action = str(getattr(log, "action", ""))
            entity_id = str(getattr(log, "entity_id", ""))
            prev_hash = str(getattr(log, "prev_hash", ""))
            curr_hash = str(getattr(log, "curr_hash", ""))
            timestamp = getattr(log, "timestamp", None)

        if timestamp is None:
            return False

        # Validate current record hash
        expected_hash = calculate_audit_hash(
            prev_hash=prev_hash,
            actor_id=actor,
            action=action,
            entity_id=entity_id,
            timestamp=timestamp,
        )

        if expected_hash.lower() != curr_hash.lower():
            return False

        # Validate parent-child linkage
        if i > 0:
            prev_log = logs[i - 1]
            prev_curr_hash = (
                prev_log.get("curr_hash")
                if isinstance(prev_log, dict)
                else getattr(prev_log, "curr_hash", None)
            )
            if prev_curr_hash is None or prev_curr_hash.lower() != prev_hash.lower():
                return False

    return True
