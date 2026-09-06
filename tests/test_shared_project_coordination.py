from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys

import test_builder_installer_runtime as base


class SharedProjectCoordinationTests(base.DistributionFixture):
    def command(self, target, *args):
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(target / "maios.py"), *args],
            cwd=target, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_installed_handoff_reaches_live_method_without_configuring_another_host(self):
        target, _ = self.install("codex")
        # Windows temporary roots may use a short-path alias. Compare resolved
        # paths on both sides while retaining the project-confinement assertion.
        target = target.resolve()
        state_paths = list((target / ".maios/state").glob("*.json"))
        before = {path: path.read_bytes() for path in state_paths}
        request = self.base / "circumstance.json"
        request.write_text(json.dumps({
            "relations": ["instance_handoff", "shared_project_continuation"],
            "requested_result": "continue project work through another harness",
        }), encoding="utf-8")
        result = self.command(target, "compose", "--circumstance", str(request))
        entry = next(item["entry"] for item in result["known_candidates"]
                     if item["id"] == "intent-preserving-delegation")
        body = target / entry
        self.assertTrue(body.is_file())
        # Follow the delivered relative link, not a source-clone import.
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", body.read_text(encoding="utf-8"))
        methods = [(body.parent / link).resolve() for link in links
                   if "shared-project-continuity" in link]
        self.assertEqual(len(methods), 1)
        method = methods[0]
        self.assertTrue(method.is_relative_to(target))
        self.assertTrue(method.is_file())
        relative = method.relative_to(target).as_posix()
        observed = self.command(target, "knowledge-status", "--path", relative)
        self.assertEqual(observed["files"][relative]["status"], "present")
        initial_digest = observed["files"][relative]["sha256"]
        # A receiving project's evolution remains visible in a fresh process.
        with method.open("a", encoding="utf-8") as stream:
            stream.write("\nLocal case: resume from the selected worktree's live sources.\n")
        evolved = self.command(target, "knowledge-status", "--path", relative)
        self.assertNotEqual(evolved["files"][relative]["sha256"], initial_digest)
        self.assertEqual(evolved["files"][relative]["sha256"],
                         hashlib.sha256(method.read_bytes()).hexdigest())
        request.write_text(json.dumps({"relations": ["ordinary_local_edit"]}), encoding="utf-8")
        ordinary = self.command(target, "compose", "--circumstance", str(request))
        self.assertNotIn("intent-preserving-delegation",
                         {item["id"] for item in ordinary["known_candidates"]})
        self.assertTrue(ordinary["open_world"])
        self.assertEqual({path: path.read_bytes() for path in state_paths}, before)
        self.assertEqual(set((target / ".maios/state").glob("*.json")), set(state_paths))
