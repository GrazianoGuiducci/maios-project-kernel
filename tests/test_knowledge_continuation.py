from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import test_builder_installer_runtime as base

from maios_project_kernel import builder, configuration, host, operating


class KnowledgeContinuationTests(base.DistributionFixture):
    def event(self, event_id):
        return base.RuntimeTests.resultant_readback(self, event_id)

    def learn(self, meaning, owner_id="design", surface="project/design"):
        return {
            "owner": {"kind": "competence", "id": owner_id, "owner": surface},
            "what_happened": meaning,
            "causal_delta": meaning,
            "why_it_matters": "preserve the useful distinction for future work",
            "future_behavior": meaning,
            "source_refs": ["project/notes.md"],
            "activation_relations": ["design_reentry"],
            "invalidator": "the source or a later result changes this distinction",
            "reentry_condition": "the design relation becomes pertinent",
        }

    def apply(self, target, event):
        context = operating.operating_status(target, event["movement"]["circumstance"])
        return operating.apply_resultant_readback(target, event, context["context_sha256"])

    def test_learning_coexists_without_forcing_the_next_field(self):
        target, _ = self.install()
        event = self.event("coexist")
        event["next_movement"]["relations"] = ["unrelated_next_work"]
        event["learning_deltas"] = [
            self.learn("first aspect", "a/b"),
            self.learn("second aspect", "a/b"),
            self.learn("first aspect", "a b"),
            self.learn("first aspect", "a/b", "another/project"),
        ]
        receipt = self.apply(target, event)
        self.assertEqual(len(set(receipt["learning_relations"])), 4)
        self.assertEqual(operating.learning_status(target)["count"], 4)
        next_field = operating.operating_status(target, {"relations": ["unrelated_next_work"]})
        self.assertFalse(any(x["kind"] == "competence_learning_relation"
                             for x in next_field["composition"]["known_candidates"]
                             if "kind" in x))
        later = operating.compose(target, {"relations": ["design_reentry"]})
        self.assertTrue(set(receipt["learning_relations"]).issubset(
            {x["id"] for x in later["known_candidates"]}))

    def test_supersession_and_cooling_preserve_revision_specific_evidence(self):
        target, _ = self.install()
        first = self.event("learn-a")
        first["learning_deltas"] = [self.learn("method A")]
        original_id = self.apply(target, first)["learning_relations"][0]
        use = self.event("use-a")
        use["movement"]["circumstance"]["relations"] = ["design_reentry"]
        use["movement"]["selected_faculties"] = [{
            "id": original_id, "reason": "the earlier distinction helps here",
            "expected_delta": "a different design decision",
        }]
        use["faculty_deltas"] = [{"faculty_id": original_id, "description": "A changed this later decision"}]
        self.apply(target, use)
        revised = self.event("learn-b")
        revised["learning_deltas"] = [dict(self.learn("method B"), supersedes=[original_id],
                                          supersession_reason="new evidence replaces only A")]
        successor_id = self.apply(target, revised)["learning_relations"][0]
        relations = {x["relation_id"]: x for x in operating.learning_status(target, include_cold=True)["relations"]}
        self.assertTrue(relations[original_id]["later_nonidentical_use_observed"])
        self.assertEqual(relations[original_id]["status"], "superseded")
        self.assertFalse(relations[successor_id]["later_nonidentical_use_observed"])
        self.assertEqual(relations[successor_id]["later_uses"], [])
        for status in ("cooled", "reachable", "retired"):
            transition = self.event("status-" + status)
            transition["learning_transitions"] = [{
                "relation_id": successor_id, "status": status,
                "reason": "the actual present relation changed",
                "reentry_condition": "new evidence makes this useful again",
            }]
            self.apply(target, transition)
            recalled = {x["id"] for x in operating.compose(target, {"relations": ["design_reentry"]})["known_candidates"]}
            self.assertEqual(successor_id in recalled, status == "reachable")
        self.assertEqual(operating.learning_status(target)["count"], 0)
        self.assertEqual(operating.learning_status(target, include_cold=True)["count"], 2)

    def test_live_native_entry_observes_changed_body_and_preserves_baseline(self):
        target, receipt = self.install("codex")
        entry = ".agents/skills/maios-project-context/SKILL.md"
        source = "skills/maios-project-context/SKILL.md"
        original = (target / source).read_bytes()
        baseline = copy.deepcopy(receipt["update_baseline"])
        observed = operating.knowledge_status(target, [entry])
        self.assertIn(source, observed["files"])
        event = self.event("knowledge-use")
        event["movement"]["circumstance"]["knowledge_refs"] = [entry]
        context = operating.operating_status(target, event["movement"]["circumstance"])
        (target / "unrelated.txt").write_text("another surface", encoding="utf-8")
        unchanged = operating.operating_status(target, event["movement"]["circumstance"])
        self.assertEqual(unchanged["context_sha256"], context["context_sha256"])
        (target / source).write_bytes(original + b"\nLearned source distinction.\n")
        current = operating.knowledge_status(target, [entry])
        self.assertNotEqual(current["files"][source], observed["files"][source])
        self.assertEqual(current["files"][entry], observed["files"][entry])
        with self.assertRaisesRegex(operating.OperatingStateError, "context changed"):
            operating.apply_resultant_readback(target, event, context["context_sha256"])
        self.assertEqual(receipt["update_baseline"], baseline)
        self.assertTrue(any(x["destination"] == source for x in baseline["files"]))
        result = subprocess.run([sys.executable, "-B", str(target / "maios.py"),
                                 "knowledge-status", "--path", entry], cwd=target, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(source, json.loads(result.stdout)["files"])
        with self.assertRaises(operating.OperatingStateError):
            operating.knowledge_status(target, ["../outside.md"])

    def test_failed_host_observation_retires_only_affected_capability(self):
        target, _ = self.install("codex")
        observed = base.RuntimeTests.host_attestation(self, "available", "instruction_discovery")
        observed["observed_capabilities"] = ["read_sources", "write_sources"]
        state = host.read_host_state(target)
        host.admit_host_attestation(target, observed, host.digest(state))
        failed = base.RuntimeTests.host_attestation(self, "changed-access", "instruction_discovery")
        failed.update(result="failed", observed_capabilities=[], invalidated_capabilities=["write_sources"])
        host.admit_host_attestation(target, failed, host.digest(host.read_host_state(target)))
        state = host.read_host_state(target)
        self.assertEqual(state["observed_capabilities"], ["read_sources"])
        self.assertIn("write_sources", state["unverified_capabilities"])
        projected = operating.operating_status(target)
        capability = next(x for x in projected["capability_relations"] if x["id"] == "write_sources")
        self.assertEqual(capability["state"], "unknown")
        self.assertEqual(len(state["attestation_history"]), 2)

    def test_historical_input_survives_live_field_evolution_but_not_tampering(self):
        isolated = self.base / "source"
        shutil.copytree(base.ROOT, isolated, ignore=shutil.ignore_patterns(".git", "package", "__pycache__"))
        field_path = isolated / "kernel/FACULTY_FIELD.json"
        field = json.loads(field_path.read_text(encoding="utf-8"))
        field["extension_rule"] += " A further situated relation."
        field_path.write_text(json.dumps(field), encoding="utf-8")
        builder.repokernel_projection_inputs(isolated)
        snapshot = isolated / "release/repokernel/input-snapshots/FACULTY_FIELD.json"
        snapshot.write_bytes(snapshot.read_bytes() + b" ")
        with self.assertRaisesRegex(builder.BuildError, "input digest drifted"):
            builder.repokernel_projection_inputs(isolated)

    def test_inferred_intent_keeps_its_source_in_working_projections(self):
        target, _ = self.install()
        state = configuration.current_configuration(target)
        state["operator_relation"]["current_intent"] = "improve source reconciliation"
        state["operator_relation"]["intent_source"] = "inferred from project notes; correctable"
        self.assertIn(state["operator_relation"]["intent_source"], configuration.current_state_markdown(state))
        self.assertIn(state["operator_relation"]["intent_source"], configuration.project_brief_markdown(state))
        context = operating._operating_status(target, configuration_override=state)
        self.assertEqual(context["active_object"]["intent_source"], state["operator_relation"]["intent_source"])
