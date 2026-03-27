def arbitrate_signals(evidence: dict, confidence: dict) -> dict:
    conflict = False
    reasons = []

    if evidence["enough_evidence"] and confidence["confidence"] == "LOW":
        conflict = True
        reasons.append("Evidence passed but confidence is low.")

    if not evidence["enough_evidence"] and confidence["confidence"] in {"MEDIUM", "HIGH"}:
        conflict = True
        reasons.append("Confidence is high but evidence is insufficient.")

    if not reasons:
        reasons.append("No signal conflict detected.")

    return {
        "conflict": conflict,
        "reasons": reasons
    }