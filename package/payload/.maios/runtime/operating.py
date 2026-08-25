"""Autological operating relation and resultant readback for MAIOS projects.

The module owns deterministic state and causal bookkeeping.  It never decides
semantic relevance, approves its own improvement, or grants external effects.
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
RESULTANT_READBACK_SCHEMA = "maios.resultant-readback.v1"
RESULTANT_ADMISSION_SCHEMA = "maios.resultant-admission.v1"
RESULT_CLASSIFICATIONS = {
    "verified_improvement",
    "no_change",
    "regression",
    "tradeoff",
    "unverified",
}
RESULT_STATUSES = {"completed", "partial", "blocked", "failed", "deferred"}
PREPROJECTION_STATUSES = {"preserved", "corrected", "noncollapse"}
SELF_IMPROVEMENT_DECISIONS = {
    "improve",
    "verify_first",
    "defer",
    "no_change",
    "reject",
}
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
    for field in ("last_input_digests", "history", "assessments"):
        expected = dict if field == "last_input_digests" else list
        if not isinstance(value.get(field), expected):
            raise OperatingStateError(f"operating state {field} has invalid type")
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


def compose(root: Path, circumstance: dict[str, Any]) -> dict[str, Any]:
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
    return {
        "schema": "maios.composition-candidates.v2",
        "circumstance_digest": digest(circumstance),
        "requested_result": circumstance.get("requested_result"),
        "silent_invariants": silent,
        "known_candidates": candidates,
        "unmatched_relations": sorted(relation_set - matched_relations),
        "open_world": True,
        "selection_rule": "select only result-changing relations; an unmatched material relation may enter as a sourced extension",
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
    projection = compose(root, circumstance)
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
                "kind": "reviewed_project_competence",
                "state": "available_reviewed",
                "reason": competence.get("work_relation"),
                "source_ref": ".maios/competences/INDEX.json",
                "claim_boundary": "reviewed availability is not current exercise",
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
                "id": "record_reviewed_resultant",
                "effect": "project_local_state",
                "reason": "close a reviewed result into canonical continuity",
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
            "record_reviewed_resultant": "project-local state, projections, and receipts only",
        },
        "recovery": {
            "configuration_receipt": ".maios/receipts/configuration/CURRENT.json",
            "resultant_receipt_directory": ".maios/receipts/resultant",
            "last_resultant_receipt": operating_state.get(
                "last_resultant_receipt"
            ),
        },
        "last_resultant": operating_state.get("last_resultant"),
        "last_assessment": operating_state.get("last_assessment"),
        "claim_boundary": "this is a deterministic self-representation of current records, not consciousness, semantic correctness, or effect authority",
        "extensions": {},
    }
    result["context_sha256"] = digest(result)
    return result


def operating_status(
    root: Path, circumstance: dict[str, Any] | None = None
) -> dict[str, Any]:
    return _operating_status(root, circumstance)


def _validate_self_improvement(value: Any, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        errors.append("self_improvement_assessment must be an object or null")
        return
    if value.get("decision") not in SELF_IMPROVEMENT_DECISIONS:
        errors.append("unsupported self improvement decision")
    target = value.get("target")
    if not isinstance(target, dict):
        errors.append("self improvement target must be an object")
    else:
        for field in ("kind", "id", "owner"):
            if not _nonempty(target.get(field)):
                errors.append(f"self improvement target.{field} must be non-empty")
    for field in ("evidence_refs", "uncertainty"):
        item = value.get(field)
        if not isinstance(item, list) or not all(_nonempty(entry) for entry in item):
            errors.append(f"self improvement {field} must be a string list")
    if not _nonempty(value.get("expected_delta")):
        errors.append("self improvement expected_delta must be non-empty")
    if value.get("decision") == "improve" and not value.get("evidence_refs"):
        errors.append("improve requires evidence; use verify_first when evidence is pending")
    candidate_ref = value.get("candidate_ref")
    if candidate_ref is not None and not _nonempty(candidate_ref):
        errors.append("self improvement candidate_ref must be null or non-empty")


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
    if actual.get("classification") not in RESULT_CLASSIFICATIONS:
        errors.append("unsupported actual result classification")
    if not _nonempty(actual.get("summary")):
        errors.append("actual_result.summary must be non-empty")
    evidence_refs = actual.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not all(
        _nonempty(item) for item in evidence_refs
    ):
        errors.append("actual_result.evidence_refs must be a string list")
    if actual.get("classification") != "unverified" and not evidence_refs:
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
        if item.get("classification") not in RESULT_CLASSIFICATIONS:
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

    _validate_self_improvement(value.get("self_improvement_assessment"), errors)
    review = value.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
    else:
        if review.get("status") != "accepted":
            errors.append("resultant readback requires accepted review")
        if not _nonempty(review.get("reviewer")):
            errors.append("reviewer must be non-empty")
        if review.get("reviewer_relation") not in {
            "operator",
            "owner",
            "independent_reviewer",
        }:
            errors.append("unsupported reviewer relation")
        if review.get("producer_is_reviewer") is not False:
            errors.append("the producing assistant cannot approve its own resultant")

    return {
        "schema": "maios.resultant-readback-validation.v1",
        "valid": not errors,
        "errors": errors,
        "event_digest": digest(value) if not errors else None,
        "movement_validation": movement_validation,
        "claim_boundary": "shape validity and accepted review do not prove semantic quality, improvement, assimilation, or external effect",
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
    composition["circumstance_relations"] = list(
        movement["circumstance"].get("relations", [])
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
        "classification": actual["classification"],
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
    assessment = readback.get("self_improvement_assessment")
    if assessment is not None:
        evolution["self_improvement_assessment_refs"] = _merge_unique(
            evolution.get("self_improvement_assessment_refs", []),
            [receipt_relative],
        )
    return candidate


def admit_resultant_readback(
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
                "schema": RESULTANT_ADMISSION_SCHEMA,
                "status": "idempotent",
                "event_id": event_id,
                "operating_state_sha256": digest(current_operating),
            }

    circumstance = readback["movement"]["circumstance"]
    current_context = operating_status(root, circumstance)
    if current_context["context_sha256"] != expected_context_sha256:
        raise OperatingStateError(
            "operating context changed after review; re-read and re-evaluate"
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
        "classification": readback["actual_result"]["classification"],
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
            "classification": readback["actual_result"]["classification"],
            "preprojection_status": readback["preprojection_readback"]["status"],
        },
    ]
    assessment = readback.get("self_improvement_assessment")
    if assessment is not None:
        compact_assessment = {
            "event_id": event_id,
            "decision": assessment["decision"],
            "target": copy.deepcopy(assessment["target"]),
            "expected_delta": assessment["expected_delta"],
            "candidate_ref": assessment.get("candidate_ref"),
            "receipt": receipt_relative,
        }
        updated_operating["assessments"] = [
            *current_operating.get("assessments", []),
            compact_assessment,
        ]
        updated_operating["last_assessment"] = compact_assessment

    host_state = host_engine.read_host_state(root)
    competence_index = _competence_index(root)
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
            raise OperatingStateError("admitted state does not reproduce reviewed context")
        receipt = {
            "schema": RESULTANT_ADMISSION_SCHEMA,
            "status": "admitted",
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
            "readback": readback,
            "global_writes": [],
            "external_effect_claimed": False,
            "claim_boundary": "admission closes reviewed project-local state; semantic improvement, assimilation, and external effects remain separate claims",
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
