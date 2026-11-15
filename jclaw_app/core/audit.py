from pathlib import Path
from datetime import datetime, timezone
import json

LOG_PATH = Path.home() / ".jclaw" / "activity.jsonl"

def record(action: str, details: dict | None = None) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    item = {"time": datetime.now(timezone.utc).isoformat(), "action": action, "details": details or {}}
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False) + "\n")
