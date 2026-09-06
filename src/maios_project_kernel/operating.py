"""Autological operating relation and forward-resultant learning for MAIOS.

The module owns deterministic state, causal bookkeeping, validated transition
with per-file atomic replacement, and handled-failure rollback. It never
decides semantic relevance or grants external effects.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from . import configuration as configuration_engine
    from . import host as host_engine
except ImportError:  # installed runtime is loaded as project-local modules
    import configuration as configuration_engine  # type: ignore[no-redef]
    import host as host_engine  # type: ignore[no-redef]


OPERATING_STATE_SCHEMA = "maios.operating-state.v3"
OPERATING_CONTEXT_SCHEMA = "maios.operating-context.v1"
RESULTANT_READBACK_SCHEMA = "maios.resultant-readback.v3"
RESULTANT_TRANSITION_SCHEMA = "maios.resultant-transition.v3"
RESULT_CLASSIFICATIONS = {
    "verified_improvement",
    "no_change",
    "regression",
    "tradeoff",
    "unverified",
}
RESULT_STATUSES = {"completed", "partial", "blocked", "failed", "deferred"}
PREPROJECTION_STATUSES = {"preserved", "corrected", "noncollapse"}
EFFECT_STATES = {"none", "effect_unbound", "effect_bound"}
SAFE_EVENT_ID = re.compile(r"^[A-Za-z0-9._-]+$")
CAUSAL_MARGIN_FIELDS = (
    "operator_relation",
    "selected_object",
    "owner_surface",
    "last_faithful_resultant",
    "current_movement",
    "next_movement",
    "supersession_condition",
)
OPEN_FRONT_FIELDS = (
    "id",
    "title",
    "owner_surface",
    "status",
    "last_faithful_resultant",
    "current_movement",
    "next_movement",
    "reentry_condition",
    "supersession_condition",
)


class OperatingStateError(RuntimeError):
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
        raise OperatingStateError(f"cannot read valid JSON: {path}: {exc}") from exc


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


def ensure_project_local(root: Path, path: Path) -> None:
    root = root.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise OperatingStateError(f"path is outside project root: {path}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise OperatingStateError(
                f"operating state path contains a symlink: {relative}"
            )
    if not path.parent.resolve().is_relative_to(root):
        raise OperatingStateError(f"operating state parent escapes root: {relative}")


def operating_state_path(root: Path) -> Path:
    return root / ".maios" / "state" / "OPERATING_STATE.json"


def operating_context_path(root: Path) -> Path:
    return root / ".maios" / "context" / "OPERATING_CONTEXT.json"


def _validate_causal_margin(value: Any, errors: list[str], prefix: str) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    for field in CAUSAL_MARGIN_FIELDS:
        if not _nonempty(value.get(field)):
            errors.append(f"{prefix}.{field} must be non-empty")


def _validate_open_fronts(
    fronts: Any, focused_front_id: Any, errors: list[str], prefix: str
) -> set[str]:
    if not isinstance(fronts, list):
        errors.append(f"{prefix} must be a list")
        return set()
    seen: set[str] = set()
    for index, front in enumerate(fronts):
        item_prefix = f"{prefix}[{index}]"
        if not isinstance(front, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        for field in OPEN_FRONT_FIELDS:
            if not _nonempty(front.get(field)):
                errors.append(f"{item_prefix}.{field} must be non-empty")
        front_id = front.get("id")
        if _nonempty(front_id):
            if not SAFE_EVENT_ID.fullmatch(front_id):
                errors.append(f"{item_prefix}.id contains unsafe characters")
            if front_id in seen:
                errors.append(f"duplicate open front id: {front_id}")
            seen.add(front_id)
        source_refs = front.get("source_refs", [])
        if not isinstance(source_refs, list) or not all(
            _nonempty(source_ref) for source_ref in source_refs
        ):
            errors.append(f"{item_prefix}.source_refs must be a string list")
    if focused_front_id is not None:
        if not _nonempty(focused_front_id):
            errors.append("focused_front_id must be a non-empty string or null")
        elif focused_front_id not in seen:
            errors.append("focused_front_id must identify a preserved open front")
    return seen


def read_operating_state(root: Path) -> dict[str, Any]:
    root = root.resolve()
    path = operating_state_path(root)
    ensure_project_local(root, path)
    value = read_json(path)
    if not isinstance(value, dict) or value.get("schema") != OPERATING_STATE_SCHEMA:
        raise OperatingStateError("unsupported operating state schema")
    if not isinstance(value.get("revision"), int):
        raise OperatingStateError("operating state revision must be an integer")
    for field in ("last_input_digests", "history"):
        expected = dict if field == "last_input_digests" else list
        if not isinstance(value.get(field), expected):
            raise OperatingStateError(f"operating state {field} has invalid type")
    if not isinstance(value.get("learning_relations", []), list):
        raise OperatingStateError("operating state learning_relations has invalid type")
    state_errors: list[str] = []
    _validate_causal_margin(value.get("causal_margin"), state_errors, "causal_margin")
    _validate_open_fronts(
        value.get("open_fronts"),
        value.get("focused_front_id"),
        state_errors,
        "open_fronts",
    )
    if not isinstance(value.get("last_learning_relations"), list):
        state_errors.append("last_learning_relations must be a list")
    _validate_learning_state(value, state_errors)
    _validate_knowledge_refs(value.get("active_knowledge_refs"))
    if state_errors:
        raise OperatingStateError("invalid operating state: " + "; ".join(state_errors))
    return value


def _competence_index(root: Path) -> dict[str, Any]:
    value = read_json(configuration_engine.project_local_file(root, root / ".maios" / "competences" / "INDEX.json"))
    if not isinstance(value, dict) or value.get("schema") != "maios.competence-index.v2":
        raise OperatingStateError("unsupported competence index schema")
    return value


def _faculty_field(root: Path) -> dict[str, Any]:
    value = read_json(configuration_engine.project_local_file(root, root / ".maios" / "kernel" / "FACULTY_FIELD.json"))
    if not isinstance(value, dict) or value.get("open_world") is not True:
        raise OperatingStateError("faculty field must be an open object")
    return value


def _string_list(value: Any, field: str, *, require: bool = False) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and bool(item.strip()) for item in value
    ):
        raise OperatingStateError(f"{field} must be a list of non-empty strings")
    if require and not value:
        raise OperatingStateError(f"{field} must not be empty")
    return value


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _owner_identity(owner: Any) -> tuple[Any, ...]:
    return tuple(owner.get(key) if isinstance(owner, dict) else None for key in ("kind", "id", "owner"))


def _validate_supersession_context(value: Any, errors: list[str], prefix: str) -> None:
    if not isinstance(value, dict) or not _nonempty(value.get("relation")):
        errors.append(f"{prefix} must explain the ownership or plural continuation relation")
    if (not isinstance(value, dict) or not isinstance(value.get("source_refs"), list)
            or not value["source_refs"] or not all(_nonempty(x) for x in value["source_refs"])):
        errors.append(f"{prefix}.source_refs must contain non-empty strings")


def _validate_learning_state(state: dict[str, Any], errors: list[str]) -> None:
    """Validate stored causal references, not the truth of learned knowledge."""
    relations = state.get("learning_relations", [])
    by_id: dict[str, Any] = {}
    history = state.get("history", [])
    events: dict[str, Any] = {}
    order: dict[str, int] = {}
    for position, event in enumerate(history):
        if not isinstance(event, dict) or not _nonempty(event.get("event_id")):
            errors.append("invalid operating history event")
            continue
        event_id = event["event_id"]
        expected = f".maios/receipts/resultant/{event_id}.json"
        if not SAFE_EVENT_ID.fullmatch(event_id) or event.get("receipt") != expected or event_id in events:
            errors.append("invalid or duplicate operating history identity")
        events[event_id] = event
        order[event_id] = position

    def strings(value: Any, field: str) -> list[str]:
        if not isinstance(value, list) or not all(_nonempty(x) for x in value):
            errors.append(f"{field} must be a string list")
            return []
        if len(value) != len(set(value)):
            errors.append(f"{field} contains duplicate references")
        return value

    for item in relations:
        if not isinstance(item, dict) or not _nonempty(item.get("relation_id")):
            errors.append("invalid learning relation identity")
            continue
        relation_id = item["relation_id"]
        if relation_id in by_id:
            errors.append("duplicate learning relation id: " + relation_id)
        by_id[relation_id] = item
        if item.get("schema") != "maios.learning-relation.v2":
            errors.append("unsupported learning relation schema: " + relation_id)
        _validate_learning_delta(item, errors, relation_id)
        origin = item.get("origin_event_id") if _nonempty(item.get("origin_event_id")) else None
        ordinal = item.get("origin_ordinal")
        if (origin not in events or not isinstance(ordinal, int) or isinstance(ordinal, bool)
                or ordinal < 0 or not isinstance(item.get("owner"), dict)):
            errors.append("invalid learning origin: " + relation_id)
        else:
            if relation_id != _learning_relation_id(item["owner"], origin, ordinal):
                errors.append("learning identity differs from its origin: " + relation_id)
            if item.get("source_resultant_receipt") != events[origin]["receipt"]:
                errors.append("learning origin receipt mismatch: " + relation_id)
        if not re.fullmatch(r"[0-9a-f]{64}", str(item.get("origin_circumstance_digest", ""))):
            errors.append("invalid learning origin digest: " + relation_id)
        strings(item.get("supersedes"), relation_id + ".supersedes")
        strings(item.get("superseded_by"), relation_id + ".superseded_by")
        if item.get("supersedes") and not _nonempty(item.get("supersession_reason")):
            errors.append("learning supersession reason is missing: " + relation_id)
        lifecycle = item.get("lifecycle")
        previous_status = None
        previous_order = -1
        if not isinstance(lifecycle, list) or not lifecycle:
            errors.append("learning lifecycle is missing: " + relation_id)
            lifecycle = []
        for step in lifecycle:
            if not isinstance(step, dict):
                errors.append("invalid learning lifecycle entry: " + relation_id)
                continue
            event_id = step.get("event_id") if _nonempty(step.get("event_id")) else None
            if (event_id not in events or order.get(event_id, -1) < previous_order
                    or step.get("resultant_receipt") != events.get(event_id, {}).get("receipt")):
                errors.append("learning lifecycle event mismatch: " + relation_id)
            if (step.get("from_status") != previous_status
                    or step.get("to_status") not in {"reachable", "superseded", "cooled", "retired"}
                    or not _nonempty(step.get("reason"))):
                errors.append("incoherent learning lifecycle: " + relation_id)
            if step.get("to_status") == "superseded" and step.get("successor_id") not in strings(item.get("superseded_by"), relation_id + ".superseded_by"):
                errors.append("supersession lifecycle lost its successor: " + relation_id)
            previous_status = step.get("to_status")
            previous_order = order.get(event_id, -1)
        if lifecycle and (not isinstance(lifecycle[0], dict) or lifecycle[0].get("event_id") != origin or item.get("status") != previous_status):
            errors.append("learning status differs from lifecycle: " + relation_id)
        if item.get("superseded_by") != [x.get("successor_id") for x in lifecycle if isinstance(x, dict) and x.get("to_status") == "superseded"]:
            errors.append("learning successor history differs from its lifecycle: " + relation_id)
        uses = item.get("later_uses")
        if not isinstance(uses, list):
            errors.append("learning later_uses must be a list: " + relation_id)
            uses = []
        for use in uses:
            if not isinstance(use, dict):
                errors.append("invalid learning use: " + relation_id)
                continue
            event_id = use.get("event_id") if _nonempty(use.get("event_id")) else None
            if (event_id not in events or order.get(event_id, -1) <= order.get(origin, -1)
                    or use.get("resultant_receipt") != events.get(event_id, {}).get("receipt")
                    or not _nonempty(use.get("description"))
                    or not re.fullmatch(r"[0-9a-f]{64}", str(use.get("circumstance_digest", "")))
                    or use.get("nonidentical_to_origin") is not
                    (use.get("circumstance_digest") != item.get("origin_circumstance_digest"))):
                errors.append("invalid learning use evidence: " + relation_id)
            strings(use.get("evidence_refs"), relation_id + ".later_use.evidence_refs")
        if (item.get("last_use") != (uses[-1] if uses else None)
                or item.get("later_nonidentical_use_observed") is not
                any(isinstance(x, dict) and x.get("nonidentical_to_origin") is True for x in uses)):
            errors.append("learning use summary differs from its evidence: " + relation_id)
    if errors:
        return
    for relation_id, item in by_id.items():
        for field, reverse in (("supersedes", "superseded_by"), ("superseded_by", "supersedes")):
            for target in strings(item.get(field), relation_id + "." + field):
                other = by_id.get(target)
                if other is None or target == relation_id or relation_id not in other.get(reverse, []):
                    errors.append("incoherent learning genealogy: " + relation_id)
                elif field == "supersedes":
                    if order.get(other.get("origin_event_id"), -1) >= order.get(item.get("origin_event_id"), -1):
                        errors.append("learning ancestry must precede its successor: " + relation_id)
                    if _owner_identity(other["owner"]) != _owner_identity(item["owner"]):
                        _validate_supersession_context(item.get("supersession_context"), errors, relation_id)
                elif item["superseded_by"].index(target) > 0:
                    _validate_supersession_context(other.get("supersession_context"), errors, target)
    for summary in state.get("last_learning_relations", []):
        if not isinstance(summary, dict) or not _nonempty(summary.get("relation_id")):
            errors.append("invalid last learning summary")
            continue
        item = by_id.get(summary["relation_id"])
        if item is None or any(summary.get(key) != item.get(key) for key in ("owner", "origin_event_id", "source_resultant_receipt")):
            errors.append("last learning summary differs from relation")


def _resolved_circumstance(circumstance: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(circumstance)
    result.setdefault("knowledge_refs", copy.deepcopy(state.get("active_knowledge_refs", [])))
    return result


def compose(
    root: Path,
    circumstance: dict[str, Any],
    *,
    operating_state_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project known relations without claiming semantic selection or action."""

    if not isinstance(circumstance, dict):
        raise OperatingStateError("circumstance must be an object")
    relations = _string_list(circumstance.get("relations"), "circumstance.relations")
    if "knowledge_refs" in circumstance:
        _validate_knowledge_refs(circumstance["knowledge_refs"])
    registry = _faculty_field(root.resolve())
    relation_set = set(relations)
    silent: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    matched_relations: set[str] = set()
    for family in registry.get("families", []):
        presence = family.get("presence")
        activation = set(family.get("activation_relations", []))
        matched = sorted(relation_set & activation)
        if presence == "permanent_silent":
            silent.append(
                {
                    "id": family["id"],
                    "entry": family["entry"],
                    "result_contract": family["result_contract"],
                }
            )
        elif matched:
            matched_relations.update(matched)
            candidates.append(
                {
                    "id": family["id"],
                    "matched_relations": matched,
                    "material_when": family["material_when"],
                    "entry": family["entry"],
                    "result_contract": family["result_contract"],
                    "proof": family["proof"],
                }
            )
    competence_index = _competence_index(root.resolve())
    indexed_competences = dict(competence_index.get("represented", {}))
    indexed_competences.update(competence_index.get("active", {}))
    for competence_id, competence in sorted(indexed_competences.items()):
        if not isinstance(competence, dict):
            raise OperatingStateError(
                f"competence index entry must be an object: {competence_id}"
            )
        activation = set(
            _string_list(
                competence.get("activation_relations"),
                f"competence.{competence_id}.activation_relations",
                require=True,
            )
        )
        matched = sorted(relation_set & activation)
        if not matched:
            continue
        for field in ("work_relation", "knowledge_entry", "expected_delta"):
            if not _nonempty(competence.get(field)):
                raise OperatingStateError(
                    f"competence.{competence_id}.{field} must be a non-empty string"
                )
        matched_relations.update(matched)
        candidates.append(
            {
                "id": competence_id,
                "kind": competence.get("kind", "project_competence"),
                "matched_relations": matched,
                "material_when": competence["work_relation"],
                "entry": competence["knowledge_entry"],
                "result_contract": competence["expected_delta"],
                "proof": "the competence changes the current result and returns reusable learning to its closest owner",
                "source_ref": competence["knowledge_entry"],
                "claim_boundary": "representation and routing eligibility are not behavioral exercise or maintained assimilation",
            }
        )
    operating_state = operating_state_override or read_operating_state(root.resolve())
    for learning_relation in operating_state.get("learning_relations", []):
        if learning_relation.get("status") != "reachable":
            continue
        activation = set(learning_relation.get("activation_relations", []))
        matched = sorted(relation_set & activation)
        if not matched:
            continue
        matched_relations.update(matched)
        candidates.append(
            {
                "id": learning_relation["relation_id"],
                "kind": "competence_learning_relation",
                "matched_relations": matched,
                "material_when": learning_relation.get("why_it_matters"),
                "entry": learning_relation.get("future_behavior"),
                "result_contract": learning_relation.get("causal_delta"),
                "proof": "a later non-identical movement changes without reconstructing the same correction",
                "source_ref": learning_relation.get("source_resultant_receipt"),
                "claim_boundary": "preserved learning enlarges the reachable field; later use is distinct from assimilation",
            }
        )
    return {
        "schema": "maios.composition-candidates.v2",
        "circumstance_digest": digest(circumstance),
        "requested_result": circumstance.get("requested_result"),
        "silent_invariants": silent,
        "known_candidates": candidates,
        "unmatched_relations": sorted(relation_set - matched_relations),
        "open_world": True,
        "selection_rule": "select only result-changing relations; owner-bound learning may reenter when its activation relations match, and an unmatched material relation may enter as a sourced extension",
        "non_claim": "candidate projection is not semantic selection, execution, authority, or proof",
    }


def validate_movement(root: Path, movement: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(movement, dict):
        return {
            "schema": "maios.movement-validation.v3",
            "valid": False,
            "errors": ["movement must be an object"],
        }
    circumstance = movement.get("circumstance")
    selected = movement.get("selected_faculties")
    if not isinstance(circumstance, dict):
        errors.append("movement.circumstance must be an object")
        circumstance = {"relations": []}
    if not isinstance(selected, list):
        errors.append("movement.selected_faculties must be a list")
        selected = []
    try:
        projection = compose(root, circumstance)
    except OperatingStateError as exc:
        errors.append(str(exc))
        projection = {
            "circumstance_digest": None,
            "known_candidates": [],
            "silent_invariants": [],
            "unmatched_relations": [],
        }
    known = {item["id"] for item in projection["known_candidates"]}
    known.update(item["id"] for item in projection["silent_invariants"])
    seen: set[str] = set()
    for item in selected:
        if not isinstance(item, dict) or not _nonempty(item.get("id")):
            errors.append("each selected faculty needs an id")
            continue
        faculty_id = item["id"]
        if faculty_id in seen:
            errors.append(f"duplicate selected faculty: {faculty_id}")
        seen.add(faculty_id)
        if not _nonempty(item.get("reason")) or not _nonempty(
            item.get("expected_delta")
        ):
            errors.append(
                f"selected faculty lacks reason or expected_delta: {faculty_id}"
            )
        if faculty_id not in known:
            extension = item.get("extension")
            if not isinstance(extension, dict):
                errors.append(f"unknown faculty lacks sourced extension: {faculty_id}")
            else:
                for field in ("source_refs", "invalidator", "reentry_condition"):
                    if not extension.get(field):
                        errors.append(f"extension {faculty_id} lacks {field}")
    effect = circumstance.get("effect")
    boundary = movement.get("effect_boundary")
    if effect and not isinstance(boundary, dict):
        errors.append("material effect requires an exact effect_boundary")
    if not effect and boundary is not None:
        errors.append("effect_boundary must be null when no material effect exists")
    return {
        "schema": "maios.movement-validation.v3",
        "valid": not errors,
        "errors": errors,
        "circumstance_digest": projection["circumstance_digest"],
        "selected_ids": sorted(seen),
        "unmatched_relations": projection["unmatched_relations"],
    }


def _default_circumstance(configuration: dict[str, Any]) -> dict[str, Any]:
    relations = configuration.get("faculty_composition", {}).get(
        "circumstance_relations", []
    )
    if not isinstance(relations, list):
        relations = []
    return {
        "relations": relations,
        "requested_result": configuration.get("result", {}).get("current")
        or configuration.get("result", {}).get("requested"),
        "effect": None,
    }


def _validate_knowledge_refs(paths: Any) -> None:
    _string_list(paths, "knowledge_refs")
    for relative in paths:
        path = PurePosixPath(relative)
        if (path.is_absolute() or ".." in path.parts or chr(92) in relative
                or ":" in relative or path.as_posix() != relative or relative == "."):
            raise OperatingStateError(f"knowledge path must be project-relative: {relative}")


def knowledge_status(root: Path, paths: list[str]) -> dict[str, Any]:
    """Observe selected files, following native entries to their living bodies."""
    root = root.resolve()
    _validate_knowledge_refs(paths)
    pending = list(paths)
    observed: dict[str, Any] = {}
    while pending:
        relative = pending.pop(0)
        path = PurePosixPath(relative)
        if (not relative or path.is_absolute() or ".." in path.parts
                or chr(92) in relative or ":" in relative or path.as_posix() != relative):
            raise OperatingStateError(f"knowledge path must be project-relative: {relative}")
        if relative in observed:
            continue
        target = root.joinpath(*path.parts)
        ensure_project_local(root, target)
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise OperatingStateError(f"knowledge path is not a regular file: {relative}")
        if not target.exists():
            observed[relative] = {"status": "missing"}
            continue
        data = target.read_bytes()
        observed[relative] = {"status": "present", "sha256": hashlib.sha256(data).hexdigest()}
        for line in data.splitlines():
            if line.startswith(b"<!-- maios-knowledge-entry: ") and line.endswith(b" -->"):
                pending.append(line.removeprefix(b"<!-- maios-knowledge-entry: ").removesuffix(b" -->").decode("utf-8"))
    return {"schema": "maios.knowledge-observation.v1", "files": observed,
            "claim_boundary": "selected content identity, not comprehension or assimilation"}


def _input_digests(
    configuration: dict[str, Any],
    host_state: dict[str, Any],
    competence_index: dict[str, Any],
    faculty_field: dict[str, Any],
    root: Path,
    knowledge_refs: list[str],
) -> dict[str, str]:
    return {
        "configuration": digest(configuration),
        "host_state": digest(host_state),
        "competence_index": digest(competence_index),
        "faculty_field": digest(faculty_field),
        "knowledge": digest(knowledge_status(root, knowledge_refs)),
    }


def _changed_inputs(previous: dict[str, Any], current: dict[str, str]) -> list[str]:
    if not previous:
        return list(current)
    return sorted(key for key, value in current.items() if previous.get(key) != value)


def _invalidated_relations(changed: list[str]) -> list[dict[str, Any]]:
    impact = {
        "configuration": [
            "operator intent",
            "project result",
            "possibility field",
            "current next movement",
        ],
        "host_state": [
            "capability eligibility",
            "blocked actions",
            "fallback",
        ],
        "competence_index": ["active competence relations", "later routing"],
        "faculty_field": ["known candidate projection", "composition reasons"],
        "knowledge": ["selected consumed knowledge", "native entry continuation"],
    }
    return [
        {"input": item, "derived_relations": impact[item]}
        for item in changed
        if item in impact
    ]


def _operating_status(
    root: Path,
    circumstance: dict[str, Any] | None = None,
    *,
    configuration_override: dict[str, Any] | None = None,
    operating_state_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    configuration = configuration_override or configuration_engine.current_configuration(root)
    host_state = host_engine.read_host_state(root)
    competence_index = _competence_index(root)
    faculty_field = _faculty_field(root)
    operating_state = operating_state_override or read_operating_state(root)
    circumstance = _resolved_circumstance(
        circumstance if circumstance is not None else _default_circumstance(configuration),
        operating_state,
    )
    projection = compose(
        root,
        circumstance,
        operating_state_override=operating_state,
    )
    inputs = _input_digests(
        configuration, host_state, competence_index, faculty_field, root,
        circumstance.get("knowledge_refs", [])
    )
    changed = _changed_inputs(operating_state.get("last_input_digests", {}), inputs)

    candidate_by_id = {
        item["id"]: item for item in projection.get("known_candidates", [])
    }
    silent_ids = {item["id"] for item in projection.get("silent_invariants", [])}
    capability_relations: list[dict[str, Any]] = []
    for family in faculty_field.get("families", []):
        family_id = family["id"]
        if family_id in silent_ids:
            state = "present"
            reason = "permanent silent relation"
        elif family_id in candidate_by_id:
            state = "eligible"
            reason = "matched current circumstance relations"
        else:
            state = "potential"
            reason = "reachable but not selected by the represented circumstance"
        capability_relations.append(
            {
                "id": family_id,
                "kind": "faculty_family",
                "state": state,
                "reason": reason,
                "source_ref": ".maios/kernel/FACULTY_FIELD.json",
            }
        )
    indexed_competences = dict(competence_index.get("represented", {}))
    indexed_competences.update(competence_index.get("active", {}))
    active_ids = set(competence_index.get("active", {}))
    for competence_id, competence in sorted(indexed_competences.items()):
        eligible = competence_id in candidate_by_id
        capability_relations.append(
            {
                "id": competence_id,
                "kind": competence.get("kind", "project_competence"),
                "state": "eligible" if eligible else "available",
                "reason": (
                    "matched current circumstance relations"
                    if eligible
                    else competence.get("work_relation")
                ),
                "source_ref": competence.get(
                    "knowledge_entry", ".maios/competences/INDEX.json"
                ),
                "index_state": "active_evolved" if competence_id in active_ids else "represented",
                "claim_boundary": "availability is not current exercise or maintained assimilation",
            }
        )
    for learning_relation in operating_state.get("learning_relations", []):
        relation_id = learning_relation["relation_id"]
        if learning_relation.get("status") != "reachable":
            continue
        if relation_id in candidate_by_id:
            state = "eligible"
            reason = "the preserved causal relation matches the represented circumstance"
        else:
            state = "potential"
            reason = "the preserved causal relation remains reachable for a later circumstance"
        capability_relations.append(
            {
                "id": relation_id,
                "kind": "competence_learning_relation",
                "state": state,
                "reason": reason,
                "owner": copy.deepcopy(learning_relation.get("owner")),
                "source_ref": learning_relation.get("source_resultant_receipt"),
                "claim_boundary": "persistence is not assimilation; later use remains observable and revisable",
            }
        )
    observed = sorted(set(host_state.get("observed_capabilities", [])))
    unverified = sorted(
        set(host_state.get("unverified_capabilities", [])) - set(observed)
    )
    for capability in observed:
        capability_relations.append(
            {
                "id": capability,
                "kind": "host_capability",
                "state": "verified_observed",
                "source_ref": ".maios/state/HOST_STATE.json",
            }
        )
    for capability in unverified:
        capability_relations.append(
            {
                "id": capability,
                "kind": "host_capability",
                "state": "unknown",
                "source_ref": ".maios/state/HOST_STATE.json",
            }
        )

    present = configuration.get("present_field", {})
    uncertainty = list(present.get("unknowns", [])) + list(
        present.get("retained_unknowns", [])
    )
    uncertainty.extend(
        {
            "id": f"host:{item}",
            "statement": f"Host capability remains unverified: {item}",
            "source_refs": [".maios/state/HOST_STATE.json"],
        }
        for item in unverified
    )
    uncertainty.extend(
        {
            "id": f"unmatched:{item}",
            "statement": f"Current relation has no known family projection: {item}",
            "source_refs": [],
        }
        for item in projection.get("unmatched_relations", [])
    )

    result: dict[str, Any] = {
        "schema": OPERATING_CONTEXT_SCHEMA,
        "state_owner": ".maios/state/OPERATING_STATE.json",
        "operating_state_sha256": digest(operating_state),
        "operating_revision": operating_state["revision"],
        "input_digests": inputs,
        "knowledge_refs": copy.deepcopy(circumstance["knowledge_refs"]),
        "freshness": {
            "status": "current" if not changed else "changed_or_unobserved",
            "changed_inputs": changed,
            "invalidated_relations": _invalidated_relations(changed),
        },
        "active_object": {
            "intent": configuration.get("operator_relation", {}).get(
                "current_intent"
            ),
            "intent_source": configuration.get("operator_relation", {}).get("intent_source"),
            "requested_result": circumstance.get("requested_result"),
            "current_result": configuration.get("result", {}).get("current"),
            "current_next": configuration.get("current_next"),
        },
        "causal_margin": copy.deepcopy(operating_state.get("causal_margin")),
        "open_fronts": copy.deepcopy(operating_state.get("open_fronts", [])),
        "focused_front_id": operating_state.get("focused_front_id"),
        "host": {
            "selected_adapter": host_state.get("selected_adapter"),
            "revision": host_state.get("revision"),
            "observed_capabilities": observed,
            "unverified_capabilities": unverified,
        },
        "composition": projection,
        "capability_relations": capability_relations,
        "eligible_actions": [
            {
                "id": "compose_faculties",
                "effect": "none",
                "reason": "interpret and compare result-changing relations",
            },
            {
                "id": "apply_resultant",
                "effect": "project_local_state",
                "reason": "let the current source-qualified resultant form canonical continuity and the next field",
            },
        ],
        "blocked_actions": [
            {
                "id": "external_material_effect",
                "reason": "the project configuration grants no standing effect authority",
                "reentry_condition": "an exact effect relation resolves source, target, controller, authority, receipt, and recovery",
            }
        ],
        "authority_ceiling": configuration.get("effect_authority", "none"),
        "uncertainty": uncertainty,
        "expected_effects": {
            "compose_faculties": "no material effect",
            "apply_resultant": "project-local state, projections, learning relations, and receipts only",
        },
        "recovery": {
            "configuration_receipt": ".maios/receipts/configuration/CURRENT.json",
            "resultant_receipt_directory": ".maios/receipts/resultant",
            "last_resultant_receipt": operating_state.get(
                "last_resultant_receipt"
            ),
        },
        "last_resultant": operating_state.get("last_resultant"),
        "last_learning_relations": copy.deepcopy(
            operating_state.get("last_learning_relations", [])
        ),
        "claim_boundary": "this is a deterministic self-representation of current records, not consciousness, semantic correctness, or effect authority",
        "extensions": {},
    }
    result["context_sha256"] = digest(result)
    return result


def continuum_status(root: Path) -> dict[str, Any]:
    root = root.resolve()
    pending = configuration_engine.pending_transitions(root)
    errors = ["pending state transition: " + path for path in pending]
    configuration = configuration_engine.current_configuration(root)
    state = read_operating_state(root)
    relation = configuration.get("faculty_composition", {}).get("last_readback") or {}
    if (relation.get("event_id") != state.get("last_event_id")
            or relation.get("receipt") != state.get("last_resultant_receipt")):
        errors.append("configuration and operating state disagree on the current resultant")
    if state.get("last_event_id"):
        relative = state.get("last_resultant_receipt")
        if not isinstance(relative, str):
            errors.append("current resultant has no receipt path")
        else:
            try:
                receipt = read_json(configuration_engine.project_local_file(root, root / relative))
                last = state["history"][-1]
                if (receipt.get("schema") != RESULTANT_TRANSITION_SCHEMA
                        or receipt.get("event_id") != state["last_event_id"]
                        or last.get("event_id") != state["last_event_id"]
                        or last.get("receipt") != relative
                        or receipt.get("event_digest") != last.get("event_digest")):
                    errors.append("current resultant receipt differs from operating history")
            except Exception as exc:
                errors.append("current resultant receipt is unavailable or invalid: " + str(exc))
    return {"valid": not errors, "errors": errors, "pending_journals": pending}


def operating_status(
    root: Path, circumstance: dict[str, Any] | None = None
) -> dict[str, Any]:
    result = _operating_status(root, circumstance)
    coherence = continuum_status(root)
    if not coherence["valid"]:
        result["eligible_actions"] = [x for x in result["eligible_actions"] if x["id"] != "apply_resultant"]
        result["blocked_actions"].append({"id": "apply_resultant", "reason": "continuum recovery required"})
        result["context_sha256"] = digest({k: v for k, v in result.items() if k != "context_sha256"})
    # Recovery evidence is a present safety readback, outside the content fingerprint.
    result["recovery_required"] = not coherence["valid"]
    result["continuum"] = coherence
    return result


def learning_status(root: Path, *, include_cold: bool = False) -> dict[str, Any]:
    operating_state = read_operating_state(root.resolve())
    all_relations = operating_state.get("learning_relations", [])
    relations = copy.deepcopy([item for item in all_relations
                               if include_cold or item.get("status") == "reachable"])
    return {
        "schema": "maios.learning-status.v1",
        "operating_revision": operating_state["revision"],
        "relations": relations,
        "count": len(relations),
        "cold_count": sum(item.get("status") != "reachable" for item in all_relations),
        "claim_boundary": "preserved learning is reachable immediately; later non-identical use remains the assimilation evidence",
    }


def competence_candidate_status(root: Path) -> dict[str, Any]:
    """Compatibility alias for callers of the superseded candidate view."""

    return learning_status(root)


def _learning_relation_id(owner: dict[str, Any], event_id: str, ordinal: int) -> str:
    identity = {key: owner[key] for key in ("kind", "id", "owner")}
    return "learning." + digest({"owner": identity, "event": event_id, "ordinal": ordinal})


def _validate_learning_delta(value: Any, errors: list[str], prefix: str) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be an object")
        return
    owner = value.get("owner")
    if not isinstance(owner, dict):
        errors.append(f"{prefix}.owner must be an object")
    else:
        for field in ("kind", "id", "owner"):
            if not _nonempty(owner.get(field)):
                errors.append(f"{prefix}.owner.{field} must be non-empty")
    for field in (
        "what_happened",
        "causal_delta",
        "why_it_matters",
        "future_behavior",
        "invalidator",
        "reentry_condition",
    ):
        if not _nonempty(value.get(field)):
            errors.append(f"{prefix}.{field} must be non-empty")
    for field in ("source_refs", "activation_relations"):
        item = value.get(field)
        if not isinstance(item, list) or not item or not all(
            _nonempty(entry) for entry in item
        ):
            errors.append(f"{prefix}.{field} must contain non-empty strings")


def _validate_front_transition(root: Path, value: Any, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append("front_transition must be an object or absent")
        return
    upserts = value.get("upserts")
    remove_ids = value.get("remove_ids")
    if "focus_id" not in value:
        errors.append("front_transition.focus_id is required")
    if not isinstance(remove_ids, list) or not all(
        _nonempty(front_id) and SAFE_EVENT_ID.fullmatch(front_id)
        for front_id in remove_ids
    ):
        errors.append("front_transition.remove_ids must be a safe string list")
        remove_ids = []
    elif len(remove_ids) != len(set(remove_ids)):
        errors.append("front_transition.remove_ids contains duplicates")
    upsert_errors: list[str] = []
    upsert_ids = _validate_open_fronts(upserts, None, upsert_errors, "front_transition.upserts")
    errors.extend(upsert_errors)
    if upsert_ids.intersection(remove_ids):
        errors.append("front_transition cannot remove and upsert the same front")
    focus_id = value.get("focus_id")
    if focus_id is not None and (
        not _nonempty(focus_id) or not SAFE_EVENT_ID.fullmatch(focus_id)
    ):
        errors.append("front_transition.focus_id must be a safe string or null")
        return
    try:
        current_ids = {
            front["id"] for front in read_operating_state(root).get("open_fronts", [])
        }
    except (OperatingStateError, KeyError, TypeError):
        current_ids = set()
    final_ids = (current_ids - set(remove_ids)) | upsert_ids
    if focus_id is not None and focus_id not in final_ids:
        errors.append("front_transition.focus_id must identify a resulting open front")


def validate_resultant_readback(root: Path, value: Any) -> dict[str, Any]:
    errors: list[str] = []
    movement_validation: dict[str, Any] | None = None
    if not isinstance(value, dict):
        return {
            "schema": "maios.resultant-readback-validation.v1",
            "valid": False,
            "errors": ["resultant readback must be an object"],
        }
    if value.get("schema") != RESULTANT_READBACK_SCHEMA:
        errors.append("unsupported resultant readback schema")
    event_id = value.get("event_id")
    if not _nonempty(event_id):
        errors.append("event_id must be non-empty")
    elif not SAFE_EVENT_ID.fullmatch(event_id):
        errors.append("event_id contains unsafe characters")
    if not _nonempty(value.get("observed_at")):
        errors.append("observed_at must be non-empty")

    movement = value.get("movement")
    movement_validation = validate_movement(root, movement)
    if not movement_validation["valid"]:
        errors.extend(
            f"movement: {item}" for item in movement_validation.get("errors", [])
        )

    positions = value.get("source_positions")
    if not isinstance(positions, dict):
        errors.append("source_positions must be an object")
        positions = {}
    for field in (
        "operator_source",
        "verified_evidence",
        "model_inference",
        "retained_unknowns",
    ):
        item = positions.get(field)
        if not isinstance(item, list) or not all(_nonempty(entry) for entry in item):
            errors.append(f"source_positions.{field} must be a string list")
    if not positions.get("operator_source") and not positions.get("verified_evidence"):
        errors.append("readback requires operator source or attributable evidence")

    candidate = value.get("candidate_resultant")
    if not isinstance(candidate, dict) or not _nonempty(candidate.get("summary")):
        errors.append("candidate_resultant.summary must be non-empty")
    preprojection = value.get("preprojection_readback")
    if not isinstance(preprojection, dict):
        errors.append("preprojection_readback must be an object")
        preprojection = {}
    if preprojection.get("status") not in PREPROJECTION_STATUSES:
        errors.append("unsupported preprojection readback status")
    if not _nonempty(preprojection.get("description")):
        errors.append("preprojection_readback.description must be non-empty")
    corrections = preprojection.get("corrections")
    if not isinstance(corrections, list) or not all(_nonempty(item) for item in corrections):
        errors.append("preprojection_readback.corrections must be a string list")
    if preprojection.get("status") == "corrected" and not corrections:
        errors.append("a corrected readback requires at least one correction")
    semantic_sensitivity = preprojection.get("semantic_sensitivity")
    if semantic_sensitivity is not None:
        if not isinstance(semantic_sensitivity, dict):
            errors.append(
                "preprojection_readback.semantic_sensitivity must be an object or absent"
            )
        else:
            if semantic_sensitivity.get("status") not in {
                "not_material",
                "preserved",
                "corrected",
                "noncollapse",
            }:
                errors.append("unsupported semantic sensitivity status")
            if not _nonempty(semantic_sensitivity.get("description")):
                errors.append("semantic sensitivity description must be non-empty")
            semantic_sources = semantic_sensitivity.get("source_refs")
            if not isinstance(semantic_sources, list) or not all(
                _nonempty(source_ref) for source_ref in semantic_sources
            ):
                errors.append("semantic sensitivity source_refs must be a string list")
            if (
                semantic_sensitivity.get("status") == "corrected"
                and preprojection.get("status") != "corrected"
            ):
                errors.append(
                    "a corrected semantic sensitivity must correct the preprojection readback"
                )

    actual = value.get("actual_result")
    if not isinstance(actual, dict):
        errors.append("actual_result must be an object")
        actual = {}
    if actual.get("status") not in RESULT_STATUSES:
        errors.append("unsupported actual result status")
    classification = actual.get("classification")
    if classification is not None and classification not in RESULT_CLASSIFICATIONS:
        errors.append("unsupported actual result classification")
    if not _nonempty(actual.get("summary")):
        errors.append("actual_result.summary must be non-empty")
    evidence_refs = actual.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not all(
        _nonempty(item) for item in evidence_refs
    ):
        errors.append("actual_result.evidence_refs must be a string list")
    if classification not in {None, "unverified"} and not evidence_refs:
        errors.append("a classified observed delta requires evidence")

    deltas = value.get("faculty_deltas")
    if not isinstance(deltas, list):
        errors.append("faculty_deltas must be a list")
        deltas = []
    selected_ids = set((movement_validation or {}).get("selected_ids", []))
    seen_delta_ids: set[str] = set()
    for item in deltas:
        if not isinstance(item, dict) or not _nonempty(item.get("faculty_id")):
            errors.append("each faculty delta requires faculty_id")
            continue
        faculty_id = item["faculty_id"]
        if faculty_id in seen_delta_ids:
            errors.append(f"duplicate faculty delta: {faculty_id}")
        seen_delta_ids.add(faculty_id)
        if faculty_id not in selected_ids:
            errors.append(f"faculty delta was not selected in movement: {faculty_id}")
        faculty_classification = item.get("classification")
        if (
            faculty_classification is not None
            and faculty_classification not in RESULT_CLASSIFICATIONS
        ):
            errors.append(f"unsupported faculty delta classification: {faculty_id}")
        if not _nonempty(item.get("description")):
            errors.append(f"faculty delta description is missing: {faculty_id}")

    impact = value.get("possibility_impact")
    if not isinstance(impact, dict):
        errors.append("possibility_impact must be an object")
        impact = {}
    for field in ("opened", "preserved", "constrained", "eliminated"):
        item = impact.get(field)
        if not isinstance(item, list) or not all(_nonempty(entry) for entry in item):
            errors.append(f"possibility_impact.{field} must be a string list")
    eliminated = set(impact.get("eliminated", []))
    if eliminated & (set(impact.get("opened", [])) | set(impact.get("preserved", []))):
        errors.append("one movement cannot both eliminate and open or preserve a possibility")

    next_movement = value.get("next_movement")
    if not isinstance(next_movement, dict):
        errors.append("next_movement must be an object")
        next_movement = {}
    for field in ("current_next", "reason", "reentry_condition"):
        if not _nonempty(next_movement.get(field)):
            errors.append(f"next_movement.{field} must be non-empty")
    if "relations" not in next_movement:
        errors.append("next_movement.relations is required")
    next_relations = next_movement.get("relations", [])
    if not isinstance(next_relations, list) or not all(
        _nonempty(item) for item in next_relations
    ):
        errors.append("next_movement.relations must be a string list")

    effect = value.get("effect")
    if not isinstance(effect, dict):
        errors.append("effect must be an object")
        effect = {}
    if effect.get("status") not in EFFECT_STATES:
        errors.append("unsupported effect status")
    receipt_refs = effect.get("receipt_refs")
    if not isinstance(receipt_refs, list) or not all(
        _nonempty(item) for item in receipt_refs
    ):
        errors.append("effect.receipt_refs must be a string list")
    movement_effect = movement.get("circumstance", {}).get("effect") if isinstance(movement, dict) else None
    if not movement_effect and effect.get("status") != "none":
        errors.append("readback effect must be none when the movement has no effect")
    if movement_effect and effect.get("status") == "none":
        errors.append("a material movement cannot report effect status none")
    if effect.get("status") == "effect_bound":
        if not isinstance(effect.get("boundary"), dict) or not receipt_refs:
            errors.append("effect_bound requires a boundary and terminal receipt")
    if effect.get("status") == "none" and (
        effect.get("boundary") is not None or receipt_refs
    ):
        errors.append("effect none cannot carry a boundary or receipt")

    if "self_improvement_assessment" in value:
        errors.append(
            "self_improvement_assessment is superseded; preserve causal changes as owner-bound learning_deltas"
        )
    if "learning_delta" in value:
        errors.append("learning_delta is superseded by the plural learning_deltas relation")
    learning_deltas = value.get("learning_deltas")
    if not isinstance(learning_deltas, list):
        errors.append("learning_deltas must be a list")
        learning_deltas = []
    current_state = read_operating_state(root)
    existing = {item["relation_id"]: item for item in current_state.get("learning_relations", [])}
    already_applied = any(item["event_id"] == value.get("event_id") and item["event_digest"] == digest(value)
                          for item in current_state["history"])
    changed_existing: set[str] = set()
    seen_deltas: set[str] = set()
    for index, learning_delta in enumerate(learning_deltas):
        prefix = f"learning_deltas[{index}]"
        _validate_learning_delta(learning_delta, errors, prefix)
        if not isinstance(learning_delta, dict):
            continue
        delta_digest = digest(learning_delta)
        if delta_digest in seen_deltas:
            errors.append("duplicate learning delta")
        seen_deltas.add(delta_digest)
        supersedes = learning_delta.get("supersedes", [])
        if not isinstance(supersedes, list) or not all(_nonempty(x) for x in supersedes):
            errors.append(f"{prefix}.supersedes must be a string list")
            continue
        if supersedes and not _nonempty(learning_delta.get("supersession_reason")):
            errors.append(f"{prefix}.supersession_reason is required")
        if len(supersedes) != len(set(supersedes)):
            errors.append(f"{prefix}.supersedes contains duplicate references")
        contextual = "supersession_context" in learning_delta
        if contextual:
            _validate_supersession_context(learning_delta["supersession_context"], errors, prefix + ".supersession_context")
        for relation_id in supersedes:
            if relation_id not in existing:
                errors.append(f"unknown learning relation: {relation_id}")
                continue
            previous = existing[relation_id]
            if (not already_applied and not contextual and (previous.get("superseded_by") or relation_id in changed_existing
                    or _owner_identity(previous["owner"]) != _owner_identity(learning_delta.get("owner", {})))):
                errors.append(f"{prefix}.supersession_context is required for cross-owner or plural continuation")
            changed_existing.add(relation_id)
    transitions = value.get("learning_transitions", [])
    if not isinstance(transitions, list):
        errors.append("learning_transitions must be a list")
        transitions = []
    for transition in transitions:
        if not isinstance(transition, dict):
            errors.append("learning transition must be an object")
            continue
        relation_id = transition.get("relation_id")
        if not _nonempty(relation_id) or relation_id not in existing:
            errors.append("learning transition must name an existing relation")
            continue
        if relation_id in changed_existing:
            errors.append(f"conflicting learning transition: {relation_id}")
        changed_existing.add(relation_id)
        if transition.get("status") not in {"reachable", "cooled", "retired"}:
            errors.append("unsupported learning transition status")
        for key in ("reason", "reentry_condition"):
            if not _nonempty(transition.get(key)):
                errors.append(f"learning transition {key} is required")

    causal_margin = value.get("causal_margin")
    _validate_causal_margin(causal_margin, errors, "causal_margin")
    if isinstance(causal_margin, dict) and causal_margin.get(
        "next_movement"
    ) != next_movement.get("current_next"):
        errors.append(
            "causal_margin.next_movement must match next_movement.current_next"
        )
    _validate_front_transition(root, value.get("front_transition"), errors)

    return {
        "schema": "maios.resultant-readback-validation.v3",
        "valid": not errors,
        "errors": errors,
        "event_digest": digest(value) if not errors else None,
        "movement_validation": movement_validation,
        "claim_boundary": "shape and causal coherence do not prove external claims, assimilation, or effect authority",
    }


def _merge_unique(existing: Any, additions: list[str]) -> list[Any]:
    """Preserve open-world entries while appending new string relations once."""

    values = list(existing) if isinstance(existing, list) else []
    for item in additions:
        if item not in values:
            values.append(item)
    return values


def _configuration_candidate(
    current: dict[str, Any], readback: dict[str, Any], receipt_relative: str
) -> dict[str, Any]:
    candidate = copy.deepcopy(current)
    actual = readback["actual_result"]
    candidate["checkpoint"] = {
        "sequence": int(current["checkpoint"]["sequence"]) + 1,
        "updated_at": readback["observed_at"],
        "summary": actual["summary"],
    }
    candidate["current_next"] = readback["next_movement"]["current_next"]
    movement = readback["movement"]
    composition = candidate.setdefault("faculty_composition", {})
    next_relations = readback["next_movement"].get("relations", [])
    composition["circumstance_relations"] = list(
        next_relations or movement["circumstance"].get("relations", [])
    )
    composition["selected"] = copy.deepcopy(movement.get("selected_faculties", []))
    composition["emergent_extensions"] = [
        copy.deepcopy(item)
        for item in movement.get("selected_faculties", [])
        if item.get("extension")
    ]
    composition["last_readback"] = {
        "event_id": readback["event_id"],
        "receipt": receipt_relative,
        "classification": actual.get("classification"),
        "summary": actual["summary"],
    }

    possibility = candidate.setdefault("possibility_field", {})
    impact = readback["possibility_impact"]
    eliminated = set(impact["eliminated"])
    for field in ("opened", "preserved", "constrained", "eliminated"):
        possibility[field] = _merge_unique(possibility.get(field, []), impact[field])
    for field in ("candidates", "opened", "preserved"):
        possibility[field] = [
            item for item in possibility.get(field, []) if item not in eliminated
        ]

    evolution = candidate.setdefault("evolution", {})
    evolution["last_crystallization"] = receipt_relative
    if readback.get("learning_deltas"):
        evolution["learning_delta_refs"] = _merge_unique(
            evolution.get("learning_delta_refs", []),
            [receipt_relative],
        )
    return candidate


def _update_learning_relations(
    current_operating: dict[str, Any],
    readback: dict[str, Any],
    receipt_relative: str,
    circumstance: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Carry a causal correction into the next field and record later use."""

    circumstance_digest = digest(circumstance)
    faculty_deltas = {
        item["faculty_id"]: item
        for item in readback.get("faculty_deltas", [])
        if isinstance(item, dict) and _nonempty(item.get("faculty_id"))
    }
    relations: list[dict[str, Any]] = []
    exercised: list[str] = []
    for source in current_operating.get("learning_relations", []):
        relation = copy.deepcopy(source)
        relation_id = relation.get("relation_id")
        faculty_delta = faculty_deltas.get(relation_id)
        if faculty_delta is not None:
            nonidentical = (
                relation.get("origin_circumstance_digest") != circumstance_digest
            )
            later_use = {
                "event_id": readback["event_id"],
                "circumstance_digest": circumstance_digest,
                "nonidentical_to_origin": nonidentical,
                "description": faculty_delta["description"],
                "classification": faculty_delta.get("classification"),
                "evidence_refs": copy.deepcopy(
                    readback["actual_result"].get("evidence_refs", [])
                ),
                "resultant_receipt": receipt_relative,
            }
            relation["later_uses"] = [
                *relation.get("later_uses", []),
                later_use,
            ]
            relation["last_use"] = later_use
            relation["later_nonidentical_use_observed"] = bool(
                relation.get("later_nonidentical_use_observed") or nonidentical
            )
            exercised.append(relation_id)
        relations.append(relation)

    changed_relation_ids: list[str] = []
    for ordinal, learning_delta in enumerate(readback.get("learning_deltas", [])):
        if not isinstance(learning_delta, dict):
            continue
        owner = copy.deepcopy(learning_delta["owner"])
        changed_relation_id = _learning_relation_id(owner, readback["event_id"], ordinal)
        changed_relation_ids.append(changed_relation_id)
        supersedes = learning_delta.get("supersedes", [])
        for previous in relations:
            if previous["relation_id"] in supersedes:
                previous["lifecycle"].append({
                    "event_id": readback["event_id"], "resultant_receipt": receipt_relative,
                    "from_status": previous["status"], "to_status": "superseded",
                    "successor_id": changed_relation_id, "reason": learning_delta["supersession_reason"],
                })
                previous["status"] = "superseded"
                previous["superseded_by"].append(changed_relation_id)
                previous["status_reason"] = learning_delta["supersession_reason"]
                previous["status_event_id"] = readback["event_id"]
        relation = {
            "schema": "maios.learning-relation.v2",
            "relation_id": changed_relation_id,
            "owner": owner,
            "status": "reachable",
            "origin_event_id": readback["event_id"],
            "origin_ordinal": ordinal,
            "origin_circumstance_digest": circumstance_digest,
            "what_happened": learning_delta["what_happened"],
            "causal_delta": learning_delta["causal_delta"],
            "why_it_matters": learning_delta["why_it_matters"],
            "future_behavior": learning_delta["future_behavior"],
            "source_refs": copy.deepcopy(learning_delta["source_refs"]),
            "activation_relations": copy.deepcopy(
                learning_delta["activation_relations"]
            ),
            "invalidator": learning_delta["invalidator"],
            "reentry_condition": learning_delta["reentry_condition"],
            "source_resultant_receipt": receipt_relative,
            "supersedes": copy.deepcopy(supersedes),
            "supersession_reason": learning_delta.get("supersession_reason"),
            "supersession_context": copy.deepcopy(learning_delta.get("supersession_context")),
            "superseded_by": [],
            "lifecycle": [{"event_id": readback["event_id"], "resultant_receipt": receipt_relative,
                           "from_status": None, "to_status": "reachable", "reason": learning_delta["causal_delta"]}],
            "later_uses": [],
            "last_use": None,
            "later_nonidentical_use_observed": False,
            "claim_boundary": "the causal relation is available now; assimilation is evidenced only by later non-identical use",
        }
        relations = [
            item
            for item in relations
            if item.get("relation_id") != changed_relation_id
        ]
        relations.append(relation)
    for transition in readback.get("learning_transitions", []):
        relation = next(item for item in relations if item["relation_id"] == transition["relation_id"])
        relation["lifecycle"].append({
            "event_id": readback["event_id"], "resultant_receipt": receipt_relative,
            "from_status": relation["status"], "to_status": transition["status"],
            "reason": transition["reason"], "reentry_condition": transition["reentry_condition"],
        })
        relation["status"] = transition["status"]
        relation["status_reason"] = transition["reason"]
        relation["reentry_condition"] = transition["reentry_condition"]
        relation["status_event_id"] = readback["event_id"]
    return relations, changed_relation_ids, exercised


def _apply_front_transition(
    current_operating: dict[str, Any], transition: Any
) -> tuple[list[dict[str, Any]], str | None]:
    fronts = copy.deepcopy(current_operating.get("open_fronts", []))
    focused_front_id = current_operating.get("focused_front_id")
    if not isinstance(transition, dict):
        return fronts, focused_front_id
    remove_ids = set(transition.get("remove_ids", []))
    fronts = [front for front in fronts if front.get("id") not in remove_ids]
    upserts = {
        front["id"]: copy.deepcopy(front)
        for front in transition.get("upserts", [])
        if isinstance(front, dict) and _nonempty(front.get("id"))
    }
    replaced: set[str] = set()
    updated: list[dict[str, Any]] = []
    for front in fronts:
        front_id = front.get("id")
        if front_id in upserts:
            updated.append(upserts[front_id])
            replaced.add(front_id)
        else:
            updated.append(front)
    updated.extend(
        front for front_id, front in upserts.items() if front_id not in replaced
    )
    return updated, transition.get("focus_id")


def apply_resultant_readback(
    root: Path, readback: Any, expected_context_sha256: str
) -> dict[str, Any]:
    root = root.resolve()
    configuration_engine.require_no_pending_transition(root)
    validation = validate_resultant_readback(root, readback)
    if not validation["valid"]:
        raise OperatingStateError(
            "invalid resultant readback: " + "; ".join(validation["errors"])
        )

    current_operating = read_operating_state(root)
    event_id = readback["event_id"]
    event_digest = validation["event_digest"]
    for prior in current_operating.get("history", []):
        if prior.get("event_id") == event_id:
            if prior.get("event_digest") != event_digest:
                raise OperatingStateError("event_id already exists with different content")
            return {
                "schema": RESULTANT_TRANSITION_SCHEMA,
                "status": "idempotent",
                "event_id": event_id,
                "operating_state_sha256": digest(current_operating),
            }

    circumstance = _resolved_circumstance(readback["movement"]["circumstance"], current_operating)
    current_context = operating_status(root, circumstance)
    if current_context["recovery_required"]:
        raise OperatingStateError("continuum recovery required before another resultant")
    if current_context["context_sha256"] != expected_context_sha256:
        raise OperatingStateError(
            "operating context changed before transition; re-read the current field"
        )
    current_configuration = configuration_engine.current_configuration(root)
    before_configuration_sha256 = configuration_engine.digest(current_configuration)
    before_operating_sha256 = digest(current_operating)
    receipt_relative = f".maios/receipts/resultant/{event_id}.json"
    receipt_path = root.joinpath(*Path(receipt_relative).parts)
    ensure_project_local(root, receipt_path)

    candidate_configuration = _configuration_candidate(
        current_configuration, readback, receipt_relative
    )
    configuration_validation = configuration_engine.validate_configuration(
        candidate_configuration
    )
    if not configuration_validation["valid"]:
        raise OperatingStateError(
            "resultant produces invalid configuration: "
            + "; ".join(configuration_validation["errors"])
        )

    updated_operating = copy.deepcopy(current_operating)
    updated_operating["revision"] = int(current_operating["revision"]) + 1
    updated_operating["last_event_id"] = event_id
    updated_operating["last_resultant_receipt"] = receipt_relative
    updated_operating["last_resultant"] = {
        "event_id": event_id,
        "classification": readback["actual_result"].get("classification"),
        "status": readback["actual_result"]["status"],
        "summary": readback["actual_result"]["summary"],
    }
    updated_operating["active_movement"] = copy.deepcopy(readback["next_movement"])
    updated_operating["history"] = [
        *current_operating.get("history", []),
        {
            "event_id": event_id,
            "event_digest": event_digest,
            "receipt": receipt_relative,
            "classification": readback["actual_result"].get("classification"),
            "preprojection_status": readback["preprojection_readback"]["status"],
            "semantic_sensitivity_status": readback["preprojection_readback"]
            .get("semantic_sensitivity", {})
            .get("status"),
        },
    ]
    competence_index = _competence_index(root)
    learning_relations, changed_learning_ids, exercised_learning_ids = (
        _update_learning_relations(
        current_operating,
        readback,
        receipt_relative,
        circumstance,
        )
    )
    updated_operating["learning_relations"] = learning_relations
    updated_operating["last_learning_relations"] = []
    for changed_learning_id in changed_learning_ids:
        changed_learning = next(
            item
            for item in learning_relations
            if item.get("relation_id") == changed_learning_id
        )
        updated_operating["last_learning_relations"].append(
            {
                "relation_id": changed_learning_id,
                "origin_event_id": event_id,
                "owner": copy.deepcopy(changed_learning["owner"]),
                "source_resultant_receipt": receipt_relative,
            }
        )
    updated_operating["causal_margin"] = copy.deepcopy(readback["causal_margin"])
    open_fronts, focused_front_id = _apply_front_transition(
        current_operating, readback.get("front_transition")
    )
    updated_operating["open_fronts"] = open_fronts
    updated_operating["focused_front_id"] = focused_front_id
    updated_operating["active_knowledge_refs"] = copy.deepcopy(circumstance["knowledge_refs"])
    state_errors: list[str] = []
    _validate_learning_state(updated_operating, state_errors)
    if state_errors:
        raise OperatingStateError("invalid resulting learning state: " + "; ".join(state_errors))

    host_state = host_engine.read_host_state(root)
    faculty_field = _faculty_field(root)
    updated_operating["last_input_digests"] = _input_digests(
        candidate_configuration, host_state, competence_index, faculty_field, root,
        circumstance.get("knowledge_refs", [])
    )
    final_context = _operating_status(
        root,
        circumstance,
        configuration_override=candidate_configuration,
        operating_state_override=updated_operating,
    )

    state_path = operating_state_path(root)
    context_path = operating_context_path(root)
    ensure_project_local(root, state_path)
    ensure_project_local(root, context_path)
    outputs = (*configuration_engine.CONFIGURATION_OUTPUTS,
               state_path.relative_to(root).as_posix(), context_path.relative_to(root).as_posix(),
               receipt_relative)
    with configuration_engine.state_transaction(root, "resultant", outputs):
        write_json_atomic(state_path, updated_operating)
        write_json_atomic(context_path, final_context)
        configuration_receipt = configuration_engine.apply_configuration(
            root, candidate_configuration, before_configuration_sha256, _within_resultant=True
        )
        # The owning transaction has not written its terminal receipt yet.
        observed_context = _operating_status(root, circumstance)
        if observed_context["context_sha256"] != final_context["context_sha256"]:
            raise OperatingStateError("applied state does not reproduce the resultant context")
        receipt = {
            "schema": RESULTANT_TRANSITION_SCHEMA,
            "status": "applied",
            "event_id": event_id,
            "event_digest": event_digest,
            "before_operating_state_sha256": before_operating_sha256,
            "after_operating_state_sha256": digest(updated_operating),
            "before_configuration_sha256": before_configuration_sha256,
            "after_configuration_sha256": configuration_engine.digest(
                candidate_configuration
            ),
            "operating_context_sha256": final_context["context_sha256"],
            "configuration_receipt": configuration_receipt,
            "learning_relations": changed_learning_ids,
            "exercised_learning_relations": exercised_learning_ids,
            "readback": readback,
            "consumed_knowledge_refs": copy.deepcopy(circumstance["knowledge_refs"]),
            "global_writes": [],
            "external_effect_claimed": False,
            "claim_boundary": "the transition records project-local resultant state; external truth, assimilation, and effect authority remain separate claims",
        }
        write_json_atomic(receipt_path, receipt)
        return receipt


def admit_resultant_readback(
    root: Path, readback: Any, expected_context_sha256: str
) -> dict[str, Any]:
    """Compatibility alias for the superseded review/admission command."""

    return apply_resultant_readback(root, readback, expected_context_sha256)
