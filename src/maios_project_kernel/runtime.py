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
    from . import filesystem as filesystem_engine
except ImportError:  # generated runtime and installer carry the same source
    import maios_filesystem as filesystem_engine  # type: ignore[no-redef]

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
SOURCE_MANIFEST_SCHEMA = "maios.source-manifest.v2"
AUTONOMOUS_ENTRY_CONTRACT_SCHEMA = "maios.autonomous-entry-contract.v1"
AUTONOMOUS_ENTRY_CONTRACT_VERSION = "1.0.0"
PRODUCT_NAME = "MAIOS Project Kernel"
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
    filesystem_engine.write_json_atomic(path, value)


def project_root(explicit: Path | None = None) -> Path:
    if explicit:
        return explicit.resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".maios" / "kernel" / "FACULTY_FIELD.json").is_file():
            project_local_file(candidate, candidate / ".maios/kernel/FACULTY_FIELD.json")
            return candidate
    raise ValueError("MAIOS project root not found")


def project_local_file(root: Path, path: Path) -> Path:
    try:
        return configuration_engine.project_local_file(root.resolve(), path)
    except configuration_engine.ConfigurationError as exc:
        raise ValueError(str(exc)) from exc


def validate_project(root: Path) -> dict[str, Any]:
    root = root.resolve()

    def read_json(path: Path) -> Any:
        return configuration_engine.read_json(project_local_file(root, path))

    required = [
        "START_HERE.md",
        "AGENTS.md",
        "maios.py",
        ".maios/kernel/SYSTEM_KERNEL.md",
        ".maios/kernel/FOUNDING_RELATIONS.md",
        ".maios/kernel/KNOWLEDGE_CONTINUUM.md",
        ".maios/kernel/UPDATE_CONTINUITY.md",
        ".maios/kernel/FACULTY_FIELD.json",
        ".maios/kernel/COMPOSITION_PROTOCOL.md",
        ".maios/kernel/COMPETENCE_CULTIVATION_PROTOCOL.md",
        ".maios/kernel/EVOLUTION_CONTRACT.json",
        ".maios/kernel/PROJECT_KERNEL_FAMILY_CONTRACT.json",
        ".maios/kernel/AUTONOMOUS_ENTRY_CONTRACT.json",
        ".maios/kernel/PROJECT_ENTITY_PROFILE.json",
        ".maios/SOURCE_MANIFEST.json",
        ".maios/config/HOST_ADAPTERS.json",
        ".maios/competences/INDEX.json",
        ".maios/runtime/host.py",
        ".maios/runtime/maios_filesystem.py",
        ".maios/installer/maios_filesystem.py",
        ".maios/runtime/operating.py",
        ".maios/schemas/RESULTANT_READBACK.schema.json",
        ".maios/state/OPERATING_STATE.json",
        ".maios/state/HOST_STATE.json",
        "setup/CONFIGURATION_STATE.json",
        "project/CURRENT_STATE.md",
        "skills/maios-project-system/SKILL.md",
        "skills/maios-start-new-project/SKILL.md",
        "skills/maios-start-existing-project/SKILL.md",
        "skills/maios-project-context/SKILL.md",
        "skills/maios-project-competence-formation/SKILL.md",
        "skills/maios-project-host-adaptation/SKILL.md",
    ]
    missing = [relative for relative in required if not (root / relative).is_file()]
    errors: list[str] = []
    unsafe = []
    for relative in required:
        if relative not in missing:
            try:
                project_local_file(root, root / relative)
            except ValueError:
                unsafe.append(relative)
                errors.append("unsafe project organ: " + relative)
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
    configuration_state_readable = True
    try:
        state = configuration_engine.current_configuration(root)
    except Exception as exc:
        configuration_state_readable = False
        errors.append(f"invalid configuration state: {exc}")
    source_error_start = len(errors)
    source_manifest: dict[str, Any] = {}
    try:
        source_manifest = read_json(root / ".maios" / "SOURCE_MANIFEST.json")
        if source_manifest.get("schema") != SOURCE_MANIFEST_SCHEMA:
            errors.append("unsupported source manifest")
        if source_manifest.get("product") != PRODUCT_NAME:
            errors.append("source manifest product mismatch")
        if not isinstance(source_manifest.get("version"), str) or not source_manifest.get(
            "version"
        ):
            errors.append("source manifest has no product version")
    except Exception as exc:
        errors.append(f"invalid source manifest: {exc}")
    family: dict[str, Any] = {}
    try:
        family = read_json(
            root / ".maios" / "kernel" / "PROJECT_KERNEL_FAMILY_CONTRACT.json"
        )
        if family.get("schema") != "maios.project-kernel-family-contract.v1":
            errors.append("unsupported Project Kernel family contract")
        if not isinstance(family.get("family_version"), str):
            errors.append("Project Kernel family contract has no version")
    except Exception as exc:
        errors.append(f"invalid Project Kernel family contract: {exc}")
    autonomous_entry: dict[str, Any] = {}
    try:
        autonomous_entry = read_json(
            root / ".maios" / "kernel" / "AUTONOMOUS_ENTRY_CONTRACT.json"
        )
        family_relation = autonomous_entry.get("family_relation", {})
        family_lane = family.get("lanes", {}).get("autonomous", {})
        entry_policy = autonomous_entry.get("entry_policy", {})
        if autonomous_entry.get("schema") != AUTONOMOUS_ENTRY_CONTRACT_SCHEMA:
            errors.append("unsupported autonomous entry contract")
        if (
            autonomous_entry.get("contract_version")
            != AUTONOMOUS_ENTRY_CONTRACT_VERSION
        ):
            errors.append("unsupported autonomous entry contract version")
        if autonomous_entry.get("product") != PRODUCT_NAME:
            errors.append("autonomous entry contract product mismatch")
        if autonomous_entry.get("product_version") != source_manifest.get("version"):
            errors.append("autonomous entry contract product version mismatch")
        if autonomous_entry.get("owner") != "maios-project-kernel":
            errors.append("autonomous entry contract owner mismatch")
        if autonomous_entry.get("effect_authority") != "none":
            errors.append("autonomous entry contract grants effect authority")
        if autonomous_entry.get("contains_form_state") is not False:
            errors.append("autonomous entry contract contains Form state")
        if (
            family_relation.get("lane") != "autonomous"
            or family_relation.get("family_version") != family.get("family_version")
            or family_relation.get("configuration_state")
            != family_lane.get("configuration_state")
            or family_relation.get("startup_context_requirement")
            != family_lane.get("startup_context_requirement")
            or entry_policy.get("startup_interview")
            != family_lane.get("startup_interview")
        ):
            errors.append("autonomous entry contract lost its family relation")
        if entry_policy.get("startup_interview") != "discretionary":
            errors.append("autonomous entry policy must remain discretionary")
    except Exception as exc:
        errors.append(f"invalid autonomous entry contract: {exc}")
    try:
        entity = read_json(root / ".maios" / "kernel" / "PROJECT_ENTITY_PROFILE.json")
        entry_contract = family.get("entry_profile", {})
        autonomous = family.get("lanes", {}).get("autonomous", {})
        autonomous_policy = autonomous_entry.get("entry_policy", {})
        if entity.get("schema") != entry_contract.get("schema"):
            errors.append("Project Entity Profile schema mismatch")
        if entity.get("version") != family.get("family_version"):
            errors.append("Project Entity Profile family version mismatch")
        if entity.get("competence_field", {}).get(
            "selection_model"
        ) != entry_contract.get("selection_model"):
            errors.append("Project Entity Profile selection model mismatch")
        if entity.get("role", {}).get(
            "startup_interview"
        ) != autonomous_policy.get("startup_interview"):
            errors.append("Project Entity Profile startup relation mismatch")
        if entity.get("configuration_state") != autonomous.get("configuration_state"):
            errors.append("Project Entity Profile configuration state mismatch")
        if any(field in entity for field in entry_contract.get("forbidden_fields", [])):
            errors.append("Project Entity Profile contains a forbidden closed field")
        for catalog in entity.get("source_catalogs", []):
            installed_path = catalog.get("installed_registry_path")
            if (
                not isinstance(installed_path, str)
                or PurePosixPath(installed_path).is_absolute()
                or ".." in PurePosixPath(installed_path).parts
                or not root.joinpath(*PurePosixPath(installed_path).parts).is_file()
            ):
                errors.append("Project Entity Profile contains an unresolved installed catalog")
    except Exception as exc:
        errors.append(f"invalid Project Entity Profile: {exc}")
    try:
        for target in registry.get("families", []):
            target_id = target.get("id")
            entry = target.get("entry")
            if not isinstance(entry, str):
                errors.append(f"faculty has no entry: {target_id}")
                continue
            path_text, separator, anchor = entry.partition("#")
            entry_path = PurePosixPath(path_text)
            if (
                entry_path.is_absolute()
                or ".." in entry_path.parts
                or not project_local_file(root, root.joinpath(*entry_path.parts)).is_file()
            ):
                errors.append(f"faculty entry is missing: {target_id}")
                continue
            if separator:
                headings = []
                for line in root.joinpath(*entry_path.parts).read_text(
                    encoding="utf-8"
                ).splitlines():
                    if line.startswith("#"):
                        heading = line.lstrip("#").strip().lower()
                        heading = re.sub(r"[^\w\s-]", "", heading)
                        headings.append(
                            re.sub(r"[\s-]+", "-", heading).strip("-")
                        )
                if anchor not in headings:
                    errors.append(
                        f"faculty anchor is missing: {target_id}"
                    )
    except Exception as exc:
        errors.append(f"invalid faculty entry: {exc}")
    try:
        evolution = read_json(root / ".maios" / "kernel" / "EVOLUTION_CONTRACT.json")
        if evolution.get("schema") != "maios.project-evolution-contract.v3":
            errors.append("unsupported evolution contract")
        if evolution.get("effect_authority_default") != "none":
            errors.append("evolution contract grants effect authority")
        if evolution.get("semantic_owner") != (
            "skills/maios-project-system/SKILL.md"
        ):
            errors.append("evolution contract semantic owner mismatch")
        if evolution.get("competence_state_owner") != ".maios/competences/INDEX.json":
            errors.append("evolution contract competence owner mismatch")
    except Exception as exc:
        errors.append(f"invalid evolution contract: {exc}")
    source_bound = len(errors) == source_error_start and not unsafe
    host_readable = True
    try:
        host_engine.read_host_catalog(root)
        host_engine.read_host_state(root)
    except Exception as exc:
        host_readable = False
        errors.append(f"invalid host state or catalogue: {exc}")
    operating_state_readable = True
    try:
        operating_engine.read_operating_state(root)
    except Exception as exc:
        operating_state_readable = False
        errors.append(f"invalid operating state: {exc}")
    try:
        coherence = operating_engine.continuum_status(root)
        errors.extend(coherence["errors"])
    except Exception as exc:
        errors.append(f"continuum recovery state cannot be read: {exc}")
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
        "validation_levels": {
            "structure_present": not missing,
            "content_valid": not errors,
            "source_bound": source_bound,
            "host_readable": host_readable,
            "configuration_state_readable": configuration_state_readable,
            "operating_state_readable": operating_state_readable,
            "behavior": "unverified",
        },
        "family_count": len(registry.get("families", [])),
        "setup_status": state.get("setup_status"),
    }


def competence_index_path(root: Path) -> Path:
    return root / ".maios" / "competences" / "INDEX.json"


def ensure_project_local(root: Path, path: Path) -> None:
    try:
        filesystem_engine.ensure_local(root, path)
    except (ValueError, OSError) as exc:
        raise ValueError(str(exc)) from exc



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
    errors = configuration_engine.owner_state_receipt_errors(root, "competence", index)
    pending = configuration_engine.pending_transitions(root)
    return {
        "valid": not errors and not pending, "recovery_required": bool(errors or pending),
        "errors": errors, "pending_journals": pending,
        "schema": "maios.competence-status.v2",
        "index_sha256": digest(index),
        "revision": index.get("revision"),
        "represented": index.get("represented", {}),
        "active": index.get("active", {}),
        "history_count": len(index.get("history", [])),
        "retained_unknowns": index.get("retained_unknowns", []),
        "claim_boundary": "an indexed entry is available knowledge; actual use and assimilation are separate",
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
    for field in ("sequence", "event_digest"):
        if field in delta:
            errors.append(f"{field} is reserved for recorded event metadata")
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
    if isinstance(event_id, str) and not configuration_engine.valid_event_id(event_id):
        errors.append("event_id is unsafe or reserved for transaction control")
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
        if observed.get("classification") is not None and observed.get("classification") not in RESULT_CLASSIFICATIONS:
            errors.append("unsupported observed delta classification")
        if not isinstance(observed.get("description"), str) or not observed["description"].strip():
            errors.append("observed_delta.description must be non-empty")
    review = delta.get("review")
    if review is not None:
        if not isinstance(review, dict) or review.get("status") not in {"pending", "accepted", "rejected"}:
            errors.append("optional review must describe a pending, accepted or rejected review")
    if isinstance(observed, dict) and observed.get("classification") not in {None, "unverified"} and not delta.get("evidence_refs"):
        errors.append("a classified observed delta requires evidence")
    return {
        "schema": "maios.competence-delta-validation.v2",
        "valid": not errors,
        "errors": errors,
        "event_digest": digest(delta) if not errors else None,
        "claim_boundary": "shape validity is not observed improvement or assimilation",
    }


def admit_competence_delta(
    root: Path, delta: Any, expected_index_sha256: str
) -> dict[str, Any]:
    root = root.resolve()
    configuration_engine.require_no_pending_transition(root)
    validation = validate_competence_delta(delta)
    if not validation["valid"]:
        raise ValueError("invalid competence delta: " + "; ".join(validation["errors"]))
    index = read_competence_index(root)
    coherence = configuration_engine.owner_state_receipt_errors(root, "competence", index)
    if coherence:
        raise ValueError("; ".join(coherence))
    before_sha256 = digest(index)
    if expected_index_sha256 != before_sha256:
        raise ValueError("competence index changed before recording; re-read the current index")

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

    classification = delta["observed_delta"].get("classification")
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
    receipt = {
        "schema": "maios.competence-admission.v2",
        "status": "admitted",
        "event_id": event_id,
        "event_digest": event_digest,
        "before_index_sha256": before_sha256,
        "after_index_sha256": after_sha256,
        "revision": updated["revision"],
        "global_writes": [],
        "claim_boundary": "registration preserves local discovery and revision history; later behavior supplies evidence of improvement",
    }
    receipt_path = root / ".maios" / "receipts" / "competence" / f"{event_id}.json"
    ensure_project_local(root, receipt_path)
    if receipt_path.exists() or filesystem_engine.is_link(receipt_path):
        raise ValueError("terminal receipt path already exists outside recorded history")
    outputs = (index_path.relative_to(root).as_posix(), receipt_path.relative_to(root).as_posix())
    with configuration_engine.state_transaction(root, "competence", outputs):
        write_json_atomic(index_path, updated)
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
    contact_status = sub.add_parser("source-contact-status")
    contact_status.add_argument("--at")
    contact_record = sub.add_parser("record-source-contact")
    contact_record.add_argument("--observation", type=Path, required=True)
    contact_record.add_argument("--expected-state-sha256", required=True)
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
    learning_parser = sub.add_parser("learning-status")
    learning_parser.add_argument("--include-cold", action="store_true")
    knowledge_parser = sub.add_parser("knowledge-status")
    knowledge_parser.add_argument("--path", dest="paths", action="append", required=True)
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
        elif args.command == "source-contact-status":
            result = configuration_engine.source_contact_status(root, args.at)
        elif args.command == "record-source-contact":
            result = configuration_engine.record_source_contact(root, read_json(args.observation), args.expected_state_sha256)
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
        elif args.command == "knowledge-status":
            result = operating_engine.knowledge_status(root, args.paths)
        elif args.command in {"learning-status", "competence-candidates"}:
            result = operating_engine.learning_status(root, include_cold=getattr(args, "include_cold", False))
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
                root, read_json(args.attestation)
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
