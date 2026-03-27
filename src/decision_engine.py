def make_decision(evidence: dict, confidence: dict, arbitration: dict) -> dict:
    if arbitration["conflict"]:
        return {
            "decision": "ESCALATE",
            "reason": "Conflicting signals require escalation."
        }

    if not evidence["enough_evidence"]:
        return {
            "decision": "REFUSE",
            "reason": "Evidence is insufficient."
        }

    if confidence["confidence"] in {"MEDIUM", "HIGH"}:
        return {
            "decision": "ANSWER",
            "reason": "Evidence is sufficient and no conflict exists."
        }

    return {
        "decision": "ESCALATE",
        "reason": "Unable to make a safe final decision."
    }