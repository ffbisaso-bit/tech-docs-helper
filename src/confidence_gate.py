def compute_confidence(evidence: dict) -> dict:
    if not evidence["enough_evidence"]:
        return {
            "confidence": "LOW",
            "score": 0.3,
            "reason": "Insufficient evidence."
        }

    strong = evidence.get("strong_chunks", 0)
    useful = evidence.get("useful_chunks", 0)

    if strong >= 2:
        return {
            "confidence": "HIGH",
            "score": 0.9,
            "reason": "Multiple strong evidence chunks."
        }

    if strong >= 1 and useful >= 2:
        return {
            "confidence": "MEDIUM",
            "score": 0.7,
            "reason": "Some strong and useful evidence."
        }

    return {
        "confidence": "LOW",
        "score": 0.4,
        "reason": "Weak supporting evidence."
    }