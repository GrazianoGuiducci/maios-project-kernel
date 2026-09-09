"""Renew the autonomous method selection from committed sources and RepoKernel."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import re
import subprocess
import sys

from .generated_kernel import destination, identity, load, owns_source, safe_path, text_hash


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Cannot read selected Git source: " + result.stderr.decode(errors="replace"))
    return result.stdout


def commit_id(root: Path, commit: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Select a full immutable source commit")
    actual = git(root, "rev-parse", "--verify", commit + "^{commit}").decode().strip()
    if actual != commit:
        raise ValueError("Source identity must identify a commit directly")
    return actual


def committed_text(root: Path, commit: str, path: str) -> str:
    safe_path(path)
    mode = git(root, "ls-tree", commit, "--", path).decode().split()
    if not mode or mode[0] not in ("100644", "100755"):
        raise ValueError("Selected source must be a committed regular file: " + path)
    return git(root, "show", commit + ":" + path).decode("utf-8").replace("\r\n", "\n")


def form_inputs(root: Path, commit: str, compiler_version: str, review_date: str) -> tuple[dict, dict, dict, str]:
    commit_id(root, commit)
    projection = json.loads(committed_text(root, commit, "release/PROJECTION.json"))
    selected = [row for row in projection["files"] if owns_source(row)]
    sources, artifacts, groups, descriptions = [], [], {}, {}
    for index, row in enumerate(selected):
        path = row["source"]
        body = committed_text(root, commit, path)
        output = (".repokernel/" + path if path.startswith("skills/")
                  else ".repokernel/resources/autonomous/" + path)
        if destination(output) != row["destination"]:
            raise ValueError("Product projection differs from the generated delivery binding: " + path)
        owner = path.split("/")[1] if path.startswith("skills/") else "maios-project-system"
        sid, aid = f"source-{index}", f"body-{index}"
        groups.setdefault(owner, []).append(aid)
        if path.endswith("/SKILL.md"):
            descriptions[owner] = next((line.split(":", 1)[1].strip() for line in body.splitlines()
                                        if line.startswith("description:")), owner)
        sources.append({"source_id": sid, "authority": "repo", "privacy": "public",
                        "freshness": "current", "instruction_handling": "data_only",
                        "path_or_origin": "https://github.com/GrazianoGuiducci/maios-project-kernel/blob/" + commit + "/" + path,
                        "sha256": text_hash(body), "used_for": ["autonomous-maintained-method-selection"]})
        artifacts.append({"id": aid, "output_path": output, "content": body, "source_refs": [sid]})
    by_id = {item["id"]: item for item in artifacts}
    competences = []
    for owner, ids in groups.items():
        entry = next((aid for aid in ids if by_id[aid]["output_path"] == f".repokernel/skills/{owner}/SKILL.md"), None)
        if entry is None:
            raise ValueError("Selected competence has no entry: " + owner)
        competences.append({"id": owner, "description": descriptions[owner], "entry_artifact": entry,
                            "artifact_ids": ids, "source_refs": [s for aid in ids for s in by_id[aid]["source_refs"]],
                            "risk": "low", "side_effect_class": "local_write_gated"})
    manifest = {"schema": "repokernel.source-manifest.v1", "sources": sources}
    model = {"schema": "repokernel.project-model.v1", "identity": {"name": "MAIOS Project Kernel"},
             "mission": "Form a self-configuring project kernel from maintained native competences.",
             "product_or_result": "A portable kernel whose recipient context forms in the actual project.",
             "source_refs": [s["source_id"] for s in sources],
             "assertions": [{"id": "committed-native-methods", "status": "verified",
                             "text": "Selected method bodies are read from the identified product source commit.",
                             "source_refs": [s["source_id"] for s in sources]}],
             "unknowns": ["Recipient context, host availability and subsequent model use are not supplied by generation."],
             "boundaries": {"effect_authority": "product selection only; no recipient writes"},
             "extensions": {"repokernel.competence_materialization": {
                 "schema": "repokernel.competence-materialization.v1", "competences": competences, "artifacts": artifacts}}}
    seed = {"schema": "repokernel.seed-spec.v1", "version": "repokernel.seed-spec.v1",
            "seed_id": "autonomous-maintained-methods", "source_manifest_hash": identity(manifest),
            "project_model_hash": identity(model), "canonical_namespace": ".repokernel",
            "project": {"name": model["identity"]["name"], "intent": model["mission"], "product": model["product_or_result"]},
            "target": {"mode": "new_repository"}, "readiness_level": "L1", "authority_mode": "propose",
            "review": {"status": "accepted", "accepted_by_role": "product-source-maintainer",
                       "accepted_at": review_date, "review_cycle": "maintained-method-renewal"},
            "compiler_compatibility": {"package_version": compiler_version,
                                       "contract_versions": {"seed_spec": "repokernel.seed-spec.v1"}},
            "file_plan_policy": "stage_only", "validation_plan": ["validate-spec", "plan"],
            "disclosure": {"public": {"name": True, "intent": True, "product": True}}}
    corpus = identity([{ "path": row["source"], "sha256": source["sha256"]}
                       for row, source in zip(selected, sources)])
    return manifest, model, seed, corpus


def renew(root: Path, source_commit: str, compiler: Path, compiler_commit: str, review_date: str) -> dict:
    """Validate and form everything before replacing the maintained selection."""
    from datetime import date
    date.fromisoformat(review_date)
    commit_id(compiler, compiler_commit)
    if git(compiler, "rev-parse", "HEAD").decode().strip() != compiler_commit or git(compiler, "status", "--porcelain").strip():
        raise ValueError("Compiler checkout must be clean at the selected commit")
    sys.path.insert(0, str(compiler / "src"))
    module = importlib.import_module("repokernel")
    if not Path(module.__file__).resolve().is_relative_to((compiler / "src").resolve()):
        raise ValueError("A different compiler is already loaded; run renewal in a fresh process")
    from repokernel.bundle import validate_bundle
    from repokernel.planner import build_generation_plan
    from repokernel.version import package_version
    manifest, model, seed, corpus = form_inputs(root, source_commit, package_version(), review_date)
    validation = validate_bundle(manifest, model, seed)
    if not validation.valid:
        raise ValueError("Invalid selection inputs: " + str(validation.errors))
    plan = build_generation_plan(seed, project_model=model, bundle_provenance=validation.provenance)
    selection = {"schema": "maios.generated-kernel-selection.v1",
                 "source_basis": {"repository": "GrazianoGuiducci/maios-project-kernel", "commit": source_commit,
                                  "corpus_identity": corpus, "identity_scope": "canonical path and normalized body hashes of selected committed methods"},
                 "compiler": {"version": package_version(), "source_revision": compiler_commit},
                 "plan": "release/generated/generation-plan.json", "plan_sha256": identity(plan)}
    import tempfile
    with tempfile.TemporaryDirectory(prefix="maios-selection-") as temp:
        check = Path(temp) / "plan.json"
        check.write_text(json.dumps(plan), encoding="utf-8")
        bodies, receipt = load(check, selection["plan_sha256"])
    targets = {"release/generated/" + name + ".json": value for name, value in (
        ("source-manifest", manifest), ("project-model", model), ("seed-spec", seed), ("generation-plan", plan))}
    targets["release/GENERATED_KERNEL_SELECTION.json"] = selection
    for path in targets:
        target = root / path
        if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
            raise ValueError("Selection output must stay within the product source")
    # The selection is written last; an interrupted renewal cannot silently
    # accept a different plan, and the ordinary builder retains the old package.
    for path, value in targets.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return {"source_commit": source_commit, "compiler_commit": compiler_commit,
            "plan_sha256": selection["plan_sha256"], "competences": len(receipt["competences"]), "bodies": len(bodies)}
