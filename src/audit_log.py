import json
from datetime import datetime
from pathlib import Path

from config import LOGS_PATH


def write_audit_log(audit_data: dict) -> str:
    Path(LOGS_PATH).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    log_file = Path(LOGS_PATH) / f"audit_{timestamp}.json"

    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)

    return str(log_file)