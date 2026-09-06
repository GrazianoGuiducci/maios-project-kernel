from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import test_builder_installer_runtime as base
from maios_project_kernel import installer


class PendingRecoveryTests(base.DistributionFixture):
    def prepare(self, name, with_backup=False):
        target = self.base / name
        target.mkdir()
        (target / "project-owned.txt").write_bytes(b"existing project knowledge\n")
        if with_backup:
            (target / "START_HERE.md").write_bytes((self.distribution / "payload/START_HERE.md").read_bytes())
        plan = installer.make_plan(self.distribution, target, "existing_repository", "generic")
        return target, plan

    def journal(self, target):
        return target / ".maios/receipts/install/PENDING.json"

    def snapshot(self, target):
        return {p.relative_to(target).as_posix(): p.read_bytes() for p in target.rglob("*") if p.is_file()}

    def seed_created(self, target, plan):
        pending = installer.pending_installation(plan)
        installer.begin_pending_installation(target, pending)
        record = lambda created: installer.record_pending_creation(target, pending, created)
        installer.backup_identical(target, plan, record)
        entry = next(e for e in plan["entries"] if e["destination"] == "AGENTS.md")
        record(installer.copy_entry(self.distribution, target, entry))
        return pending

    def test_corrupt_journal_is_rejected_whole_before_any_deletion(self):
        target, plan = self.prepare("tamper", with_backup=True)
        original = self.seed_created(target, plan)
        foreign = {"path": "project-owned.txt", "sha256": installer.digest_file(target / "project-owned.txt"),
                   "bytes": (target / "project-owned.txt").stat().st_size, "kind": "payload"}
        mutations = [
            lambda p: p["planned_files"].append(foreign),
            lambda p: p["planned_backup_files"].append(dict(foreign, source_path="project-owned.txt")),
            lambda p: p.update(planned_files=[]),
            lambda p: p.update(planned_backup_files=[]),
            lambda p: p["install_plan"]["creates"].append("project-owned.txt"),
            lambda p: p.update(plan_digest="0" * 64),
            lambda p: p.update(package_identity={}),
            lambda p: p.update(target=str(self.base)),
            lambda p: p["created_files"].append({"path": "project-owned.txt", "sha256": foreign["sha256"],
                                                 "file_identity": installer.file_identity((target / "project-owned.txt").stat())}),
            lambda p: p["created_files"].append(copy.deepcopy(p["created_files"][0])),
            lambda p: p["created_files"][-1].update(file_identity={"inode": 1}),
            lambda p: p.update(schema="maios.pending-installation.v2"),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(mutation=index):
                altered = copy.deepcopy(original)
                mutate(altered)
                installer.write_json(self.journal(target), altered)
                before = self.snapshot(target)
                with self.assertRaises(installer.InstallerError):
                    installer.recover_pending(target)
                if index in (0, 1):
                    result = subprocess.run([sys.executable, "-B", str(self.distribution / "install.py"),
                                             "recover-pending", "--target", str(target)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stdout or result.stderr)
                self.assertEqual(before, self.snapshot(target))
        installer.write_json(self.journal(target), original)
        # This empty directory existed before recovery and is not installer-owned.
        (target / "pre-existing-empty").mkdir()
        result = installer.recover_pending(target)
        self.assertTrue(result["complete"], result)
        self.assertEqual(set(result["removed"]), {r["path"] for r in original["created_files"]})
        self.assertTrue((target / "project-owned.txt").is_file())
        self.assertTrue((target / "START_HERE.md").is_file())
        self.assertTrue((target / "pre-existing-empty").is_dir())

    def test_foreign_files_appearing_after_preview_survive_automatic_recovery(self):
        for kind in ("payload", "backup"):
            with self.subTest(kind=kind):
                target, plan = self.prepare("race-" + kind, with_backup=kind == "backup")
                relative = "AGENTS.md" if kind == "payload" else installer.pending_installation(plan)["planned_backup_files"][0]["path"]
                create = installer.create_file
                foreign = []
                def concurrent_create(base_path, destination, data):
                    if base_path == target and destination == relative:
                        path = installer.native(target, destination)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_bytes(data)  # same bytes, a different creator
                        foreign.append(data)
                    return create(base_path, destination, data)
                with patch.object(installer, "create_file", side_effect=concurrent_create):
                    with self.assertRaises(installer.InstallerError):
                        installer.apply_plan(self.distribution, plan)
                self.assertTrue(foreign)
                self.assertEqual(installer.native(target, relative).read_bytes(), foreign[0])
                pending = installer.read_json(self.journal(target))
                self.assertNotIn(relative, {r["path"] for r in pending["created_files"]})
                result = installer.recover_pending(target)
                self.assertFalse(result["complete"])
                self.assertIn(relative, result["preserved_uncertain"])
                self.assertTrue(self.journal(target).exists())
                self.assertTrue((target / "project-owned.txt").exists())

    def test_unrecorded_replaced_or_unidentifiable_files_are_preserved(self):
        # Observed Windows fstat/stat mismatch: birth time agrees, ctime differs.
        descriptor = SimpleNamespace(st_dev=1, st_ino=2, st_birthtime_ns=30, st_ctime_ns=40)
        pathname = SimpleNamespace(st_dev=1, st_ino=2, st_birthtime_ns=30, st_ctime_ns=30)
        self.assertEqual(installer.file_identity(descriptor), installer.file_identity(pathname))
        for uncertainty in ("unrecorded", "replaced", "unidentifiable", "changed"):
            with self.subTest(uncertainty=uncertainty):
                target, plan = self.prepare(uncertainty)
                pending = installer.pending_installation(plan)
                installer.begin_pending_installation(target, pending)
                entry = next(e for e in plan["entries"] if e["destination"] == "AGENTS.md")
                record = installer.copy_entry(self.distribution, target, entry)
                path = target / "AGENTS.md"
                if uncertainty != "unrecorded":
                    if uncertainty == "unidentifiable":
                        record["file_identity"] = None
                    installer.record_pending_creation(target, pending, record)
                if uncertainty == "replaced":
                    replacement = target / "replacement.tmp"
                    replacement.write_bytes(path.read_bytes())
                    os.replace(replacement, path)
                if uncertainty == "changed":
                    path.write_bytes(b"locally evolved knowledge\n")
                before = self.snapshot(target)
                result = installer.recover_pending(target)
                self.assertFalse(result["complete"])
                self.assertIn("AGENTS.md", result["preserved_uncertain"] + result["preserved_changed"])
                self.assertEqual(before, self.snapshot(target))

    def test_failed_creation_record_keeps_file_and_journal_for_reentry(self):
        target, plan = self.prepare("record-failure")
        write = installer.write_json
        def fail_record(path, value):
            if path == self.journal(target):
                raise OSError("simulated interruption while recording creation")
            return write(path, value)
        with patch.object(installer, "write_json", side_effect=fail_record):
            with self.assertRaises(installer.InstallerError):
                installer.apply_plan(self.distribution, plan)
        pending = installer.read_json(self.journal(target))
        self.assertEqual(pending["created_files"], [])
        result = installer.recover_pending(target)
        self.assertFalse(result["complete"])
        self.assertTrue(result["preserved_uncertain"])
        self.assertTrue(self.journal(target).is_file())

    def test_failed_attempt_acquisition_cannot_recover_another_attempt(self):
        target, plan = self.prepare("competing-journal")
        foreign = installer.pending_installation(plan)
        begin = installer.begin_pending_installation
        def competitor(base_path, pending):
            begin(base_path, foreign)
            return begin(base_path, pending)
        with patch.object(installer, "begin_pending_installation", side_effect=competitor):
            with self.assertRaises(installer.InstallerError):
                installer.apply_plan(self.distribution, plan)
        self.assertEqual(installer.read_json(self.journal(target)), foreign)
        with self.assertRaises(installer.InstallerError):
            installer.recover_pending(target, expected_attempt="another-attempt")
        self.assertTrue(self.journal(target).exists())
        new_target = self.base / "new-competing-stage"
        new_plan = installer.make_plan(self.distribution, new_target, "new_repository", "generic")
        stage = new_target.parent / f".{new_target.name}.maios-stage-{new_plan['plan_digest'][:12]}"
        mkdir = Path.mkdir
        def competing_stage(path, *args, **kwargs):
            if path == stage and not path.exists():
                mkdir(path, *args, **kwargs)
                (path / "foreign.txt").write_bytes(b"other attempt\n")
            return mkdir(path, *args, **kwargs)
        with patch.object(Path, "mkdir", competing_stage):
            with self.assertRaises(installer.InstallerError):
                installer.apply_plan(self.distribution, new_plan)
        self.assertEqual((stage / "foreign.txt").read_bytes(), b"other attempt\n")

    def test_journal_cleanup_failure_after_commit_preserves_installed_files(self):
        target, plan = self.prepare("committed")
        unlink = Path.unlink
        def fail_cleanup(path, *args, **kwargs):
            if path == self.journal(target):
                raise OSError("simulated journal cleanup failure")
            return unlink(path, *args, **kwargs)
        with patch.object(Path, "unlink", fail_cleanup):
            with self.assertRaisesRegex(installer.InstallerError, "installation committed"):
                installer.apply_plan(self.distribution, plan)
        receipt = installer.load_receipt(target, None)
        self.assertTrue(installer.verify_installation(target, receipt)["valid"])
        before = self.snapshot(target)
        result = installer.recover_pending(target)
        self.assertTrue(result["complete"])
        self.assertTrue(result["installation_retained"])
        self.assertEqual(result["removed"], [])
        before.pop(".maios/receipts/install/PENDING.json")
        self.assertEqual(before, self.snapshot(target))
