from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from maios_project_kernel import (  # noqa: E402
    builder,
    configuration,
    host,
    installer,
    operating,
    runtime,
)


class DistributionFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.distribution = self.base / "distribution"
        builder.render_distribution(ROOT, self.distribution)
        verification = builder.verify_distribution(ROOT, self.distribution)
        self.assertTrue(verification["valid"], verification["errors"])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def install(self, host: str = "generic") -> tuple[Path, dict]:
        target = self.base / f"target-{host}"
        plan = installer.make_plan(
            self.distribution, target, "new_repository", host
        )
        self.assertEqual(plan["status"], "ready")
        receipt = installer.apply_plan(self.distribution, plan)
        return target, receipt


class BuilderTests(DistributionFixture):
    def test_distribution_is_source_bound_and_deterministic(self) -> None:
        manifest = builder.read_json(self.distribution / "MANIFEST.json")
        inventory = builder.read_json(self.distribution / "PACKAGE_INVENTORY.json")
        inventory_paths = [item["path"] for item in inventory["files"]]
        self.assertEqual(
            manifest["source_identity"]["tree_sha256"],
            builder.source_tree_digest(ROOT),
        )
        self.assertEqual(inventory_paths, sorted(inventory_paths))
        first = self.base / "first.zip"
        second = self.base / "second.zip"
        self.assertEqual(
            builder.deterministic_zip(self.distribution, first),
            builder.deterministic_zip(self.distribution, second),
        )
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_generated_staging_cannot_enter_source_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.txt").write_text("source\n", encoding="utf-8")
            before = builder.source_tree_digest(root)
            staging = root / ".package.staging"
            staging.mkdir()
            (staging / "generated.txt").write_text("generated\n", encoding="utf-8")
            self.assertEqual(builder.source_tree_digest(root), before)


class InstallerTests(DistributionFixture):
    def test_inventory_refuses_untracked_extraction_residue(self) -> None:
        residue = self.distribution / "payload" / ".maios" / "installer" / "__pycache__" / "installer.pyc"
        residue.parent.mkdir(parents=True)
        residue.write_bytes(b"host-generated residue")
        with self.assertRaisesRegex(installer.InstallerError, "differs from inventory"):
            installer.make_plan(
                self.distribution,
                self.base / "residue-target",
                "new_repository",
                "generic",
            )

    def test_new_install_verify_idempotency_and_changed_file_recovery(self) -> None:
        target, receipt = self.install()
        verification = installer.verify_installation(target, receipt)
        self.assertTrue(verification["installed"])
        repeated = installer.make_plan(
            self.distribution, target, "new_repository", "generic"
        )
        self.assertEqual(repeated["status"], "idempotent")
        self.assertEqual(
            installer.apply_plan(self.distribution, repeated)["plan_digest"],
            receipt["plan_digest"],
        )

        changed = target / "project" / "PROJECT_BRIEF.md"
        changed.write_text("project-owned evolution\n", encoding="utf-8")
        removal = installer.uninstall(target, receipt)
        self.assertFalse(removal["complete"])
        self.assertIn("project/PROJECT_BRIEF.md", removal["preserved_changed"])
        self.assertEqual(changed.read_text(encoding="utf-8"), "project-owned evolution\n")
        self.assertTrue(
            (target / ".maios" / "receipts" / "install" / "CURRENT.json").is_file()
        )

    def test_existing_project_conflict_refuses_and_identical_content_is_preserved(self) -> None:
        conflict_target = self.base / "conflict"
        conflict_target.mkdir()
        (conflict_target / "START_HERE.md").write_text("different\n", encoding="utf-8")
        blocked = installer.make_plan(
            self.distribution, conflict_target, "existing_repository", "generic"
        )
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("target_conflicts_present", blocked["blocked_reasons"])

        target = self.base / "existing"
        target.mkdir()
        preexisting = target / "START_HERE.md"
        preexisting.write_bytes(
            (self.distribution / "payload" / "START_HERE.md").read_bytes()
        )
        plan = installer.make_plan(
            self.distribution, target, "existing_repository", "generic"
        )
        self.assertEqual(plan["status"], "ready")
        self.assertIn("START_HERE.md", plan["preserves_identical"])
        receipt = installer.apply_plan(self.distribution, plan)
        removal = installer.uninstall(target, receipt)
        self.assertTrue(removal["complete"])
        self.assertTrue(preexisting.is_file())
        self.assertFalse((target / ".maios" / "backups").exists())

    def test_selected_host_state_and_native_projection_are_installed_but_unverified(self) -> None:
        target, _ = self.install("codex")
        host_state = json.loads(
            (target / ".maios" / "state" / "HOST_STATE.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(host_state["selected_adapter"], "codex")
        self.assertEqual(host_state["skill_discovery"], "unverified")
        self.assertEqual(
            (target / ".agents" / "skills" / "maios-project-system" / "SKILL.md").read_bytes(),
            (target / "skills" / "maios-project-system" / "SKILL.md").read_bytes(),
        )

    def test_every_declared_host_adapter_projects_the_same_semantic_owner(self) -> None:
        native_paths = {
            "codex": ".agents/skills/maios-project-system/SKILL.md",
            "claude": ".claude/skills/maios-project-system/SKILL.md",
            "opencode": ".opencode/skills/maios-project-system/SKILL.md",
            "hermes": ".hermes/skills/maios-project-system/SKILL.md",
            "dsh": ".agents/skills/maios-project-system/SKILL.md",
        }
        for host in ("generic", "codex", "claude", "opencode", "hermes", "dsh"):
            with self.subTest(host=host):
                target, _ = self.install(host)
                state = json.loads(
                    (target / ".maios" / "state" / "HOST_STATE.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(state["selected_adapter"], host)
                canonical = target / "skills" / "maios-project-system" / "SKILL.md"
                if host in native_paths:
                    self.assertEqual(
                        target.joinpath(*Path(native_paths[host]).parts).read_bytes(),
                        canonical.read_bytes(),
                    )
                if host == "hermes":
                    ignore = (target / ".hermes" / ".gitignore").read_text(
                        encoding="utf-8"
                    )
                    self.assertIn("!skills/maios-project-system/SKILL.md", ignore)
                self.assertTrue(runtime.validate_project(target)["valid"])

    def test_pending_existing_install_has_deterministic_recovery(self) -> None:
        target = self.base / "pending-existing"
        target.mkdir()
        plan = installer.make_plan(
            self.distribution, target, "existing_repository", "generic"
        )
        pending_path = target / ".maios" / "receipts" / "install" / "PENDING.json"
        installer.write_json(pending_path, installer.pending_installation(plan))
        first = next(
            entry for entry in plan["entries"] if entry["destination"] in plan["creates"]
        )
        installer.copy_entry(self.distribution, target, first)
        blocked = installer.make_plan(
            self.distribution, target, "existing_repository", "generic"
        )
        self.assertIn("pending_install_recovery_required", blocked["blocked_reasons"])
        recovery = installer.recover_pending(target)
        self.assertTrue(recovery["complete"])
        self.assertFalse((target / first["destination"]).exists())
        self.assertFalse(pending_path.exists())

    def test_windows_separator_and_drive_paths_are_refused(self) -> None:
        for value in ("..\\escape", "C:/escape", "folder\\child"):
            with self.assertRaises(installer.InstallerError):
                installer.safe_relative(value)
            with self.assertRaises(builder.BuildError):
                builder.safe_relative(value)

    def test_copy_primitive_never_overwrites_a_path_that_appeared(self) -> None:
        target = self.base / "race-target"
        target.mkdir()
        entry = installer.source_entries(self.distribution, "generic")[0]
        destination = target.joinpath(*Path(entry["destination"]).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("concurrent owner bytes\n", encoding="utf-8")
        with self.assertRaises(installer.InstallerError):
            installer.copy_entry(self.distribution, target, entry)
        self.assertEqual(
            destination.read_text(encoding="utf-8"), "concurrent owner bytes\n"
        )


class RuntimeTests(DistributionFixture):
    def resultant_readback(self, event_id: str = "resultant-01") -> dict:
        return {
            "schema": "maios.resultant-readback.v1",
            "event_id": event_id,
            "observed_at": "2026-08-25T08:00:00Z",
            "movement": {
                "circumstance": {
                    "relations": ["configuration_pending", "project_birth"],
                    "requested_result": "form the first correctable useful result",
                    "effect": None,
                },
                "selected_faculties": [
                    {
                        "id": "maios-configuration",
                        "reason": "the project relation is still being situated",
                        "expected_delta": "a source-bound next movement",
                    }
                ],
                "effect_boundary": None,
            },
            "source_positions": {
                "operator_source": ["operator selected a source-first movement"],
                "verified_evidence": ["fixture/resultant-01"],
                "model_inference": ["terminal coupling reduces reentry drift"],
                "retained_unknowns": ["later host behavior remains unverified"],
            },
            "candidate_resultant": {
                "summary": "a reviewed source-bound next movement"
            },
            "preprojection_readback": {
                "status": "corrected",
                "description": "removed the assumption that package presence proves operation",
                "corrections": ["restored the living project relation as source"],
            },
            "actual_result": {
                "status": "completed",
                "classification": "verified_improvement",
                "summary": "the reviewed result now controls project reentry",
                "evidence_refs": ["fixture/resultant-01"],
            },
            "faculty_deltas": [
                {
                    "faculty_id": "maios-configuration",
                    "classification": "verified_improvement",
                    "description": "configuration now receives the terminal result and next movement",
                }
            ],
            "possibility_impact": {
                "opened": ["later recomposition from reviewed result"],
                "preserved": ["unmatched future faculty extensions"],
                "constrained": ["unreviewed self-promotion"],
                "eliminated": ["package presence as operation proof"],
            },
            "next_movement": {
                "current_next": "exercise the next situated movement from reviewed state",
                "reason": "the terminal result is now recoverable without transcript replay",
                "reentry_condition": "current operator intent and causal inputs still agree",
            },
            "effect": {"status": "none", "boundary": None, "receipt_refs": []},
            "self_improvement_assessment": {
                "decision": "no_change",
                "target": {
                    "kind": "router",
                    "id": "situated-faculty-composition",
                    "owner": "project",
                },
                "evidence_refs": ["fixture/resultant-01"],
                "uncertainty": [],
                "expected_delta": "retain open-world routing after this movement",
                "candidate_ref": None,
            },
            "review": {
                "status": "accepted",
                "reviewer": "project operator",
                "reviewer_relation": "operator",
                "producer_is_reviewer": False,
            },
        }

    def test_operating_context_admits_reviewed_resultant_into_reentry(self) -> None:
        target, _ = self.install()
        readback = self.resultant_readback()
        before = operating.operating_status(
            target, readback["movement"]["circumstance"]
        )
        self.assertEqual(before["freshness"]["status"], "changed_or_unobserved")
        self.assertIn(
            "maios-configuration",
            {
                item["id"]
                for item in before["capability_relations"]
                if item["state"] == "eligible"
            },
        )
        validation = operating.validate_resultant_readback(target, readback)
        self.assertTrue(validation["valid"], validation["errors"])

        receipt = operating.admit_resultant_readback(
            target, readback, before["context_sha256"]
        )
        self.assertEqual(receipt["status"], "admitted")
        configuration_state = configuration.current_configuration(target)
        self.assertEqual(configuration_state["checkpoint"]["sequence"], 1)
        self.assertEqual(
            configuration_state["current_next"],
            readback["next_movement"]["current_next"],
        )
        self.assertEqual(
            configuration_state["faculty_composition"]["last_readback"][
                "event_id"
            ],
            readback["event_id"],
        )
        admitted = operating.operating_status(
            target, readback["movement"]["circumstance"]
        )
        self.assertEqual(admitted["freshness"]["status"], "current")
        self.assertEqual(admitted["last_resultant"]["event_id"], readback["event_id"])
        self.assertEqual(admitted["last_assessment"]["decision"], "no_change")
        capsule = configuration.read_json(
            target / ".maios" / "context" / "CONTEXT_CAPSULE.json"
        )
        self.assertEqual(capsule["operating_relation"]["status"], "current")
        self.assertEqual(
            capsule["operating_relation"]["context_sha256"],
            admitted["context_sha256"],
        )
        idempotent = operating.admit_resultant_readback(
            target, readback, admitted["context_sha256"]
        )
        self.assertEqual(idempotent["status"], "idempotent")

    def test_resultant_refuses_unproved_self_improvement_and_stale_context(self) -> None:
        target, _ = self.install()
        readback = self.resultant_readback("resultant-stale")
        invalid = json.loads(json.dumps(readback))
        invalid["self_improvement_assessment"]["decision"] = "improve"
        invalid["self_improvement_assessment"]["evidence_refs"] = []
        validation = operating.validate_resultant_readback(target, invalid)
        self.assertFalse(validation["valid"])
        self.assertTrue(any("improve requires evidence" in item for item in validation["errors"]))

        status = operating.operating_status(
            target, readback["movement"]["circumstance"]
        )
        current = configuration.current_configuration(target)
        changed = json.loads(json.dumps(current))
        changed["checkpoint"] = {
            "sequence": 1,
            "updated_at": "2026-08-25T08:01:00Z",
            "summary": "concurrent project movement",
        }
        changed["current_next"] = "follow the concurrent project movement"
        configuration.apply_configuration(target, changed, configuration.digest(current))
        with self.assertRaisesRegex(
            operating.OperatingStateError, "operating context changed after review"
        ):
            operating.admit_resultant_readback(
                target, readback, status["context_sha256"]
            )

    def test_context_change_reroutes_known_candidates_without_closing_field(self) -> None:
        target, _ = self.install()
        failure = runtime.compose(
            target,
            {
                "relations": ["failure", "unexpected_result"],
                "requested_result": "locate first wrong seam",
            },
        )
        configuration = runtime.compose(
            target,
            {
                "relations": ["configuration_pending", "project_birth"],
                "requested_result": "form first useful movement",
            },
        )
        self.assertTrue(failure["open_world"])
        self.assertIn(
            "failure-localization", {item["id"] for item in failure["known_candidates"]}
        )
        self.assertIn(
            "maios-configuration",
            {item["id"] for item in configuration["known_candidates"]},
        )
        self.assertNotEqual(failure["known_candidates"], configuration["known_candidates"])
        self.assertTrue(runtime.validate_project(target)["valid"])
        emerging = runtime.validate_movement(
            target,
            {
                "circumstance": {
                    "relations": ["unrepresented_domain_relation"],
                    "requested_result": "form a source-native method",
                },
                "selected_faculties": [
                    {
                        "id": "domain-native-method",
                        "reason": "the domain relation changes the result",
                        "expected_delta": "a falsifiable source-native method",
                        "extension": {
                            "source_refs": ["domain/source-1"],
                            "invalidator": "the method cannot reproduce the domain evidence",
                            "reentry_condition": "when the same causal relation returns",
                        },
                    }
                ],
            },
        )
        self.assertTrue(emerging["valid"], emerging["errors"])
        missing_effect_boundary = runtime.validate_movement(
            target,
            {
                "circumstance": {
                    "relations": ["external_action"],
                    "effect": "publish",
                },
                "selected_faculties": [],
            },
        )
        self.assertFalse(missing_effect_boundary["valid"])

    def competence_delta(self) -> dict:
        return {
            "schema": "maios.competence-delta.v2",
            "event_id": "case-01-v1",
            "competence_id": "source-reconciliation",
            "disposition": "retain",
            "work_relation": "reconstruct one owner-correct source lane",
            "source_refs": ["project/source-a", "operator/correction-1"],
            "expected_delta": "avoid package-first implementation",
            "observed_delta": {
                "classification": "verified_improvement",
                "description": "the later build began from the living source tree",
            },
            "evidence_refs": ["tests/source-to-package-identity"],
            "invalidator": "a later case again promotes package-only logic",
            "reentry_condition": "when source and generated artifact may be confused",
            "supersedes_event_id": None,
            "review": {
                "status": "accepted",
                "reviewer": "project operator",
                "reviewer_relation": "operator",
                "producer_is_reviewer": False,
            },
        }

    def test_reviewed_competence_delta_is_admitted_and_self_approval_is_refused(self) -> None:
        target, _ = self.install()
        delta = self.competence_delta()
        validation = runtime.validate_competence_delta(delta)
        self.assertTrue(validation["valid"], validation["errors"])
        status = runtime.competence_status(target)
        receipt = runtime.admit_competence_delta(
            target, delta, status["index_sha256"]
        )
        self.assertEqual(receipt["status"], "admitted")
        after = runtime.competence_status(target)
        self.assertIn("source-reconciliation", after["active"])
        self.assertEqual(after["history_count"], 1)
        idempotent = runtime.admit_competence_delta(
            target, delta, after["index_sha256"]
        )
        self.assertEqual(idempotent["status"], "idempotent")

        revision = self.competence_delta()
        revision["event_id"] = "case-01-v2"
        revision["disposition"] = "revise"
        revision["supersedes_event_id"] = "case-01-v1"
        revision["observed_delta"] = {
            "classification": "tradeoff",
            "description": "the source check costs one read but prevents duplicated implementation",
        }
        revised = runtime.admit_competence_delta(
            target, revision, after["index_sha256"]
        )
        self.assertEqual(revised["status"], "admitted")
        revised_status = runtime.competence_status(target)
        self.assertEqual(
            revised_status["active"]["source-reconciliation"]["event_id"],
            "case-01-v2",
        )
        self.assertEqual(revised_status["history_count"], 2)

        self_approved = self.competence_delta()
        self_approved["event_id"] = "case-02-v1"
        self_approved["competence_id"] = "unreviewed"
        self_approved["review"]["producer_is_reviewer"] = True
        invalid = runtime.validate_competence_delta(self_approved)
        self.assertFalse(invalid["valid"])
        self.assertTrue(any("cannot approve" in error for error in invalid["errors"]))

    def test_configuration_apply_derives_hash_linked_state_and_recovers(self) -> None:
        target, _ = self.install()
        current = configuration.current_configuration(target)
        candidate = json.loads(json.dumps(current))
        candidate["setup_status"] = "configured"
        candidate["checkpoint"] = {
            "sequence": 1,
            "updated_at": "2026-08-24T00:00:00Z",
            "summary": "first reviewed situated configuration",
        }
        candidate["operator_relation"]["current_intent"] = "form a source-backed project"
        candidate["operator_relation"]["point_of_view"] = "project operator"
        candidate["operator_relation"]["direction_status"] = "selected"
        candidate["result"].update(
            {
                "current": "an owner-correct project source",
                "beneficiary": "project operator",
                "value_mechanism": "less repeated reconstruction",
                "smallest_deliverable": "one reviewed source lane",
                "owner_review": "accepted",
            }
        )
        candidate["first_proof"].update(
            {
                "statement": "the next movement starts from the selected source",
                "falsifiable_test": "a fresh reentry selects a generated payload as source",
                "reviewer": "project operator",
                "result": "unverified",
            }
        )
        candidate["people_and_environment"]["sources"] = ["project/source-a"]
        candidate["current_next"] = "produce the first useful result"

        validation = configuration.validate_configuration(candidate)
        self.assertTrue(validation["valid"], validation["errors"])
        receipt = configuration.apply_configuration(
            target, candidate, configuration.digest(current)
        )
        self.assertEqual(receipt["status"], "applied")
        status = configuration.configuration_status(target)
        self.assertTrue(status["handoff_ready"])
        self.assertEqual(status["context_projection"], "current")
        self.assertEqual(status["setup_spec_projection"], "current")
        spec = configuration.read_json(
            target / ".maios" / "context" / "SETUP_SPEC.json"
        )
        self.assertFalse(spec["form_state_imported"])
        self.assertEqual(spec["status"], "accepted")
        stale_candidate = json.loads(json.dumps(candidate))
        stale_candidate["checkpoint"]["sequence"] = 2
        stale_candidate["current_next"] = "a concurrent next movement"
        with self.assertRaises(configuration.ConfigurationError):
            configuration.apply_configuration(
                target, stale_candidate, configuration.digest(current)
            )

        recovery = configuration.recover_configuration(target, receipt)
        self.assertEqual(recovery["status"], "recovered")
        self.assertEqual(
            configuration.current_configuration(target)["setup_status"], "pending"
        )

    def host_attestation(self, event_id: str, stage: str) -> dict:
        return {
            "schema": "maios.host-attestation.v2",
            "event_id": event_id,
            "host": "codex",
            "stage": stage,
            "result": "verified",
            "observation": f"observed {stage} in a fresh process",
            "evidence_refs": [f"fixture/{event_id}"],
            "observed_capabilities": [stage],
            "review": {
                "status": "accepted",
                "reviewer": "project operator",
                "reviewer_relation": "operator",
                "producer_is_reviewer": False,
            },
        }

    def test_host_claims_advance_only_from_reviewed_observation_dependencies(self) -> None:
        target, _ = self.install("codex")
        initial = host.host_status(target)
        premature = self.host_attestation("host-early", "behavioral_activation")
        with self.assertRaises(host.HostAttestationError):
            host.admit_host_attestation(
                target, premature, initial["host_state_sha256"]
            )

        current_sha = initial["host_state_sha256"]
        for event_id, stage in (
            ("host-skill", "skill_discovery"),
            ("host-state", "state_read"),
            ("host-behavior", "behavioral_activation"),
            ("host-reentry", "maintained_reentry"),
        ):
            attestation = self.host_attestation(event_id, stage)
            validation = host.validate_host_attestation(attestation)
            self.assertTrue(validation["valid"], validation["errors"])
            receipt = host.admit_host_attestation(
                target, attestation, current_sha
            )
            self.assertEqual(receipt["status"], "admitted")
            current_sha = host.host_status(target)["host_state_sha256"]
        final = host.host_status(target)
        self.assertEqual(final["behavioral_activation"], "verified")
        self.assertEqual(final["maintained_reentry"], "verified")


class ArchiveFreshProcessTests(DistributionFixture):
    def test_extracted_archive_installs_and_runs_without_source_imports(self) -> None:
        archive = self.base / "candidate.zip"
        builder.deterministic_zip(self.distribution, archive)
        extracted = self.base / "extracted"
        with zipfile.ZipFile(archive) as zipped:
            zipped.extractall(extracted)
        target = self.base / "fresh-target"
        plan = self.base / "fresh-plan.json"

        preview = subprocess.run(
            [
                sys.executable,
                str(extracted / "install.py"),
                "preview",
                "--target",
                str(target),
                "--mode",
                "new_repository",
                "--host",
                "codex",
                "--plan-out",
                str(plan),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(preview.returncode, 0, preview.stderr)
        apply = subprocess.run(
            [
                sys.executable,
                str(extracted / "install.py"),
                "apply",
                "--plan",
                str(plan),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(apply.returncode, 0, apply.stderr)
        self.assertFalse(any(path.name == "__pycache__" for path in extracted.rglob("*")))
        status = subprocess.run(
            [sys.executable, "-B", str(target / "maios.py"), "status"],
            cwd=target,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertTrue(json.loads(status.stdout)["valid"])
        competence_status = subprocess.run(
            [
                sys.executable,
                "-B",
                str(target / "maios.py"),
                "competence-status",
            ],
            cwd=target,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(competence_status.returncode, 0, competence_status.stderr)
        self.assertEqual(json.loads(competence_status.stdout)["history_count"], 0)
        operating_status = subprocess.run(
            [
                sys.executable,
                "-B",
                str(target / "maios.py"),
                "operating-status",
            ],
            cwd=target,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(operating_status.returncode, 0, operating_status.stderr)
        operating_projection = json.loads(operating_status.stdout)
        self.assertEqual(operating_projection["schema"], "maios.operating-context.v1")
        self.assertEqual(operating_projection["authority_ceiling"], "none")
        self.assertEqual(
            operating_projection["freshness"]["status"],
            "changed_or_unobserved",
        )
        self.assertTrue(
            (target / ".agents" / "skills" / "maios-project-system" / "SKILL.md").is_file()
        )


if __name__ == "__main__":
    unittest.main()
