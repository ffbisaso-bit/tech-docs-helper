import json
from pathlib import Path

from config import LOGS_PATH


def load_logs() -> list:
    log_files = sorted(Path(LOGS_PATH).glob("audit_*.json"))

    logs = []
    for file in log_files:
        with open(file, "r", encoding="utf-8") as f:
            logs.append(json.load(f))

    return logs


def compute_drift(logs: list) -> dict:
    if not logs:
        return {
            "status": "NO_DATA",
            "total_runs": 0,
            "answer_rate": 0,
            "refuse_rate": 0,
            "escalate_rate": 0,
            "average_attempts": 0,
            "verification_pass_rate": 0
        }

    total_runs = len(logs)

    answer_count = 0
    refuse_count = 0
    escalate_count = 0

    total_attempts = 0
    pass_count = 0

    for log in logs:
        decision = log.get("final_decision")

        if decision == "ANSWER":
            answer_count += 1
        elif decision == "REFUSE":
            refuse_count += 1
        elif decision == "ESCALATE":
            escalate_count += 1

        total_attempts += log.get("attempts", 0)

        verification = log.get("verification_result", {})
        if verification.get("verdict") == "PASS":
            pass_count += 1

    return {
        "total_runs": total_runs,
        "answer_rate": answer_count / total_runs,
        "refuse_rate": refuse_count / total_runs,
        "escalate_rate": escalate_count / total_runs,
        "average_attempts": total_attempts / total_runs,
        "verification_pass_rate": pass_count / total_runs
    }


def detect_drift(metrics: dict) -> dict:
    issues = []

    if metrics.get("refuse_rate", 0) > 0.4:
        issues.append("High refusal rate")

    if metrics.get("escalate_rate", 0) > 0.3:
        issues.append("High escalation rate")

    if metrics.get("average_attempts", 0) > 2:
        issues.append("Too many retries")

    if metrics.get("verification_pass_rate", 1) < 0.7:
        issues.append("Low verification pass rate")

    status = "HEALTHY" if not issues else "DRIFT_DETECTED"

    return {
        "status": status,
        "issues": issues,
        "metrics": metrics
    }


def run_drift_detection() -> dict:
    logs = load_logs()
    metrics = compute_drift(logs)
    result = detect_drift(metrics)

    return result