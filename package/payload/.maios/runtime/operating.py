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
    if not isinstance(value.get("competence_candidates", []), list):
        raise OperatingStateError(
            "operating state competence_candidates has invalid type"
        )
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
    for competence_candidate in operating_state.get("competence_candidates", []):
        if competence_candidate.get("status") not in {
            "ready_for_exercise",
            "needs_evidence",
        }:
            continue
        formation = competence_candidate.get("formation", {})
        activation = set(formation.get("activation_relations", []))
        matched = sorted(relation_set & activation)
        if not matched:
            continue
        matched_relations.update(matched)
        candidates.append(
            {
                "id": competence_candidate["candidate_id"],
                "kind": "competence_formation_candidate",
                "matched_relations": matched,
                "material_when": formation.get("work_relation"),
                "entry": formation.get("next_exercise"),
                "result_contract": competence_candidate.get("expected_delta"),
                "proof": "a later faculty_delta and independent competence review",
                "source_ref": competence_candidate.get("source_resultant_receipt"),
                "claim_boundary": "eligible candidate is not an admitted competence",
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
        "selection_rule": "select only result-changing relations; reviewed formation candidates may be exercised without being treated as admitted competences, and an unmatched material relation may enter as a sourced extension",
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
                "kind": "reviewed_project_competence",
                "state": "available_reviewed",
                "reason": competence.get("work_relation"),
                "source_ref": ".maios/competences/INDEX.json",
                "claim_boundary": "reviewed availability is not current exercise",
            }
        )
    admitted_candidate_ids = {
        item.get("candidate_id")
        for item in competence_index.get("history", [])
        if _nonempty(item.get("candidate_id"))
    }
    for competence_candidate in operating_state.get("competence_candidates", []):
        candidate_id = competence_candidate["candidate_id"]
        if candidate_id in admitted_candidate_ids:
            state = "admitted_reviewed"
            reason = "an independently accepted competence delta records this candidate"
        elif candidate_id in candidate_by_id:
            state = "candidate_eligible"
            reason = "formation relations match the represented circumstance"
        else:
            state = competence_candidate.get("status", "candidate_potential")
            reason = "formation remains project-local and has not been admitted"
        capability_relations.append(
            {
                "id": candidate_id,
                "kind": "competence_formation_candidate",
                "state": state,
                "reason": reason,
                "source_ref": competence_candidate.get("source_resultant_receipt"),
                "claim_boundary": "formation and exercise do not equal reviewed competence admission",
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
        "last_competence_candidate": operating_state.get(
            "last_competence_candidate"
        ),
        "claim_boundary": "this is a deterministic self-representation of current records, not consciousness, semantic correctness, or effect authority",
        "extensions": {},
    }
    result["context_sha256"] = digest(result)
    return result


def operating_status(
    root: Path, circumstance: dict[str, Any] | None = None
) -> dict[str, Any]:
    return _operating_status(root, circumstance)


def competence_candidate_status(root: Path) -> dict[str, Any]:
    operating_state = read_operating_state(root.resolve())
    competence_index = _competence_index(root.resolve())
    admitted = {
        item.get("candidate_id"): item.get("event_id")
        for item in competence_index.get("history", [])
        if _nonempty(item.get("candidate_id"))
    }
    candidates: list[dict[str, Any]] = []
    for item in operating_state.get("competence_candidates", []):
        candidate = copy.deepcopy(item)
        if candidate.get("candidate_id") in admitted:
            candidate["status"] = "admitted_reviewed"
            candidate["admitted_event_id"] = admitted[candidate["candidate_id"]]
        candidates.append(candidate)
    return {
        "schema": "maios.competence-candidate-status.v1",
        "operating_revision": operating_state["revision"],
        "candidates": candidates,
        "count": len(candidates),
        "claim_boundary": "formation, exercise, and a proposed delta remain distinct from independently reviewed admission and later assimilation",
    }


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
    method_readback = value.get("method_readback")
    if not isinstance(method_readback, dict):
        errors.append("self improvement method_readback must be an object")
        method_readback = {}
    for field in (
        "current_method",
        "observed_relation",
        "causal_delta",
        "selected_level",
        "stop_condition",
    ):
        if not _nonempty(method_readback.get(field)):
            errors.append(f"self improvement method_readback.{field} must be non-empty")
    alternatives = method_readback.get("alternatives_preserved")
    if not isinstance(alternatives, list) or not all(
        _nonempty(item) for item in alternatives
    ):
        errors.append(
            "self improvement method_readback.alternatives_preserved must be a string list"
        )
    if value.get("decision") == "improve" and not value.get("evidence_refs"):
        errors.append("improve requires evidence; use verify_first when evidence is pending")
    formation = value.get("formation_candidate")
    if value.get("decision") == "improve":
        if not isinstance(formation, dict):
            errors.append("improve requires a formation_candidate")
            formation = {}
        for field in (
            "candidate_id",
            "form",
            "purpose",
            "work_relation",
            "invalidator",
            "reentry_condition",
            "next_exercise",
        ):
            if not _nonempty(formation.get(field)):
                errors.append(f"formation_candidate.{field} must be non-empty")
        candidate_id = formation.get("candidate_id")
        if _nonempty(candidate_id) and not SAFE_EVENT_ID.fullmatch(candidate_id):
            errors.append("formation_candidate.candidate_id contains unsafe characters")
        for field in ("source_refs", "activation_relations"):
            item = formation.get(field)
            if not isinstance(item, list) or not item or not all(
                _nonempty(entry) for entry in item
            ):
                errors.append(
                    f"formation_candidate.{field} must contain non-empty strings"
                )
    elif formation is not None:
        errors.append("formation_candidate is only valid for decision improve")
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

    assessment = value.get("self_improvement_assessment")
    _validate_self_improvement(assessment, errors)
    if isinstance(assessment, dict) and assessment.get("decision") == "improve":
        activation_relations = set(
            assessment.get("formation_candidate", {}).get(
                "activation_relations", []
            )
        )
        if not activation_relations.intersection(next_relations):
            errors.append(
                "an improvement candidate must enter the next movement through at least one activation relation"
            )
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


def _proposed_competence_delta(
    readback: dict[str, Any],
    competence_candidate: dict[str, Any],
    faculty_delta: dict[str, Any],
    competence_index: dict[str, Any],
) -> dict[str, Any]:
    target = competence_candidate["target"]
    competence_id = target["id"]
    current = competence_index.get("active", {}).get(competence_id)
    disposition = "revise" if current else "retain"
    return {
        "schema": "maios.competence-delta.v2",
        "event_id": f"{readback['event_id']}.{competence_candidate['candidate_id']}",
        "candidate_id": competence_candidate["candidate_id"],
        "origin_resultant_event_id": competence_candidate["origin_event_id"],
        "competence_id": competence_id,
        "disposition": disposition,
        "work_relation": competence_candidate["formation"]["work_relation"],
        "source_refs": competence_candidate["formation"]["source_refs"],
        "expected_delta": competence_candidate["expected_delta"],
        "observed_delta": {
            "classification": faculty_delta["classification"],
            "description": faculty_delta["description"],
        },
        "evidence_refs": readback["actual_result"]["evidence_refs"],
        "invalidator": competence_candidate["formation"]["invalidator"],
        "reentry_condition": competence_candidate["formation"][
            "reentry_condition"
        ],
        "supersedes_event_id": current.get("event_id") if current else None,
        "review": {
            "status": "pending",
            "reviewer": "pending owner review",
            "reviewer_relation": "owner",
            "producer_is_reviewer": False,
        },
    }


def _evaluate_competence_candidates(
    current_operating: dict[str, Any],
    readback: dict[str, Any],
    competence_index: dict[str, Any],
    receipt_relative: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Read later exercise back into candidate state without admitting it."""

    deltas = {
        item["faculty_id"]: item
        for item in readback.get("faculty_deltas", [])
        if isinstance(item, dict) and _nonempty(item.get("faculty_id"))
    }
    updated: list[dict[str, Any]] = []
    evaluated_ids: list[str] = []
    for item in current_operating.get("competence_candidates", []):
        candidate = copy.deepcopy(item)
        candidate_id = candidate.get("candidate_id")
        faculty_delta = deltas.get(candidate_id)
        if (
            faculty_delta is None
            or candidate.get("status")
            not in {"ready_for_exercise", "needs_evidence"}
        ):
            updated.append(candidate)
            continue
        classification = faculty_delta["classification"]
        candidate["evaluation"] = {
            "result_event_id": readback["event_id"],
            "classification": classification,
            "description": faculty_delta["description"],
            "evidence_refs": copy.deepcopy(
                readback["actual_result"]["evidence_refs"]
            ),
            "resultant_receipt": receipt_relative,
        }
        if classification in {"verified_improvement", "tradeoff"}:
            candidate["status"] = "ready_for_review"
            candidate["proposed_delta"] = _proposed_competence_delta(
                readback, candidate, faculty_delta, competence_index
            )
        elif classification == "unverified":
            candidate["status"] = "needs_evidence"
            candidate["proposed_delta"] = None
        else:
            candidate["status"] = "closed_without_promotion"
            candidate["proposed_delta"] = None
        evaluated_ids.append(candidate_id)
        updated.append(candidate)
    return updated, evaluated_ids


def _formed_competence_candidate(
    readback: dict[str, Any], receipt_relative: str
) -> dict[str, Any] | None:
    assessment = readback.get("self_improvement_assessment")
    if not isinstance(assessment, dict) or assessment.get("decision") != "improve":
        return None
    formation = assessment["formation_candidate"]
    return {
        "candidate_id": formation["candidate_id"],
        "origin_event_id": readback["event_id"],
        "status": "ready_for_exercise",
        "target": copy.deepcopy(assessment["target"]),
        "method_readback": copy.deepcopy(assessment["method_readback"]),
        "formation": copy.deepcopy(formation),
        "expected_delta": assessment["expected_delta"],
        "evidence_refs": copy.deepcopy(assessment["evidence_refs"]),
        "uncertainty": copy.deepcopy(assessment["uncertainty"]),
        "source_resultant_receipt": receipt_relative,
        "evaluation": None,
        "proposed_delta": None,
    }


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
    competence_index = _competence_index(root)
    competence_candidates, evaluated_candidate_ids = _evaluate_competence_candidates(
        current_operating,
        readback,
        competence_index,
        receipt_relative,
    )
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

    formed_candidate = _formed_competence_candidate(readback, receipt_relative)
    if formed_candidate is not None:
        candidate_id = formed_candidate["candidate_id"]
        if any(
            item.get("candidate_id") == candidate_id
            for item in current_operating.get("competence_candidates", [])
        ):
            raise OperatingStateError(
                f"competence formation candidate already exists: {candidate_id}"
            )
        reserved_ids = {
            item.get("id") for item in _faculty_field(root).get("families", [])
        }
        reserved_ids.update(competence_index.get("active", {}))
        if candidate_id in reserved_ids:
            raise OperatingStateError(
                f"competence formation candidate conflicts with an existing faculty or competence: {candidate_id}"
            )
        competence_candidates.append(formed_candidate)
        updated_operating["last_competence_candidate"] = {
            "candidate_id": candidate_id,
            "status": formed_candidate["status"],
            "target": copy.deepcopy(formed_candidate["target"]),
            "source_resultant_receipt": receipt_relative,
        }
    elif evaluated_candidate_ids:
        last_evaluated = next(
            item
            for item in reversed(competence_candidates)
            if item.get("candidate_id") == evaluated_candidate_ids[-1]
        )
        updated_operating["last_competence_candidate"] = {
            "candidate_id": last_evaluated["candidate_id"],
            "status": last_evaluated["status"],
            "target": copy.deepcopy(last_evaluated["target"]),
            "source_resultant_receipt": last_evaluated[
                "source_resultant_receipt"
            ],
        }
    updated_operating["competence_candidates"] = competence_candidates

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
            "formed_competence_candidate": (
                formed_candidate["candidate_id"] if formed_candidate else None
            ),
            "evaluated_competence_candidates": evaluated_candidate_ids,
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
