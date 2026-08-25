"""Canonical MAIOS situated-configuration state transition engine."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from typing import Any


CONFIGURATION_SCHEMA = "maios.configuration-state.v2"
RECEIPT_SCHEMA = "maios.configuration-receipt.v2"
RECOVERY_SCHEMA = "maios.configuration-recovery.v2"


class ConfigurationError(RuntimeError):
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
        raise ConfigurationError(f"cannot read valid JSON: {path}: {exc}") from exc


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.maios-tmp-{os.getpid()}")
    text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        temporary.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.maios-tmp-{os.getpid()}")
    try:
        temporary.write_text(text, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def configuration_path(root: Path) -> Path:
    return root / "setup" / "CONFIGURATION_STATE.json"


def ensure_project_local(root: Path, path: Path) -> None:
    root = root.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ConfigurationError(f"path is outside project root: {path}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise ConfigurationError(f"project state path contains a symlink: {relative}")
    resolved_parent = path.parent.resolve()
    if not resolved_parent.is_relative_to(root):
        raise ConfigurationError(f"project state parent escapes root: {relative}")


def safe_receipt_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or "\\" in value
        or ":" in value
        or "\x00" in value
    ):
        raise ConfigurationError("unsafe configuration receipt path")
    return path


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_configuration(value: Any) -> dict[str, Any]:
    errors: list[str] = []
    missing_decisions: list[str] = []
    if not isinstance(value, dict):
        return {
            "schema": "maios.configuration-validation.v2",
            "valid": False,
            "errors": ["configuration must be an object"],
            "missing_decisions": [],
        }
    if value.get("schema") != CONFIGURATION_SCHEMA:
        errors.append("unsupported configuration schema")
    if value.get("state_owner") != "setup/CONFIGURATION_STATE.json":
        errors.append("configuration state_owner mismatch")
    status = value.get("setup_status")
    if status not in {"pending", "configured", "stale"}:
        errors.append("unsupported setup_status")
    if value.get("effect_authority") != "none":
        errors.append("configuration cannot pre-grant material effect authority")
    checkpoint = value.get("checkpoint")
    if not isinstance(checkpoint, dict) or not isinstance(checkpoint.get("sequence"), int):
        errors.append("checkpoint.sequence must be an integer")
    operator = value.get("operator_relation")
    field = value.get("present_field")
    possibility = value.get("possibility_field")
    result = value.get("result")
    proof = value.get("first_proof")
    composition = value.get("faculty_composition")
    people = value.get("people_and_environment")
    data_boundary = value.get("data_boundary")
    for name, item in (
        ("operator_relation", operator),
        ("present_field", field),
        ("possibility_field", possibility),
        ("result", result),
        ("first_proof", proof),
        ("faculty_composition", composition),
        ("people_and_environment", people),
        ("data_boundary", data_boundary),
    ):
        if not isinstance(item, dict):
            errors.append(f"{name} must be an object")

    if status == "configured" and not errors:
        if not _nonempty(operator.get("current_intent")):
            missing_decisions.append("operator_relation.current_intent")
        if not _nonempty(operator.get("point_of_view")):
            missing_decisions.append("operator_relation.point_of_view")
        if operator.get("direction_status") not in {"selected", "open_reviewed"}:
            missing_decisions.append("operator_relation.direction_status")
        if not _nonempty(result.get("current")):
            missing_decisions.append("result.current")
        if not _nonempty(result.get("beneficiary")):
            missing_decisions.append("result.beneficiary")
        if not _nonempty(result.get("smallest_deliverable")):
            missing_decisions.append("result.smallest_deliverable")
        if result.get("owner_review") != "accepted":
            missing_decisions.append("result.owner_review=accepted")
        if not _nonempty(proof.get("statement")):
            missing_decisions.append("first_proof.statement")
        if not _nonempty(proof.get("falsifiable_test")):
            missing_decisions.append("first_proof.falsifiable_test")
        if not _nonempty(proof.get("reviewer")):
            missing_decisions.append("first_proof.reviewer")
        if proof.get("result") not in {
            "unverified",
            "verified_improvement",
            "no_change",
            "regression",
            "tradeoff",
        }:
            missing_decisions.append("first_proof.result")
        if not _nonempty(value.get("current_next")):
            missing_decisions.append("current_next")
        if data_boundary.get("provider_consent") not in {
            "none",
            "explicit_bounded",
        }:
            missing_decisions.append("data_boundary.provider_consent")
    if status == "configured" and missing_decisions:
        errors.append("configured state has missing consequential decisions")
    return {
        "schema": "maios.configuration-validation.v2",
        "valid": not errors,
        "errors": errors,
        "missing_decisions": missing_decisions,
        "configuration_sha256": digest(value) if not errors else None,
        "handoff_ready": status == "configured" and not missing_decisions and not errors,
        "claim_boundary": "valid accepted state does not prove external action or behavioral outcome",
    }


def current_configuration(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = configuration_path(root)
    ensure_project_local(root, path)
    value = read_json(path)
    validation = validate_configuration(value)
    if not validation["valid"]:
        raise ConfigurationError("invalid current configuration: " + "; ".join(validation["errors"]))
    return value


def operating_context_relation(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    """Expose the derived operating relation without making it a state owner."""

    root = root.resolve()
    path = root / ".maios" / "context" / "OPERATING_CONTEXT.json"
    ensure_project_local(root, path)
    if not path.is_file():
        return {
            "projection": ".maios/context/OPERATING_CONTEXT.json",
            "status": "not_yet_observed",
            "context_sha256": None,
            "operating_state_sha256": None,
            "freshness": None,
            "eligible_actions": [],
            "blocked_actions": [],
            "authority_ceiling": state.get("effect_authority", "none"),
            "uncertainty_count": len(
                state.get("present_field", {}).get("unknowns", [])
            ),
        }
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema") != "maios.operating-context.v1":
        raise ConfigurationError("unsupported operating context projection")
    represented_configuration = value.get("input_digests", {}).get("configuration")
    status = (
        "current"
        if represented_configuration == digest(state)
        else "stale_after_configuration_change"
    )
    return {
        "projection": ".maios/context/OPERATING_CONTEXT.json",
        "status": status,
        "context_sha256": value.get("context_sha256"),
        "operating_state_sha256": value.get("operating_state_sha256"),
        "freshness": value.get("freshness"),
        "eligible_actions": value.get("eligible_actions", []),
        "blocked_actions": value.get("blocked_actions", []),
        "authority_ceiling": value.get("authority_ceiling"),
        "uncertainty_count": len(value.get("uncertainty", [])),
    }


def context_capsule(root: Path, state: dict[str, Any]) -> dict[str, Any]:
    root = root.resolve()
    host_state_path = root / ".maios" / "state" / "HOST_STATE.json"
    ensure_project_local(root, host_state_path)
    host = read_json(host_state_path) if host_state_path.is_file() else {}
    present = state["present_field"]
    people = state["people_and_environment"]
    result = state["result"]
    operating_relation = operating_context_relation(root, state)
    return {
        "schema": "maios.context-capsule.v2",
        "route": "self_configuring",
        "revision": state["checkpoint"]["sequence"],
        "configuration_sha256": digest(state),
        "status": "accepted" if state["setup_status"] == "configured" else "provisional",
        "intent": state["operator_relation"],
        "authorized_sources": people.get("sources", []),
        "operational_dynamics": {
            "facts": present.get("facts", []),
            "evidence": present.get("evidence", []),
            "inferences": present.get("inferences", []),
            "hypotheses": present.get("hypotheses", []),
            "contradictions": present.get("contradictions", []),
        },
        "roles": {
            "users": people.get("users", []),
            "reviewers": people.get("reviewers", []),
            "human_responsibilities": people.get("human_responsibilities", []),
        },
        "boundaries": {
            "constraints": people.get("constraints", []),
            "effect_authority": state.get("effect_authority"),
            "data_boundary": state.get("data_boundary"),
        },
        "host": {
            "selected_adapter": host.get("selected_adapter"),
            "observed_capabilities": host.get("observed_capabilities", []),
            "unverified_capabilities": host.get("unverified_capabilities", []),
        },
        "operating_relation": operating_relation,
        "delivery": {
            "result": result.get("current"),
            "beneficiary": result.get("beneficiary"),
            "value_mechanism": result.get("value_mechanism"),
            "smallest_deliverable": result.get("smallest_deliverable"),
        },
        "requested_faculties": state["faculty_composition"].get("selected", []),
        "unknowns": present.get("unknowns", []),
        "retained_unknowns": present.get("retained_unknowns", []),
        "review": {
            "owner_review": result.get("owner_review"),
            "first_proof_reviewer": state["first_proof"].get("reviewer"),
        },
    }


def setup_spec(state: dict[str, Any], capsule: dict[str, Any]) -> dict[str, Any]:
    validation = validate_configuration(state)
    return {
        "schema": "maios.setup-spec.v2",
        "route": "self_configuring",
        "configuration_sha256": digest(state),
        "context_capsule_sha256": digest(capsule),
        "operating_context": {
            "status": capsule["operating_relation"]["status"],
            "context_sha256": capsule["operating_relation"]["context_sha256"],
            "authority_ceiling": capsule["operating_relation"][
                "authority_ceiling"
            ],
        },
        "status": "accepted" if validation["handoff_ready"] else "incomplete",
        "missing_decisions": validation["missing_decisions"],
        "project_result": state["result"],
        "first_proof": state["first_proof"],
        "faculty_composition": state["faculty_composition"],
        "current_next": state.get("current_next"),
        "effect_authority": "none",
        "form_state_imported": False,
    }


def current_state_markdown(state: dict[str, Any]) -> str:
    result = state["result"]
    lines = [
        "# Project current state",
        "",
        f"setup_status: {state['setup_status']}",
        f"revision: {state['checkpoint']['sequence']}",
        f"living_intent: {state['operator_relation'].get('current_intent') or 'pending'}",
        f"current_result: {result.get('current') or 'pending'}",
        f"owner_review: {result.get('owner_review') or 'pending'}",
        f"effect_authority: {state.get('effect_authority')}",
        f"current_next: {state.get('current_next') or 'pending'}",
        "",
        "source_of_truth: setup/CONFIGURATION_STATE.json",
        "context_capsule: .maios/context/CONTEXT_CAPSULE.json",
        "setup_spec: .maios/context/SETUP_SPEC.json",
        "operating_context: .maios/context/OPERATING_CONTEXT.json",
    ]
    return "\n".join(lines) + "\n"


def project_brief_markdown(state: dict[str, Any]) -> str:
    result = state["result"]
    proof = state["first_proof"]
    return "\n".join(
        [
            "# Project brief",
            "",
            f"Intent: {state['operator_relation'].get('current_intent') or 'pending'}",
            f"Result: {result.get('current') or 'pending'}",
            f"Beneficiary: {result.get('beneficiary') or 'pending'}",
            f"Value mechanism: {result.get('value_mechanism') or 'pending'}",
            f"Smallest deliverable: {result.get('smallest_deliverable') or 'pending'}",
            f"First proof: {proof.get('statement') or 'pending'}",
            f"Falsifiable test: {proof.get('falsifiable_test') or 'pending'}",
            f"Current next: {state.get('current_next') or 'pending'}",
            "",
            "This is a projection of setup/CONFIGURATION_STATE.json, not a second state owner.",
        ]
    ) + "\n"


def project_state(root: Path, state: dict[str, Any]) -> dict[str, str]:
    root = root.resolve()
    for path in (
        root / ".maios" / "context" / "CONTEXT_CAPSULE.json",
        root / ".maios" / "context" / "SETUP_SPEC.json",
        root / "project" / "CURRENT_STATE.md",
        root / "project" / "PROJECT_BRIEF.md",
    ):
        ensure_project_local(root, path)
    capsule = context_capsule(root, state)
    spec = setup_spec(state, capsule)
    write_json_atomic(root / ".maios" / "context" / "CONTEXT_CAPSULE.json", capsule)
    write_json_atomic(root / ".maios" / "context" / "SETUP_SPEC.json", spec)
    write_text_atomic(root / "project" / "CURRENT_STATE.md", current_state_markdown(state))
    write_text_atomic(root / "project" / "PROJECT_BRIEF.md", project_brief_markdown(state))
    return {
        "context_capsule_sha256": digest(capsule),
        "setup_spec_sha256": digest(spec),
    }


def configuration_status(root: Path) -> dict[str, Any]:
    root = root.resolve()
    state = current_configuration(root)
    validation = validate_configuration(state)
    capsule_path = root / ".maios" / "context" / "CONTEXT_CAPSULE.json"
    spec_path = root / ".maios" / "context" / "SETUP_SPEC.json"
    expected_capsule = context_capsule(root, state)
    expected_spec = setup_spec(state, expected_capsule)
    return {
        "schema": "maios.configuration-status.v2",
        "setup_status": state["setup_status"],
        "revision": state["checkpoint"]["sequence"],
        "configuration_sha256": digest(state),
        "valid": validation["valid"],
        "handoff_ready": validation["handoff_ready"],
        "missing_decisions": validation["missing_decisions"],
        "context_projection": (
            "current"
            if capsule_path.is_file() and read_json(capsule_path) == expected_capsule
            else "missing_or_stale"
        ),
        "setup_spec_projection": (
            "current"
            if spec_path.is_file() and read_json(spec_path) == expected_spec
            else "missing_or_stale"
        ),
    }


def apply_configuration(
    root: Path, candidate: Any, expected_state_sha256: str
) -> dict[str, Any]:
    root = root.resolve()
    validation = validate_configuration(candidate)
    if not validation["valid"]:
        raise ConfigurationError("invalid candidate: " + "; ".join(validation["errors"]))
    current = current_configuration(root)
    before_sha256 = digest(current)
    if expected_state_sha256 != before_sha256:
        raise ConfigurationError("configuration changed after review; re-read and re-evaluate")
    after_sha256 = digest(candidate)
    if after_sha256 != before_sha256:
        expected_sequence = int(current["checkpoint"]["sequence"]) + 1
        if candidate["checkpoint"]["sequence"] != expected_sequence:
            raise ConfigurationError(
                f"candidate checkpoint sequence must be {expected_sequence}"
            )
        backup = (
            root
            / ".maios"
            / "backups"
            / "configuration"
            / after_sha256
            / "CONFIGURATION_STATE.json"
        )
        ensure_project_local(root, backup)
        if backup.exists() and read_json(backup) != current:
            raise ConfigurationError("configuration backup path contains different bytes")
        if not backup.exists():
            write_json_atomic(backup, current)
        ensure_project_local(root, configuration_path(root))
        write_json_atomic(configuration_path(root), candidate)
        status = "applied"
    else:
        status = "idempotent"

    projections = project_state(root, candidate)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "status": status,
        "before_state_sha256": before_sha256,
        "after_state_sha256": after_sha256,
        "revision": candidate["checkpoint"]["sequence"],
        "backup_path": (
            f".maios/backups/configuration/{after_sha256}/CONFIGURATION_STATE.json"
            if after_sha256 != before_sha256
            else None
        ),
        "projections": projections,
        "global_writes": [],
        "external_effect_claimed": False,
    }
    receipt_path = root / ".maios" / "receipts" / "configuration" / "CURRENT.json"
    ensure_project_local(root, receipt_path)
    write_json_atomic(receipt_path, receipt)
    return receipt


def recover_configuration(root: Path, receipt: Any) -> dict[str, Any]:
    root = root.resolve()
    if not isinstance(receipt, dict) or receipt.get("schema") != RECEIPT_SCHEMA:
        raise ConfigurationError("unsupported configuration receipt")
    backup_rel = receipt.get("backup_path")
    if not isinstance(backup_rel, str) or not backup_rel.startswith(
        ".maios/backups/configuration/"
    ):
        raise ConfigurationError("receipt has no recoverable backup")
    current = current_configuration(root)
    if digest(current) != receipt.get("after_state_sha256"):
        raise ConfigurationError("current configuration evolved after the receipt")
    backup_parts = safe_receipt_relative(backup_rel)
    if backup_parts.parts[:3] != (".maios", "backups", "configuration"):
        raise ConfigurationError("configuration backup is outside its owner directory")
    backup = root.joinpath(*backup_parts.parts)
    ensure_project_local(root, backup)
    prior = read_json(backup)
    if digest(prior) != receipt.get("before_state_sha256"):
        raise ConfigurationError("configuration backup digest mismatch")
    ensure_project_local(root, configuration_path(root))
    write_json_atomic(configuration_path(root), prior)
    projections = project_state(root, prior)
    result = {
        "schema": RECOVERY_SCHEMA,
        "status": "recovered",
        "from_state_sha256": receipt["after_state_sha256"],
        "to_state_sha256": receipt["before_state_sha256"],
        "projections": projections,
        "global_writes": [],
    }
    recovery_path = root / ".maios" / "receipts" / "configuration" / "RECOVERY.json"
    ensure_project_local(root, recovery_path)
    write_json_atomic(recovery_path, result)
    return result
