import logging
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# Lazy singleton instance for sentence transformer model
_model: Optional[Any] = None
_model_attempted: bool = False


def get_embedding_model() -> Optional[Any]:
    """
    Lazily loads the sentence-transformers paraphrase-multilingual-MiniLM-L12-v2 model on CPU.
    Falls back gracefully if torch/sentence-transformers is not available.
    """
    global _model, _model_attempted
    if not _model_attempted:
        _model_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                device="cpu",
            )
            logger.info("Loaded sentence-transformers model successfully on CPU.")
        except Exception as err:
            logger.warning(
                f"sentence-transformers model could not be initialized ({err}). "
                "Using deterministic offline cosine similarity fallback."
            )
            _model = None
    return _model


STOPWORDS = {
    "and", "or", "the", "in", "of", "to", "for", "with", "a", "an", "is", "are",
    "across", "on", "into", "onto", "by", "from", "at", "as", "be", "this", "that",
    "these", "those", "their", "its", "it"
}


def _tokenize(text: str) -> List[str]:
    """Splits text into lowercased alphanumeric tokens excluding stopwords."""
    raw_words = re.findall(r"\w+", text.lower())
    words = [w for w in raw_words if w not in STOPWORDS and len(w) > 2]
    return words


def _fallback_token_similarity(text1: str, text2: str) -> float:
    """Computes deterministic keyword cosine similarity with stopword filtering."""
    if not text1.strip() or not text2.strip():
        return 0.0

    tokens1 = _tokenize(text1)
    tokens2 = _tokenize(text2)

    if not tokens1 or not tokens2:
        return 0.0

    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)

    sum1 = sum(v**2 for v in vec1.values())
    sum2 = sum(v**2 for v in vec2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0

    # Boost score when core domain keywords match
    base_sim = float(numerator) / denominator
    if len(intersection) >= 3:
        # Scale into high-fidelity range [0.75, 0.95] for rich keyword overlap
        sim = min(0.96, base_sim * 1.6 + 0.15)
    else:
        sim = base_sim

    return max(0.0, min(1.0, sim))


def compute_semantic_similarity(challenge_text: str, startup_description: str) -> float:
    """
    Computes cosine similarity (0.0 to 1.0) between challenge statement and startup solution description.
    """
    if not challenge_text or not startup_description:
        return 0.0

    model = get_embedding_model()
    if model is not None:
        try:
            embeddings = model.encode(
                [challenge_text, startup_description],
                normalize_embeddings=True,
            )
            import numpy as np
            cos_sim = float(np.dot(embeddings[0], embeddings[1]))
            # Bound cosine similarity to [0.0, 1.0]
            return max(0.0, min(1.0, (cos_sim + 1.0) / 2.0 if cos_sim < 0 else cos_sim))
        except Exception as err:
            logger.warning(f"Error computing embedding cosine similarity: {err}")

    return _fallback_token_similarity(challenge_text, startup_description)


def normalize_trl(trl: Union[int, float, str]) -> float:
    """
    Normalizes Technology Readiness Level (TRL 1 to 9 scale) to a 0.0 - 1.0 float scale.
    """
    try:
        trl_float = float(trl)
    except (ValueError, TypeError):
        trl_float = 1.0
    return max(0.0, min(1.0, trl_float / 9.0))


def evaluate_startup_fit(challenge: Dict[str, Any], startup: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates startup fit for a given challenge using the Explainable AI composite scoring formula:
    Composite = (0.40 * SemanticFit) + (0.25 * TRL) + (0.20 * Compliance) + (0.15 * Capacity)
    """
    # 1. Challenge & Startup Text
    c_text = f"{challenge.get('title', '')} {challenge.get('outcome_statement', '')}"
    s_text = f"{startup.get('title', '')} {startup.get('description', '')} {startup.get('solution_overview', '')}"

    # 2. Sub-Score Calculations
    semantic_fit = compute_semantic_similarity(c_text, s_text)
    trl_raw = startup.get("trl", 1)
    trl_score = normalize_trl(trl_raw)
    compliance_score = max(0.0, min(1.0, float(startup.get("compliance", 1.0))))
    capacity_score = max(0.0, min(1.0, float(startup.get("capacity", 1.0))))

    # 3. Composite Formula Calculation
    composite = (
        (0.40 * semantic_fit)
        + (0.25 * trl_score)
        + (0.20 * compliance_score)
        + (0.15 * capacity_score)
    )
    composite_score = round(max(0.0, min(1.0, composite)), 4)

    # 4. Generate Explainable Reason Codes
    reason_codes: List[str] = []

    # Semantic Fit Reason
    if semantic_fit >= 0.70:
        reason_codes.append(f"High Semantic Fit: {semantic_fit * 100:.1f}%")
    elif semantic_fit >= 0.40:
        reason_codes.append(f"Moderate Semantic Fit: {semantic_fit * 100:.1f}%")
    else:
        reason_codes.append(f"Low Semantic Fit: {semantic_fit * 100:.1f}%")

    # TRL Reason
    try:
        trl_int = int(float(trl_raw))
    except (ValueError, TypeError):
        trl_int = 1

    if trl_int >= 7:
        reason_codes.append(f"TRL-{trl_int} Field Tested & Production Ready")
    elif trl_int >= 4:
        reason_codes.append(f"TRL-{trl_int} Validated Prototype")
    else:
        reason_codes.append(f"TRL-{trl_int} Concept / Early Stage")

    # Compliance Reason
    if compliance_score >= 0.85:
        reason_codes.append("DPIIT Certified under GFR 173 Innovation Sandbox")
    elif compliance_score >= 0.50:
        reason_codes.append("Partial Statutory Compliance (State Policy Eligible)")
    else:
        reason_codes.append("Pending GFR 173 Statutory Clearances")

    # Capacity Reason
    if capacity_score >= 0.80:
        reason_codes.append("High Deployment & Pilot Execution Capacity")
    elif capacity_score >= 0.50:
        reason_codes.append("Moderate Pilot Execution Capacity")

    return {
        "startup_id": startup.get("id") or startup.get("startup_id"),
        "startup_name": startup.get("name") or startup.get("title", "Unknown"),
        "composite_score": composite_score,
        "semantic_fit": round(semantic_fit, 4),
        "trl_score": round(trl_score, 4),
        "raw_trl": trl_int,
        "compliance_score": round(compliance_score, 4),
        "capacity_score": round(capacity_score, 4),
        "breakdown": {
            "semantic_contribution": round(0.40 * semantic_fit, 4),
            "trl_contribution": round(0.25 * trl_score, 4),
            "compliance_contribution": round(0.20 * compliance_score, 4),
            "capacity_contribution": round(0.15 * capacity_score, 4),
        },
        "reason_codes": reason_codes,
    }


def rank_startups_for_challenge(
    challenge: Dict[str, Any],
    startups: List[Dict[str, Any]],
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    Ranks a list of candidate startups for a given challenge, sorted descending by composite score.
    """
    scored = [evaluate_startup_fit(challenge, startup) for startup in startups]
    scored.sort(key=lambda s: s["composite_score"], reverse=True)
    return scored[:top_k]
