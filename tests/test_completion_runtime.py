"""Receiver discriminants for the reviewed completion, not semantic assimilation."""
import copy
import json
from unittest.mock import patch
import test_builder_installer_runtime as base
from maios_project_kernel import builder, configuration, host, operating, runtime


class CompletionRuntimeTests(base.DistributionFixture):
    def event(self, name):
        return base.RuntimeTests.resultant_readback(self, name)

    def apply(self, target, event):
        context = operating.operating_status(target, event["movement"]["circumstance"])
        return operating.apply_resultant_readback(target, event, context["context_sha256"])

    def test_R01_explicit_empty_relations_survive_reentry(self):
        target, _ = self.install()
        event = self.event("empty-next")
        event["next_movement"]["relations"] = []
        self.apply(target, event)
        state = configuration.current_configuration(target)
        self.assertEqual(state["faculty_composition"]["circumstance_relations"], [])
        self.assertEqual(operating.operating_status(target)["composition"]["known_candidates"], [])
        self.assertTrue(operating.continuum_status(target)["valid"])

    def test_R02_opened_and_preserved_remove_current_elimination_keep_receipt(self):
        target, _ = self.install()
        first = self.event("eliminate")
        first["possibility_impact"]["eliminated"] = ["a", {"id": "b", "meaning": "second"}]
        self.apply(target, first)
        receipt = target / ".maios/receipts/resultant/eliminate.json"
        before = receipt.read_bytes()
        second = self.event("reopen")
        second["possibility_impact"]["opened"] = ["a"]
        second["possibility_impact"]["preserved"] = [{"id": "b", "meaning": "second"}]
        self.apply(target, second)
        eliminated = configuration.current_configuration(target)["possibility_field"]["eliminated"]
        self.assertNotIn("a", eliminated)
        self.assertNotIn({"id": "b", "meaning": "second"}, eliminated)
        self.assertEqual(receipt.read_bytes(), before)

    def test_R05_terminal_digest_binds_operating_state_but_not_living_bodies(self):
        target, _ = self.install()
        self.apply(target, self.event("first"))
        body = target / "skills/maios-project-system/SKILL.md"
        body.write_bytes(body.read_bytes() + b"\nLearned receiver-native distinction.\n")
        self.assertTrue(operating.continuum_status(target)["valid"])
        path = operating.operating_state_path(target)
        state = json.loads(path.read_text())
        state["causal_margin"]["current_movement"] = "unreceipted change"
        path.write_text(json.dumps(state))
        result = operating.continuum_status(target)
        self.assertFalse(result["valid"])
        self.assertTrue(any("current state digest" in e for e in result["errors"]))

    def test_C02_cold_receipts_are_auditable_and_current_reads_are_bounded(self):
        target, _ = self.install()
        for n in range(12):
            self.apply(target, self.event(f"event-{n}"))
        with patch.object(configuration, "terminal_receipt_errors", wraps=configuration.terminal_receipt_errors) as calls:
            current = operating.continuum_status(target)
            self.assertTrue(current["valid"], current)
            self.assertEqual(calls.call_count, 1)
        old = target / ".maios/receipts/resultant/event-0.json"
        original = old.read_bytes()
        old.write_text("corrupt cold receipt")
        self.assertTrue(operating.continuum_status(target)["valid"])
        audit = operating.continuum_status(target, deep=True)
        self.assertFalse(audit["valid"])
        self.assertTrue(audit["operational_valid"])
        self.assertFalse(audit["genealogical_valid"])
        self.assertEqual(old.read_text(), "corrupt cold receipt")
        selected = operating.continuum_status(target, circumstance={"knowledge_refs": [old.relative_to(target).as_posix()]})
        self.assertFalse(selected["valid"])
        with self.assertRaises(operating.OperatingStateError):
            self.apply(target, self.event("event-0"))
        old.write_bytes(original)
        self.assertTrue(operating.continuum_status(target, deep=True)["valid"])
        self.apply(target, self.event("next"))
        current_receipt = target / ".maios/receipts/resultant/next.json"
        current_receipt.unlink()
        self.assertFalse(operating.continuum_status(target)["valid"])

    def test_C02_explicit_current_cross_owner_dependency_is_required(self):
        target, _ = self.install()
        first = self.event("referencing")
        first["source_positions"]["verified_evidence"] = [".maios/receipts/host/missing.json"]
        before = operating.operating_state_path(target).read_bytes()
        with self.assertRaises(operating.OperatingStateError):
            self.apply(target, first)
        self.assertEqual(before, operating.operating_state_path(target).read_bytes())

    def test_C02_cold_learning_and_repeated_host_stage_preserve_history_without_blocking(self):
        import test_knowledge_continuation as knowledge
        target, _ = self.install()
        event = self.event("learn")
        event["learning_deltas"] = [knowledge.KnowledgeContinuationTests.learn(self, "a situated distinction")]
        relation = self.apply(target, event)["learning_relations"][0]
        cold = self.event("cool")
        cold["learning_transitions"] = [{"relation_id": relation, "status": "cooled",
            "reason": "no longer pertinent", "reentry_condition": "this distinction becomes pertinent again"}]
        self.apply(target, cold)
        self.apply(target, self.event("independent-work"))
        for event_id in ("host-first", "host-current"):
            attestation = base.RuntimeTests.host_attestation(self, event_id, "instruction_discovery", "generic")
            host.admit_host_attestation(target, attestation, host.digest(host.read_host_state(target)))
        before = operating.operating_state_path(target).read_bytes()
        for path in (".maios/receipts/resultant/learn.json", ".maios/receipts/host/host-first.json"):
            (target / path).unlink()
        self.assertTrue(operating.continuum_status(target)["valid"])
        self.assertFalse(operating.continuum_status(target, deep=True)["genealogical_valid"])
        self.assertEqual(before, operating.operating_state_path(target).read_bytes())
        self.assertEqual(operating.learning_status(target)["cold_count"], 1)

    def test_C01_resolved_inputs_and_existing_intent_source_are_sufficient(self):
        target, _ = self.install()
        prior = configuration.current_configuration(target)
        configured = copy.deepcopy(prior)
        configured["checkpoint"] = {"sequence": 1, "updated_at": "2026-09-20T20:00:00Z",
                                    "summary": "persist the operator relation"}
        configured["operator_relation"]["current_intent"] = "understand the current sources"
        configured["operator_relation"]["intent_source"] = "operator request retained at entry"
        configuration.apply_configuration(target, configured, configuration.digest(prior))
        first = self.event("knowledge")
        first["movement"]["circumstance"]["knowledge_refs"] = ["skills/maios-project-context/SKILL.md"]
        self.apply(target, first)
        configuration_state = configuration.current_configuration(target)
        circumstance = operating._default_circumstance(configuration_state)
        fallback = operating.operating_status(target)
        explicit = operating.operating_status(target, circumstance)
        self.assertEqual(fallback["context_sha256"], explicit["context_sha256"])
        refs = operating.read_operating_state(target)["active_knowledge_refs"]
        explicit_refs = operating.operating_status(target, dict(circumstance, knowledge_refs=refs))
        self.assertEqual(explicit["context_sha256"], explicit_refs["context_sha256"])
        cleared = operating.operating_status(target, dict(circumstance, knowledge_refs=[]))
        self.assertNotEqual(explicit["context_sha256"], cleared["context_sha256"])
        different = operating.operating_status(target, dict(circumstance, relations=[]))
        self.assertNotEqual(explicit["context_sha256"], different["context_sha256"])
        self.assertEqual(fallback["active_object"]["intent_source"], configuration_state["operator_relation"]["intent_source"])
        self.assertEqual(fallback["active_object"]["intent"], "understand the current sources")

    def test_current_catalogue_digest_and_general_owner_native_discovery(self):
        target, _ = self.install("codex")
        profile = json.loads((target / ".maios/kernel/PROJECT_ENTITY_PROFILE.json").read_text())
        catalog = profile["source_catalogs"][0]
        self.assertEqual(catalog["sha256"], builder.source_file_digest(target / catalog["installed_registry_path"]))
        for name in ("maios-system-understanding", "maios-possibility-formation", "maios-knowledge-acquisition", "maios-source-grounded-expression"):
            entry = target / f".agents/skills/{name}/SKILL.md"
            owner = f"skills/{name}/SKILL.md"
            self.assertIn(f"maios-knowledge-entry: {owner}", entry.read_text())
            self.assertIn(owner, operating.knowledge_status(target, [entry.relative_to(target).as_posix()])["files"])
        field = target / catalog["installed_registry_path"]
        value = json.loads(field.read_text())
        value["new_learning"] = "requires a current profile identity"
        field.write_text(json.dumps(value))
        self.assertIn("Project Entity Profile catalog identity is stale", runtime.validate_project(target)["errors"])
