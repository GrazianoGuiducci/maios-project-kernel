"""Consume an identified RepoKernel result through product-owned delivery paths.

The generator's materialization record selects the bodies. This adapter owns
their autonomous product locations, not their formation or runtime behavior.
Only the Python standard library is required by the product builder.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote


RECORD = ".repokernel/knowledge/COMPETENCE_MATERIALIZATION.json"
SCHEMA = "maios.generated-kernel-delivery.v1"
RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$",
    *(f"COM{n}" for n in "123456789¹²³"),
    *(f"LPT{n}" for n in "123456789¹²³"),
}


def identity(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_path(value: str) -> str:
    if not isinstance(value, str) or not value or PurePosixPath(value).as_posix() != value:
        raise ValueError("Delivery requires a canonical relative path")
    if PurePosixPath(value).is_absolute() or any(p in (".", "..") for p in value.split("/")):
        raise ValueError("Delivery path must stay inside its product root")
    for part in value.split("/"):
        if (not part or part.endswith((".", " ")) or part.casefold() == ".git"
                or re.search(r'[<>:"\\|?*\x00-\x1f\x7f]', part)
                or part.split(".", 1)[0].rstrip(" ").upper() in RESERVED_WINDOWS_NAMES):
            raise ValueError("Delivery path is not portable")
    return value


def destination(path: str) -> str:
    safe_path(path)
    # Most-specific source prefix first. The autonomous kernel binding is
    # product-owned; generic resource/skill relationships retain their layout.
    for source, target in (
        (".repokernel/resources/autonomous/kernel/", "payload/.maios/kernel/"),
        (".repokernel/skills/", "payload/skills/"),
        (".repokernel/resources/", "payload/resources/"),
    ):
        if path.startswith(source):
            return safe_path(target + path[len(source):])
    raise ValueError(f"Generated artifact needs an explicit product delivery binding: {path}")


def owns_source(row: dict) -> bool:
    source = row.get("source", "")
    return row.get("destination", "").startswith("payload/") and (
        source.startswith("skills/") or (source.startswith("kernel/") and source.endswith(".md")))


def load(path: Path, expected_hash: str) -> tuple[dict[str, str], dict]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict):
        raise ValueError("RepoKernel plan must be an object")
    if identity(plan) != expected_hash:
        raise ValueError("RepoKernel plan differs from the selected canonical SHA-256")
    if (plan.get("schema") != "repokernel.generation-plan.v1" or plan.get("blocked") is not False
            or plan.get("apply_policy") != "stage_only" or plan.get("blocked_reasons")):
        raise ValueError("A complete unblocked RepoKernel generation plan is required")
    if plan.get("target", {}).get("mode") != "new_repository":
        raise ValueError("Autonomous distribution requires a new-repository generation result")
    items = plan.get("items", [])
    if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
        raise ValueError("Generated plan items must be objects")
    by_path = {i["path"]: i for i in items}
    if len(by_path) != len(items):
        raise ValueError("Duplicate generated plan paths")

    def content(path: str) -> str:
        item = by_path[path]
        value = item.get("content")
        if (item.get("action") not in ("create", "propose_update")
                or item.get("authority_effect") != "none" or not isinstance(value, str)
                or text_hash(value) != item.get("content_hash")):
            raise ValueError(f"Generated content is missing, withheld or inconsistent: {path}")
        return value

    record = json.loads(content(RECORD))
    if record.get("schema") != "repokernel.competence-materialization-record.v1":
        raise ValueError("Unsupported competence materialization record")
    output, artifacts, rows = {}, {}, []
    for item in record["artifacts"]:
        if item["id"] in artifacts:
            raise ValueError("Duplicate generated artifact ids")
        target = destination(item["output_path"])
        folded = target.casefold()
        if any(folded == p.casefold() or folded.startswith(p.casefold()+"/")
               or p.casefold().startswith(folded+"/") for p in output):
            raise ValueError("Generated delivery path collision")
        value = content(item["output_path"])
        if text_hash(value) != item["content_hash"]:
            raise ValueError("Materialization identity differs from generated body")
        output[target] = value
        artifacts[item["id"]] = target
        rows.append({"id": item["id"], "path": target, "sha256": text_hash(value),
                     "source_refs": item["source_refs"]})
    entries, ids = [], set()
    for competence in record["competences"]:
        if competence["id"] in ids:
            raise ValueError("Duplicate generated competence ids")
        ids.add(competence["id"])
        entry = artifacts[competence["entry_artifact"]]
        if not entry.startswith("payload/skills/") or not entry.endswith("/SKILL.md"):
            raise ValueError("Generated competence entry must be a delivered skill")
        if competence["entry_artifact"] not in competence["artifact_ids"]:
            raise ValueError("Competence entry is outside its selected resources")
        entries.append({"id": competence["id"], "entry": entry,
                        "resources": [artifacts[key] for key in competence["artifact_ids"]]})
    if not output or not entries:
        raise ValueError("Generation selected no operating competences")
    provenance = plan.get("bundle_provenance", {})
    receipt = {"schema": SCHEMA, "plan_sha256": expected_hash, "plan_id": plan["plan_id"],
               "compiler_version": plan["compiler_version"],
               "input_hashes": {key: provenance.get(key) for key in
                                ("source_manifest_hash", "project_model_hash", "seed_spec_hash")},
               "artifacts": rows, "competences": entries,
               "identity_scope": "selected generated content; product source identity describes the builder base",
               "authority": "product build selection, not authority inherited from a generation plan",
               "model_use_observed": False}
    for value in receipt["input_hashes"].values():
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("Generated plan lacks input provenance identities")
    return output, receipt


def discovery(receipt: dict) -> str:
    lines = ["\n## Generated competence selection\n",
             "The project system competence remains the operating entry. These methods\n"
             "and their resources belong to its available field; use them when pertinent.\n"]
    for entry in receipt["competences"]:
        path = entry["entry"].removeprefix("payload/")
        label = path.replace("[", "\\[").replace("]", "\\]")
        lines.append(f"- [{label}]({quote(path, safe='/')})")
    return "\n".join(lines) + "\n"


def verification_errors(package: Path, receipt: dict) -> list[str]:
    errors = []
    if receipt.get("schema") != SCHEMA:
        return ["unsupported generated kernel receipt"]
    for row in receipt.get("artifacts", []):
        path = safe_path(row["path"])
        file = package / path
        if (not file.is_file() or file.is_symlink()
                or hashlib.sha256(file.read_bytes()).hexdigest() != row["sha256"]):
            errors.append(f"generated delivery identity differs: {path}")
    for entry in receipt.get("competences", []):
        for rel in [entry["entry"], *entry["resources"]]:
            if not (package / safe_path(rel)).is_file():
                errors.append(f"generated competence is unreachable: {rel}")
    if discovery(receipt) not in (package / "payload/AGENTS.md").read_text(encoding="utf-8"):
        errors.append("generated competences are not reached by the project entry")
    return errors
