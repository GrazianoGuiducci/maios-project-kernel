from __future__ import annotations

import json
import subprocess
import sys

import test_builder_installer_runtime as base
import test_owner_event_integrity as integrity


class InitialOwnerStateTests(base.DistributionFixture):
    owner_case = integrity.OwnerEventIntegrityTests.owner_case
    command = integrity.OwnerEventIntegrityTests.command
    admit = integrity.OwnerEventIntegrityTests.admit

    def test_equivalent_root_spelling_preserves_receipt_and_pending_readback(self):
        script = """
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / '.maios/runtime'))
import configuration, host, kernel
owner = sys.argv[2]
result = host.host_status(root) if owner == 'host' else kernel.competence_status(root)
relative = '.maios/receipts/' + owner + '/first.json'
try:
    configuration.project_local_file(root, root / '..' / root.name / relative)
except configuration.ConfigurationError:
    result['child_traversal_rejected'] = True
else:
    result['child_traversal_rejected'] = False
print(json.dumps(result))
"""
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, event, path = self.owner_case(owner, "root-spelling-" + owner)
                self.assertEqual(self.admit(target, owner, event, path)[1]["status"], "admitted")
                # Both roots select the same directory; descendants must still
                # be checked before following links or parent traversals.
                alias = target / ".." / target.name
                process = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(alias), owner],
                                         capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
                result = json.loads(process.stdout)
                self.assertTrue(result["valid"], result)
                self.assertFalse(result["recovery_required"])
                self.assertTrue(result["child_traversal_rejected"])

    def assert_unrecorded_claim_rejected(self, target, owner, event, state_path):
        before = state_path.read_bytes()
        status = self.command(target, owner + "-status")[1]
        general = self.command(target, "status")[1]
        context = self.command(target, "operating-status")[1]
        code, result = self.admit(target, owner, event, state_path)
        after = self.command(target, owner + "-status")[1]
        with self.subTest(check="initial readback"):
            self.assertFalse(status["valid"], status)
            self.assertTrue(status["recovery_required"])
            self.assertFalse(general["valid"])
            self.assertTrue(context["recovery_required"])
        with self.subTest(check="first admission cannot absorb unrecorded claims"):
            self.assertNotEqual(code, 0, result)
            self.assertIn("recovery required", str(result))
            self.assertEqual(state_path.read_bytes(), before)
            self.assertFalse((target / f".maios/receipts/{owner}").exists())
            self.assertFalse(after["valid"])
        if owner == "host":
            with self.subTest(check="unverified host projection"):
                self.assertEqual(status["observed_capabilities"], [])
                self.assertEqual(context["host"]["observed_capabilities"], [])
                for stage in base.host.STAGE_FIELDS:
                    self.assertEqual(status[stage], "unverified")

    def test_unattested_initial_capability_cannot_be_absorbed_by_first_receipt(self):
        target, event, path = self.owner_case("host", "initial-capability")
        state = json.loads(path.read_text(encoding="utf-8"))
        state["observed_capabilities"].append("network access")
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_unrecorded_claim_rejected(target, "host", event, path)

    def test_initial_stage_and_evidence_claims_cannot_satisfy_prerequisites(self):
        mutations = [(stage, result) for stage in base.host.STAGE_FIELDS
                     for result in ("verified", "failed")]
        mutations.append(("evidence", ["unrecorded-observation"]))
        for number, (field, value) in enumerate(mutations):
            with self.subTest(field=field, value=value):
                target, event, path = self.owner_case("host", f"initial-stage-{number}")
                state = json.loads(path.read_text(encoding="utf-8"))
                state[field] = value
                path.write_text(json.dumps(state), encoding="utf-8")
                if field == "behavioral_activation" and value == "verified":
                    event["stage"] = "maintained_reentry"
                self.assert_unrecorded_claim_rejected(target, "host", event, path)

    def test_unadmitted_initial_competence_cannot_be_absorbed_by_another_event(self):
        target, event, path = self.owner_case("competence", "initial-active")
        state = json.loads(path.read_text(encoding="utf-8"))
        state["active"]["unrecorded"] = {
            **event, "event_id": "unrecorded-event",
            "classification": "verified_improvement",
        }
        path.write_text(json.dumps(state), encoding="utf-8")
        self.assert_unrecorded_claim_rejected(target, "competence", event, path)
        # State recovery does not make its independently readable method disappear.
        knowledge = self.command(target, "knowledge-status", "--path", event["knowledge_entry"])[1]
        self.assertEqual(knowledge["files"][event["knowledge_entry"]]["status"], "present")

    def test_initial_extensions_unknowns_and_living_methods_remain_open(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, event, path = self.owner_case(owner, "initial-open-" + owner)
                state = json.loads(path.read_text(encoding="utf-8"))
                state["local_context"] = {"verified": "a domain term, not a host-stage claim"}
                if owner == "host":
                    state["unverified_capabilities"].append("future device interface")
                    event["result"] = "failed"  # A genuinely recorded first failure is lawful.
                else:
                    state["retained_unknowns"].append("future coordination mechanism")
                    state["represented"]["readable-method"] = {
                        k: event[k] for k in ("knowledge_entry", "work_relation",
                                             "activation_relations", "expected_delta")
                    }
                path.write_text(json.dumps(state), encoding="utf-8")
                self.assertTrue(self.command(target, "status")[1]["valid"])
                self.assertEqual(self.admit(target, owner, event, path)[1]["status"], "admitted")
                self.assertTrue(self.command(target, "status")[1]["valid"])
                self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["local_context"], state["local_context"])
                if owner == "competence":
                    body = target / event["knowledge_entry"]
                    body.write_text("# Method evolved through another useful case.\n", encoding="utf-8")
                    self.assertTrue(self.command(target, "status")[1]["valid"])
