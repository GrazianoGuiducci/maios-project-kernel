"""Direct production, portable paths and invocation ownership under failure."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import test_builder_installer_runtime as base
from maios_project_kernel import builder, filesystem, generated_kernel, installer


class CompletionProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "package"
        self.target.mkdir()
        (self.target / "previous.txt").write_bytes(b"previous verified package")
        self.before = builder.directory_snapshot(self.target)

    def test_all_production_consumers_share_portable_path_and_collision_rules(self):
        for name in ("AUX.txt", "conout$.md", "COM1 .md", "LPT².md", "a.", "a ",
                     "a\x00", "a\x1f", "a\x7f", "a:b", "a\\b", "a//b", "./a", "a/../b", ".git/config"):
            for check in (filesystem.portable_path, builder.safe_relative, installer.safe_relative, generated_kernel.safe_path):
                with self.subTest(name=name, check=check), self.assertRaises((ValueError, RuntimeError)):
                    check(name)
        for paths in (("A.txt", "a.txt"), ("folder", "folder/file"), ("A/file", "a")):
            with self.subTest(paths=paths), self.assertRaisesRegex(ValueError, "collision"):
                filesystem.distinct_paths(paths)
        filesystem.distinct_paths(["a/file", "b/file", "COM10.txt"])

    def test_projection_collisions_fail_before_delivery(self):
        original = builder.read_json
        for extra in ("payload/AGENTS.MD", "payload/skills", "payload/CON.md", "MANIFEST.json"):
            def read(path):
                value = original(path)
                if path.name == "PROJECTION.json":
                    value["files"].append({"source": "README.md", "destination": extra})
                return value
            with self.subTest(extra=extra), patch.object(builder, "read_json", side_effect=read):
                output = self.root / "candidate"
                with self.assertRaises(builder.BuildError):
                    builder.render_distribution(base.ROOT, output)
                self.assertFalse(any(output.rglob("*")))

    def test_inventory_and_adapter_collision_are_refused_before_installation(self):
        package = self.root / "distribution"
        builder.render_distribution(base.ROOT, package)
        inventory_path = package / "PACKAGE_INVENTORY.json"
        inventory = json.loads(inventory_path.read_text())
        inventory["files"].append(dict(inventory["files"][0], path=inventory["files"][0]["path"].upper()))
        inventory_path.write_text(json.dumps(inventory))
        with self.assertRaisesRegex(installer.InstallerError, "collision"):
            installer.verified_inventory_rows(package)
        inventory["files"].pop()
        inventory_path.write_text(json.dumps(inventory))
        with patch.object(installer, "adapter_projection", return_value=[{
            "source": "payload/AGENTS.md", "destination": "agents.md"}]), self.assertRaisesRegex(installer.InstallerError, "collision"):
            installer.source_entries(package, "codex")

    def test_R04_foreign_fixed_staging_and_backup_names_are_untouched(self):
        foreign = self.root / ".package.staging"
        foreign.mkdir()
        (foreign / "other-work").write_bytes(b"foreign")
        old_backup = self.root / f".package.previous-{os.getpid()}"
        old_backup.mkdir()
        (old_backup / "other-work").write_bytes(b"foreign backup")
        result = builder.build_distribution(base.ROOT, self.target)
        self.assertTrue(result["verification"]["valid"])
        self.assertEqual((foreign / "other-work").read_bytes(), b"foreign")
        self.assertEqual((old_backup / "other-work").read_bytes(), b"foreign backup")

    def test_R04_render_and_verify_failure_preserve_previous_package(self):
        with patch.object(builder, "render_distribution", side_effect=builder.BuildError("render failure")):
            with self.assertRaisesRegex(builder.BuildError, "render failure"):
                builder.build_distribution(base.ROOT, self.target)
        self.assertEqual(builder.directory_snapshot(self.target), self.before)
        with patch.object(builder, "verify_distribution", return_value={"valid": False, "errors": ["verify failure"]}):
            with self.assertRaisesRegex(builder.BuildError, "verify failure"):
                builder.build_distribution(base.ROOT, self.target)
        self.assertEqual(builder.directory_snapshot(self.target), self.before)

    def test_R04_failed_promotion_restores_owned_backup(self):
        replace = os.replace
        def fail(source, destination):
            if ".staging-" in str(source):
                raise OSError("promotion failure")
            return replace(source, destination)
        with patch.object(builder.os, "replace", side_effect=fail):
            with self.assertRaisesRegex(OSError, "promotion failure"):
                builder.build_distribution(base.ROOT, self.target)
        self.assertEqual(builder.directory_snapshot(self.target), self.before)

    def test_R04_uncertain_staging_and_concurrent_target_are_preserved(self):
        verify = builder.verify_distribution
        captured = []
        def foreign_change(root, staging):
            result = verify(root, staging)
            captured.append(staging)
            (staging / "foreign.txt").write_bytes(b"do not delete")
            return result
        with patch.object(builder, "verify_distribution", side_effect=foreign_change):
            with self.assertRaisesRegex(builder.BuildError, "staging changed"):
                builder.build_distribution(base.ROOT, self.target)
        self.assertEqual(builder.directory_snapshot(self.target), self.before)
        self.assertEqual((captured[0] / "foreign.txt").read_bytes(), b"do not delete")
        def concurrent_change(root, staging):
            result = verify(root, staging)
            (self.target / "concurrent.txt").write_bytes(b"keep this")
            return result
        with patch.object(builder, "verify_distribution", side_effect=concurrent_change):
            with self.assertRaisesRegex(builder.BuildError, "target changed"):
                builder.build_distribution(base.ROOT, self.target)
        self.assertEqual((self.target / "concurrent.txt").read_bytes(), b"keep this")

    def test_R04_replaced_invocation_directory_is_never_deleted(self):
        owned = builder.OwnedDirectory(self.root, ".package.staging-")
        (owned.path / "candidate").write_text("ours")
        owned.seal()
        moved = self.root / "displaced"
        owned.path.rename(moved)
        owned.path.mkdir()
        (owned.path / "foreign").write_text("theirs")
        owned.cleanup()
        self.assertEqual((owned.path / "foreign").read_text(), "theirs")
        self.assertTrue((moved / "candidate").exists())

    def test_two_builds_are_byte_identical(self):
        first, second = self.root / "one", self.root / "two"
        for target in (first, second):
            builder.render_distribution(base.ROOT, target)
            self.assertTrue(builder.verify_distribution(base.ROOT, target)["valid"])
        def files(path):
            return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob("*") if p.is_file()}
        self.assertEqual(files(first), files(second))

    def test_public_boundary_does_not_require_private_workspace_names(self):
        package = self.root / "boundary"
        builder.render_distribution(base.ROOT, package)
        document = package / "README.md"
        for private_path in ("X:/Users/example/private", "Y:\\Users\\example\\private", "/home/example/private"):
            document.write_text(private_path)
            result = builder.verify_distribution(base.ROOT, package)
            self.assertIn("private home path is forbidden: README.md", result["errors"])
        document.write_text("C:/Projects/MyProject")
        self.assertNotIn("private home path is forbidden: README.md",
                         builder.verify_distribution(base.ROOT, package)["errors"])

    def test_portable_owners_are_declarative_and_archive_bytes_are_reproducible(self):
        import importlib.util
        import zipfile
        original = builder.read_json
        def read(path):
            value = original(path)
            if path == base.ROOT / "adapters/ADAPTERS.json":
                owner = "skills/maios-software-design/SKILL.md"
                value["portable_competence_owners"].append(owner)
                codex = next(a for a in value["adapters"] if a["id"] == "codex")
                codex["projections"].append({"source": owner,
                    "destination": ".agents/skills/maios-software-design/SKILL.md"})
            return value
        with patch.object(builder, "read_json", side_effect=read):
            package = self.root / "declarative"
            builder.render_distribution(base.ROOT, package)
            result = builder.verify_distribution(base.ROOT, package)
            self.assertTrue(result["valid"], result)
        package = self.root / "archive-source"
        builder.render_distribution(base.ROOT, package)
        spec = importlib.util.spec_from_file_location("archive_candidate", base.ROOT / "tools/archive_candidate.py")
        tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tool)
        one = tool.archive_candidate(base.ROOT, package, self.root / "one")
        two = tool.archive_candidate(base.ROOT, package, self.root / "two")
        self.assertEqual(one["sha256"], two["sha256"])
        self.assertEqual(Path(one["checksum"]).name, "maios-project-kernel-5.0.0.sha256")
        self.assertEqual(Path(one["checksum"]).read_text(),
                         one["sha256"] + "  maios-project-kernel-5.0.0.zip\n")
        with zipfile.ZipFile(one["archive"]) as archive:
            members = {name.split("/", 1)[1]: archive.read(name) for name in archive.namelist()}
        self.assertEqual(members, {p.relative_to(package).as_posix(): p.read_bytes()
                                  for p in package.rglob("*") if p.is_file()})
