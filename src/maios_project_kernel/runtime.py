#!/usr/bin/env python3
"""Canonical runtime for a situated MAIOS faculty field."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

try:
    from . import configuration as configuration_engine
    from . import host as host_engine
    from . import operating as operating_engine
except ImportError:  # installed runtime is loaded as a project-local module
    import configuration as configuration_engine  # type: ignore[no-redef]
    import host as host_engine  # type: ignore[no-redef]
    import operating as operating_engine  # type: ignore[no-redef]


COMPETENCE_INDEX_SCHEMA = "maios.competence-index.v2"
COMPETENCE_DELTA_SCHEMA = "maios.competence-delta.v2"
RESULT_CLASSIFICATIONS = {
    "verified_improvement",
    "no_change",
    "regression",
    "tradeoff",
    "unverified",
}
COMPETENCE_DISPOSITIONS = {"retain", "revise", "supersede", "retire", "evaluate"}
SAFE_EVENT_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.maios-tmp-{os.getpid()}")
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    try:
        temporary.write_text(data, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def project_root(explicit: Path | None = None) -> Path:
    if explicit:
        return explicit.resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".maios" / "kernel" / "FACULTY_FIELD.json").is_file():
            return candidate
    raise ValueError("MAIOS project root not found")


def validate_project(root: Path) -> dict[str, Any]:
    required = [
        "START_HERE.md",
        "AGENTS.md",
        "maios.py",
        ".maios/kernel/SYSTEM_KERNEL.md",
        ".maios/kernel/FACULTY_FIELD.json",
        ".maios/kernel/COMPOSITION_PROTOCOL.md",
        ".maios/kernel/COMPETENCE_CULTIVATION_PROTOCOL.md",
        ".maios/kernel/EVOLUTION_CONTRACT.json",
        ".maios/competences/INDEX.json",
        ".maios/runtime/operating.py",
        ".maios/schemas/RESULTANT_READBACK.schema.json",
        ".maios/state/OPERATING_STATE.json",
        "setup/CONFIGURATION_STATE.json",
        "project/CURRENT_STATE.md",
        "skills/maios-project-system/SKILL.md",
        "skills/maios-start-new-project/SKILL.md",
        "skills/maios-start-existing-project/SKILL.md",
        "skills/maios-project-context/SKILL.md",
    ]
    missing = [relative for relative in required if not (root / relative).is_file()]
    errors: list[str] = []
    registry: dict[str, Any] = {}
    state: dict[str, Any] = {}
    try:
        registry = read_json(root / ".maios" / "kernel" / "FACULTY_FIELD.json")
        if registry.get("open_world") is not True:
            errors.append("faculty field must remain open_world")
        ids = [item.get("id") for item in registry.get("families", [])]
        if None in ids or len(ids) != len(set(ids)):
            errors.append("faculty family ids must be present and unique")
    except Exception as exc:
        errors.append(f"invalid faculty field: {exc}")
    try:
        state = read_json(root / "setup" / "CONFIGURATION_STATE.json")
        if state.get("effect_authority") != "none":
            errors.append("initial effect_authority must be none")
        if state.get("state_owner") != "setup/CONFIGURATION_STATE.json":
            errors.append("configuration state owner mismatch")
    except Exception as exc:
        errors.append(f"invalid configuration state: {exc}")
    try:
        index = read_competence_index(root)
        if not isinstance(index.get("represented"), dict):
            errors.append("competence index represented must be an object")
        if not isinstance(index.get("active"), dict):
            errors.append("competence index active must be an object")
        if not isinstance(index.get("history"), list):
            errors.append("competence index history must be a list")
        for collection_name in ("represented", "active"):
            collection = index.get(collection_name, {})
            if not isinstance(collection, dict):
                continue
            for competence_id, competence in collection.items():
                if not isinstance(competence, dict):
                    errors.append(
                        f"competence index {collection_name}.{competence_id} must be an object"
                    )
                    continue
                if not _nonempty_strings(competence.get("activation_relations")):
                    errors.append(
                        f"competence index {collection_name}.{competence_id} activation_relations must not be empty"
                    )
                try:
                    competence_knowledge_path(root, competence.get("knowledge_entry"))
                except ValueError as exc:
                    errors.append(
                        f"competence index {collection_name}.{competence_id}: {exc}"
                    )
    except Exception as exc:
        errors.append(f"invalid competence index: {exc}")
    return {
        "schema": "maios.project-validation.v2",
        "root": str(root),
        "valid": not missing and not errors,
        "missing": missing,
        "errors": errors,
        "family_count": len(registry.get("families", [])),
        "setup_status": state.get("setup_status"),
    }


def competence_index_path(root: Path) -> Path:
    return root / ".maios" / "competences" / "INDEX.json"


def ensure_project_local(root: Path, path: Path) -> None:
    root = root.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path is outside project root: {path}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise ValueError(f"project state path contains a symlink: {relative}")
    if not path.parent.resolve().is_relative_to(root):
        raise ValueError(f"project state parent escapes root: {relative}")


def competence_knowledge_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("knowledge_entry must be a non-empty project-relative path")
    if "\\" in value:
        raise ValueError("knowledge_entry must use POSIX separators")
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or ".." in relative.parts
        or (relative.parts and relative.parts[0].endswith(":"))
    ):
        raise ValueError("knowledge_entry must remain inside the project")
    path = root.resolve().joinpath(*relative.parts)
    ensure_project_local(root, path)
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"knowledge_entry is missing or unsafe: {value}")
    return path


def read_competence_index(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = competence_index_path(root)
    ensure_project_local(root, path)
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema") != COMPETENCE_INDEX_SCHEMA:
        raise ValueError("unsupported competence index schema")
    return value


def competence_status(root: Path) -> dict[str, Any]:
    index = read_competence_index(root)
    return {
        "schema": "maios.competence-status.v2",
        "index_sha256": digest(index),
        "revision": index.get("revision"),
        "represented": index.get("represented", {}),
        "active": index.get("active", {}),
        "history_count": len(index.get("history", [])),
        "retained_unknowns": index.get("retained_unknowns", []),
        "claim_boundary": "indexed or reviewed is not behavioral activation or maintained assimilation",
    }


def _nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value
    )


def validate_competence_delta(delta: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(delta, dict):
        return {
            "schema": "maios.competence-delta-validation.v2",
            "valid": False,
            "errors": ["delta must be an object"],
        }
    if delta.get("schema") != COMPETENCE_DELTA_SCHEMA:
        errors.append("unsupported competence delta schema")
    for field in (
        "event_id",
        "competence_id",
        "work_relation",
        "expected_delta",
        "invalidator",
        "reentry_condition",
    ):
        if not isinstance(delta.get(field), str) or not delta[field].strip():
            errors.append(f"{field} must be a non-empty string")
    event_id = delta.get("event_id")
    if isinstance(event_id, str) and not SAFE_EVENT_ID.fullmatch(event_id):
        errors.append("event_id contains unsafe characters")
    if delta.get("disposition") not in COMPETENCE_DISPOSITIONS:
        errors.append("unsupported competence disposition")
    if delta.get("disposition") in {"retain", "revise", "supersede"}:
        if not isinstance(delta.get("knowledge_entry"), str) or not delta[
            "knowledge_entry"
        ].strip():
            errors.append("knowledge_entry must be a non-empty string")
        if not _nonempty_strings(delta.get("activation_relations")):
            errors.append("activation_relations must contain at least one relation")
    if not _nonempty_strings(delta.get("source_refs")):
        errors.append("source_refs must contain at least one source")
    if not isinstance(delta.get("evidence_refs"), list) or not all(
        isinstance(item, str) and bool(item.strip()) for item in delta.get("evidence_refs", [])
    ):
        errors.append("evidence_refs must be a list of non-empty strings")
    observed = delta.get("observed_delta")
    if not isinstance(observed, dict):
        errors.append("observed_delta must be an object")
    else:
        if observed.get("classification") not in RESULT_CLASSIFICATIONS:
            errors.append("unsupported observed delta classification")
        if not isinstance(observed.get("description"), str) or not observed["description"].strip():
            errors.append("observed_delta.description must be non-empty")
    review = delta.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
    else:
        if review.get("status") not in {"pending", "accepted", "rejected"}:
            errors.append("unsupported review status")
        if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
            errors.append("review.reviewer must be non-empty")
        if review.get("reviewer_relation") not in {
            "operator",
            "owner",
            "independent_reviewer",
        }:
            errors.append("unsupported reviewer relation")
        if review.get("producer_is_reviewer") is not False:
            errors.append("the producing assistant cannot approve its own competence delta")
    return {
        "schema": "maios.competence-delta-validation.v2",
        "valid": not errors,
        "errors": errors,
        "event_digest": digest(delta) if not errors else None,
        "claim_boundary": "shape validity is not semantic review, improvement, or assimilation proof",
    }


def admit_competence_delta(
    root: Path, delta: Any, expected_index_sha256: str
) -> dict[str, Any]:
    root = root.resolve()
    validation = validate_competence_delta(delta)
    if not validation["valid"]:
        raise ValueError("invalid competence delta: " + "; ".join(validation["errors"]))
    if delta["review"]["status"] != "accepted":
        raise ValueError("only an explicitly accepted review can be admitted")

    index = read_competence_index(root)
    before_sha256 = digest(index)
    if expected_index_sha256 != before_sha256:
        raise ValueError("competence index changed after review; re-read and re-evaluate")

    history = list(index.get("history", []))
    event_id = delta["event_id"]
    event_digest = validation["event_digest"]
    for prior in history:
        if prior.get("event_id") == event_id:
            if prior.get("event_digest") != event_digest:
                raise ValueError("event_id already exists with different content")
            return {
                "schema": "maios.competence-admission.v2",
                "status": "idempotent",
                "event_id": event_id,
                "index_sha256": before_sha256,
            }

    competence_id = delta["competence_id"]
    active = dict(index.get("active", {}))
    current = active.get(competence_id)
    disposition = delta["disposition"]
    supersedes = delta.get("supersedes_event_id")
    if disposition == "retain" and current:
        raise ValueError("retain cannot replace an active competence; use revise or supersede")
    if disposition in {"revise", "supersede", "retire"}:
        if not current:
            raise ValueError(f"{disposition} requires an active competence")
        if supersedes != current.get("event_id"):
            raise ValueError("supersedes_event_id must identify the active competence event")

    classification = delta["observed_delta"]["classification"]
    activation_allowed = classification in {"verified_improvement", "tradeoff"}
    if disposition in {"retain", "revise", "supersede"} and not activation_allowed:
        raise ValueError("active competence requires verified_improvement or reviewed tradeoff")
    if disposition in {"retain", "revise", "supersede", "retire"} and not delta[
        "evidence_refs"
    ]:
        raise ValueError("a competence disposition that changes routing requires evidence")
    if disposition in {"retain", "revise", "supersede"}:
        competence_knowledge_path(root, delta["knowledge_entry"])

    admitted = dict(delta)
    admitted["event_digest"] = event_digest
    admitted["sequence"] = int(index.get("revision", 0)) + 1
    history.append(admitted)
    if disposition == "retire":
        active.pop(competence_id, None)
    elif disposition != "evaluate":
        active[competence_id] = {
            "event_id": event_id,
            "classification": classification,
            "work_relation": delta["work_relation"],
            "knowledge_entry": delta["knowledge_entry"],
            "activation_relations": delta["activation_relations"],
            "source_refs": delta["source_refs"],
            "expected_delta": delta["expected_delta"],
            "observed_delta": delta["observed_delta"],
            "evidence_refs": delta["evidence_refs"],
            "invalidator": delta["invalidator"],
            "reentry_condition": delta["reentry_condition"],
        }
    updated = dict(index)
    updated["revision"] = int(index.get("revision", 0)) + 1
    updated["active"] = active
    updated["history"] = history
    updated["last_event_id"] = event_id
    after_sha256 = digest(updated)
    index_path = competence_index_path(root)
    ensure_project_local(root, index_path)
    write_json_atomic(index_path, updated)

    receipt = {
        "schema": "maios.competence-admission.v2",
        "status": "admitted",
        "event_id": event_id,
        "event_digest": event_digest,
        "before_index_sha256": before_sha256,
        "after_index_sha256": after_sha256,
        "revision": updated["revision"],
        "global_writes": [],
        "claim_boundary": "admission records reviewed local state; later behavior is separate proof",
    }
    receipt_path = root / ".maios" / "receipts" / "competence" / f"{event_id}.json"
    ensure_project_local(root, receipt_path)
    write_json_atomic(receipt_path, receipt)
    return receipt


def compose(root: Path, circumstance: dict[str, Any]) -> dict[str, Any]:
    """Compatibility seam; the operating module owns composition semantics."""

    return operating_engine.compose(root, circumstance)


def validate_movement(root: Path, movement: dict[str, Any]) -> dict[str, Any]:
    """Compatibility seam; the operating module owns movement validation."""

    return operating_engine.validate_movement(root, movement)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Operate MAIOS Project Kernel state")
    result.add_argument("--project-root", type=Path)
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    compose_parser = sub.add_parser("compose")
    compose_parser.add_argument("--circumstance", type=Path, required=True)
    movement_parser = sub.add_parser("validate-movement")
    movement_parser.add_argument("--movement", type=Path, required=True)
    operating_parser = sub.add_parser("operating-status")
    operating_parser.add_argument("--circumstance", type=Path)
    resultant_parser = sub.add_parser("validate-resultant")
    resultant_parser.add_argument("--readback", type=Path, required=True)
    apply_resultant_parser = sub.add_parser("apply-resultant")
    apply_resultant_parser.add_argument("--readback", type=Path, required=True)
    apply_resultant_parser.add_argument("--expected-context-sha256", required=True)
    admit_resultant_parser = sub.add_parser("admit-resultant")
    admit_resultant_parser.add_argument("--readback", type=Path, required=True)
    admit_resultant_parser.add_argument("--expected-context-sha256", required=True)
    sub.add_parser("competence-status")
    sub.add_parser("learning-status")
    sub.add_parser("competence-candidates")
    delta_parser = sub.add_parser("validate-competence-delta")
    delta_parser.add_argument("--delta", type=Path, required=True)
    admit_parser = sub.add_parser("admit-competence-delta")
    admit_parser.add_argument("--delta", type=Path, required=True)
    admit_parser.add_argument("--expected-index-sha256", required=True)
    sub.add_parser("configuration-status")
    configuration_parser = sub.add_parser("validate-configuration")
    configuration_parser.add_argument("--candidate", type=Path, required=True)
    apply_configuration_parser = sub.add_parser("apply-configuration")
    apply_configuration_parser.add_argument("--candidate", type=Path, required=True)
    apply_configuration_parser.add_argument("--expected-state-sha256", required=True)
    recover_configuration_parser = sub.add_parser("recover-configuration")
    recover_configuration_parser.add_argument("--receipt", type=Path, required=True)
    sub.add_parser("host-status")
    host_attestation_parser = sub.add_parser("validate-host-attestation")
    host_attestation_parser.add_argument("--attestation", type=Path, required=True)
    admit_host_parser = sub.add_parser("admit-host-attestation")
    admit_host_parser.add_argument("--attestation", type=Path, required=True)
    admit_host_parser.add_argument("--expected-state-sha256", required=True)
    return result


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        root = project_root(args.project_root)
        if args.command == "status":
            result = validate_project(root)
        elif args.command == "compose":
            result = compose(root, read_json(args.circumstance))
        elif args.command == "validate-movement":
            result = validate_movement(root, read_json(args.movement))
        elif args.command == "operating-status":
            circumstance = (
                read_json(args.circumstance) if args.circumstance else None
            )
            result = operating_engine.operating_status(root, circumstance)
        elif args.command == "validate-resultant":
            result = operating_engine.validate_resultant_readback(
                root, read_json(args.readback)
            )
        elif args.command in {"apply-resultant", "admit-resultant"}:
            result = operating_engine.apply_resultant_readback(
                root,
                read_json(args.readback),
                args.expected_context_sha256,
            )
        elif args.command == "competence-status":
            result = competence_status(root)
        elif args.command in {"learning-status", "competence-candidates"}:
            result = operating_engine.learning_status(root)
        elif args.command == "validate-competence-delta":
            result = validate_competence_delta(read_json(args.delta))
        elif args.command == "admit-competence-delta":
            result = admit_competence_delta(
                root, read_json(args.delta), args.expected_index_sha256
            )
        elif args.command == "configuration-status":
            result = configuration_engine.configuration_status(root)
        elif args.command == "validate-configuration":
            result = configuration_engine.validate_configuration(
                read_json(args.candidate)
            )
        elif args.command == "apply-configuration":
            result = configuration_engine.apply_configuration(
                root,
                read_json(args.candidate),
                args.expected_state_sha256,
            )
        elif args.command == "recover-configuration":
            result = configuration_engine.recover_configuration(
                root, read_json(args.receipt)
            )
        elif args.command == "host-status":
            result = host_engine.host_status(root)
        elif args.command == "validate-host-attestation":
            result = host_engine.validate_host_attestation(
                read_json(args.attestation)
            )
        elif args.command == "admit-host-attestation":
            result = host_engine.admit_host_attestation(
                root,
                read_json(args.attestation),
                args.expected_state_sha256,
            )
        else:  # argparse prevents this; keep dispatch exhaustive.
            raise ValueError(f"unsupported command: {args.command}")
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result.get("valid", True) else 2
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ValueError,
        configuration_engine.ConfigurationError,
        host_engine.HostAttestationError,
        operating_engine.OperatingStateError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
