from __future__ import annotations

import shutil
import subprocess
import sys

import test_builder_installer_runtime as base
from maios_project_kernel import builder, installer


class UninstallOwnershipTests(base.DistributionFixture):
    def snapshot(self, target):
        return {p.relative_to(target).as_posix(): p.read_bytes()
                for p in target.rglob("*") if p.is_file()}

    def test_archived_receipt_cannot_uninstall_a_later_artifact_on_same_target(self):
        target, receipt_a = self.install()
        archive = self.base / "archived-receipt.json"
        installer.write_json(archive, receipt_a)
        self.assertTrue(installer.uninstall(target, receipt_a)["complete"])

        source_b = self.base / "source-b"
        shutil.copytree(base.ROOT, source_b, ignore=shutil.ignore_patterns(
            ".git", "package", "__pycache__", ".pytest_cache"))
        body = source_b / "kernel/KNOWLEDGE_CONTINUUM.md"
        body.write_text(body.read_text(encoding="utf-8") + "\nA later source learning.\n",
                        encoding="utf-8")
        distribution_b = self.base / "distribution-b"
        builder.render_distribution(source_b, distribution_b)
        self.assertTrue(builder.verify_distribution(source_b, distribution_b)["valid"])
        plan_b = installer.make_plan(distribution_b, target, "new_repository", "generic")
        receipt_b = installer.apply_plan(distribution_b, plan_b)
        self.assertNotEqual(receipt_a["package_identity"], receipt_b["package_identity"])
        before = self.snapshot(target)
        result = subprocess.run([sys.executable, "-B", str(distribution_b / "install.py"),
                                 "uninstall", "--target", str(target), "--receipt", str(archive)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout or result.stderr)
        self.assertEqual(before, self.snapshot(target))
        with self.assertRaisesRegex(installer.InstallerError, "current_mismatch"):
            installer.uninstall(target, installer.load_receipt(target, archive))
        self.assertEqual(before, self.snapshot(target))
        verification = installer.verify_installation(target, receipt_a)
        self.assertEqual(verification["current_relation"], "current_mismatch")
        self.assertTrue(verification["receipt_validation"]["valid"])
        self.assertTrue(verification["files_present"])
        self.assertFalse(verification["installed"])
        self.assertFalse(verification["valid"])
        self.assertTrue(installer.verify_installation(target, receipt_b)["installed"])

    def test_missing_or_invalid_current_refuses_archived_receipt_without_mutation(self):
        target, receipt = self.install()
        current = target / ".maios/receipts/install/CURRENT.json"
        original = current.read_bytes()
        for state, contents in (("current_missing", None), ("current_invalid", b"{broken")):
            with self.subTest(state=state):
                if contents is None:
                    current.unlink()
                else:
                    current.write_bytes(contents)
                before = self.snapshot(target)
                with self.assertRaisesRegex(installer.InstallerError, state):
                    installer.uninstall(target, receipt)
                self.assertEqual(before, self.snapshot(target))
                verification = installer.verify_installation(target, receipt)
                self.assertEqual(verification["current_relation"], state)
                self.assertTrue(verification["files_present"])
                self.assertFalse(verification["installed"])
                current.write_bytes(original)
        # A separate copy of the actual current receipt is still usable.
        archive = self.base / "current-copy.json"
        installer.write_json(archive, receipt)
        self.assertTrue(installer.uninstall(target, installer.load_receipt(target, archive))["complete"])

    def test_existing_project_retains_preexisting_empty_directory_identities(self):
        target = (self.base / "existing-directories").resolve()
        for relative in ("skills", ".maios/backups", ".maios/receipts/install",
                         ".maios/runtime/__pycache__"):
            (target / relative).mkdir(parents=True, exist_ok=True)
        original_dirs = {p.relative_to(target).as_posix(): (p.stat().st_dev, p.stat().st_ino)
                         for p in target.rglob("*") if p.is_dir()}
        preexisting = target / "START_HERE.md"
        preexisting.write_bytes((self.distribution / "payload/START_HERE.md").read_bytes())
        plan = installer.make_plan(self.distribution, target, "existing_repository", "generic")
        receipt = installer.apply_plan(self.distribution, plan)
        compiled = subprocess.run([sys.executable, "-m", "py_compile",
                                   str(target / ".maios/runtime/kernel.py")],
                                  capture_output=True, text=True)
        self.assertEqual(compiled.returncode, 0, compiled.stderr)
        result = installer.uninstall(target, receipt)
        self.assertTrue(result["complete"], result)
        self.assertTrue(result["removed_runtime_cache"])
        for relative, identity in original_dirs.items():
            with self.subTest(directory=relative):
                directory = target / relative
                self.assertTrue(directory.is_dir())
                self.assertEqual(identity, (directory.stat().st_dev, directory.stat().st_ino))
        self.assertEqual(list(self.snapshot(target)), ["START_HERE.md"])
