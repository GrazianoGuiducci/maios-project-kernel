"""Detect when control language displaces the requested result and movement."""
from __future__ import annotations

import re
from typing import Any

CONTROL = re.compile(r"\b(?:check|verify|validation|gate|retry|procedure|process|control|review)\b", re.IGNORECASE)
RESULT = re.compile(r"\b(?:produced|completed|changed|result|delivered|implemented|fixed|created|updated|movement|next)\b", re.IGNORECASE)


def handle(event: dict[str, Any]) -> dict[str, Any]:
    if event.get("stop_hook_active") is True:
        return {"continue": True}
    message = event.get("last_assistant_message")
    if not isinstance(message, str) or not message.strip():
        return {"continue": True}
    controls = len(CONTROL.findall(message))
    results = len(RESULT.findall(message))
    if controls < 4 or results > 0:
        return {"continue": True}
    return {"decision": "block", "reason": "The response is dominated by control language while the selected reason, produced result, or consequent movement is weak."}
