"""Challenge unsupported closures introduced by the response itself."""
from __future__ import annotations

import re
from typing import Any

CLOSURE = re.compile(r"\b(?:only option|only possible|cannot evolve|must always|impossible|no alternative)\b", re.IGNORECASE)
GROUND = re.compile(r"\b(?:source|evidence|verified|operator selected|authority|invariant|constraint)\b", re.IGNORECASE)


def handle(event: dict[str, Any]) -> dict[str, Any]:
    if event.get("stop_hook_active") is True:
        return {"continue": True}
    message = event.get("last_assistant_message")
    if not isinstance(message, str) or not message.strip():
        return {"continue": True}
    if not CLOSURE.search(message) or GROUND.search(message):
        return {"continue": True}
    return {"decision": "block", "reason": "The response introduces a strong closure without naming a source, verified condition, authority boundary, invariant, or operator-selected direction."}
