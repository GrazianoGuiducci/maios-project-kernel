from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import test_builder_installer_runtime as base

from maios_project_kernel import builder, configuration, host, installer, operating, runtime


class KnowledgeContinuationTests(base.DistributionFixture):
    def event(self, event_id):
        return base.RuntimeTests.resultant_readback(self, event_id)

    def learn(self, meaning, owner_id="design", surface="project/design"):
        return {
            "owner": {"kind": "competence", "id": owner_id, "owner": surface},
            "what_happened": meaning,
            "causal_delta": meaning,
            "why_it_matters": "preserve the useful distinction for future work",
            "future_behavior": meaning,
            "source_refs": ["project/notes.md"],
            "activation_relations": ["design_reentry"],
            "invalidator": "the source or a later result changes this distinction",
            "reentry_condition": "the design relation becomes pertinent",
        }

    def apply(self, target, event):
        context = operating.operating_status(target, event["movement"]["circumstance"])
        return operating.apply_resultant_readback(target, event, context["context_sha256"])

    def test_learning_coexists_without_forcing_the_next_field(self):
        target, _ = self.install()
        event = self.event("coexist")
        event["next_movement"]["relations"] = ["unrelated_next_work"]
        event["learning_deltas"] = [
            self.learn("first aspect", "a/b"),
            self.learn("second aspect", "a/b"),
            self.learn("first aspect", "a b"),
            self.learn("first aspect", "a/b", "another/project"),
        ]
        receipt = self.apply(target, event)
        self.assertEqual(len(set(receipt["learning_relations"])), 4)
        self.assertEqual(operating.learning_status(target)["count"], 4)
        next_field = operating.operating_status(target, {"relations": ["unrelated_next_work"]})
        self.assertFalse(any(x["kind"] == "competence_learning_relation"
                             for x in next_field["composition"]["known_candidates"]
                             if "kind" in x))
        later = operating.compose(target, {"relations": ["design_reentry"]})
        self.assertTrue(set(receipt["learning_relations"]).issubset(
            {x["id"] for x in later["known_candidates"]}))
        next_event = self.event("choose-another-contribution")
        next_event["movement"]["circumstance"]["relations"] = ["design_reentry"]
        selected = receipt["learning_relations"][0]
        next_event["movement"]["selected_faculties"] = [{"id": selected,
            "reason": "only this aspect changes the present result", "expected_delta": "a useful design distinction"}]
        next_event["faculty_deltas"] = [{"faculty_id": selected, "description": "one aspect changed the result"}]
        self.assertTrue(operating.validate_resultant_readback(target, next_event)["valid"])
        self.apply(target, next_event)
        self.assertEqual([x["relation_id"] for x in operating.learning_status(target)["relations"] if x["later_uses"]], [selected])

    def test_supersession_and_cooling_preserve_revision_specific_evidence(self):
        target, _ = self.install()
        first = self.event("learn-a")
        first["learning_deltas"] = [self.learn("method A")]
        original_id = self.apply(target, first)["learning_relations"][0]
        use = self.event("use-a")
        use["movement"]["circumstance"]["relations"] = ["design_reentry"]
        use["movement"]["selected_faculties"] = [{
            "id": original_id, "reason": "the earlier distinction helps here",
            "expected_delta": "a different design decision",
        }]
        use["faculty_deltas"] = [{"faculty_id": original_id, "description": "A changed this later decision"}]
        self.apply(target, use)
        revised = self.event("learn-b")
        revised["learning_deltas"] = [dict(self.learn("method B"), supersedes=[original_id],
                                          supersession_reason="new evidence replaces only A")]
        successor_id = self.apply(target, revised)["learning_relations"][0]
        relations = {x["relation_id"]: x for x in operating.learning_status(target, include_cold=True)["relations"]}
        self.assertTrue(relations[original_id]["later_nonidentical_use_observed"])
        self.assertEqual(relations[original_id]["status"], "superseded")
        self.assertFalse(relations[successor_id]["later_nonidentical_use_observed"])
        self.assertEqual(relations[successor_id]["later_uses"], [])
        for status in ("cooled", "reachable", "retired"):
            transition = self.event("status-" + status)
            transition["learning_transitions"] = [{
                "relation_id": successor_id, "status": status,
                "reason": "the actual present relation changed",
                "reentry_condition": "new evidence makes this useful again",
            }]
            self.apply(target, transition)
            recalled = {x["id"] for x in operating.compose(target, {"relations": ["design_reentry"]})["known_candidates"]}
            self.assertEqual(successor_id in recalled, status == "reachable")
        self.assertEqual(operating.learning_status(target)["count"], 0)
        self.assertEqual(operating.learning_status(target, include_cold=True)["count"], 2)

    def test_live_native_entry_observes_changed_body_and_preserves_baseline(self):
        target, receipt = self.install("codex")
        entry = ".agents/skills/maios-project-context/SKILL.md"
        source = "skills/maios-project-context/SKILL.md"
        original = (target / source).read_bytes()
        baseline = copy.deepcopy(receipt["update_baseline"])
        observed = operating.knowledge_status(target, [entry])
        self.assertIn(source, observed["files"])
        event = self.event("knowledge-use")
        event["movement"]["circumstance"]["knowledge_refs"] = [entry]
        context = operating.operating_status(target, event["movement"]["circumstance"])
        (target / "unrelated.txt").write_text("another surface", encoding="utf-8")
        unchanged = operating.operating_status(target, event["movement"]["circumstance"])
        self.assertEqual(unchanged["context_sha256"], context["context_sha256"])
        (target / source).write_bytes(original + b"\nLearned source distinction.\n")
        current = operating.knowledge_status(target, [entry])
        self.assertNotEqual(current["files"][source], observed["files"][source])
        self.assertEqual(current["files"][entry], observed["files"][entry])
        with self.assertRaisesRegex(operating.OperatingStateError, "context changed"):
            operating.apply_resultant_readback(target, event, context["context_sha256"])
        self.assertEqual(receipt["update_baseline"], baseline)
        self.assertTrue(any(x["destination"] == source for x in baseline["files"]))
        result = subprocess.run([sys.executable, "-B", str(target / "maios.py"),
                                 "knowledge-status", "--path", entry], cwd=target, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(source, json.loads(result.stdout)["files"])
        with self.assertRaises(operating.OperatingStateError):
            operating.knowledge_status(target, ["../outside.md"])

    def test_failed_host_observation_retires_only_affected_capability(self):
        target, _ = self.install("codex")
        observed = base.RuntimeTests.host_attestation(self, "available", "instruction_discovery")
        observed["observed_capabilities"] = ["read_sources", "write_sources"]
        state = host.read_host_state(target)
        host.admit_host_attestation(target, observed, host.digest(state))
        failed = base.RuntimeTests.host_attestation(self, "changed-access", "instruction_discovery")
        failed.update(result="failed", observed_capabilities=[], invalidated_capabilities=["write_sources"])
        host.admit_host_attestation(target, failed, host.digest(host.read_host_state(target)))
        state = host.read_host_state(target)
        self.assertEqual(state["observed_capabilities"], ["read_sources"])
        self.assertIn("write_sources", state["unverified_capabilities"])
        projected = operating.operating_status(target)
        capability = next(x for x in projected["capability_relations"] if x["id"] == "write_sources")
        self.assertEqual(capability["state"], "unknown")
        self.assertEqual(len(state["attestation_history"]), 2)

    def test_historical_input_survives_live_field_evolution_but_not_tampering(self):
        isolated = self.base / "source"
        shutil.copytree(base.ROOT, isolated, ignore=shutil.ignore_patterns(".git", "package", "__pycache__", ".pytest_cache"))
        field_path = isolated / "kernel/FACULTY_FIELD.json"
        field = json.loads(field_path.read_text(encoding="utf-8"))
        field["extension_rule"] += " A further situated relation."
        field_path.write_text(json.dumps(field), encoding="utf-8")
        builder.repokernel_projection_inputs(isolated)
        snapshot = isolated / "release/repokernel/input-snapshots/FACULTY_FIELD.json"
        snapshot.write_bytes(snapshot.read_bytes() + b" ")
        with self.assertRaisesRegex(builder.BuildError, "input digest drifted"):
            builder.repokernel_projection_inputs(isolated)

    def test_inferred_intent_keeps_its_source_in_working_projections(self):
        target, _ = self.install()
        state = configuration.current_configuration(target)
        state["operator_relation"]["current_intent"] = "improve source reconciliation"
        state["operator_relation"]["intent_source"] = "inferred from project notes; correctable"
        self.assertIn(state["operator_relation"]["intent_source"], configuration.current_state_markdown(state))
        self.assertIn(state["operator_relation"]["intent_source"], configuration.project_brief_markdown(state))
        context = operating._operating_status(target, configuration_override=state)
        self.assertEqual(context["active_object"]["intent_source"], state["operator_relation"]["intent_source"])

    def fresh(self, target, *arguments, expected=0):
        result = subprocess.run([sys.executable, "-B", str(target / "maios.py"), *arguments],
                                cwd=target, capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def test_default_reentry_keeps_source_identity_and_can_change_selection(self):
        target, _ = self.install("codex")
        entry = ".agents/skills/maios-project-context/SKILL.md"
        body = target / "skills/maios-project-context/SKILL.md"
        event = self.event("retain-knowledge")
        event["movement"]["circumstance"]["knowledge_refs"] = [entry]
        receipt = self.apply(target, event)
        self.assertEqual(receipt["consumed_knowledge_refs"], [entry])
        initial = self.fresh(target, "operating-status")
        self.assertEqual(initial["knowledge_refs"], [entry])
        self.assertEqual(initial["freshness"]["changed_inputs"], [])
        body.write_bytes(body.read_bytes() + b"\nA new distinction changes the next use.\n")
        changed = self.fresh(target, "operating-status")
        self.assertEqual(changed["freshness"]["changed_inputs"], ["knowledge"])
        self.apply(target, self.event("inherit-selected-knowledge"))
        self.assertEqual(self.fresh(target, "operating-status")["knowledge_refs"], [entry])
        cleared = self.event("different-work")
        cleared["movement"]["circumstance"]["knowledge_refs"] = []
        self.apply(target, cleared)
        body.write_bytes(body.read_bytes() + b"\nNo longer a selected input.\n")
        final = self.fresh(target, "operating-status")
        self.assertEqual(final["knowledge_refs"], [])
        self.assertEqual(final["freshness"]["changed_inputs"], [])

    def test_plural_cross_owner_genealogy_and_predecessor_reopening(self):
        target, _ = self.install()
        first = self.event("origin")
        first["learning_deltas"] = [self.learn("original method")]
        original = self.apply(target, first)["learning_relations"][0]
        context = {"relation": "transfer the useful method and preserve independent continuations",
                   "source_refs": ["project/ownership-decision.md"]}
        branch = self.event("branch")
        branch["learning_deltas"] = [dict(self.learn("security method", "security", "project/security"),
                                         supersedes=[original], supersession_reason="new receiving responsibility")]
        self.assertFalse(operating.validate_resultant_readback(target, branch)["valid"])
        branch["learning_deltas"][0]["supersession_context"] = context
        successor = self.apply(target, branch)["learning_relations"][0]
        self.assertEqual(self.apply(target, branch)["status"], "idempotent")
        plural = self.event("plural")
        plural["learning_deltas"] = [dict(self.learn("another method"), supersedes=[original],
                                         supersession_reason="another continuation is now useful")]
        self.assertFalse(operating.validate_resultant_readback(target, plural)["valid"])
        plural["learning_deltas"][0]["supersession_context"] = context
        plural["learning_deltas"].append(dict(self.learn("a third method"), supersedes=[original],
                                              supersession_reason="independent parallel meaning", supersession_context=context))
        successors = [successor, *self.apply(target, plural)["learning_relations"]]
        reopened = self.event("reopen-predecessor")
        reopened["learning_transitions"] = [{"relation_id": original, "status": "reachable",
            "reason": "the earlier method applies in this different present", "reentry_condition": "the original source applies"}]
        self.apply(target, reopened)
        rows = {x["relation_id"]: x for x in operating.learning_status(target, include_cold=True)["relations"]}
        self.assertEqual(rows[original]["superseded_by"], successors)
        self.assertEqual(rows[original]["status"], "reachable")
        self.assertEqual(rows[original]["lifecycle"][-1]["from_status"], "superseded")
        self.assertEqual(len(rows[original]["lifecycle"]), 5)
        self.assertTrue(all(rows[x]["supersedes"] == [original] for x in successors))
        self.assertFalse(any(rows[x]["later_nonidentical_use_observed"] for x in successors))
        self.assertEqual(self.fresh(target, "learning-status")["count"], 4)

    def test_corrupt_learning_state_is_rejected_before_recall(self):
        target, _ = self.install()
        event = self.event("one-learning")
        event["learning_deltas"] = [self.learn("a reusable distinction")]
        self.apply(target, event)
        original = operating.read_operating_state(target)
        mutations = [
            lambda s: s["learning_relations"].append(copy.deepcopy(s["learning_relations"][0])),
            lambda s: s["learning_relations"][0].update(status="unsupported"),
            lambda s: s["learning_relations"][0].update(owner=None),
            lambda s: s["learning_relations"][0].update(origin_event_id=[]),
            lambda s: s["learning_relations"][0].update(superseded_by=["missing-relation"]),
            lambda s: s["learning_relations"][0].update(later_nonidentical_use_observed=True),
            lambda s: s["learning_relations"][0].update(lifecycle=[None]),
            lambda s: s.update(active_knowledge_refs=["../outside.md"]),
            lambda s: s.pop("active_knowledge_refs"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutations.index(mutate)):
                candidate = copy.deepcopy(original)
                mutate(candidate)
                operating.write_json_atomic(operating.operating_state_path(target), candidate)
                with self.assertRaises(operating.OperatingStateError):
                    operating.operating_status(target)
                result = self.fresh(target, "status", expected=2)
                self.assertFalse(result["valid"])
                self.assertFalse(result["validation_levels"]["operating_state_readable"])
        operating.write_json_atomic(operating.operating_state_path(target), original)
        self.assertEqual(operating.learning_status(target)["count"], 1)

    def test_runtime_reports_missing_continuum_organs(self):
        target, _ = self.install()
        for name in ("FOUNDING_RELATIONS.md", "KNOWLEDGE_CONTINUUM.md", "UPDATE_CONTINUITY.md"):
            with self.subTest(organ=name):
                relative = ".maios/kernel/" + name
                path = target / relative
                original = path.read_bytes()
                path.unlink()
                result = self.fresh(target, "status", expected=2)
                self.assertFalse(result["valid"])
                self.assertIn(relative, result["missing"])
                path.write_bytes(original)

    def test_configured_intent_requires_provenance_and_keeps_it_after_apply(self):
        target, _ = self.install()
        current = configuration.current_configuration(target)
        candidate = copy.deepcopy(current)
        candidate["setup_status"] = "configured"
        candidate["operator_relation"].update(current_intent="improve the existing design", point_of_view="project operator", direction_status="selected")
        candidate["result"].update(current="a useful change", beneficiary="operator", smallest_deliverable="design correction", owner_review="accepted")
        candidate["first_proof"].update(statement="the result is usable", falsifiable_test="inspect the receiving behavior", reviewer="operator", result="unverified")
        candidate["checkpoint"]["sequence"] += 1
        validation = configuration.validate_configuration(candidate)
        self.assertIn("operator_relation.intent_source", validation["missing_decisions"])
        with self.assertRaises(configuration.ConfigurationError):
            configuration.apply_configuration(target, candidate, configuration.digest(current))
        provenance = "inferred from project/design.md and the present correction; revisable"
        candidate["operator_relation"]["intent_source"] = provenance
        configuration.apply_configuration(target, candidate, configuration.digest(current))
        self.assertEqual(self.fresh(target, "operating-status")["active_object"]["intent_source"], provenance)
        self.assertIn(provenance, (target / "project/CURRENT_STATE.md").read_text(encoding="utf-8"))

    def test_source_contact_records_no_change_and_retains_last_success_on_failure(self):
        target, _ = self.install()
        status = self.fresh(target, "source-contact-status", "--at", "2026-09-05T00:00:00Z")
        self.assertTrue(status["ordinary_contact_due"])
        observation = {"observed_at": "2026-09-05T00:00:00Z", "status": "observed",
                       "source_identity": "upstream-commit-a", "summary": "no useful upstream difference"}
        path = target / "contact.json"
        path.write_text(json.dumps(observation), encoding="utf-8")
        self.fresh(target, "record-source-contact", "--observation", str(path), "--expected-state-sha256", status["configuration_sha256"])
        self.assertFalse(self.fresh(target, "source-contact-status", "--at", "2026-09-11T23:59:59Z")["ordinary_contact_due"])
        due = self.fresh(target, "source-contact-status", "--at", "2026-09-12T00:00:00Z")
        self.assertTrue(due["ordinary_contact_due"])
        failed = dict(observation, observed_at="2026-09-12T00:00:00Z", status="unavailable", source_identity=None, summary="source unavailable; resume when connectivity returns")
        configuration.record_source_contact(target, failed, due["configuration_sha256"])
        final = self.fresh(target, "source-contact-status", "--at", "2026-09-13T00:00:00Z")
        self.assertEqual(final["last_success"], observation)
        self.assertEqual(final["last_attempt"], failed)
        self.assertTrue(final["pending"])
        self.assertFalse(final["ordinary_contact_due"])
        state = configuration.current_configuration(target)
        malformed = copy.deepcopy(state)
        malformed["source_contact"]["last_success"] = failed
        self.assertFalse(configuration.validate_configuration(malformed)["valid"])

    def test_update_baseline_validates_original_plan_without_rejecting_local_learning(self):
        target, receipt = self.install("codex")
        body = target / "skills/maios-project-context/SKILL.md"
        body.write_bytes(body.read_bytes() + b"\nLocal learned method.\n")
        valid = installer.verify_installation(target, receipt)
        self.assertTrue(valid["valid"])
        self.assertIn("target_evolved", [item["state"] for item in valid["files"]])
        mutations = [lambda r: r["update_baseline"].update(schema="invalid"),
                     lambda r: r["update_baseline"].update(files=[]),
                     lambda r: r["update_baseline"]["files"][0].update(sha256="0" * 64),
                     lambda r: r["update_baseline"]["package_identity"].update(version="unknown"),
                     lambda r: r["install_plan"]["entries"][0].update(sha256="0" * 64)]
        for mutate in mutations:
            altered = copy.deepcopy(receipt)
            mutate(altered)
            result = installer.verify_installation(target, altered)
            self.assertFalse(result["installed"])
            self.assertFalse(result["valid"])
            self.assertTrue(result["baseline"]["errors"])

    def test_corrupt_receipt_cannot_verify_reapply_or_remove_an_installation(self):
        for mode in ("new_repository", "existing_repository"):
            target = self.base / mode
            if mode == "existing_repository":
                target.mkdir()
                shutil.copyfile(self.distribution / "payload/AGENTS.md", target / "AGENTS.md")
            plan = installer.make_plan(self.distribution, target, mode, "generic")
            receipt = installer.apply_plan(self.distribution, plan)
            repeated = installer.make_plan(self.distribution, target, mode, "generic")
            self.assertEqual(repeated["status"], "idempotent")
            current = target / ".maios/receipts/install/CURRENT.json"
            snapshot = lambda: {p.relative_to(target).as_posix(): p.read_bytes()
                                for p in target.rglob("*") if p.is_file()}
            original = snapshot()
            mutations = {
                "installer_owned_files": [],
                "preserved_preexisting_identical": ["unowned.txt"],
                "backup_root": ".maios/backups/unrelated",
                "installer_owned_backup_files": [{"path": "unowned.txt", "sha256": "0" * 64}],
            }
            for key, value in mutations.items():
                with self.subTest(mode=mode, field=key):
                    altered = copy.deepcopy(receipt)
                    altered[key] = value
                    installer.write_json(current, altered)
                    before = snapshot()
                    result = installer.verify_installation(target, altered)
                    self.assertTrue(result["baseline"]["valid"])
                    self.assertFalse(result["valid"])
                    self.assertFalse(result["installed"])
                    self.assertIn(key, " ".join(result["receipt_validation"]["errors"]))
                    self.assertIsNone(installer.current_receipt(target))
                    for explicit in (None, current):
                        with self.assertRaises(installer.InstallerError):
                            installer.load_receipt(target, explicit)
                    blocked = installer.make_plan(self.distribution, target, mode, "generic")
                    self.assertEqual(blocked["status"], "blocked")
                    self.assertIn("invalid_current_installation_receipt", blocked["blocked_reasons"])
                    for reapply in (repeated, blocked):
                        with self.assertRaises(installer.InstallerError):
                            installer.apply_plan(self.distribution, reapply)
                    with self.assertRaises(installer.InstallerError):
                        installer.uninstall(target, altered)
                    cli = subprocess.run([sys.executable, "-B", str(target / ".maios/installer/installer.py"),
                                          "uninstall", "--target", str(target)], capture_output=True, text=True)
                    self.assertEqual(cli.returncode, 2, cli.stdout or cli.stderr)
                    self.assertEqual(before, snapshot())
                    current.write_bytes(original[".maios/receipts/install/CURRENT.json"])
            self.assertEqual(original, snapshot())
            self.assertEqual(installer.apply_plan(self.distribution, repeated), receipt)
            self.assertTrue(installer.uninstall(target, receipt)["complete"])
            if mode == "existing_repository":
                self.assertEqual((target / "AGENTS.md").read_bytes(), original["AGENTS.md"])

    def test_general_status_rejects_invalid_configuration_through_its_owner(self):
        target, _ = self.install()
        original = configuration.current_configuration(target)
        configured = copy.deepcopy(original)
        configured["setup_status"] = "configured"
        configured["operator_relation"].update(current_intent="improve the design", intent_source="operator's project direction",
                                              point_of_view="project operator", direction_status="selected")
        configured["result"].update(current="a useful change", beneficiary="operator", smallest_deliverable="design correction", owner_review="accepted")
        configured["first_proof"].update(statement="the result is usable", falsifiable_test="inspect the receiving behavior", reviewer="operator", result="unverified")
        self.assertTrue(configuration.validate_configuration(configured)["valid"])
        mutations = [
            lambda s: s["operator_relation"].update(intent_source=None),
            lambda s: s.pop("source_contact"),
            lambda s: s.update(source_contact={"last_attempt": "invalid", "last_success": None}),
        ]
        path = target / "setup/CONFIGURATION_STATE.json"
        for mutate in mutations:
            candidate = copy.deepcopy(configured)
            mutate(candidate)
            path.write_text(json.dumps(candidate), encoding="utf-8")
            with self.assertRaises(configuration.ConfigurationError):
                configuration.current_configuration(target)
            result = self.fresh(target, "status", expected=2)
            self.assertFalse(result["valid"])
            self.assertFalse(result["validation_levels"]["configuration_state_readable"])
        path.write_text(json.dumps(configured), encoding="utf-8")
        self.assertTrue(self.fresh(target, "status")["valid"])

    def test_first_user_contracts_distinguish_incompatible_state_shapes(self):
        target, receipt = self.install()
        self.assertEqual(receipt["schema"], "maios.installation-receipt.v3")
        self.assertEqual(receipt["update_baseline"]["configuration_schema"], "maios.configuration-state.v3")
        self.assertEqual(receipt["update_baseline"]["operating_schema"], "maios.operating-state.v3")
        for relative, schema, reader in (
            ("setup/CONFIGURATION_STATE.json", "maios.configuration-state.v3", configuration.current_configuration),
            (".maios/state/OPERATING_STATE.json", "maios.operating-state.v3", operating.read_operating_state),
        ):
            path = target / relative
            state = reader(target)
            self.assertEqual(state["schema"], schema)
            state["schema"] = schema.replace(".v3", ".v2")
            path.write_text(json.dumps(state), encoding="utf-8")
            self.assertFalse(self.fresh(target, "status", expected=2)["valid"])
            state["schema"] = schema
            path.write_text(json.dumps(state), encoding="utf-8")
        receipt["schema"] = "maios.installation-receipt.v2"
        self.assertFalse(installer.validate_installation_receipt(receipt)["valid"])
