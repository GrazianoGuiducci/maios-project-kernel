"""Protect operator-source continuity and require a post-mutation readback."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

HOOK_ROOT = Path(__file__).resolve().parents[1]
STATE_ROOT = HOOK_ROOT / ".state" / "project_lifecycle"
MUTATING_COMMAND = re.compile(r"(?:^|[;&|\s])(?:rm|mv|cp|touch|mkdir|rmdir|del|move|copy|new-item|remove-item|move-item|copy-item|set-content|add-content|out-file|git\s+(?:add|commit|push|checkout|switch|merge|rebase|reset|clean)|pip\s+install|npm\s+(?:install|publish)|python\s+-m\s+pip\s+install)(?:$|\s)|(?:^|[^<])>{1,2}(?!>)", re.IGNORECASE)


def _state_path(event: dict[str, Any]) -> Path:
    session = str(event.get("session_id") or event.get("sessionId") or "default")
    safe = hashlib.sha256(session.encode("utf-8")).hexdigest()[:24]
    return STATE_ROOT / f"{safe}.json"


def _read(event: dict[str, Any]) -> dict[str, Any]:
    try:
        value = json.loads(_state_path(event).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write(event: dict[str, Any], value: dict[str, Any]) -> None:
    path = _state_path(event)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def _remove(event: dict[str, Any]) -> None:
    path = _state_path(event)
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
    for directory in (path.parent, STATE_ROOT.parent):
        try:
            directory.rmdir()
        except OSError:
            pass


def _context(event_name: str, text: str) -> dict[str, Any]:
    return {"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": text}}


def _is_mutating(event: dict[str, Any]) -> bool:
    tool = str(event.get("tool_name") or event.get("toolName") or "")
    if tool in {"Edit", "Write", "apply_patch"}:
        return True
    if tool != "Bash":
        return False
    tool_input = event.get("tool_input") or event.get("toolInput")
    if not isinstance(tool_input, dict):
        return False
    command = tool_input.get("command", tool_input.get("cmd", ""))
    return isinstance(command, str) and bool(MUTATING_COMMAND.search(command))


def handle(event: dict[str, Any]) -> dict[str, Any]:
    name = event.get("hook_event_name") or event.get("hookEventName")
    if name == "SessionStart":
        if event.get("source") in {"startup", "clear", None}:
            _remove(event)
        return _context(name, "Treat the operator prompt as intent and direction, not as the whole solution. Preserve source, verified evidence, model inference, unknowns, reusable competence deltas, and the produced form as distinguishable relations. Do not extend a relation by proximity, and do not mistake a capability contribution for material authority.")
    if name == "UserPromptSubmit":
        prompt = event.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return {"continue": True}
        if prompt.startswith("FINAL PROJECT RESULT REVIEW:"):
            return {"continue": True}
        _write(event, {"prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "mutation_seen": False, "post_readback_sent": False, "stop_review_sent": False})
        return _context(name, "Form a source-bound project result from the operator's intent, current evidence, pertinent project faculties, and explicit unknowns. Preserve causal relations; remove only unsupported propagation. Resolve authority only when an exact material effect emerges.")
    if name == "PreToolUse":
        if not _is_mutating(event):
            return {}
        state = _read(event)
        if not state.get("prompt_sha256"):
            return {"hookSpecificOutput": {"hookEventName": name, "permissionDecision": "deny", "permissionDecisionReason": "PROJECT SOURCE CONTINUITY BLOCK: the current operator source is not sealed for this session."}}
        return _context(name, "Before mutation, name the exact project-owned effect internally and keep adjacent repositories, hosts, public surfaces, and credentials outside its authority. Preserve reversibility and do not let the current implementation form limit the result.")
    if name == "PostToolUse":
        if not _is_mutating(event):
            return {}
        state = _read(event)
        state["mutation_seen"] = True
        if state.get("post_readback_sent"):
            _write(event, state)
            return {}
        state["post_readback_sent"] = True
        _write(event, state)
        return _context(name, "Read the actual diff or effect back against the source-bound result. Tests prove implementation consistency, not semantic fidelity. Keep supported causal relations and remove unsupported proximity, private residue, hidden authority, and agent-introduced limits.")
    if name == "Stop":
        state = _read(event)
        if not state.get("mutation_seen") or state.get("stop_review_sent"):
            return {"continue": True}
        state["stop_review_sent"] = True
        _write(event, state)
        return {"decision": "block", "reason": "FINAL PROJECT RESULT REVIEW: no operator action is required. Re-read the actual result against the current source-bound field. Distinguish operator source, evidence, model inference, reusable competence delta, unknown, and produced form. Preserve supported relations, remove only unsupported propagation, and close only the verified owner-local delta. Conclude with one exact outcome: state_updated, competence_integrated, queued, or no_change."}
    if name == "SessionEnd":
        _remove(event)
    return {}
