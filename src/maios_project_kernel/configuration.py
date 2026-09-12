"""Canonical MAIOS situated-configuration state transition engine."""

from __future__ import annotations

import hashlib
import base64
import json
import os
import re
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from . import filesystem as filesystem_engine
except ImportError:  # generated runtime and installer carry the same source
    import maios_filesystem as filesystem_engine  # type: ignore[no-redef]


CONFIGURATION_SCHEMA = "maios.configuration-state.v3"
RECEIPT_SCHEMA = "maios.configuration-receipt.v2"
RECOVERY_SCHEMA = "maios.configuration-recovery.v2"
HOST_ATTESTATION_STAGES = (
    "instruction_discovery", "skill_discovery", "state_read",
    "behavioral_activation", "maintained_reentry",
)


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
    filesystem_engine.write_json_atomic(path, value)


def write_text_atomic(path: Path, text: str) -> None:
    filesystem_engine.write_text_atomic(path, text)


def configuration_path(root: Path) -> Path:
    return root / "setup" / "CONFIGURATION_STATE.json"


def ensure_project_local(root: Path, path: Path) -> None:
    try:
        filesystem_engine.ensure_local(root, path)
    except (ValueError, OSError) as exc:
        raise ConfigurationError(str(exc)) from exc



def project_local_file(root: Path, path: Path) -> Path:
    # Preserve the paired root/path spelling until the confinement helper has
    # derived the relative path; it then resolves the root and checks children.
    ensure_project_local(root, path)
    if not path.is_file():
        raise ConfigurationError(f"project-local file is missing: {path}")
    return path


CONFIGURATION_OUTPUTS = (
    "setup/CONFIGURATION_STATE.json", ".maios/context/CONTEXT_CAPSULE.json",
    ".maios/context/SETUP_SPEC.json", "project/CURRENT_STATE.md",
    "project/PROJECT_BRIEF.md", ".maios/receipts/configuration/CURRENT.json",
)


def pending_transitions(root: Path) -> list[str]:
    result = []
    for owner in ("configuration", "resultant", "host", "competence"):
        relative = f".maios/receipts/{owner}/PENDING.json"
        path = root / relative
        try:
            ensure_project_local(root, path)
        except ConfigurationError:
            result.append(relative)
            continue
        if path.exists() or path.is_symlink():
            result.append(relative)
    return result


def valid_event_id(value: Any) -> bool:
    return (isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9._-]+", value) is not None
            and value.casefold() != "pending")


def terminal_receipt_errors(root: Path, owner: str, prior: Any) -> list[str]:
    """Validate historical evidence against its own body, never today's semantic field."""
    schemas = {"resultant": "maios.resultant-transition.v3",
               "host": "maios.host-attestation-receipt.v2", "competence": "maios.competence-admission.v2"}
    try:
        if not isinstance(prior, dict) or not valid_event_id(prior.get("event_id")):
            raise ValueError("invalid recorded event identity")
        event_id = prior["event_id"]
        relative = f".maios/receipts/{owner}/{event_id}.json"
        if owner == "resultant" and prior.get("receipt") != relative:
            raise ValueError("history receipt path differs from event identity")
        receipt = read_json(project_local_file(root, root / relative))
        if not isinstance(receipt, dict) or receipt.get("schema") != schemas[owner]:
            raise ValueError("unsupported terminal receipt")
        if receipt.get("event_id") != event_id:
            raise ValueError("terminal receipt event differs from history")
        expected_status = "applied" if owner == "resultant" else "admitted"
        if receipt.get("status") != expected_status:
            raise ValueError("receipt is not terminal")
        if owner == "resultant":
            body = receipt.get("readback")
            if not isinstance(body, dict) or body.get("schema") != "maios.resultant-readback.v3":
                raise ValueError("terminal readback is missing or malformed")
        else:
            body = {k: v for k, v in prior.items() if k not in {"event_digest", "sequence"}}
            if receipt.get("revision") != prior.get("sequence"):
                raise ValueError("terminal revision differs from recorded transition")
        body_digest = digest(body)
        if body.get("event_id") != event_id or body_digest != prior.get("event_digest"):
            raise ValueError("recorded event digest differs from its body")
        # Older host v2 receipts use the full digest-bound attestation in history.
        if owner != "host" or "event_digest" in receipt:
            if receipt.get("event_digest") != body_digest:
                raise ValueError("terminal event digest differs from its body")
        if owner == "host" and any(receipt.get(k) != body.get(k) for k in ("stage", "result")):
            raise ValueError("terminal host observation differs from history")
        hash_fields = {"resultant": ("before_operating_state_sha256", "after_operating_state_sha256",
                                     "before_configuration_sha256", "after_configuration_sha256", "operating_context_sha256"),
                       "host": ("before_state_sha256", "after_state_sha256"),
                       "competence": ("before_index_sha256", "after_index_sha256")}[owner]
        if any(not isinstance(receipt.get(k), str) or not re.fullmatch(r"[0-9a-f]{64}", receipt[k]) for k in hash_fields):
            raise ValueError("terminal state digests are malformed")
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        return [f"{owner} terminal receipt recovery required: {exc}"]
    return []


def history_receipt_errors(root: Path, owner: str, history: Any) -> list[str]:
    if not isinstance(history, list):
        return [f"{owner} history must be a list"]
    return [error for prior in history for error in terminal_receipt_errors(root, owner, prior)]


def owner_state_receipt_errors(root: Path, owner: str, state: dict[str, Any]) -> list[str]:
    """Bind only the latest host/index transition to its current managed state.

    Historical receipts retain their own context. Competence knowledge bodies
    are separate living sources, not bytes owned by an index admission.
    """
    history_field, after_field = {
        "host": ("attestation_history", "after_state_sha256"),
        "competence": ("history", "after_index_sha256"),
    }[owner]
    history = state.get(history_field, [])
    errors = history_receipt_errors(root, owner, history)
    if errors:
        return errors
    try:
        revision = state.get("revision")
        if type(revision) is not int or revision < 0:
            raise ValueError("current revision is malformed")
        if not history:
            if revision != 0 or state.get("last_event_id") is not None:
                raise ValueError("current transition has no recorded history")
            # Validate the zero-transition claims, not equality to a fixed
            # template. Unknowns, extensions and represented knowledge are free
            # to evolve; these fields specifically record completed admissions.
            if owner == "host":
                for stage in HOST_ATTESTATION_STAGES:
                    if state.get(stage, "unverified") != "unverified":
                        raise ValueError(f"initial {stage} has no recorded attestation")
                for field in ("observed_capabilities", "evidence"):
                    if state.get(field, []) != []:
                        raise ValueError(f"initial {field} has no recorded attestation")
            elif state.get("active", {}) != {}:
                raise ValueError("initial active competences have no recorded admission")
            return []
        latest = history[-1]
        if (revision != len(history) or type(latest.get("sequence")) is not int
                or revision != latest["sequence"] or state.get("last_event_id") != latest["event_id"]):
            raise ValueError("current revision or event differs from the latest transition")
        relative = f".maios/receipts/{owner}/{latest['event_id']}.json"
        receipt = read_json(project_local_file(root, root / relative))
        if receipt[after_field] != digest(state):
            raise ValueError("current state digest differs from the latest terminal receipt")
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as exc:
        return [f"{owner} current state recovery required: {exc}"]
    return []


def require_no_pending_transition(root: Path, allowed_owner: str | None = None) -> None:
    pending = [p for p in pending_transitions(root)
               if p != f".maios/receipts/{allowed_owner}/PENDING.json"]
    if pending:
        raise ConfigurationError("state transition recovery required: " + ", ".join(pending))


def write_bytes_atomic(path: Path, data: bytes) -> None:
    filesystem_engine.write_bytes_atomic(path, data)


@contextmanager
def state_transaction(root: Path, owner: str, relatives: tuple[str, ...], *, allowed_owner: str | None = None):
    """Capture recovery before state writes; retain evidence if caught rollback fails.

    This handles caught exceptions, not arbitrary writers or crash-safe multi-file commit.
    The journal is evidence for qualified recovery, never an automatic deletion plan.
    """
    root = root.resolve()
    require_no_pending_transition(root, allowed_owner)
    journal = root / f".maios/receipts/{owner}/PENDING.json"
    if any((root / r).as_posix().casefold() == journal.as_posix().casefold() for r in relatives):
        raise ConfigurationError("event output collides with transaction control path")
    snapshot = {}
    for relative in relatives:
        path = root / relative
        ensure_project_local(root, path)
        if path.exists() and not path.is_file():
            raise ConfigurationError(f"state output is not a regular file: {relative}")
        snapshot[relative] = path.read_bytes() if path.is_file() else None
    journal = root / f".maios/receipts/{owner}/PENDING.json"
    ensure_project_local(root, journal)
    journal.parent.mkdir(parents=True, exist_ok=True)
    evidence = {"schema": "maios.state-transition-journal.v1", "owner": owner,
                "target": str(root), "state": "prepared", "before": {
                    p: base64.b64encode(data).decode("ascii") if data is not None else None
                    for p, data in snapshot.items()}}
    with journal.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(evidence, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        yield
    except Exception as original:
        failures = []
        for relative, data in reversed(list(snapshot.items())):
            path = root / relative
            try:
                ensure_project_local(root, path)
                if data is None:
                    if path.exists():
                        if not path.is_file():
                            raise ConfigurationError("changed output type")
                        path.unlink()
                elif not path.is_file() or path.read_bytes() != data:
                    write_bytes_atomic(path, data)
            except Exception:
                failures.append(relative)
        if not failures:
            try:
                ensure_project_local(root, journal)
                journal.unlink()
            except Exception:
                failures.append(journal.relative_to(root).as_posix())
        if failures:
            raise ConfigurationError("state rollback incomplete; recovery required: " +
                                     ", ".join(failures) + "; evidence: " + str(journal)) from original
        raise
    else:
        # All state and terminal receipts are committed; cleanup cannot undo that result.
        try:
            ensure_project_local(root, journal)
            journal.unlink()
        except Exception as exc:
            raise ConfigurationError("state transition committed; journal cleanup required: " + str(journal)) from exc


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


def valid_possibility_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        _nonempty(item) or isinstance(item, dict) for item in value
    )


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
    _validate_source_contact(value.get("source_contact"), errors)
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
    integration_handoff = value.get("integration_handoff")
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

    if isinstance(composition, dict):
        readback = composition.get("last_readback")
        if readback is not None:
            if not isinstance(readback, dict):
                errors.append("faculty_composition.last_readback must be null or an event reference object")
            elif (not valid_event_id(readback.get("event_id"))
                  or readback.get("receipt") !=
                  f".maios/receipts/resultant/{readback.get('event_id')}.json"):
                errors.append("faculty_composition.last_readback requires an event_id and its resultant receipt")
    if isinstance(possibility, dict):
        for name in ("candidates", "opened", "preserved", "constrained", "eliminated"):
            if name in possibility and not valid_possibility_list(possibility[name]):
                errors.append(f"possibility_field.{name} must be a list of strings or objects")

    if integration_handoff is not None:
        if not isinstance(integration_handoff, dict):
            errors.append("integration_handoff must be an object or null")
        else:
            for field_name in (
                "active_object",
                "desired_result",
                "expected_contribution",
                "return_relation",
            ):
                if not _nonempty(integration_handoff.get(field_name)):
                    errors.append(
                        f"integration_handoff.{field_name} must be non-empty"
                    )
            for field_name in ("source_refs", "retained_unknowns"):
                entries = integration_handoff.get(field_name)
                if not isinstance(entries, list) or not all(
                    _nonempty(entry) for entry in entries
                ):
                    errors.append(
                        f"integration_handoff.{field_name} must be a string list"
                    )
            if "effect_boundary" not in integration_handoff or not isinstance(
                integration_handoff.get("effect_boundary"), (dict, type(None))
            ):
                errors.append(
                    "integration_handoff.effect_boundary must be an object or null"
                )

    if status == "configured" and not errors:
        if not _nonempty(operator.get("current_intent")):
            missing_decisions.append("operator_relation.current_intent")
        if not _nonempty(operator.get("intent_source")):
            missing_decisions.append("operator_relation.intent_source")
        if not _nonempty(operator.get("point_of_view")):
            missing_decisions.append("operator_relation.point_of_view")
        if operator.get("direction_status") not in {"selected", "open_reviewed"}:
            missing_decisions.append("operator_relation.direction_status")
        if not _nonempty(result.get("current")):
            missing_decisions.append("result.current")
        # A proof plan is optional: configuration also serves explanations,
        # methods and open inquiry, not only hypotheses requiring an experiment.
        if proof.get("result") is not None and proof.get("result") not in {
            "unverified", "verified_improvement", "no_change", "regression", "tradeoff"
        }:
            errors.append("unsupported first_proof.result")
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


def _contact_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("contact time must be a timezone-qualified timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("contact time must include a timezone")
    return result


def _validate_source_contact(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("source_contact must be an object")
        return
    for key in ("last_attempt", "last_success"):
        if key not in value:
            errors.append("source_contact." + key + " is missing")
        item = value.get(key)
        if item is None:
            continue
        if not isinstance(item, dict):
            errors.append("source_contact." + key + " must be an observation or null")
            continue
        try:
            _contact_time(item.get("observed_at"))
        except ValueError as exc:
            errors.append(str(exc))
        if (item.get("status") not in {"observed", "unavailable"}
                or not _nonempty(item.get("summary"))
                or (item.get("status") == "observed" and not _nonempty(item.get("source_identity")))
                or (item.get("status") == "unavailable" and item.get("source_identity") is not None)
                or (key == "last_success" and item.get("status") != "observed")):
            errors.append("invalid source_contact." + key)
    attempt, success = value.get("last_attempt"), value.get("last_success")
    if isinstance(attempt, dict) and attempt.get("status") == "observed" and success != attempt:
        errors.append("successful source contact must preserve the same last_success")
    if success is not None:
        try:
            if attempt is None or _contact_time(success["observed_at"]) > _contact_time(attempt["observed_at"]):
                errors.append("source contact chronology is inconsistent")
        except (KeyError, TypeError, ValueError):
            errors.append("source contact chronology is invalid")


def source_contact_status(root: Path, at: str | None = None) -> dict[str, Any]:
    state = current_configuration(root)
    contact = state["source_contact"]
    now = _contact_time(at) if at is not None else datetime.now(timezone.utc)
    attempt = contact["last_attempt"]
    due_at = _contact_time(attempt["observed_at"]) + timedelta(days=7) if attempt else None
    return {"schema": "maios.source-contact-status.v1", "state_owner": "setup/CONFIGURATION_STATE.json#source_contact",
            **contact, "configuration_sha256": digest(state),
            "ordinary_contact_due": due_at is None or now >= due_at,
            "next_ordinary_contact_at": due_at.isoformat() if due_at else None,
            "pending": bool(attempt and attempt["status"] == "unavailable"),
            "claim_boundary": "a due contact is for an active reentry; this command performs no network call or background work"}


def record_source_contact(root: Path, observation: Any, expected_state_sha256: str) -> dict[str, Any]:
    current = current_configuration(root)
    if not isinstance(observation, dict):
        raise ConfigurationError("source contact observation must be an object")
    candidate = json.loads(json.dumps(current))
    previous = current["source_contact"]["last_attempt"]
    candidate["source_contact"]["last_attempt"] = observation
    if observation.get("status") == "observed":
        candidate["source_contact"]["last_success"] = observation
    errors: list[str] = []
    _validate_source_contact(candidate["source_contact"], errors)
    if errors:
        raise ConfigurationError("invalid source contact: " + "; ".join(errors))
    if previous and _contact_time(observation["observed_at"]) < _contact_time(previous["observed_at"]):
        raise ConfigurationError("source contact cannot move its observation time backwards")
    candidate["checkpoint"] = {"sequence": current["checkpoint"]["sequence"] + 1,
                               "updated_at": observation["observed_at"], "summary": observation["summary"]}
    return apply_configuration(root, candidate, expected_state_sha256)


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
        "integration_handoff": state.get("integration_handoff"),
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
        "integration_handoff": state.get("integration_handoff"),
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
        f"intent_source: {state['operator_relation'].get('intent_source') or 'not yet qualified'}",
        f"current_result: {result.get('current') or 'pending'}",
        *([f"owner_review: {result['owner_review']}"] if result.get("owner_review") else []),
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
            f"Intent source: {state['operator_relation'].get('intent_source') or 'not yet qualified'}",
            f"Result: {result.get('current') or 'pending'}",
            *[
                f"{label}: {value}"
                for label, value in (
                    ("Beneficiary", result.get("beneficiary")),
                    ("Value mechanism", result.get("value_mechanism")),
                    ("Smallest deliverable", result.get("smallest_deliverable")),
                    ("First proof", proof.get("statement")),
                    ("Falsifiable test", proof.get("falsifiable_test")),
                )
                if value
            ],
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
    try:
        state = current_configuration(root)
    except ConfigurationError as exc:
        return {"schema": "maios.configuration-status.v2", "valid": False,
                "errors": [str(exc)], "handoff_ready": False,
                "recovery_required": True, "configuration_sha256": None,
                "pending_journals": pending_transitions(root)}
    validation = validate_configuration(state)
    capsule_path = root / ".maios" / "context" / "CONTEXT_CAPSULE.json"
    spec_path = root / ".maios" / "context" / "SETUP_SPEC.json"
    ensure_project_local(root, capsule_path)
    ensure_project_local(root, spec_path)
    expected_capsule = context_capsule(root, state)
    expected_spec = setup_spec(state, expected_capsule)
    return {
        "schema": "maios.configuration-status.v2",
        "setup_status": state["setup_status"],
        "revision": state["checkpoint"]["sequence"],
        "configuration_sha256": digest(state),
        "valid": validation["valid"] and not pending_transitions(root),
        "pending_journals": pending_transitions(root),
        "handoff_ready": validation["handoff_ready"],
        "integration_handoff_present": state.get("integration_handoff") is not None,
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
    root: Path, candidate: Any, expected_state_sha256: str, *, _within_resultant: bool = False
) -> dict[str, Any]:
    root = root.resolve()
    require_no_pending_transition(root, "resultant" if _within_resultant else None)
    validation = validate_configuration(candidate)
    if not validation["valid"]:
        raise ConfigurationError("invalid candidate: " + "; ".join(validation["errors"]))
    current = current_configuration(root)
    before_sha256 = digest(current)
    if expected_state_sha256 != before_sha256:
        raise ConfigurationError("configuration changed after review; re-read and re-evaluate")
    if (not _within_resultant
            and candidate["faculty_composition"].get("last_readback")
            != current["faculty_composition"].get("last_readback")):
        raise ConfigurationError("last_readback is maintained by apply-resultant; preserve the current event reference")
    after_sha256 = digest(candidate)
    if after_sha256 == before_sha256:
        return {"schema": RECEIPT_SCHEMA, "status": "idempotent",
                "before_state_sha256": before_sha256, "after_state_sha256": after_sha256,
                "revision": candidate["checkpoint"]["sequence"],
                "last_transition_receipt": ".maios/receipts/configuration/CURRENT.json",
                "global_writes": [], "external_effect_claimed": False}
    with state_transaction(root, "configuration", CONFIGURATION_OUTPUTS,
                           allowed_owner="resultant" if _within_resultant else None):
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
    # An older validator may have accepted the exact state being recovered.
    # The receipt still binds its bytes; ordinary edits retain strict reading.
    ensure_project_local(root, configuration_path(root))
    current = read_json(configuration_path(root))
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
    validation = validate_configuration(prior)
    if not validation["valid"]:
        raise ConfigurationError("invalid recovery configuration: " + "; ".join(validation["errors"]))
    outputs = (*CONFIGURATION_OUTPUTS, ".maios/receipts/configuration/RECOVERY.json")
    with state_transaction(root, "configuration", outputs):
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
