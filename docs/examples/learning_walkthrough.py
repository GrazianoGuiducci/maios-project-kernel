"""Illustrative local contracts, not a receiving-model learning experiment."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from maios_project_kernel import builder, installer, operating  # noqa: E402

BODY = "skills/data-import/SKILL.md"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def rejected(rows, method):
    if method == "header":
        return [i for i, row in enumerate(rows) if "record_id" not in row]
    if method == "false-value":
        return [i for i, row in enumerate(rows) if not row.get("record_id")]
    return [i for i, row in enumerate(rows)
            if row.get("record_id") is None or
            (isinstance(row["record_id"], str) and not row["record_id"].strip())]


def write_json(target, path, value):
    destination = target / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def learning(summary, future):
    return {
        "owner": {"kind": "competence", "id": "data-import", "owner": BODY},
        "what_happened": summary,
        "causal_delta": future,
        "why_it_matters": "Column presence and usable identifiers are different checks.",
        "future_behavior": future,
        "source_refs": ["project/import-requirements.md", "project/import-A.json"],
        "activation_relations": ["data_import"],
        "invalidator": "A valid identifier is rejected or a missing identifier is accepted.",
        "reentry_condition": "A later import needs required-value validation.",
    }


def event(event_id, summary, evidence, relation_id=None):
    selected = [] if relation_id is None else [{
        "id": relation_id, "reason": "Inspect the earlier rule in this fixture.",
        "expected_delta": "Distinguish missing values from valid identifiers.",
    }]
    return {
        "schema": "maios.resultant-readback.v3", "event_id": event_id,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "movement": {
            "circumstance": {"relations": ["data_import"], "case": event_id,
                             "knowledge_refs": [BODY], "effect": None},
            "selected_faculties": selected, "effect_boundary": None,
        },
        "source_positions": {
            "operator_source": ["Documentation fixture; no supplier or receiving LLM."],
            "verified_evidence": evidence,
            "model_inference": [],
            "retained_unknowns": ["Receiving-model participation and assimilation are unobserved."],
        },
        "candidate_resultant": {"summary": summary},
        "preprojection_readback": {"status": "preserved", "description":
            "Keep scripted validator execution separate from agent learning.", "corrections": []},
        "actual_result": {"status": "completed", "classification": "unverified",
                          "summary": summary, "evidence_refs": evidence},
        "faculty_deltas": [] if relation_id is None else [{
            "faculty_id": relation_id, "description": summary, "classification": "unverified"}],
        "possibility_impact": {k: [] for k in ("opened", "preserved", "constrained", "eliminated")},
        "next_movement": {"current_next": "Inspect another situated import if useful.",
            "reason": "This fixture does not establish general adequacy.",
            "reentry_condition": "Another relevant import occurs.", "relations": ["data_import"]},
        "effect": {"status": "none", "boundary": None, "receipt_refs": []},
        "causal_margin": {
            "operator_relation": "Illustrate existing local contracts.",
            "selected_object": "Required record identifiers in sample imports.",
            "owner_surface": BODY, "last_faithful_resultant": summary,
            "current_movement": summary, "next_movement": "Inspect another situated import if useful.",
            "supersession_condition": "New requirement or counterexample changes this rule.",
        },
        "learning_deltas": [],
    }


def apply(target, readback):
    validation = operating.validate_resultant_readback(target, readback)
    require(validation["valid"], str(validation["errors"]))
    context = operating.operating_status(target, readback["movement"]["circumstance"])
    require(not context["recovery_required"], str(context["continuum"]))
    return operating.apply_resultant_readback(target, readback, context["context_sha256"])


def relations(target):
    return {r["relation_id"]: r for r in
            operating.learning_status(target, include_cold=True)["relations"]}


def candidates(target):
    return {r["id"] for r in operating.compose(target, {"relations": ["data_import"]})["known_candidates"]}


def main():
    with tempfile.TemporaryDirectory(prefix="mpk-learning-example-") as directory:
        base = Path(directory)
        distribution, target = base / "distribution", base / "project"
        builder.render_distribution(ROOT, distribution)
        verification = builder.verify_distribution(ROOT, distribution)
        require(verification["valid"], str(verification["errors"]))
        plan = installer.make_plan(distribution, target, "new_repository", "generic")
        require(plan["status"] == "ready", str(plan))
        installer.apply_plan(distribution, plan)

        body = target / BODY
        body.parent.mkdir(parents=True, exist_ok=True)
        body.write_text("# Data import — illustrative v0\n\nInspect required column presence.\n", encoding="utf-8")
        (target / "project/import-requirements.md").write_text(
            "# Fixture requirements\n\nrecord_id is required. Numeric zero is valid. Null and blank strings are missing.\n",
            encoding="utf-8")
        a = [{"record_id": "A-1"}, {"record_id": None}]
        b = [{"record_id": 0}, {"record_id": "  "}, {"record_id": None}]
        c = [{"record_id": "0"}, {"record_id": ""}, {"record_id": " "}, {"record_id": None}]
        observations = {}
        for name, rows in (("A", a), ("B", b), ("C", c)):
            observations[name] = {m: rejected(rows, m) for m in ("header", "false-value", "qualified")}
            write_json(target, "project/import-" + name + ".json",
                       {"fixture": True, "rows": rows, "rejected_zero_based_rows": observations[name]})
        require(observations["A"]["header"] == [] and observations["A"]["false-value"] == [1], "Import A mismatch")
        require(observations["B"]["false-value"] == [0, 2] and observations["B"]["qualified"] == [1, 2], "Import B mismatch")
        require(observations["C"]["qualified"] == [1, 2, 3], "Import C mismatch")

        body.write_text("# Data import — illustrative v1\n\nInspect required values using a provisional false-value rule. Reconsider when a valid identifier is rejected or a missing one accepted.\n", encoding="utf-8")
        snapshots = target / "project/method-history"
        snapshots.mkdir()
        (snapshots / "v1.md").write_bytes(body.read_bytes())
        first = event("import-A", "The provisional rule rejects the null identifier in A.", ["project/import-A.json", "project/method-history/v1.md"])
        first["learning_deltas"] = [learning(first["actual_result"]["summary"], "Inspect values; false-value handling remains provisional.")]
        first["learning_deltas"][0]["source_refs"].append("project/method-history/v1.md")
        l1 = apply(target, first)["learning_relations"][0]
        require(l1 in candidates(target) and relations(target)[l1]["later_uses"] == [], "Availability is not use")

        use = event("import-B", "The first rule rejects valid zero and accepts whitespace in B.", ["project/import-B.json", "project/method-history/v1.md"], l1)
        apply(target, use)
        require(len(relations(target)[l1]["later_uses"]) == 1, "L1 use not preserved")

        body.write_text("# Data import — illustrative v2\n\nCheck values as well as columns. A value is missing if null or a string empty after trimming. Numeric zero is valid under the fixture requirements. Reconsider when requirements change.\n", encoding="utf-8")
        (snapshots / "v2.md").write_bytes(body.read_bytes())
        revision = event("revise-after-B", "Qualify the rule after B's counterexample.", ["project/import-B.json", BODY])
        successor = learning(revision["actual_result"]["summary"], "Reject null and trimmed-empty strings; accept valid numeric zero.")
        successor.update(source_refs=["project/import-requirements.md", "project/import-B.json", "project/method-history/v2.md"],
                         supersedes=[l1], supersession_reason="The false-value rule fails B's identifier requirements.")
        revision["learning_deltas"] = [successor]
        l2 = apply(target, revision)["learning_relations"][0]
        require(relations(target)[l1]["status"] == "superseded" and
                relations(target)[l2]["later_uses"] == [], "Successor inherited predecessor proof")
        apply(target, event("import-C", "The qualified validator accepts string zero and rejects C's missing identifiers.", ["project/import-C.json", "project/method-history/v2.md"], l2))
        require(relations(target)[l2]["later_nonidentical_use_observed"], "Different circumstance not recorded")

        for status in ("retired", "reachable"):
            transition = event("L2-" + status, "Illustrate recall state " + status + ".", [BODY])
            transition["learning_transitions"] = [{"relation_id": l2, "status": status,
                "reason": "Fixture lifecycle operation, not a supplier event.",
                "reentry_condition": "A source-qualified decision makes this rule useful again."}]
            apply(target, transition)
            require((l2 in candidates(target)) == (status == "reachable"), "Recall state mismatch")
        final = relations(target)
        require(len(final[l1]["later_uses"]) == 1 and len(final[l2]["later_uses"]) == 1, "Use evidence lost")
        audit = operating.continuum_status(target, deep=True)
        require(audit["valid"], str(audit["errors"]))
        return {"fixture_only": True, "receiving_llm_exercised": False,
                "sample_rejected_rows": observations,
                "L1": {"id": l1, "status": final[l1]["status"], "later_uses": len(final[l1]["later_uses"])},
                "L2": {"id": l2, "status": final[l2]["status"], "later_uses": len(final[l2]["later_uses"])},
                "local_continuum_valid": audit["valid"],
                "claim": "Scripted sample outcomes and local contract transitions; LLM assimilation unobserved."}


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
