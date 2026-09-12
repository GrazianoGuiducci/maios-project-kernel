from __future__ import annotations

import copy
import json
import subprocess
import sys

import test_builder_installer_runtime as base
from maios_project_kernel import configuration, operating


class ConfigurationReaderContractTests(base.DistributionFixture):
    def event(self, event_id):
        return base.RuntimeTests.resultant_readback(self, event_id)

    def snapshot(self, target):
        return {str(p.relative_to(target)): p.read_bytes()
                for p in target.rglob("*") if p.is_file()}

    def test_invalid_event_reference_is_rejected_without_writes(self):
        target, _ = self.install()
        current = configuration.current_configuration(target)
        before = self.snapshot(target)
        for invalid in ("a narrative summary", [], False,
                        {"event_id": "missing-receipt"},
                        {"event_id": "../escape", "receipt": "../escape.json"}):
            with self.subTest(value=invalid):
                candidate = copy.deepcopy(current)
                candidate["checkpoint"]["sequence"] += 1
                candidate["faculty_composition"]["last_readback"] = invalid
                result = configuration.validate_configuration(candidate)
                self.assertFalse(result["valid"])
                self.assertIn("last_readback", " ".join(result["errors"]))
                with self.assertRaises(configuration.ConfigurationError):
                    configuration.apply_configuration(target, candidate, configuration.digest(current))
                self.assertEqual(before, self.snapshot(target))

    def test_configuration_cannot_clear_a_committed_event_reference(self):
        target, _ = self.install()
        event = self.event("existing-event")
        context = operating.operating_status(target, event["movement"]["circumstance"])
        operating.apply_resultant_readback(target, event, context["context_sha256"])
        current = configuration.current_configuration(target)
        candidate = copy.deepcopy(current)
        candidate["checkpoint"]["sequence"] += 1
        candidate["faculty_composition"]["last_readback"] = None
        before = self.snapshot(target)
        with self.assertRaisesRegex(configuration.ConfigurationError, "last_readback"):
            configuration.apply_configuration(target, candidate, configuration.digest(current))
        self.assertEqual(before, self.snapshot(target))

    def test_installed_diagnostics_report_legacy_invalid_state(self):
        target, _ = self.install()
        state = configuration.current_configuration(target)
        state["faculty_composition"]["last_readback"] = "legacy accepted narrative"
        configuration.write_json_atomic(configuration.configuration_path(target), state)
        before = self.snapshot(target)
        for command in ("status", "configuration-status", "operating-status"):
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, "-B", str(target / "maios.py"), command],
                                        cwd=target, capture_output=True, text=True)
                self.assertNotIn("Traceback", result.stderr)
                status = json.loads(result.stdout)
                self.assertFalse(status["valid"])
                self.assertIn("last_readback", " ".join(status["errors"]))
                if command == "operating-status":
                    self.assertTrue(status["recovery_required"])
                    self.assertEqual(status["eligible_actions"], [])
                    self.assertIsNone(status["context_sha256"])
        self.assertEqual(before, self.snapshot(target))

    def test_receipt_can_recover_state_accepted_by_an_older_validator(self):
        target, _ = self.install()
        prior = configuration.current_configuration(target)
        bad = copy.deepcopy(prior)
        bad["checkpoint"]["sequence"] += 1
        bad["faculty_composition"]["last_readback"] = "legacy accepted narrative"
        backup = ".maios/backups/configuration/legacy/CONFIGURATION_STATE.json"
        configuration.write_json_atomic(target / backup, prior)
        configuration.write_json_atomic(configuration.configuration_path(target), bad)
        receipt = {"schema": configuration.RECEIPT_SCHEMA, "backup_path": backup,
                   "before_state_sha256": configuration.digest(prior),
                   "after_state_sha256": configuration.digest(bad)}
        evolved = copy.deepcopy(bad)
        evolved["checkpoint"]["summary"] = "later work"
        configuration.write_json_atomic(configuration.configuration_path(target), evolved)
        with self.assertRaisesRegex(configuration.ConfigurationError, "evolved"):
            configuration.recover_configuration(target, receipt)
        configuration.write_json_atomic(configuration.configuration_path(target), bad)
        configuration.recover_configuration(target, receipt)
        self.assertEqual(configuration.current_configuration(target), prior)
        self.assertTrue(operating.continuum_status(target)["valid"])

    def test_structured_possibilities_survive_configuration_and_resultant(self):
        target, _ = self.install()
        current = configuration.current_configuration(target)
        keep = {"possibility": "Explore", "reason": {"source": "operator", "unknowns": ["scope"]}}
        remove = {"possibility": "Defer", "reason": "superseded"}
        opened = {"possibility": "Build", "reason": "new evidence"}
        candidate = copy.deepcopy(current)
        candidate["checkpoint"]["sequence"] += 1
        candidate["possibility_field"]["candidates"] = [keep, remove, "old option"]
        configuration.apply_configuration(target, candidate, configuration.digest(current))
        event = self.event("structured-possibilities")
        event["possibility_impact"] = {"opened": [opened], "preserved": [keep],
                                      "constrained": [], "eliminated": [remove, "old option"]}
        self.assertTrue(operating.validate_resultant_readback(target, event)["valid"])
        context = operating.operating_status(target, event["movement"]["circumstance"])
        operating.apply_resultant_readback(target, event, context["context_sha256"])
        result = configuration.current_configuration(target)["possibility_field"]
        self.assertEqual(result["candidates"], [keep])
        self.assertIn(keep, result["preserved"])
        self.assertIn(opened, result["opened"])
        self.assertIn(remove, result["eliminated"])
        self.assertTrue(operating.continuum_status(target)["valid"])
        conflict = copy.deepcopy(event)
        conflict["possibility_impact"]["opened"].append(copy.deepcopy(remove))
        self.assertFalse(operating.validate_resultant_readback(target, conflict)["valid"])

    def test_possibility_containers_are_validated_before_reader_use(self):
        target, _ = self.install()
        current = configuration.current_configuration(target)
        for value in ("one option", None, {"possibility": "not a list"}):
            with self.subTest(value=value):
                candidate = copy.deepcopy(current)
                candidate["possibility_field"]["candidates"] = value
                self.assertFalse(configuration.validate_configuration(candidate)["valid"])
                event = self.event("invalid-possibility-container")
                event["possibility_impact"]["eliminated"] = value
                self.assertFalse(operating.validate_resultant_readback(target, event)["valid"])
