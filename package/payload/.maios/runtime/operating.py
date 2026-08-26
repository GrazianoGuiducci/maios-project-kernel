"""Autological operating relation and forward-resultant learning for MAIOS.

The module owns deterministic state, causal bookkeeping, atomic transition and
recovery.  It never decides semantic relevance or grants external effects.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

try:
    from . import configuration as configuration_engine
    from . import host as host_engine
except ImportError:  # installed runtime is loaded as project-local modules
    import configuration as configuration_engine  # type: ignore[no-redef]
    import host as host_engine  # type: ignore[no-redef]


OPERATING_STATE_SCHEMA = "maios.operating-state.v1"
OPERATING_CONTEXT_SCHEMA = "maios.operating-context.v1"
RESULTANT_READBACK_SCHEMA = "maios.resultant-readback.v2"
RESULTANT_TRANSITION_SCHEMA = "maios.resultant-transition.v2"
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
        if current.exists() and current.is_symlink():
            raise OperatingStateError(
                f"operating state path contains a symlink: {relative}"
            )
    if not path.parent.resolve().is_relative_to(root):
        raise OperatingStateError(f"operating state parent escapes root: {relative}")


def operating_state_path(root: Path) -> Path:
    return root / ".maios" / "state" / "OPERATING_STATE.json"


def operating_context_path(root: Path) -> Path:
    return root / ".maios" / "context" / "OPERATING_CONTEXT.json"


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
    return value


def _competence_index(root: Path) -> dict[str, Any]:
    value = read_json(root / ".maios" / "competences" / "INDEX.json")
    if not isinstance(value, dict) or value.get("schema") != "maios.competence-index.v2":
        raise OperatingStateError("unsupported competence index schema")
    return value


def _faculty_field(root: Path) -> dict[str, Any]:
    value = read_json(root / ".maios" / "kernel" / "FACULTY_FIELD.json")
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


def _input_digests(
    configuration: dict[str, Any],
    host_state: dict[str, Any],
    competence_index: dict[str, Any],
    faculty_field: dict[str, Any],
) -> dict[str, str]:
    return {
        "configuration": digest(configuration),
        "host_state": digest(host_state),
        "competence_index": digest(competence_index),
        "faculty_field": digest(faculty_field),
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
    circumstance = circumstance or _default_circumstance(configuration)
    projection = compose(
        root,
        circumstance,
        operating_state_override=operating_state,
    )
    inputs = _input_digests(
        configuration, host_state, competence_index, faculty_field
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
    for competence_id, competence in sorted(
        competence_index.get("active", {}).items()
    ):
        capability_relations.append(
            {
                "id": competence_id,
                "kind": "project_competence",
                "state": "available",
                "reason": competence.get("work_relation"),
                "source_ref": ".maios/competences/INDEX.json",
                "claim_boundary": "availability is not current exercise or maintained assimilation",
            }
        )
    for learning_relation in operating_state.get("learning_relations", []):
        relation_id = learning_relation["relation_id"]
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
        "freshness": {
            "status": "current" if not changed else "changed_or_unobserved",
            "changed_inputs": changed,
            "invalidated_relations": _invalidated_relations(changed),
        },
        "active_object": {
            "intent": configuration.get("operator_relation", {}).get(
                "current_intent"
            ),
            "requested_result": circumstance.get("requested_result"),
            "current_result": configuration.get("result", {}).get("current"),
            "current_next": configuration.get("current_next"),
        },
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
        "last_learning_relation": operating_state.get("last_learning_relation"),
        "claim_boundary": "this is a deterministic self-representation of current records, not consciousness, semantic correctness, or effect authority",
        "extensions": {},
    }
    result["context_sha256"] = digest(result)
    return result


def operating_status(
    root: Path, circumstance: dict[str, Any] | None = None
) -> dict[str, Any]:
    return _operating_status(root, circumstance)


def learning_status(root: Path) -> dict[str, Any]:
    operating_state = read_operating_state(root.resolve())
    relations = copy.deepcopy(operating_state.get("learning_relations", []))
    return {
        "schema": "maios.learning-status.v1",
        "operating_revision": operating_state["revision"],
        "relations": relations,
        "count": len(relations),
        "claim_boundary": "preserved learning is reachable immediately; later non-identical use remains the assimilation evidence",
    }


def competence_candidate_status(root: Path) -> dict[str, Any]:
    """Compatibility alias for callers of the superseded candidate view."""

    return learning_status(root)


def _learning_relation_id(owner: dict[str, Any]) -> str:
    kind = re.sub(r"[^A-Za-z0-9._-]+", "-", owner["kind"].strip()).strip("-")
    owner_id = re.sub(r"[^A-Za-z0-9._-]+", "-", owner["id"].strip()).strip("-")
    return f"learning.{kind}.{owner_id}"


def _validate_learning_delta(value: Any, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append("learning_delta must be an object or null")
        return
    owner = value.get("owner")
    if not isinstance(owner, dict):
        errors.append("learning_delta.owner must be an object")
    else:
        for field in ("kind", "id", "owner"):
            if not _nonempty(owner.get(field)):
                errors.append(f"learning_delta.owner.{field} must be non-empty")
        if all(_nonempty(owner.get(field)) for field in ("kind", "id", "owner")):
            relation_id = _learning_relation_id(owner)
            if not SAFE_EVENT_ID.fullmatch(relation_id):
                errors.append("learning_delta owner cannot form a safe relation id")
    for field in (
        "what_happened",
        "causal_delta",
        "why_it_matters",
        "future_behavior",
        "invalidator",
        "reentry_condition",
    ):
        if not _nonempty(value.get(field)):
            errors.append(f"learning_delta.{field} must be non-empty")
    for field in ("source_refs", "activation_relations"):
        item = value.get(field)
        if not isinstance(item, list) or not item or not all(
            _nonempty(entry) for entry in item
        ):
            errors.append(f"learning_delta.{field} must contain non-empty strings")


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
            "self_improvement_assessment is superseded; preserve the causal change as learning_delta"
        )
    learning_delta = value.get("learning_delta")
    _validate_learning_delta(learning_delta, errors)
    if isinstance(learning_delta, dict) and not set(
        learning_delta.get("activation_relations", [])
    ).intersection(next_relations):
        errors.append(
            "learning_delta must enter the next movement through an activation relation"
        )

    return {
        "schema": "maios.resultant-readback-validation.v2",
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
    if readback.get("learning_delta") is not None:
        evolution["learning_delta_refs"] = _merge_unique(
            evolution.get("learning_delta_refs", []),
            [receipt_relative],
        )
    return candidate


def _update_learning_relations(
    current_operating: dict[str, Any],
    readback: dict[str, Any],
    receipt_relative: str,
) -> tuple[list[dict[str, Any]], str | None, list[str]]:
    """Carry a causal correction into the next field and record later use."""

    circumstance_digest = digest(readback["movement"]["circumstance"])
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

    learning_delta = readback.get("learning_delta")
    changed_relation_id: str | None = None
    if isinstance(learning_delta, dict):
        owner = copy.deepcopy(learning_delta["owner"])
        changed_relation_id = _learning_relation_id(owner)
        prior = next(
            (
                item
                for item in relations
                if item.get("relation_id") == changed_relation_id
            ),
            None,
        )
        relation = {
            "schema": "maios.learning-relation.v1",
            "relation_id": changed_relation_id,
            "owner": owner,
            "status": "reachable",
            "origin_event_id": readback["event_id"],
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
            "supersedes_origin_event_id": (
                prior.get("origin_event_id") if prior else None
            ),
            "supersedes_relation_digest": digest(prior) if prior else None,
            "later_uses": copy.deepcopy(prior.get("later_uses", [])) if prior else [],
            "last_use": copy.deepcopy(prior.get("last_use")) if prior else None,
            "later_nonidentical_use_observed": bool(
                prior and prior.get("later_nonidentical_use_observed")
            ),
            "claim_boundary": "the causal relation is available now; assimilation is evidenced only by later non-identical use",
        }
        relations = [
            item
            for item in relations
            if item.get("relation_id") != changed_relation_id
        ]
        relations.append(relation)
    return relations, changed_relation_id, exercised


def apply_resultant_readback(
    root: Path, readback: Any, expected_context_sha256: str
) -> dict[str, Any]:
    root = root.resolve()
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

    circumstance = readback["movement"]["circumstance"]
    current_context = operating_status(root, circumstance)
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
        },
    ]
    competence_index = _competence_index(root)
    learning_relations, changed_learning_id, exercised_learning_ids = (
        _update_learning_relations(
        current_operating,
        readback,
        receipt_relative,
        )
    )
    updated_operating["learning_relations"] = learning_relations
    if changed_learning_id is not None:
        changed_learning = next(
            item
            for item in learning_relations
            if item.get("relation_id") == changed_learning_id
        )
        updated_operating["last_learning_relation"] = {
            "relation_id": changed_learning_id,
            "origin_event_id": event_id,
            "owner": copy.deepcopy(changed_learning["owner"]),
            "source_resultant_receipt": receipt_relative,
        }

    host_state = host_engine.read_host_state(root)
    faculty_field = _faculty_field(root)
    updated_operating["last_input_digests"] = _input_digests(
        candidate_configuration, host_state, competence_index, faculty_field
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
    prior_context = read_json(context_path) if context_path.is_file() else None
    configuration_receipt: dict[str, Any] | None = None
    try:
        write_json_atomic(state_path, updated_operating)
        write_json_atomic(context_path, final_context)
        configuration_receipt = configuration_engine.apply_configuration(
            root, candidate_configuration, before_configuration_sha256
        )
        observed_context = operating_status(root, circumstance)
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
            "learning_relation": changed_learning_id,
            "exercised_learning_relations": exercised_learning_ids,
            "readback": readback,
            "global_writes": [],
            "external_effect_claimed": False,
            "claim_boundary": "the transition records project-local resultant state; external truth, assimilation, and effect authority remain separate claims",
        }
        write_json_atomic(receipt_path, receipt)
        return receipt
    except Exception:
        write_json_atomic(state_path, current_operating)
        if prior_context is None:
            if context_path.exists():
                context_path.unlink()
        else:
            write_json_atomic(context_path, prior_context)
        if configuration_receipt and configuration_receipt.get("status") == "applied":
            configuration_engine.recover_configuration(root, configuration_receipt)
        raise


def admit_resultant_readback(
    root: Path, readback: Any, expected_context_sha256: str
) -> dict[str, Any]:
    """Compatibility alias for the superseded review/admission command."""

    return apply_resultant_readback(root, readback, expected_context_sha256)
