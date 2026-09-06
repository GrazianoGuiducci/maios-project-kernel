from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import test_builder_installer_runtime as base
from maios_project_kernel import installer, operating, runtime


class DeliveryBoundaryTests(base.DistributionFixture):
    def snapshot(self, target):
        return {p.relative_to(target).as_posix(): p.read_bytes()
                for p in target.rglob("*") if p.is_file()}

    def cli(self, package, *args):
        return subprocess.run([sys.executable, "-B", "install.py", *map(str, args)],
                              cwd=package, capture_output=True, text=True)

    def test_documented_external_plan_roundtrip_preserves_distribution_and_rejects_unsafe_outputs(self):
        checkout = self.base / "checkout"
        package = checkout / "package"
        shutil.copytree(self.distribution, package)
        for marker in ("release/PROJECTION.json", "src/maios_project_kernel/builder.py"):
            path = checkout / marker
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("source marker", encoding="utf-8")
        target = self.base / "new-project"
        before = self.snapshot(package)
        for output in ("install-plan.json", checkout / "local-plan.json", target / "plan.json"):
            with self.subTest(output=str(output)):
                refused = self.cli(package, "preview", "--target", target, "--mode", "new_repository",
                                   "--host", "codex", "--plan-out", output)
                self.assertEqual(refused.returncode, 2, refused.stdout or refused.stderr)
                self.assertIn("outside", refused.stderr)
                self.assertEqual(before, self.snapshot(package))
                self.assertFalse(target.exists())
        plan = self.base / "maios-install-plan.json"
        preview = self.cli(package, "preview", "--target", target, "--mode", "new_repository",
                           "--host", "codex", "--plan-out", plan)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(before, self.snapshot(package))
        applied = self.cli(package, "apply", "--plan", plan)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        installed = self.snapshot(target)
        refused = self.cli(package, "uninstall", "--target", target, "--receipt-out", "uninstall-receipt.json")
        self.assertEqual(refused.returncode, 2, refused.stdout or refused.stderr)
        self.assertEqual(installed, self.snapshot(target))
        removed = self.cli(package, "uninstall", "--target", target,
                           "--receipt-out", self.base / "maios-uninstall-receipt.json")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(before, self.snapshot(package))

    def test_unregistered_matching_bytecode_survives_uninstall_even_after_source_evolution(self):
        for evolved in (False, True):
            with self.subTest(evolved=evolved):
                target = self.base / ("evolved" if evolved else "unchanged")
                cache = target / ".maios/runtime/__pycache__/kernel.project-owned.pyc"
                cache.parent.mkdir(parents=True)
                cache.write_bytes(b"target-owned matching name\n")
                before = (cache.read_bytes(), cache.stat().st_ino)
                receipt = installer.apply_plan(self.distribution, installer.make_plan(
                    self.distribution, target, "existing_repository", "generic"))
                if evolved:
                    source = target / ".maios/runtime/kernel.py"
                    source.write_bytes(source.read_bytes() + b"\n# project evolution\n")
                removed = installer.uninstall(target, receipt)
                self.assertTrue(cache.is_file())
                self.assertEqual(before, (cache.read_bytes(), cache.stat().st_ino))
                self.assertIn(".maios/runtime/__pycache__/kernel.project-owned.pyc", removed["preserved_runtime_cache"])
                self.assertEqual(removed["complete"], not evolved)

    def test_runtime_rejects_linked_organs_and_ancestors(self):
        for index, relative in enumerate((".maios/kernel/FACULTY_FIELD.json", ".maios/competences/INDEX.json",
                                          ".maios/kernel")):
            target = self.base / ("symlink-" + str(index))
            installer.apply_plan(self.distribution, installer.make_plan(
                self.distribution, target, "new_repository", "generic"))
            path = target / relative
            external = self.base / ("external-" + str(index))
            directory = path.is_dir()
            path.rename(external)
            try:
                os.symlink(external, path, target_is_directory=directory)
            except OSError as exc:
                external.rename(path)
                self.skipTest("host does not permit creating symlinks: " + str(exc))
            try:
                self.assertFalse(runtime.validate_project(target)["valid"])
                with self.assertRaises(Exception):
                    operating.operating_status(target)
            finally:
                # Remove only the link; the temporary fixture owns both paths.
                path.unlink()
                external.rename(path)
