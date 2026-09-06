import unittest
from datetime import datetime
from app.core.audit_chain import calculate_audit_hash, verify_audit_log_integrity


class TestAuditChain(unittest.TestCase):
    def test_calculate_audit_hash_deterministic(self):
        prev = "0" * 64
        actor = "officer_101"
        action = "PUBLISH_CHALLENGE"
        entity = "challenge:42"
        ts = "2026-09-05T12:00:00"

        hash1 = calculate_audit_hash(prev, actor, action, entity, ts)
        hash2 = calculate_audit_hash(prev, actor, action, entity, ts)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_verify_audit_log_integrity_valid_chain(self):
        logs = []
        prev_hash = "0" * 64
        for i in range(5):
            ts = f"2026-09-05T12:0{i}:00"
            actor = f"actor_{i}"
            action = f"ACTION_{i}"
            entity = f"entity_{i}"
            curr_hash = calculate_audit_hash(prev_hash, actor, action, entity, ts)
            logs.append({
                "actor": actor,
                "action": action,
                "entity_id": entity,
                "prev_hash": prev_hash,
                "curr_hash": curr_hash,
                "timestamp": ts,
            })
            prev_hash = curr_hash

        self.assertTrue(verify_audit_log_integrity(logs))

    def test_verify_audit_log_integrity_tampered_payload(self):
        logs = []
        prev_hash = "0" * 64
        for i in range(3):
            ts = f"2026-09-05T12:0{i}:00"
            actor = f"actor_{i}"
            action = f"ACTION_{i}"
            entity = f"entity_{i}"
            curr_hash = calculate_audit_hash(prev_hash, actor, action, entity, ts)
            logs.append({
                "actor": actor,
                "action": action,
                "entity_id": entity,
                "prev_hash": prev_hash,
                "curr_hash": curr_hash,
                "timestamp": ts,
            })
            prev_hash = curr_hash

        # Tamper middle record payload without updating hash
        logs[1]["action"] = "TAMPERED_ACTION"
        self.assertFalse(verify_audit_log_integrity(logs))

    def test_verify_audit_log_integrity_broken_linkage(self):
        logs = []
        prev_hash = "0" * 64
        for i in range(3):
            ts = f"2026-09-05T12:0{i}:00"
            actor = f"actor_{i}"
            action = f"ACTION_{i}"
            entity = f"entity_{i}"
            curr_hash = calculate_audit_hash(prev_hash, actor, action, entity, ts)
            logs.append({
                "actor": actor,
                "action": action,
                "entity_id": entity,
                "prev_hash": prev_hash,
                "curr_hash": curr_hash,
                "timestamp": ts,
            })
            prev_hash = curr_hash

        # Tamper prev_hash linkage
        logs[2]["prev_hash"] = "f" * 64
        # Even if curr_hash is recalculated to match the corrupted prev_hash:
        logs[2]["curr_hash"] = calculate_audit_hash(
            logs[2]["prev_hash"], logs[2]["actor"], logs[2]["action"], logs[2]["entity_id"], logs[2]["timestamp"]
        )
        self.assertFalse(verify_audit_log_integrity(logs))


if __name__ == "__main__":
    unittest.main()
