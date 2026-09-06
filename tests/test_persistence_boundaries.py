from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_builder_installer_runtime as base
from maios_project_kernel import configuration, host, installer, operating, runtime


class PersistenceBoundaryTests(base.DistributionFixture):
    def event(self, event_id="one"):
        return base.RuntimeTests.resultant_readback(self, event_id)

    def apply_event(self, target, event):
        context = operating.operating_status(target, event["movement"]["circumstance"])
        return operating.apply_resultant_readback(target, event, context["context_sha256"])

    def new_target(self, name):
        target = self.base / name
        receipt = installer.apply_plan(self.distribution, installer.make_plan(
            self.distribution, target, "new_repository", "generic"))
        return target, receipt

    def owner_case(self, target, owner, event_id="owner-event"):
        if owner == "host":
            event = {"schema": "maios.host-attestation.v2", "event_id": event_id,
                     "host": "generic", "stage": "instruction_discovery", "result": "verified",
                     "observation": "fixture discovered instructions", "evidence_refs": ["fixture/discovery"],
                     "observed_capabilities": ["instruction_discovery"],
                     "review": {"status": "accepted", "reviewer": "operator", "reviewer_relation": "operator",
                                "producer_is_reviewer": False}}
            path = host.host_state_path(target)
            apply = lambda: host.admit_host_attestation(target, event, host.digest(host.read_host_state(target)))
            module = host
        else:
            event = base.RuntimeTests.competence_delta(self)
            event["event_id"] = event_id
            knowledge = target / event["knowledge_entry"]
            knowledge.parent.mkdir(parents=True, exist_ok=True)
            knowledge.write_text("# Useful living method\n", encoding="utf-8")
            path = runtime.competence_index_path(target)
            apply = lambda: runtime.admit_competence_delta(target, event, runtime.digest(runtime.read_competence_index(target)))
            module = runtime
        return path, target / f".maios/receipts/{owner}/{event_id}.json", apply, module

    def fresh_status(self, target):
        r = subprocess.run([sys.executable, "-B", str(target / "maios.py"), "status"],
                           cwd=target, capture_output=True, text=True)
        return json.loads(r.stdout)

    def test_reserved_event_paths_never_destroy_terminal_receipts(self):
        for number, event_id in enumerate(("PENDING", "pending", "PeNdInG")):
            with self.subTest(event_id=event_id):
                target, _ = self.new_target("reserved-" + str(number))
                before = configuration.configuration_path(target).read_bytes()
                try:
                    self.apply_event(target, self.event(event_id))
                except (ValueError, RuntimeError):
                    self.assertEqual(before, configuration.configuration_path(target).read_bytes())
                else:
                    self.assertTrue((target / f".maios/receipts/resultant/{event_id}.json").is_file())
                    self.assertTrue(self.fresh_status(target)["valid"])

        for owner in ("host", "competence"):
            target, _ = self.new_target("reserved-" + owner)
            state, receipt, apply, _ = self.owner_case(target, owner, "PeNdInG")
            before = state.read_bytes()
            with self.assertRaises(Exception):
                apply()
            self.assertEqual(before, state.read_bytes())
            self.assertFalse(receipt.exists())

    def test_host_and_competence_failures_preserve_state_before_and_after_receipt_write(self):
        for owner in ("host", "competence"):
            for when in ("directory", "before", "after"):
                with self.subTest(owner=owner, when=when):
                    target, _ = self.new_target(owner + "-" + when)
                    state, receipt, apply, module = self.owner_case(target, owner)
                    before = state.read_bytes()
                    original = module.write_json_atomic
                    def fail(path, value):
                        if path == receipt and when == "before":
                            raise OSError("receipt unavailable")
                        original(path, value)
                        if path == receipt and when == "after":
                            raise OSError("late receipt failure")
                    if when == "directory":
                        receipt.mkdir(parents=True)
                    with patch.object(module, "write_json_atomic", side_effect=fail):
                        with self.assertRaises(Exception):
                            apply()
                    self.assertEqual(before, state.read_bytes())
                    self.assertTrue(self.fresh_status(target)["valid"])
                    if when == "directory":
                        receipt.rmdir()
                    self.assertEqual(apply()["status"], "admitted")
                    self.assertTrue(receipt.is_file())

            self.installed_owner_rollback(owner)

    def installed_owner_rollback(self, owner):
        target, _ = self.new_target(owner + "-installed-process")
        self.owner_case(target, owner)
        if owner == "host":
            event = base.RuntimeTests.host_attestation(self, "owner-event", "instruction_discovery", "generic")
        else:
            event = base.RuntimeTests.competence_delta(self)
            event["event_id"] = "owner-event"
        event_path = self.base / (owner + "-event.json")
        event_path.write_text(json.dumps(event), encoding="utf-8")
        script = """
import json, sys
from pathlib import Path
from unittest.mock import patch
root, event_path, owner = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, str(root / '.maios/runtime'))
import kernel, host, configuration, maios_filesystem
assert all(Path(m.__file__).is_relative_to(root) for m in (kernel,host,configuration,maios_filesystem))
event = json.loads(event_path.read_text(encoding='utf-8'))
module = host if owner == 'host' else kernel
state = host.host_state_path(root) if owner == 'host' else kernel.competence_index_path(root)
read = host.read_host_state if owner == 'host' else kernel.read_competence_index
admit = host.admit_host_attestation if owner == 'host' else kernel.admit_competence_delta
receipt = root / f'.maios/receipts/{owner}/owner-event.json'
before = state.read_bytes()
original = module.write_json_atomic
def fail(path, value):
    original(path, value)
    if path == receipt: raise OSError('installed late failure')
with patch.object(module, 'write_json_atomic', side_effect=fail):
    try: admit(root, event, module.digest(read(root)))
    except OSError: pass
    else: raise AssertionError('injection did not fail')
assert state.read_bytes() == before and not receipt.exists()
assert kernel.validate_project(root)['valid']
assert admit(root, event, module.digest(read(root)))['status'] == 'admitted'
assert receipt.is_file() and kernel.validate_project(root)['valid']
"""
        result = subprocess.run([sys.executable, "-I", "-B", "-c", script, str(target), str(event_path), owner],
                                cwd=target, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.fresh_status(target)["valid"])

    def test_host_and_competence_incomplete_recovery_blocks_retry_at_fresh_reentry(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, _ = self.new_target(owner + "-incomplete")
                state, receipt, apply, module = self.owner_case(target, owner)
                original = module.write_json_atomic
                def fail(path, value):
                    original(path, value)
                    if path == receipt:
                        raise OSError("late receipt failure")
                with patch.object(module, "write_json_atomic", side_effect=fail), \
                     patch.object(configuration, "write_bytes_atomic", side_effect=OSError("rollback unavailable")):
                    with self.assertRaises(Exception):
                        apply()
                self.assertFalse(self.fresh_status(target)["valid"])
                self.assertTrue(operating.operating_status(target)["recovery_required"])
                with self.assertRaises(Exception):
                    apply()

    def test_owner_replay_requires_its_terminal_receipt(self):
        for owner in ("host", "competence"):
            with self.subTest(owner=owner):
                target, _ = self.new_target(owner + "-retry")
                state, receipt, apply, _ = self.owner_case(target, owner)
                apply()
                before = state.read_bytes()
                receipt.unlink()
                self.assertFalse(self.fresh_status(target)["valid"])
                with self.assertRaises(Exception):
                    apply()
                self.assertEqual(before, state.read_bytes())

    def writer_cases(self):
        return [(configuration.write_json_atomic, {"a": 1}, "tmp"),
                (operating.write_json_atomic, {"a": 1}, "tmp"),
                (runtime.write_json_atomic, {"a": 1}, "tmp"),
                (host.write_json_atomic, {"a": 1}, "tmp"),
                (installer.write_json, {"a": 1}, "tmp"),
                (configuration.write_text_atomic, "new text", "tmp"),
                (configuration.write_bytes_atomic, b"restored bytes", "restore")]

    def test_all_atomic_writers_preserve_preexisting_temporaries_and_hardlinks(self):
        for i, (writer, value, suffix) in enumerate(self.writer_cases()):
            for kind in ("file", "hardlink"):
                with self.subTest(writer=i, kind=kind):
                    folder = self.base / f"writer-{i}-{kind}"
                    folder.mkdir()
                    dest = folder / "state.json"
                    temp = folder / f".{dest.name}.maios-{suffix}-{os.getpid()}"
                    sentinel = self.base / f"sentinel-{i}-{kind}"
                    sentinel.write_bytes(b"foreign bytes")
                    if kind == "hardlink":
                        os.link(sentinel, temp)
                    else:
                        temp.write_bytes(b"foreign bytes")
                    writer(dest, value)
                    self.assertTrue(temp.exists())
                    self.assertEqual(temp.read_bytes(), b"foreign bytes")
                    self.assertEqual(sentinel.read_bytes(), b"foreign bytes")
                    self.assertFalse(dest.is_symlink())

    def test_acquired_temporary_collision_and_cleanup_preserve_foreign_objects(self):
        from maios_project_kernel import filesystem
        folder = self.base / "exclusive-output"
        folder.mkdir()
        destination = folder / "state.json"
        destination.write_bytes(b"canonical before")
        foreign = folder / ".state.json.maios-tmp-occupied"
        foreign.write_bytes(b"foreign temporary")
        with patch.object(filesystem.tempfile, "_get_candidate_names", return_value=iter(["occupied", "ours"])):
            filesystem.write_bytes_atomic(destination, b"canonical after")
        self.assertEqual(foreign.read_bytes(), b"foreign temporary")
        self.assertEqual(destination.read_bytes(), b"canonical after")
        replaced = []
        def change_temporary_and_fail(source, target):
            source.unlink()
            source.write_bytes(b"replacement belongs to another writer")
            replaced.append(source)
            raise OSError("promotion failed after another writer replaced the temporary")
        with patch.object(filesystem.os, "replace", side_effect=change_temporary_and_fail):
            with self.assertRaises(OSError):
                filesystem.write_bytes_atomic(destination, b"uncommitted output")
        self.assertEqual(destination.read_bytes(), b"canonical after")
        self.assertEqual(len(replaced), 1)
        self.assertEqual(replaced[0].read_bytes(), b"replacement belongs to another writer")

    def test_all_atomic_writers_preserve_external_symlink_sentinels(self):
        for i, (writer, value, suffix) in enumerate(self.writer_cases()):
            folder = self.base / f"writer-link-{i}"
            folder.mkdir()
            dest = folder / "state.json"
            temp = folder / f".{dest.name}.maios-{suffix}-{os.getpid()}"
            sentinel = self.base / f"link-sentinel-{i}"
            sentinel.write_bytes(b"external sentinel")
            try:
                temp.symlink_to(sentinel)
            except OSError as exc:
                self.skipTest(str(exc))
            writer(dest, value)
            self.assertEqual(sentinel.read_bytes(), b"external sentinel")
            self.assertTrue(temp.is_symlink())
            self.assertFalse(dest.is_symlink())

    @unittest.skipUnless(os.name == "nt", "real Windows junction case")
    def test_windows_junction_is_refused_for_preview_verify_recovery_and_uninstall(self):
        def junction(link, external):
            # PowerShell owns this creation end-to-end; no elevated or cross-shell deletion.
            r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                "New-Item -ItemType Junction -Path '" + str(link).replace("'", "''") +
                "' -Target '" + str(external).replace("'", "''") + "' | Out-Null"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
        target = self.base / "junction-preview"
        target.mkdir()
        external = self.base / "junction-sentinel"
        external.mkdir()
        sentinel = external / "sentinel.txt"
        sentinel.write_bytes(b"outside project")
        junction(target / ".maios", external)
        try:
            try:
                plan = installer.make_plan(self.distribution, target, "existing_repository", "generic")
            except installer.InstallerError:
                pass
            else:
                self.assertNotEqual(plan["status"], "ready")
        finally:
            os.rmdir(target / ".maios")  # unlink the junction, never traverse its target
        target, receipt = self.new_target("junction-installed")
        external = self.base / "junction-installed-external"
        (target / ".maios").rename(external)
        before = {p.relative_to(external): p.read_bytes() for p in external.rglob("*") if p.is_file()}
        junction(target / ".maios", external)
        try:
            self.assertFalse(installer.verify_installation(target, receipt)["valid"])
            with self.assertRaises(Exception):
                installer.uninstall(target, receipt)
            with self.assertRaises(Exception):
                installer.recover_pending(target)
            self.assertEqual(before, {p.relative_to(external): p.read_bytes() for p in external.rglob("*") if p.is_file()})
        finally:
            os.rmdir(target / ".maios")
            external.rename(target / ".maios")
        self.assertEqual(sentinel.read_bytes(), b"outside project")

    def test_resultant_replay_refuses_missing_current_or_historical_receipt(self):
        for historical in (False, True):
            with self.subTest(historical=historical):
                target, _ = self.new_target("replay-" + str(historical))
                first = self.event("first")
                self.apply_event(target, first)
                if historical:
                    self.apply_event(target, self.event("second"))
                (target / ".maios/receipts/resultant/first.json").unlink()
                context = operating.operating_status(target)
                with self.assertRaises(Exception):
                    operating.apply_resultant_readback(target, first, context["context_sha256"])

    def test_terminal_body_corruption_is_visible_and_replay_cannot_hide_it(self):
        target, _ = self.install()
        first = self.event()
        self.apply_event(target, first)
        receipt = target / ".maios/receipts/resultant/one.json"
        value = json.loads(receipt.read_text(encoding="utf-8"))
        value["readback"]["actual_result"]["summary"] = "isolated corruption"
        receipt.write_text(json.dumps(value), encoding="utf-8")
        self.assertFalse(self.fresh_status(target)["valid"])
        for malformed in ([], None, "not a receipt"):
            receipt.write_text(json.dumps(malformed), encoding="utf-8")
            self.assertFalse(self.fresh_status(target)["valid"])
        receipt.write_text(json.dumps(value), encoding="utf-8")
        context = operating.operating_status(target)
        self.assertTrue(context["recovery_required"])
        with self.assertRaises(Exception):
            operating.apply_resultant_readback(target, first, context["context_sha256"])

    def test_historical_replay_survives_later_resultant_and_configuration_evolution(self):
        target, _ = self.install()
        first = self.event("first")
        self.apply_event(target, first)
        self.apply_event(target, self.event("second"))
        state = configuration.current_configuration(target)
        candidate = copy.deepcopy(state)
        candidate["checkpoint"]["sequence"] += 1
        candidate["checkpoint"]["summary"] = "independent later evolution"
        configuration.apply_configuration(target, candidate, configuration.digest(state))
        context = operating.operating_status(target)
        with patch.object(operating, "validate_resultant_readback", side_effect=AssertionError("old event must not be rejudged against current semantics")):
            self.assertEqual(operating.apply_resultant_readback(target, first, context["context_sha256"])["status"], "idempotent")
        self.assertTrue(self.fresh_status(target)["valid"])
