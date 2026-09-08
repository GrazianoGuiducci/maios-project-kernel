"""Product consumer tests: identified generation, delivery and failure behavior."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from maios_project_kernel import builder, generated_kernel as generated


def source_plan() -> dict:
    projection = json.loads((ROOT / "release/PROJECTION.json").read_text(encoding="utf-8"))
    items, artifacts, owners = [], [], {}
    for index, row in enumerate(projection["files"]):
        if not generated.owns_source(row):
            continue
        source = row["source"]
        path = (".repokernel/" + source if source.startswith("skills/")
                else ".repokernel/resources/autonomous/" + source)
        value = builder.source_identity_bytes(ROOT / source).decode("utf-8")
        aid = f"source-{index}"
        items.append({"path": path, "action": "create", "authority_effect": "none",
                      "content": value, "content_hash": generated.text_hash(value)})
        artifacts.append({"id": aid, "output_path": path, "source_refs": ["product-source"],
                          "content_hash": generated.text_hash(value)})
        owner = source.split("/")[1] if source.startswith("skills/") else "maios-project-system"
        owners.setdefault(owner, []).append(aid)
    by_id = {a["id"]: a for a in artifacts}
    competences = [{"id": owner, "artifact_ids": ids,
                    "entry_artifact": next(aid for aid in ids if by_id[aid]["output_path"] ==
                                           f".repokernel/skills/{owner}/SKILL.md")}
                   for owner, ids in owners.items()]
    record = {"schema": "repokernel.competence-materialization-record.v1",
              "artifacts": artifacts, "competences": competences}
    value = json.dumps(record)
    items.append({"path": generated.RECORD, "action": "create", "authority_effect": "none",
                  "content": value, "content_hash": generated.text_hash(value)})
    return {"schema": "repokernel.generation-plan.v1", "blocked": False,
            "blocked_reasons": [], "apply_policy": "stage_only", "target": {"mode": "new_repository"},
            "plan_id": "1"*64, "compiler_version": "fixture-contract-v1",
            "bundle_provenance": {key: "2"*64 for key in
                                  ("source_manifest_hash", "project_model_hash", "seed_spec_hash")},
            "items": items}


class GeneratedKernelBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = source_plan()

    def save(self, plan=None):
        plan = self.plan if plan is None else plan
        path = self.root / "plan.json"
        path.write_text(json.dumps(plan), encoding="utf-8")
        return path, generated.identity(plan)

    def test_normal_build_consumes_and_reaches_exact_selection(self):
        plan, digest = self.save()
        output = self.root / "package"
        builder.render_distribution(ROOT, output, kernel_plan=plan, kernel_plan_sha256=digest)
        self.assertTrue(builder.verify_distribution(ROOT, output)["valid"])
        receipt = json.loads((output / "MANIFEST.json").read_text())["generated_kernel"]
        self.assertEqual(receipt["plan_sha256"], digest)
        self.assertFalse((output / "payload/.repokernel").exists())
        for row in receipt["artifacts"]:
            self.assertEqual(generated.text_hash((output / row["path"]).read_text(encoding="utf-8")), row["sha256"])
        context = output / "payload/skills/maios-project-context/SKILL.md"
        context.write_text("altered", encoding="utf-8")
        self.assertTrue(any("generated delivery identity" in error
                            for error in builder.verify_distribution(ROOT, output)["errors"]))

    def test_modified_plan_or_blocked_result_cannot_write_output(self):
        path, digest = self.save()
        self.plan["items"][0]["content"] += "\nchanged"
        self.save()
        output = self.root / "package"
        with self.assertRaisesRegex(builder.BuildError, "SHA-256"):
            builder.render_distribution(ROOT, output, kernel_plan=path, kernel_plan_sha256=digest)
        self.assertFalse(output.exists())
        self.plan["blocked"] = True
        path, digest = self.save()
        with self.assertRaisesRegex(builder.BuildError, "unblocked"):
            builder.render_distribution(ROOT, output, kernel_plan=path, kernel_plan_sha256=digest)
        self.assertFalse(output.exists())

    def test_unselected_old_body_is_not_silently_restored(self):
        record_item = next(i for i in self.plan["items"] if i["path"] == generated.RECORD)
        record = json.loads(record_item["content"])
        removed = next(a for a in record["artifacts"] if a["output_path"].endswith("maios-project-context/SKILL.md"))
        record["artifacts"].remove(removed)
        record["competences"] = [c for c in record["competences"] if c["id"] != "maios-project-context"]
        record_item["content"] = json.dumps(record)
        record_item["content_hash"] = generated.text_hash(record_item["content"])
        path, digest = self.save()
        output = self.root / "package"
        builder.render_distribution(ROOT, output, kernel_plan=path, kernel_plan_sha256=digest)
        self.assertFalse((output / "payload/skills/maios-project-context/SKILL.md").exists())
        self.assertFalse(builder.verify_distribution(ROOT, output)["valid"])

    def test_portable_paths_and_unknown_bindings_are_not_guessed(self):
        for path in (".repokernel/skills/../../escape", ".repokernel/skills/AUX.txt",
                     ".repokernel/skills/name:stream", ".repokernel/state/private.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                generated.destination(path)
        self.assertEqual(generated.destination(".repokernel/skills/new-method/references/guide.md"),
                         "payload/skills/new-method/references/guide.md")

    def test_windows_device_identity_matches_generator_policy(self):
        for name in ("CONIN$", "conout$.md", "CON .txt", "COM1 .md", "COM¹.txt",
                     "LPT².md", "lpt³", "name\x7f.md"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                generated.safe_path("payload/skills/method/" + name)
        for name in ("console.md", "COM10.md", "contribution.md"):
            self.assertEqual(generated.safe_path("payload/resources/" + name),
                             "payload/resources/" + name)

    def test_result_hash_is_mandatory_when_selecting_generation(self):
        path, _ = self.save()
        with self.assertRaises(builder.BuildError):
            builder.render_distribution(ROOT, self.root/"package", kernel_plan=path)
        self.assertFalse((self.root/"package").exists())


if __name__ == "__main__":
    unittest.main()
