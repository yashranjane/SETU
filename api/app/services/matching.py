import math
import re
from typing import List, Dict, Any


def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    tokens = re.findall(r"[a-z0-9]+", text)
    # Filter common stop words
    stops = {"the", "and", "a", "an", "in", "on", "of", "for", "with", "to", "at", "by", "from", "is", "are", "was", "were"}
    return [t for t in tokens if t not in stops and len(t) > 1]


def compute_cosine_similarity(text1: str, text2: str) -> float:
    t1 = tokenize(text1)
    t2 = tokenize(text2)
    if not t1 or not t2:
        return 0.15

    v1: Dict[str, int] = {}
    v2: Dict[str, int] = {}
    for w in t1:
        v1[w] = v1.get(w, 0) + 1
    for w in t2:
        v2[w] = v2.get(w, 0) + 1

    all_words = set(v1.keys()).union(set(v2.keys()))
    dot = sum(v1.get(w, 0) * v2.get(w, 0) for w in all_words)
    mag1 = math.sqrt(sum(c * c for c in v1.values()))
    mag2 = math.sqrt(sum(c * c for c in v2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.15

    raw_sim = dot / (mag1 * mag2)
    # Check domain/keyword overlaps
    domain_overlap = sum(1 for w in t1 if w in v2)
    boost = min(0.35, domain_overlap * 0.08)
    sim = min(0.99, max(0.20, raw_sim + boost))
    return round(sim, 3)


def calculate_explainable_fit(challenge_outcome: str, startup_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    CompositeScore = (0.40 * SemanticFit) + (0.25 * TRL) + (0.20 * Compliance) + (0.15 * Capacity)
    """
    # 1. Semantic Fit (40%)
    st_text = f"{startup_data.get('domain', '')} {startup_data.get('solution_title', '')} {startup_data.get('description', '')}"
    semantic_fit = compute_cosine_similarity(challenge_outcome, st_text)

    # 2. TRL Score (25%)
    # TRL ranges from 1 to 9. TRL 7+ represents field-tested innovation.
    trl_level = int(startup_data.get("trl_level", 7))
    trl_score = min(1.0, max(0.4, (trl_level / 9.0) * 1.1))

    # 3. Compliance Score (20%)
    # DPIIT Certification (0.50) + GeM Verification (0.50)
    dpiit = 0.50 if startup_data.get("dpiit_certified", True) else 0.10
    gem = 0.50 if startup_data.get("is_gem_verified", True) else 0.10
    compliance_score = dpiit + gem

    # 4. Capacity Score (15%)
    capacity_score = float(startup_data.get("financial_capacity_score", 0.85))

    # Weighted Composite Score
    composite = (0.40 * semantic_fit) + (0.25 * trl_score) + (0.20 * compliance_score) + (0.15 * capacity_score)
    percentage = round(composite * 100, 1)

    # Generate Dynamic Reason Chips
    reason_chips = []
    if trl_level >= 7:
        reason_chips.append(f"#TRL-{trl_level} Field Ready")
    else:
        reason_chips.append(f"#TRL-{trl_level} Lab Validated")

    if startup_data.get("dpiit_certified"):
        reason_chips.append("#DPIIT Certified")
    if startup_data.get("is_gem_verified"):
        reason_chips.append("#GeM Verified")

    sem_pct = int(semantic_fit * 100)
    if sem_pct >= 80:
        reason_chips.append(f"#High Semantic Fit: {sem_pct}%")
    else:
        reason_chips.append(f"#Semantic Fit: {sem_pct}%")

    return {
        "composite_score": composite,
        "match_percentage": percentage,
        "semantic_fit": semantic_fit,
        "trl_score": round(trl_score, 2),
        "compliance_score": round(compliance_score, 2),
        "capacity_score": round(capacity_score, 2),
        "reason_chips": reason_chips,
    }
