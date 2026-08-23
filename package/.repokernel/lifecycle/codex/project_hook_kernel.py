#!/usr/bin/env python3
"""Project-local, manifest-bound lifecycle competence kernel."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

HOOK_ROOT = Path(__file__).resolve().parent
FACULTY_ROOT = HOOK_ROOT / "faculties"
REGISTRY_PATH = HOOK_ROOT / "project_hook_faculties.v1.json"
SUPPORTED_EVENTS = {"SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop", "SessionEnd"}


def _degraded(event_name: str, reason: str) -> dict[str, Any]:
    message = f"PROJECT LIFECYCLE KERNEL DEGRADED: {reason}."
    if event_name == "PreToolUse":
        return {"hookSpecificOutput": {"hookEventName": event_name, "permissionDecision": "deny", "permissionDecisionReason": message}}
    if event_name == "Stop":
        return {"decision": "block", "reason": message}
    if event_name == "SessionEnd":
        return {}
    return {"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": message}}


def _load_registry() -> dict[str, Any]:
    value = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") != "repokernel.project-hook-faculty-registry.v1":
        raise ValueError("invalid faculty registry")
    if value.get("binding_registry_is_not_capability_ceiling") is not True:
        raise ValueError("closed faculty registry")
    faculties = value.get("faculties")
    if not isinstance(faculties, list) or not faculties:
        raise ValueError("missing faculties")
    primary = [item for item in faculties if item.get("stop_projection", {}).get("mode") == "primary"]
    if len(primary) != 1 or primary[0].get("failure_mode") != "protect":
        raise ValueError("exactly one protective primary is required")
    return value


def _load_handler(binding: dict[str, Any]):
    module_name = binding.get("module")
    handler_name = binding.get("handler")
    if not isinstance(module_name, str) or not module_name.replace("_", "a").isalnum():
        raise ValueError("invalid module name")
    if not isinstance(handler_name, str) or not handler_name.replace("_", "a").isalnum():
        raise ValueError("invalid handler name")
    if str(FACULTY_ROOT) not in sys.path:
        sys.path.insert(0, str(FACULTY_ROOT))
    module = importlib.import_module(module_name)
    observed = Path(module.__file__ or "").resolve()
    if observed.parent != FACULTY_ROOT.resolve():
        raise ImportError("faculty escaped project hook root")
    handler = getattr(module, handler_name, None)
    if not callable(handler):
        raise AttributeError("faculty handler missing")
    return handler


def _merge(event_name: str, registry: dict[str, Any], results: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
    denials: list[str] = []
    contexts: list[tuple[str, bool]] = []
    stop_items: list[tuple[dict[str, Any], str]] = []
    for binding, response in results:
        if response.get("decision") == "block" and isinstance(response.get("reason"), str):
            stop_items.append((binding, response["reason"]))
        specific = response.get("hookSpecificOutput")
        if not isinstance(specific, dict):
            continue
        if specific.get("permissionDecision") == "deny" and isinstance(specific.get("permissionDecisionReason"), str):
            denials.append(specific["permissionDecisionReason"])
        if isinstance(specific.get("additionalContext"), str):
            contexts.append((specific["additionalContext"], binding.get("failure_mode") == "protect"))
    if denials:
        return {"hookSpecificOutput": {"hookEventName": event_name, "permissionDecision": "deny", "permissionDecisionReason": "\n\n".join(dict.fromkeys(denials))}}
    if event_name == "Stop":
        if not stop_items:
            return {"continue": True}
        primary = [reason for binding, reason in stop_items if binding.get("stop_projection", {}).get("mode") == "primary"]
        if not primary:
            return _degraded(event_name, "protective primary produced no continuation")
        message = " ".join(primary)
        guidance = [binding["stop_projection"]["text"].strip().rstrip(".") for binding, _ in stop_items if binding.get("stop_projection", {}).get("mode") == "guidance"]
        if guidance:
            message += " Active correction: " + "; ".join(guidance) + "."
        if len(message) > int(registry.get("context_budgets", {}).get("Stop", 900)):
            return _degraded(event_name, "protected stop continuation exceeds budget")
        return {"decision": "block", "reason": message}
    if not contexts:
        return {}
    budget = int(registry.get("context_budgets", {}).get(event_name, 650))
    admitted: list[str] = []
    for context, protected in contexts:
        candidate = "\n\n".join([*admitted, context])
        if len(candidate) <= budget:
            admitted.append(context)
        elif protected:
            return _degraded(event_name, "protected context exceeds budget")
    return {"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": "\n\n".join(admitted)}} if admitted else {}


def handle(event: dict[str, Any]) -> dict[str, Any]:
    event_name = event.get("hook_event_name") or event.get("hookEventName")
    if event_name not in SUPPORTED_EVENTS:
        return {}
    if event_name == "Stop" and event.get("stop_hook_active") is True:
        return {"continue": True}
    try:
        registry = _load_registry()
    except Exception as exc:
        return _degraded(str(event_name), f"registry unavailable: {type(exc).__name__}")
    bindings = [item for item in registry["faculties"] if event_name in item.get("events", [])]
    bindings.sort(key=lambda item: (-int(item.get("priority", 0)), str(item.get("faculty_id", ""))))
    results: list[tuple[dict[str, Any], dict[str, Any]]] = []
    protected_errors: list[str] = []
    for binding in bindings:
        try:
            response = _load_handler(binding)(event)
            if not isinstance(response, dict):
                raise TypeError("faculty response must be an object")
            results.append((binding, response))
        except Exception as exc:
            if binding.get("failure_mode") == "protect":
                protected_errors.append(f"{binding.get('faculty_id')}: {type(exc).__name__}")
    if protected_errors:
        return _degraded(str(event_name), ", ".join(protected_errors))
    return _merge(str(event_name), registry, results)


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            event = {}
    except (json.JSONDecodeError, OSError):
        event = {}
    json.dump(handle(event), sys.stdout, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
