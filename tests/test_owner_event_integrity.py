from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import test_builder_installer_runtime as base
from maios_project_kernel import host, installer, operating, runtime


class OwnerEventIntegrityTests(base.DistributionFixture):
    """Review of 3.1.2: accepted bodies and the latest owner transition."""

    def owner_case(self, owner, name):
        target = self.base / name
        installer.apply_plan(self.distribution, installer.make_plan(
            self.distribution, target, "new_repository", "generic"))
        if owner == "host":
            event = base.RuntimeTests.host_attestation(self, "first", "instruction_discovery", "generic")
            state_path = host.host_state_path(target)
        else:
            event = base.RuntimeTests.competence_delta(self)
            event["event_id"] = "first"
            body = target / event["knowledge_entry"]
            body.parent.mkdir(parents=True, exist_ok=True)
            body.write_text("# Living competence\nInitial method.\n", encoding="utf-8")
            state_path = runtime.competence_index_path(target)
        return target, event, state_path

    def command(self, target, *args):
        result = subprocess.run([sys.executable, "-I", "-B", str(target / "maios.py"), *args],
                                cwd=target, capture_output=True, text=True)
        if result.returncode and not result.stdout:
            self.assertIn("ERROR:", result.stderr)
            return result.returncode, {"error": result.stderr.strip()}
        self.assertTrue(result.stdout, result.stderr)
        return result.returncode, json.loads(result.stdout)

    def admit(self, target, owner, event, state_path):
        event_path = target / "review-event.json"
        event_path.write_text(json.dumps(event), encoding="utf-8")
        state_hash = host.digest(json.loads(state_path.read_text(encoding="utf-8")))
        command, payload, expected = (
            ("admit-host-attestation", "--attestation", "--expected-state-sha256") if owner == "host" else
            ("admit-competence-delta", "--delta", "--expected-index-sha256"))
        return self.command(target, command, payload, str(event_path), expected, state_hash)

    def check_recovery(self, target, owner, event, state_path):
        before = state_path.read_bytes()
        _, status = self.command(target, owner + "-status")
        self.assertFalse(status["valid"], status)
        self.assertTrue(status["recovery_required"])
        self.assertFalse(self.command(target, "status")[1]["valid"])
        self.assertTrue(self.command(target, "operating-status")[1]["recovery_required"])
        code, result = self.admit(target, owner, event, state_path)
        self.assertNotEqual(code, 0, result)
        self.assertEqual(state_path.read_bytes(), before)

    def test_internal_metadata_names_are_rejected_before_any_owner_write(self):
        for owner in ("host", "competence"):
            for field, value in (("sequence", 42), ("event_digest", "caller value")):
                with self.subTest(owner=owner, field=field):
                    target, event, state_path = self.owner_case(owner, owner + field)
                    event[field] = value
                    before = state_path.read_bytes()
                    code, result = self.admit(target, owner, event, state_path)
                    self.assertNotEqual(code, 0, result)
                    self.assertIn(field, str(result))
                    self.assertEqual(state_path.read_bytes(), before)
                    self.assertFalse((target / f".maios/receipts/{owner}").exists())
                    self.assertTrue(self.command(target, "status")[1]["valid"])
        schema = json.loads((base.ROOT / "schemas/COMPETENCE_DELTA.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(schema["additionalProperties"])
        for field in ("sequence", "event_digest"):
            self.assertIs(schema["properties"].get(field), False)

    def test_extensions_survive_admission_and_fresh_replay(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, event, state_path = self.owner_case(owner, owner)
                event["custom_note"] = {"sequence": 42, "event_digest": "domain-owned nested data"}
                self.assertEqual(self.admit(target, owner, event, state_path)[1]["status"], "admitted")
                self.assertTrue(self.command(target, "status")[1]["valid"])
                history = json.loads(state_path.read_text(encoding="utf-8"))[
                    "attestation_history" if owner == "host" else "history"]
                body = {k: v for k, v in history[-1].items() if k not in ("event_digest", "sequence")}
                self.assertEqual(body, event)
                self.assertEqual(self.admit(target, owner, event, state_path)[1]["status"], "idempotent")

    def test_unrecorded_current_projection_is_detected_at_reentry_and_retry(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, event, state_path = self.owner_case(owner, owner)
                self.assertEqual(self.admit(target, owner, event, state_path)[1]["status"], "admitted")
                state = json.loads(state_path.read_text(encoding="utf-8"))
                if owner == "host":
                    state["observed_capabilities"].append("network access")
                else:
                    state["active"][event["competence_id"]]["activation_relations"].append("unrecorded relation")
                state_path.write_text(json.dumps(state), encoding="utf-8")
                self.check_recovery(target, owner, event, state_path)
                if owner == "host":
                    status = self.command(target, "host-status")[1]
                    self.assertNotIn("network access", status["observed_capabilities"])
                    self.assertIn("network access", status["unverified_capabilities"])
                    context = self.command(target, "operating-status")[1]
                    self.assertNotIn("network access", context["host"]["observed_capabilities"])
                    self.assertFalse(any(c["id"] == "network access" and c["state"] == "verified_observed"
                                         for c in context["capability_relations"]))

    def test_latest_after_hash_is_checked_against_current_owner_state(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, event, state_path = self.owner_case(owner, owner)
                self.admit(target, owner, event, state_path)
                receipt_path = target / f".maios/receipts/{owner}/first.json"
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt["after_state_sha256" if owner == "host" else "after_index_sha256"] = "0" * 64
                receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
                self.check_recovery(target, owner, event, state_path)

    def test_latest_event_relation_cannot_disappear_with_its_history(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, event, state_path = self.owner_case(owner, owner)
                self.admit(target, owner, event, state_path)
                state = json.loads(state_path.read_text(encoding="utf-8"))
                state["attestation_history" if owner == "host" else "history"] = []
                state_path.write_text(json.dumps(state), encoding="utf-8")
                self.check_recovery(target, owner, event, state_path)

    def test_historical_replay_and_living_knowledge_survive_later_evolution(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, event, state_path = self.owner_case(owner, owner)
                self.assertEqual(self.admit(target, owner, event, state_path)[1]["status"], "admitted")
                original_receipt = (target / f".maios/receipts/{owner}/first.json").read_bytes()
                second = copy.deepcopy(event)
                second["event_id"] = "second"
                if owner == "host":
                    second["stage"] = "state_read"
                else:
                    second["disposition"] = "revise"
                    second["supersedes_event_id"] = "first"
                    body = target / second["knowledge_entry"]
                    body.write_text("# Living competence\nA useful learned difference.\n", encoding="utf-8")
                    self.assertTrue(self.command(target, "status")[1]["valid"])
                self.assertEqual(self.admit(target, owner, second, state_path)[1]["status"], "admitted")
                self.assertTrue(self.command(target, "status")[1]["valid"])
                self.assertEqual(self.admit(target, owner, event, state_path)[1]["status"], "idempotent")
                self.assertEqual((target / f".maios/receipts/{owner}/first.json").read_bytes(), original_receipt)
                # A different owner may evolve independently of this owner's latest receipt.
                candidate = base.RuntimeTests.resultant_readback(self, "resultant-after")
                context = operating.operating_status(target, candidate["movement"]["circumstance"])
                operating.apply_resultant_readback(target, candidate, context["context_sha256"])
                self.assertTrue(self.command(target, "status")[1]["valid"])
