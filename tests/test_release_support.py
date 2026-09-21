"""Exercise the changed runtime and Hermes installation boundaries."""
import json
from pathlib import Path
import subprocess
import sys

import test_builder_installer_runtime as base
from maios_project_kernel import installer


class ReleaseSupportTests(base.DistributionFixture):
    def test_distribution_entry_guards_reject_310_and_accept_minimum(self):
        for entry in [self.distribution / "install.py", self.distribution / "payload/maios.py"]:
            for version, succeeds in [("(3, 10, 99)", False), ("(3, 11, 0)", True)]:
                with self.subTest(entry=entry.name, version=version):
                    code = ("import runpy,sys; sys.version_info=" + version + "; "
                            "sys.argv=[sys.argv[1],'--help']; "
                            "runpy.run_path(sys.argv[0],run_name='__main__')")
                    result = subprocess.run([sys.executable, "-B", "-c", code, str(entry)],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode == 0, succeeds, result.stderr)
                    if not succeeds:
                        self.assertIn("requires Python >=3.11", result.stderr)

    def test_hermes_preserves_existing_profile_and_does_not_grant_trust(self):
        target = self.base / "existing"
        profile = target / ".hermes"
        profile.mkdir(parents=True)
        sentinels = {"config.yaml": b"user configuration\n", ".gitignore": b"user rules\n",
                     "sessions/keep.json": b"user session\n"}
        for name, data in sentinels.items():
            path = profile / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        plan = installer.make_plan(self.distribution, target, "existing_repository", "hermes")
        self.assertEqual(plan["status"], "ready")
        receipt = installer.apply_plan(self.distribution, plan)
        self.assertTrue((profile / "skills/maios-project-system/SKILL.md").is_file())
        for name, data in sentinels.items():
            self.assertEqual((profile / name).read_bytes(), data)
        installer.uninstall(target, receipt)
        for name, data in sentinels.items():
            self.assertEqual((profile / name).read_bytes(), data)

    def test_qualified_support_metadata_and_codex_identity(self):
        manifest = json.loads((self.distribution / "MANIFEST.json").read_text())
        support = manifest["runtime_requirements"]
        self.assertEqual(support["python"], ">=3.11")
        self.assertEqual(support["qualified_python_versions"], ["3.11", "3.12", "3.13", "3.14"])
        self.assertEqual(support["qualified_operating_systems"], ["Linux", "Windows", "macOS"])
        self.assertEqual(support["third_party_python_packages"], [])
        adapters = json.loads((self.distribution / "adapters/ADAPTERS.json").read_text())
        codex = next(a for a in adapters["adapters"] if a["id"] == "codex")
        self.assertEqual(codex["display_name"], "Codex")
        self.assertTrue(all(p["destination"].startswith(".agents/skills/") for p in codex["projections"]))
