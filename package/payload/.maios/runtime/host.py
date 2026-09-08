"""Reviewed project-local host capability attestation."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

try:
    from . import filesystem as filesystem_engine
    from . import configuration as configuration_engine
except ImportError:  # generated runtime and installer carry the same source
    import maios_filesystem as filesystem_engine  # type: ignore[no-redef]
    import configuration as configuration_engine  # type: ignore[no-redef]


HOST_STATE_SCHEMA = "maios.host-state.v2"
HOST_ATTESTATION_SCHEMA = "maios.host-attestation.v2"
HOST_RECEIPT_SCHEMA = "maios.host-attestation-receipt.v2"
HOST_CATALOG_SCHEMA = "maios.installed-host-adapters.v1"
STAGE_FIELDS = {stage: stage for stage in configuration_engine.HOST_ATTESTATION_STAGES}
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
    try:
        filesystem_engine.ensure_local(root, path)
    except (ValueError, OSError) as exc:
        raise HostAttestationError(str(exc)) from exc



def write_json_atomic(path: Path, value: Any) -> None:
    filesystem_engine.write_json_atomic(path, value)


def host_state_path(root: Path) -> Path:
    return root / ".maios" / "state" / "HOST_STATE.json"


def read_host_catalog(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = root / ".maios" / "config" / "HOST_ADAPTERS.json"
    ensure_project_local(root, path)
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema") != HOST_CATALOG_SCHEMA:
        raise HostAttestationError("unsupported installed host adapter catalogue")
    adapters = value.get("adapters")
    if not isinstance(adapters, list) or not adapters:
        raise HostAttestationError("installed host adapter catalogue is empty")
    ids = [item.get("id") for item in adapters if isinstance(item, dict)]
    if (
        len(ids) != len(adapters)
        or any(not isinstance(item, str) or not item for item in ids)
        or len(ids) != len(set(ids))
    ):
        raise HostAttestationError("installed host adapter ids must be present and unique")
    return value


def supported_host_ids(root: Path) -> set[str]:
    return {item["id"] for item in read_host_catalog(root)["adapters"]}


def read_host_state(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = host_state_path(root)
    ensure_project_local(root, path)
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema") != HOST_STATE_SCHEMA:
        raise HostAttestationError("unsupported host state schema")
    if value.get("selected_adapter") not in supported_host_ids(root):
        raise HostAttestationError("host state has no supported selected adapter")
    return value


def host_status(root: Path) -> dict[str, Any]:
    state = read_host_state(root)
    errors = configuration_engine.owner_state_receipt_errors(root, "host", state)
    pending = configuration_engine.pending_transitions(root)
    return {
        "valid": not errors and not pending, "recovery_required": bool(errors or pending),
        "errors": errors, "pending_journals": pending,
        "schema": "maios.host-status.v2",
        "selected_adapter": state["selected_adapter"],
        "revision": state.get("revision", 0),
        "host_state_sha256": digest(state),
        **{stage: "unverified" if errors else state.get(stage) for stage in STAGE_FIELDS},
        "observed_capabilities": [] if errors else state.get("observed_capabilities", []),
        "unverified_capabilities": sorted(set(state.get("unverified_capabilities", []))
                                          | (set(state.get("observed_capabilities", [])) if errors else set())),
        "claim_boundary": "installation and indexed attestations do not substitute for their referenced observations",
    }


def validate_host_attestation(root: Path, value: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return {
            "schema": "maios.host-attestation-validation.v2",
            "valid": False,
            "errors": ["attestation must be an object"],
        }
    if value.get("schema") != HOST_ATTESTATION_SCHEMA:
        errors.append("unsupported host attestation schema")
    for field in ("sequence", "event_digest"):
        if field in value:
            errors.append(f"{field} is reserved for recorded event metadata")
    event_id = value.get("event_id")
    if not isinstance(event_id, str) or not event_id:
        errors.append("event_id must be non-empty")
    elif not configuration_engine.valid_event_id(event_id):
        errors.append("event_id is unsafe or reserved for transaction control")
    if value.get("stage") not in STAGE_FIELDS:
        errors.append("unsupported host attestation stage")
    try:
        if value.get("host") not in supported_host_ids(root):
            errors.append("unsupported attestation host")
    except HostAttestationError as exc:
        errors.append(str(exc))
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
    invalidated = value.get("invalidated_capabilities", [])
    if not isinstance(invalidated, list) or not all(
        isinstance(item, str) and bool(item.strip()) for item in invalidated
    ):
        errors.append("invalidated_capabilities must be a list of non-empty strings")
    elif (value.get("result") == "verified" and isinstance(capabilities, list)
          and all(isinstance(x, str) for x in capabilities)
          and set(invalidated) & set(capabilities)):
        errors.append("a capability cannot be verified and invalidated in the same observation")
    review = value.get("review")
    if review is not None:
        if not isinstance(review, dict) or review.get("status") not in {
            "pending", "accepted", "rejected"
        }:
            errors.append("optional review must describe a pending, accepted or rejected review")
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
    configuration_engine.require_no_pending_transition(root)
    validation = validate_host_attestation(root, attestation)
    if not validation["valid"]:
        raise HostAttestationError(
            "invalid host attestation: " + "; ".join(validation["errors"])
        )
    state = read_host_state(root)
    coherence = configuration_engine.owner_state_receipt_errors(root, "host", state)
    if coherence:
        raise HostAttestationError("; ".join(coherence))
    before_sha256 = digest(state)
    if expected_state_sha256 != before_sha256:
        raise HostAttestationError("host state changed before recording the observation")
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
    if stage == "behavioral_activation" and attestation["result"] == "verified":
        discovered = (
            state.get("instruction_discovery") == "verified"
            or state.get("skill_discovery") == "verified"
        )
        if not discovered or state.get("state_read") != "verified":
            raise HostAttestationError(
                "behavioral activation requires verified discovery and state read"
            )
    if (stage == "maintained_reentry" and attestation["result"] == "verified"
            and state.get("behavioral_activation") != "verified"):
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
    invalidated = set(attestation.get("invalidated_capabilities", []))
    if attestation["result"] == "failed":
        invalidated.update(attestation.get("observed_capabilities", []))
    updated["observed_capabilities"] = sorted(
        set(updated.get("observed_capabilities", [])) - invalidated
    )
    updated["unverified_capabilities"] = sorted(
        (set(state.get("unverified_capabilities", [])) | invalidated)
        - set(updated["observed_capabilities"])
    )
    after_sha256 = digest(updated)
    path = host_state_path(root)
    ensure_project_local(root, path)
    receipt = {
        "schema": HOST_RECEIPT_SCHEMA,
        "status": "admitted",
        "event_id": attestation["event_id"],
        "event_digest": validation["event_digest"],
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
    if receipt_path.exists() or filesystem_engine.is_link(receipt_path):
        raise HostAttestationError("terminal receipt path already exists outside recorded history")
    outputs = (path.relative_to(root).as_posix(), receipt_path.relative_to(root).as_posix())
    with configuration_engine.state_transaction(root, "host", outputs):
        write_json_atomic(path, updated)
        write_json_atomic(receipt_path, receipt)
        return receipt
