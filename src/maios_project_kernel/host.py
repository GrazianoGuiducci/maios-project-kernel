"""Reviewed project-local host capability attestation."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


HOST_STATE_SCHEMA = "maios.host-state.v2"
HOST_ATTESTATION_SCHEMA = "maios.host-attestation.v2"
HOST_RECEIPT_SCHEMA = "maios.host-attestation-receipt.v2"
STAGE_FIELDS = {
    "instruction_discovery": "instruction_discovery",
    "skill_discovery": "skill_discovery",
    "state_read": "state_read",
    "behavioral_activation": "behavioral_activation",
    "maintained_reentry": "maintained_reentry",
}
SAFE_EVENT_ID = re.compile(r"^[A-Za-z0-9._-]+$")


class HostAttestationError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise HostAttestationError(f"cannot read valid JSON: {path}: {exc}") from exc


def ensure_project_local(root: Path, path: Path) -> None:
    root = root.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise HostAttestationError(f"path is outside project root: {path}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise HostAttestationError(f"host state path contains a symlink: {relative}")
    if not path.parent.resolve().is_relative_to(root):
        raise HostAttestationError(f"host state parent escapes root: {relative}")


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.maios-tmp-{os.getpid()}")
    try:
        temporary.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def host_state_path(root: Path) -> Path:
    return root / ".maios" / "state" / "HOST_STATE.json"


def read_host_state(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = host_state_path(root)
    ensure_project_local(root, path)
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema") != HOST_STATE_SCHEMA:
        raise HostAttestationError("unsupported host state schema")
    if value.get("selected_adapter") not in {
        "generic",
        "codex",
        "claude",
        "opencode",
        "hermes",
        "dsh",
    }:
        raise HostAttestationError("host state has no supported selected adapter")
    return value


def host_status(root: Path) -> dict[str, Any]:
    state = read_host_state(root)
    return {
        "schema": "maios.host-status.v2",
        "selected_adapter": state["selected_adapter"],
        "revision": state.get("revision", 0),
        "host_state_sha256": digest(state),
        "instruction_discovery": state.get("instruction_discovery"),
        "skill_discovery": state.get("skill_discovery"),
        "state_read": state.get("state_read"),
        "behavioral_activation": state.get("behavioral_activation"),
        "maintained_reentry": state.get("maintained_reentry"),
        "observed_capabilities": state.get("observed_capabilities", []),
        "claim_boundary": "installation and indexed attestations do not substitute for their referenced observations",
    }


def validate_host_attestation(value: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return {
            "schema": "maios.host-attestation-validation.v2",
            "valid": False,
            "errors": ["attestation must be an object"],
        }
    if value.get("schema") != HOST_ATTESTATION_SCHEMA:
        errors.append("unsupported host attestation schema")
    event_id = value.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        errors.append("event_id must be non-empty")
    elif not SAFE_EVENT_ID.fullmatch(event_id):
        errors.append("event_id contains unsafe characters")
    if value.get("stage") not in STAGE_FIELDS:
        errors.append("unsupported host attestation stage")
    if value.get("host") not in {
        "generic",
        "codex",
        "claude",
        "opencode",
        "hermes",
        "dsh",
    }:
        errors.append("unsupported attestation host")
    if value.get("result") not in {"verified", "failed"}:
        errors.append("host attestation result must be verified or failed")
    if not isinstance(value.get("observation"), str) or not value["observation"].strip():
        errors.append("observation must be non-empty")
    evidence = value.get("evidence_refs")
    if not isinstance(evidence, list) or not evidence or not all(
        isinstance(item, str) and bool(item.strip()) for item in evidence
    ):
        errors.append("evidence_refs must contain at least one reference")
    capabilities = value.get("observed_capabilities", [])
    if not isinstance(capabilities, list) or not all(
        isinstance(item, str) and bool(item.strip()) for item in capabilities
    ):
        errors.append("observed_capabilities must be a list of non-empty strings")
    review = value.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
    else:
        if review.get("status") != "accepted":
            errors.append("host attestation must be explicitly accepted")
        if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
            errors.append("reviewer must be non-empty")
        if review.get("reviewer_relation") not in {
            "operator",
            "owner",
            "independent_observer",
        }:
            errors.append("unsupported reviewer relation")
        if review.get("producer_is_reviewer") is not False:
            errors.append("the producer cannot approve its own host attestation")
    return {
        "schema": "maios.host-attestation-validation.v2",
        "valid": not errors,
        "errors": errors,
        "event_digest": digest(value) if not errors else None,
        "claim_boundary": "contract validity is not observation validity",
    }


def admit_host_attestation(
    root: Path, attestation: Any, expected_state_sha256: str
) -> dict[str, Any]:
    root = root.resolve()
    validation = validate_host_attestation(attestation)
    if not validation["valid"]:
        raise HostAttestationError(
            "invalid host attestation: " + "; ".join(validation["errors"])
        )
    state = read_host_state(root)
    before_sha256 = digest(state)
    if expected_state_sha256 != before_sha256:
        raise HostAttestationError("host state changed after review")
    if attestation.get("host") != state["selected_adapter"]:
        raise HostAttestationError("attestation host does not match installed adapter")

    history = list(state.get("attestation_history", []))
    for prior in history:
        if prior.get("event_id") == attestation["event_id"]:
            if prior.get("event_digest") != validation["event_digest"]:
                raise HostAttestationError("event_id already exists with different content")
            return {
                "schema": HOST_RECEIPT_SCHEMA,
                "status": "idempotent",
                "event_id": attestation["event_id"],
                "host_state_sha256": before_sha256,
            }

    stage = attestation["stage"]
    if stage == "behavioral_activation":
        discovered = (
            state.get("instruction_discovery") == "verified"
            or state.get("skill_discovery") == "verified"
        )
        if not discovered or state.get("state_read") != "verified":
            raise HostAttestationError(
                "behavioral activation requires verified discovery and state read"
            )
    if stage == "maintained_reentry" and state.get("behavioral_activation") != "verified":
        raise HostAttestationError(
            "maintained reentry requires prior verified behavioral activation"
        )

    admitted = dict(attestation)
    admitted["event_digest"] = validation["event_digest"]
    admitted["sequence"] = int(state.get("revision", 0)) + 1
    history.append(admitted)
    updated = dict(state)
    updated["revision"] = int(state.get("revision", 0)) + 1
    updated[STAGE_FIELDS[stage]] = attestation["result"]
    updated["attestation_history"] = history
    updated["last_event_id"] = attestation["event_id"]
    updated["evidence"] = list(state.get("evidence", [])) + attestation["evidence_refs"]
    if attestation["result"] == "verified":
        updated["observed_capabilities"] = sorted(
            set(state.get("observed_capabilities", []))
            | set(attestation.get("observed_capabilities", []))
        )
    after_sha256 = digest(updated)
    path = host_state_path(root)
    ensure_project_local(root, path)
    write_json_atomic(path, updated)
    receipt = {
        "schema": HOST_RECEIPT_SCHEMA,
        "status": "admitted",
        "event_id": attestation["event_id"],
        "stage": stage,
        "result": attestation["result"],
        "before_state_sha256": before_sha256,
        "after_state_sha256": after_sha256,
        "revision": updated["revision"],
        "global_writes": [],
    }
    receipt_path = (
        root
        / ".maios"
        / "receipts"
        / "host"
        / f"{attestation['event_id']}.json"
    )
    ensure_project_local(root, receipt_path)
    write_json_atomic(receipt_path, receipt)
    return receipt
