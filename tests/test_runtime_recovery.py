from __future__ import annotations

import copy
import json
import subprocess
import sys
from unittest.mock import patch

import test_builder_installer_runtime as base
from maios_project_kernel import configuration, operating, runtime


class RuntimeRecoveryTests(base.DistributionFixture):
    def event(self, event_id):
        return base.RuntimeTests.resultant_readback(self, event_id)

    def snapshot(self, target):
        paths = ["setup/CONFIGURATION_STATE.json", ".maios/state/OPERATING_STATE.json",
                 ".maios/context/OPERATING_CONTEXT.json", ".maios/context/CONTEXT_CAPSULE.json",
                 ".maios/context/SETUP_SPEC.json", "project/CURRENT_STATE.md", "project/PROJECT_BRIEF.md",
                 ".maios/receipts/configuration/CURRENT.json"]
        return {p: (target / p).read_bytes() if (target / p).is_file() else None for p in paths}

    def test_installed_resultant_receipt_collision_leaves_continuum_unchanged(self):
        target, _ = self.install()
        event = self.event("receipt-collision")
        collision = target / ".maios/receipts/configuration/CURRENT.json"
        collision.mkdir(parents=True)
        before = self.snapshot(target)
        context = operating.operating_status(target, event["movement"]["circumstance"])
        readback = self.base / "readback.json"
        readback.write_text(json.dumps(event), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(target / "maios.py"), "apply-resultant",
                                 "--readback", str(readback), "--expected-context-sha256", context["context_sha256"]],
                                cwd=target, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, self.snapshot(target))
        self.assertFalse((target / ".maios/receipts/resultant/receipt-collision.json").exists())

    def test_caught_late_failures_restore_configuration_operating_projections_and_receipts(self):
        target, _ = self.install()
        first = self.event("first")
        context = operating.operating_status(target, first["movement"]["circumstance"])
        operating.apply_resultant_readback(target, first, context["context_sha256"])
        for owner in ("configuration", "resultant"):
            with self.subTest(owner=owner):
                event = self.event("late-" + owner)
                before = self.snapshot(target)
                context = operating.operating_status(target, event["movement"]["circumstance"])
                module = configuration if owner == "configuration" else operating
                original = module.write_json_atomic
                destination = (target / (".maios/receipts/configuration/CURRENT.json" if owner == "configuration"
                                         else ".maios/receipts/resultant/late-resultant.json")).resolve()
                def fail_after_write(path, value):
                    original(path, value)
                    if path.resolve() == destination:
                        raise OSError("injected failure after receipt replacement")
                with patch.object(module, "write_json_atomic", side_effect=fail_after_write):
                    with self.assertRaises(Exception):
                        operating.apply_resultant_readback(target, event, context["context_sha256"])
                self.assertEqual(before, self.snapshot(target))
                self.assertFalse((target / (".maios/receipts/resultant/" + event["event_id"] + ".json")).exists())
                self.assertTrue(runtime.validate_project(target)["valid"])

    def test_identical_configuration_preserves_last_recoverable_transition(self):
        target, _ = self.install()
        current = configuration.current_configuration(target)
        candidate = copy.deepcopy(current)
        candidate["checkpoint"]["sequence"] += 1
        candidate["checkpoint"]["summary"] = "one material transition"
        receipt = configuration.apply_configuration(target, candidate, configuration.digest(current))
        path = target / ".maios/receipts/configuration/CURRENT.json"
        before = self.snapshot(target)
        repeated = configuration.apply_configuration(target, candidate, configuration.digest(candidate))
        self.assertEqual(repeated["status"], "idempotent")
        self.assertEqual(before, self.snapshot(target))
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), receipt)
        configuration.recover_configuration(target, json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(configuration.current_configuration(target), current)

    def test_incomplete_rollback_is_visible_to_fresh_status_and_blocks_further_writes(self):
        target, _ = self.install()
        event = self.event("incomplete-rollback")
        context = operating.operating_status(target, event["movement"]["circumstance"])
        original = configuration.write_json_atomic
        destination = (target / ".maios/receipts/configuration/CURRENT.json").resolve()
        def fail_receipt(path, value):
            original(path, value)
            if path.resolve() == destination:
                raise OSError("receipt unavailable")
        with patch.object(configuration, "write_json_atomic", side_effect=fail_receipt), \
             patch.object(configuration, "write_bytes_atomic", side_effect=OSError("restore unavailable")):
            with self.assertRaisesRegex(configuration.ConfigurationError, "rollback incomplete"):
                operating.apply_resultant_readback(target, event, context["context_sha256"])
        result = subprocess.run([sys.executable, "-B", str(target / "maios.py"), "status"],
                                cwd=target, capture_output=True, text=True)
        self.assertFalse(json.loads(result.stdout)["valid"])
        self.assertTrue(configuration.pending_transitions(target))
        next_context = operating.operating_status(target)
        self.assertTrue(next_context["recovery_required"])
        with self.assertRaisesRegex(configuration.ConfigurationError, "recovery required"):
            configuration.apply_configuration(target, configuration.current_configuration(target),
                                              configuration.digest(configuration.current_configuration(target)))

    def test_reentry_detects_unlinked_configuration_event_without_a_journal(self):
        target, _ = self.install()
        current = configuration.current_configuration(target)
        orphan = operating._configuration_candidate(current, self.event("orphan"),
                                                     ".maios/receipts/resultant/orphan.json")
        configuration.write_json_atomic(configuration.configuration_path(target), orphan)
        configuration.project_state(target, orphan)
        self.assertFalse(runtime.validate_project(target)["valid"])
        self.assertTrue(operating.operating_status(target)["recovery_required"])
