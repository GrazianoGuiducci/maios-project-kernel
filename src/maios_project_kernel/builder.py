"""Deterministically project the living source system into a distribution."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Any


PROJECTION_SCHEMA = "maios.release-projection.v2"
MANIFEST_SCHEMA = "maios.project-kernel-distribution.v2"
INVENTORY_SCHEMA = "maios.package-inventory.v2"
REPOKERNEL_RECEIPT_SCHEMA = "maios.repokernel-projection-receipt.v1"
REPOKERNEL_META_SCHEMA = "repokernel.project-meta-faculty.v1"
REPOKERNEL_ENTITY_SCHEMA = "repokernel.project-entity-profile.v1"
PACKAGED_SEMANTIC_OWNER = "skills/maios-project-system/SKILL.md"
FAMILY_CONTRACT_SCHEMA = "maios.project-kernel-family-contract.v1"
AUTONOMOUS_ENTRY_CONTRACT_SCHEMA = "maios.autonomous-entry-contract.v1"
AUTONOMOUS_ENTRY_CONTRACT_VERSION = "1.0.0"
INSTALLED_HOST_CATALOG_SCHEMA = "maios.installed-host-adapters.v1"


class BuildError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def source_identity_bytes(path: Path) -> bytes:
    """Return checkout-independent bytes for the source-tree identity."""
    data = path.read_bytes()
    if b"\x00" in data:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def project_source_file(source: Path, destination: Path) -> None:
    """Project canonical bytes so checkout line endings cannot change artifacts."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source_identity_bytes(source))


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"cannot read valid JSON: {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(formatted_json_bytes(value))


def formatted_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def project_kernel_family_contract(root: Path) -> dict[str, Any]:
    contract = read_json(root / "kernel" / "PROJECT_KERNEL_FAMILY_CONTRACT.json")
    if contract.get("schema") != FAMILY_CONTRACT_SCHEMA:
        raise BuildError("unsupported Project Kernel family contract")
    version = contract.get("family_version")
    if not isinstance(version, str) or not version:
        raise BuildError("Project Kernel family contract has no version")
    return contract


def autonomous_entry_contract(
    root: Path, family_contract: dict[str, Any], product_version: str
) -> dict[str, Any]:
    """Read the product-owned entry policy without rewriting the family lane."""

    contract = read_json(root / "kernel" / "AUTONOMOUS_ENTRY_CONTRACT.json")
    if contract.get("schema") != AUTONOMOUS_ENTRY_CONTRACT_SCHEMA:
        raise BuildError("unsupported autonomous entry contract")
    if contract.get("contract_version") != AUTONOMOUS_ENTRY_CONTRACT_VERSION:
        raise BuildError("unsupported autonomous entry contract version")
    if contract.get("product") != "MAIOS Project Kernel":
        raise BuildError("autonomous entry contract product mismatch")
    if contract.get("product_version") != product_version:
        raise BuildError("autonomous entry contract product version mismatch")
    if contract.get("owner") != "maios-project-kernel":
        raise BuildError("autonomous entry contract owner mismatch")
    if contract.get("effect_authority") != "none":
        raise BuildError("autonomous entry contract grants effect authority")
    if contract.get("contains_form_state") is not False:
        raise BuildError("autonomous entry contract must not contain Form state")

    family_relation = contract.get("family_relation", {})
    family_lane = family_contract.get("lanes", {}).get("autonomous", {})
    if (
        family_relation.get("lane") != "autonomous"
        or family_relation.get("family_version")
        != family_contract.get("family_version")
        or family_relation.get("configuration_state")
        != family_lane.get("configuration_state")
        or family_relation.get("startup_context_requirement")
        != family_lane.get("startup_interview")
    ):
        raise BuildError("autonomous entry contract lost its family relation")

    policy = contract.get("entry_policy", {})
    for field in (
        "normal_movement",
        "expanded_entry_condition",
        "operator_correction_rule",
        "future_form_rule",
    ):
        if not isinstance(policy.get(field), str) or not policy[field].strip():
            raise BuildError(f"autonomous entry contract has no {field}")
    if policy.get("startup_interview") != "discretionary":
        raise BuildError("autonomous product entry must remain discretionary")
    return contract


def safe_relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or "\\" in value
        or ":" in value
        or "\x00" in value
    ):
        raise BuildError(f"unsafe projection path: {value}")
    return path


def native(root: Path, relative: str) -> Path:
    return root.joinpath(*safe_relative(relative).parts)


def source_tree_files(root: Path) -> list[Path]:
    excluded_roots = {".git", "package", ".pytest_cache", "__pycache__"}
    result: list[Path] = []
    for path in sorted(
        root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()
    ):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        top = relative.parts[0]
        if (
            any(part in excluded_roots for part in relative.parts)
            or top.startswith(".package.")
        ):
            continue
        if path.is_symlink():
            raise BuildError(f"source tree contains a symlinked file: {relative}")
        result.append(path)
    return result


def source_tree_digest(root: Path) -> str:
    rows = []
    for path in source_tree_files(root):
        data = source_identity_bytes(path)
        rows.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": digest_bytes(data),
                "bytes": len(data),
            }
        )
    return digest_bytes(canonical_bytes(rows))


def transformed_adapters(root: Path) -> dict[str, Any]:
    value = read_json(root / "adapters" / "ADAPTERS.json")
    result = json.loads(json.dumps(value))
    owner = result.get("semantic_owner")
    if not isinstance(owner, str):
        raise BuildError("adapter semantic_owner is missing")
    result["source_owner"] = owner
    result["semantic_owner"] = f"payload/{owner}"
    host_adaptation_owner = result.get("host_adaptation_owner")
    if not isinstance(host_adaptation_owner, str):
        raise BuildError("adapter host_adaptation_owner is missing")
    result["host_adaptation_owner"] = f"payload/{host_adaptation_owner}"
    portable_owners = result.get("portable_competence_owners", [])
    if not isinstance(portable_owners, list) or not all(
        isinstance(item, str) for item in portable_owners
    ):
        raise BuildError("portable_competence_owners must be a list of paths")
    result["portable_competence_owners"] = [
        f"payload/{item}" for item in portable_owners
    ]
    for adapter in result.get("adapters", []):
        for projection in adapter.get("projections", []):
            source = projection.get("source")
            if not isinstance(source, str):
                raise BuildError("adapter projection source is missing")
            projection["source"] = f"payload/{source}"
    return result


def installed_host_catalog(root: Path) -> dict[str, Any]:
    """Project the canonical adapter catalogue into the installed runtime."""

    source = read_json(root / "adapters" / "ADAPTERS.json")
    adapters = source.get("adapters", [])
    if source.get("schema") != "maios.host-adapters.v2" or not isinstance(
        adapters, list
    ):
        raise BuildError("unsupported canonical host adapter catalogue")
    projected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for adapter in adapters:
        if not isinstance(adapter, dict):
            raise BuildError("host adapter catalogue contains a non-object entry")
        adapter_id = adapter.get("id")
        if not isinstance(adapter_id, str) or not adapter_id or adapter_id in seen:
            raise BuildError("host adapter ids must be present and unique")
        seen.add(adapter_id)
        projected.append(
            {
                "id": adapter_id,
                "display_name": adapter.get("display_name"),
                "native_skill_root": adapter.get("native_skill_root"),
            }
        )
    return {
        "schema": INSTALLED_HOST_CATALOG_SCHEMA,
        "source": "adapters/ADAPTERS.json",
        "adapters": projected,
    }


def project_meta_crosswalk_errors(
    crosswalk: Any,
    meta_faculty: dict[str, Any],
    faculty_field: dict[str, Any],
    payload_root: Path,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(crosswalk, dict) or crosswalk.get("schema") != (
        "maios.project-meta-faculty-crosswalk.v1"
    ):
        return ["unsupported Project Meta-Faculty crosswalk"]
    if (
        crosswalk.get("source_schema") != meta_faculty.get("schema")
        or crosswalk.get("target_schema") != faculty_field.get("schema")
        or crosswalk.get("semantic_owner") != PACKAGED_SEMANTIC_OWNER
        or crosswalk.get("open_world") is not True
    ):
        errors.append("Project Meta-Faculty crosswalk owner or schema mismatch")
    source_ids = [
        item.get("id") for item in meta_faculty.get("function_families", [])
    ]
    target_by_id = {
        item.get("id"): item for item in faculty_field.get("families", [])
    }
    mappings = crosswalk.get("mappings", [])
    mapping_source_ids = [
        item.get("source_id") for item in mappings if isinstance(item, dict)
    ]
    if (
        len(mapping_source_ids) != len(mappings)
        or None in mapping_source_ids
        or len(mapping_source_ids) != len(set(mapping_source_ids))
        or sorted(mapping_source_ids) != sorted(source_ids)
    ):
        errors.append("Project Meta-Faculty crosswalk source coverage is incomplete")
    resolved_target_ids: set[str] = set()
    for mapping in mappings:
        if not isinstance(mapping, dict):
            continue
        target_ids = mapping.get("target_faculty_ids")
        if not isinstance(target_ids, list) or not target_ids:
            errors.append(f"crosswalk mapping has no targets: {mapping.get('source_id')}")
            continue
        for target_id in target_ids:
            target = target_by_id.get(target_id)
            if target is None:
                errors.append(f"crosswalk target does not exist: {target_id}")
                continue
            resolved_target_ids.add(target_id)
            entry = target.get("entry")
            if not isinstance(entry, str) or not entry:
                errors.append(f"crosswalk target has no entry: {target_id}")
                continue
            path_text, separator, anchor = entry.partition("#")
            try:
                entry_path = native(payload_root, path_text)
            except BuildError:
                errors.append(f"crosswalk target entry is unsafe: {target_id}")
                continue
            if not entry_path.is_file():
                errors.append(f"crosswalk target entry is missing: {target_id}")
                continue
            if separator:
                headings = []
                for line in entry_path.read_text(encoding="utf-8").splitlines():
                    if not line.startswith("#"):
                        continue
                    heading = line.lstrip("#").strip().lower()
                    heading = re.sub(r"[^\w\s-]", "", heading)
                    headings.append(re.sub(r"[\s-]+", "-", heading).strip("-"))
                if anchor not in headings:
                    errors.append(f"crosswalk target anchor is missing: {target_id}")
    if resolved_target_ids != set(target_by_id):
        errors.append("Project Meta-Faculty crosswalk does not resolve every MAIOS faculty")
    return errors


def repokernel_projection_inputs(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Read and bind the reviewed RepoKernel projection to its source bundle."""

    base = root / "release" / "repokernel"
    source_manifest = read_json(base / "source-manifest.json")
    project_model = read_json(base / "project-model.json")
    seed_spec = read_json(base / "seed-spec.json")
    meta_faculty = read_json(base / "generated" / "PROJECT_META_FACULTY.json")
    receipt = read_json(base / "PROJECTION_RECEIPT.json")

    if receipt.get("schema") != REPOKERNEL_RECEIPT_SCHEMA:
        raise BuildError("unsupported RepoKernel projection receipt schema")
    if meta_faculty.get("schema") != REPOKERNEL_META_SCHEMA:
        raise BuildError("unsupported generated Project Meta-Faculty schema")
    project_entity = seed_spec.get("extensions", {}).get("repokernel.project_entity")
    if (
        not isinstance(project_entity, dict)
        or project_entity.get("schema") != REPOKERNEL_ENTITY_SCHEMA
    ):
        raise BuildError("seed spec does not contain a valid Project Entity Profile")

    bundle = receipt.get("source_bundle", {})
    expected_bundle_hashes = {
        "source_manifest_canonical_sha256": digest_bytes(
            canonical_bytes(source_manifest)
        ),
        "project_model_canonical_sha256": digest_bytes(canonical_bytes(project_model)),
        "seed_spec_canonical_sha256": digest_bytes(canonical_bytes(seed_spec)),
    }
    for field, actual in expected_bundle_hashes.items():
        if bundle.get(field) != actual:
            raise BuildError(f"RepoKernel projection receipt has stale {field}")
    if seed_spec.get("source_manifest_hash") != expected_bundle_hashes[
        "source_manifest_canonical_sha256"
    ]:
        raise BuildError("RepoKernel seed has a stale source manifest hash")
    if seed_spec.get("project_model_hash") != expected_bundle_hashes[
        "project_model_canonical_sha256"
    ]:
        raise BuildError("RepoKernel seed has a stale project model hash")
    if seed_spec.get("compiler_compatibility", {}).get(
        "package_version"
    ) != receipt.get("repokernel", {}).get("compiler_version"):
        raise BuildError("RepoKernel compiler version drifted between seed and receipt")
    if receipt.get("repokernel", {}).get("source_revision") != receipt.get(
        "repokernel", {}
    ).get("baseline_revision"):
        raise BuildError("RepoKernel source revision is not bound to its reviewed baseline")
    source_owner_manifest = read_json(root / "sources" / "SOURCE_MANIFEST.json")
    if source_owner_manifest.get("repokernel_plan_id") != receipt.get(
        "repokernel", {}
    ).get("plan_id"):
        raise BuildError("MAIOS source manifest is not bound to the RepoKernel plan")
    for source in source_manifest.get("sources", []):
        if not isinstance(source, dict) or "sha256" not in source:
            continue
        source_path = source.get("path_or_origin")
        source_file = native(root, source_path) if isinstance(source_path, str) else None
        if (
            source_file is None
            or not source_file.is_file()
            or digest_file(source_file) != source.get("sha256")
        ):
            raise BuildError(f"RepoKernel input digest drifted: {source_path}")

    generated = receipt.get("generated_source", {})
    if generated.get("project_meta_faculty_sha256") != digest_file(
        base / "generated" / "PROJECT_META_FACULTY.json"
    ):
        raise BuildError("RepoKernel Project Meta-Faculty hash is stale")
    if generated.get("project_entity_profile_sha256") != digest_bytes(
        formatted_json_bytes(project_entity)
    ):
        raise BuildError("RepoKernel Project Entity Profile hash is stale")

    composition = receipt.get("composition", {})
    invocation = meta_faculty.get("invocation", {})
    role = project_entity.get("role", {})
    if invocation.get("entry") != composition.get("source_entry"):
        raise BuildError("RepoKernel semantic source entry drifted from its receipt")
    if composition.get("semantic_owner") != PACKAGED_SEMANTIC_OWNER:
        raise BuildError("RepoKernel projection does not bind the packaged semantic owner")
    if (
        role.get("startup_interview") != "required"
        or composition.get("startup_interview") != "required"
        or composition.get("configuration_state")
        != "deferred_to_first_operator_relation"
    ):
        raise BuildError("direct package must retain deferred situated configuration")
    if meta_faculty.get("open_world") is not True:
        raise BuildError("generated Project Meta-Faculty must remain open_world")
    if meta_faculty.get("effect_authority") != "none":
        raise BuildError("generated Project Meta-Faculty must not grant effect authority")
    return meta_faculty, project_entity, receipt


def composed_project_meta_faculty(
    meta_faculty: dict[str, Any], receipt: dict[str, Any]
) -> dict[str, Any]:
    """Rebind the generated neutral map to the one living MAIOS semantic owner."""

    result = json.loads(json.dumps(meta_faculty))
    result["invocation"]["entry"] = receipt["composition"]["semantic_owner"]
    return result


def composed_project_entry_profile(
    project_entity: dict[str, Any],
    receipt: dict[str, Any],
    family_contract: dict[str, Any],
    entry_contract: dict[str, Any],
) -> dict[str, Any]:
    """Translate RepoKernel's generated entity into the open MAIOS entry relation."""

    capabilities = project_entity.get("capability_requirements", [])
    source_catalogs: list[dict[str, Any]] = []
    for source_catalog in project_entity.get("source_catalogs", []):
        if not isinstance(source_catalog, dict):
            raise BuildError("Project Entity source catalog entry must be an object")
        translated = json.loads(json.dumps(source_catalog))
        registry_path = translated.pop("registry_path", None)
        if registry_path == "kernel/FACULTY_FIELD.json":
            translated["source_registry_path"] = registry_path
            translated["installed_registry_path"] = (
                ".maios/kernel/FACULTY_FIELD.json"
            )
        elif registry_path is not None:
            raise BuildError(f"untranslated Project Entity registry path: {registry_path}")
        source_catalogs.append(translated)
    return {
        "schema": family_contract["entry_profile"]["schema"],
        "product": "MAIOS Project Kernel",
        "version": family_contract["family_version"],
        "source_relation": {
            "kind": "repokernel_generated_function_translated_to_owner_native_form",
            "plan_id": receipt["repokernel"]["plan_id"],
            "source_schema": project_entity["schema"],
            "source_profile_sha256": receipt["generated_source"][
                "project_entity_profile_sha256"
            ],
        },
        "role": {
            **project_entity["role"],
            "startup_interview": entry_contract["entry_policy"][
                "startup_interview"
            ],
        },
        "configuration_state": "deferred_to_first_operator_relation",
        "competence_field": {
            "selection_model": family_contract["entry_profile"]["selection_model"],
            "permanent_entry": PACKAGED_SEMANTIC_OWNER,
            "reachable_competences": [
                item["id"] for item in capabilities if isinstance(item, dict) and "id" in item
            ],
            "composition_rule": (
                "Let every pertinent owner-native competence participate; no mandatory "
                "primary or fixed support count is imposed."
            ),
        },
        "environment_readiness": {
            "owner": "maios-project-integration and maios-project-host-adaptation",
            "rule": (
                "Observe what the current coder, model access and target already provide. "
                "Begin directly when the field is sufficient; explain and establish only "
                "a material missing condition for the selected project."
            ),
            "requirements": [
                {
                    "id": "capable-ai-coder-or-harness",
                    "required": True,
                    "relation": "A capable coder or agentic harness can read project instructions and act on files.",
                },
                {
                    "id": "model-access",
                    "required": True,
                    "relation": "The coder has usable model access through a provider, API or local model.",
                },
                {
                    "id": "python-runtime",
                    "required": True,
                    "relation": "Python 3.10 or later can run installation and deterministic helpers.",
                },
                {
                    "id": "version-control-and-repository",
                    "required": False,
                    "recommended": True,
                    "relation": "Git and a repository service such as GitHub preserve collaboration and recovery when useful.",
                },
                {
                    "id": "remote-infrastructure",
                    "required": False,
                    "recommended": False,
                    "relation": "A VPS or project-specific stack is prepared only when the selected work needs it.",
                },
            ],
            "credential_boundary": "Explain and request access when needed; never embed credentials in the package.",
        },
        "capability_requirements": capabilities,
        "source_catalogs": source_catalogs,
        "requested_bundle_ids": project_entity.get("requested_bundle_ids", []),
        "completion": project_entity.get("completion", {}),
    }


def distribution_files(package_dir: Path, include_inventory: bool = True) -> list[Path]:
    result = []
    for path in sorted(
        package_dir.rglob("*"),
        key=lambda item: item.relative_to(package_dir).as_posix(),
    ):
        if path.is_file():
            if not include_inventory and path.name == "PACKAGE_INVENTORY.json":
                continue
            result.append(path)
    return result


def render_distribution(root: Path, package_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    if package_dir.expanduser().is_symlink():
        raise BuildError("distribution target must not be a symlink")
    package_dir = package_dir.resolve()
    if package_dir.exists() and any(package_dir.iterdir()):
        raise BuildError(f"render target must be absent or empty: {package_dir}")
    package_dir.mkdir(parents=True, exist_ok=True)

    projection_path = root / "release" / "PROJECTION.json"
    projection = read_json(projection_path)
    family_contract = project_kernel_family_contract(root)
    if projection.get("schema") != PROJECTION_SCHEMA:
        raise BuildError("unsupported release projection schema")
    project_version = projection.get("version")
    if not isinstance(project_version, str) or not project_version:
        raise BuildError("release projection has no product version")
    if read_json(root / "sources" / "SOURCE_MANIFEST.json").get(
        "version"
    ) != project_version:
        raise BuildError("product version drifted between projection and source manifest")
    entry_contract = autonomous_entry_contract(
        root, family_contract, project_version
    )

    destinations: set[str] = set()
    for item in projection.get("files", []):
        source_rel = item.get("source")
        destination_rel = item.get("destination")
        if not isinstance(source_rel, str) or not isinstance(destination_rel, str):
            raise BuildError("projection entries require source and destination")
        safe_relative(source_rel)
        safe_relative(destination_rel)
        if destination_rel in destinations:
            raise BuildError(f"duplicate projection destination: {destination_rel}")
        destinations.add(destination_rel)
        source = native(root, source_rel)
        if not source.is_file() or source.is_symlink():
            raise BuildError(f"projection source is missing or unsafe: {source_rel}")
        destination = native(package_dir, destination_rel)
        project_source_file(source, destination)

    meta_faculty, project_entity, repokernel_receipt = repokernel_projection_inputs(
        root
    )
    write_json(
        package_dir / "payload" / ".maios" / "kernel" / "PROJECT_META_FACULTY.json",
        composed_project_meta_faculty(meta_faculty, repokernel_receipt),
    )
    write_json(
        package_dir / "payload" / ".maios" / "kernel" / "PROJECT_ENTITY_PROFILE.json",
        composed_project_entry_profile(
            project_entity, repokernel_receipt, family_contract, entry_contract
        ),
    )

    write_json(package_dir / "adapters" / "ADAPTERS.json", transformed_adapters(root))
    write_json(
        package_dir / "payload" / ".maios" / "config" / "HOST_ADAPTERS.json",
        installed_host_catalog(root),
    )

    tree_sha256 = source_tree_digest(root)
    payload_count = len(
        [path for path in (package_dir / "payload").rglob("*") if path.is_file()]
    )
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "product": "MAIOS Project Kernel",
        "version": project_version,
        "project_kernel_family_version": family_contract["family_version"],
        "entrypoint": "install.py",
        "runtime_requirements": {
            "python": ">=3.10",
            "third_party_python_packages": [],
        },
        "distribution_entry": {
            "instructions": "AGENTS.md",
            "neutral_competence": "skills/maios-project-integration/SKILL.md",
            "codex_projection": ".agents/skills/maios-project-integration/SKILL.md",
        },
        "project_entrypoint": "payload/START_HERE.md",
        "target_modes": ["new_repository", "existing_repository"],
        "host_adapters": [
            item["id"] for item in installed_host_catalog(root)["adapters"]
        ],
        "source_identity": {
            "owner": "maios-project-kernel repository",
            "tree_sha256": tree_sha256,
            "projection_sha256": digest_file(projection_path),
            "source_manifest_sha256": digest_file(root / "sources" / "SOURCE_MANIFEST.json"),
            "autonomous_entry_contract_sha256": digest_file(
                root / "kernel" / "AUTONOMOUS_ENTRY_CONTRACT.json"
            ),
            "repokernel_projection_receipt_sha256": digest_file(
                root / "release" / "repokernel" / "PROJECTION_RECEIPT.json"
            ),
            "revision_claim": "content_addressed_source_tree",
        },
        "payload_file_count": payload_count,
        "distribution_file_count": len(distribution_files(package_dir)) + 2,
        "self_installation": {
            "preview_required": True,
            "exact_plan_apply": True,
            "conflict_refusal": True,
            "idempotency": True,
            "recovery": "remove_only_unchanged_installer_owned_bytes",
            "global_writes": [],
        },
        "competence_cultivation": {
            "state_owner": "payload/.maios/competences/INDEX.json",
            "protocol": "payload/.maios/kernel/COMPETENCE_CULTIVATION_PROTOCOL.md",
            "represented_owners": [
                "payload/skills/maios-start-new-project/SKILL.md",
                "payload/skills/maios-start-existing-project/SKILL.md",
                "payload/skills/maios-project-context/SKILL.md",
                "payload/skills/maios-project-competence-formation/SKILL.md",
                "payload/skills/maios-project-host-adaptation/SKILL.md",
            ],
            "producer_self_approval": False,
            "behavioral_proof_separate": True,
        },
        "repokernel_projection": {
            "plan_id": repokernel_receipt["repokernel"]["plan_id"],
            "receipt": "payload/.maios/REPOKERNEL_PROJECTION.json",
            "project_meta_faculty": "payload/.maios/kernel/PROJECT_META_FACULTY.json",
            "project_entity_profile": "payload/.maios/kernel/PROJECT_ENTITY_PROFILE.json",
            "autonomous_entry_contract": "payload/.maios/kernel/AUTONOMOUS_ENTRY_CONTRACT.json",
            "semantic_owner": f"payload/{PACKAGED_SEMANTIC_OWNER}",
            "startup_interview": entry_contract["entry_policy"][
                "startup_interview"
            ],
            "configuration_state": "deferred_to_first_operator_relation",
        },
        "contains_repokernel_source": False,
        "contains_form_state": False,
        "contains_private_topology": False,
        "contains_lifecycle_hooks": False,
        "global_writes": [],
    }
    write_json(package_dir / "MANIFEST.json", manifest)

    inventory_rows = [
        {
            "path": path.relative_to(package_dir).as_posix(),
            "sha256": digest_file(path),
            "bytes": path.stat().st_size,
        }
        for path in distribution_files(package_dir, include_inventory=False)
    ]
    inventory = {
        "schema": INVENTORY_SCHEMA,
        "algorithm": "sha256",
        "files": inventory_rows,
    }
    write_json(package_dir / "PACKAGE_INVENTORY.json", inventory)
    return {
        "version": project_version,
        "source_tree_sha256": tree_sha256,
        "package_file_count": len(distribution_files(package_dir)),
        "payload_file_count": payload_count,
    }


def inventory_errors(package_dir: Path) -> list[str]:
    errors: list[str] = []
    inventory = read_json(package_dir / "PACKAGE_INVENTORY.json")
    if inventory.get("schema") != INVENTORY_SCHEMA:
        return ["unsupported package inventory schema"]
    actual = {
        path.relative_to(package_dir).as_posix(): {
            "sha256": digest_file(path),
            "bytes": path.stat().st_size,
        }
        for path in distribution_files(package_dir, include_inventory=False)
    }
    declared_rows = [
        item for item in inventory.get("files", []) if isinstance(item, dict)
    ]
    declared = {
        item.get("path"): {"sha256": item.get("sha256"), "bytes": item.get("bytes")}
        for item in declared_rows
    }
    if len(declared) != len(declared_rows):
        errors.append("package inventory contains duplicate paths")
    if declared != actual:
        errors.append("package inventory does not exactly match distribution bytes")
    return errors


def verify_distribution(root: Path, package_dir: Path) -> dict[str, Any]:
    root = root.resolve()
    package_dir = package_dir.resolve()
    errors: list[str] = []
    required = {
        "AGENTS.md",
        "install.py",
        "MANIFEST.json",
        "PACKAGE_INVENTORY.json",
        "skills/maios-project-integration/SKILL.md",
        ".agents/skills/maios-project-integration/SKILL.md",
        "payload/START_HERE.md",
        "payload/maios.py",
        "payload/.maios/installer/installer.py",
        "payload/.maios/config/HOST_ADAPTERS.json",
        "payload/.maios/runtime/kernel.py",
        "payload/.maios/runtime/host.py",
        "payload/.maios/runtime/operating.py",
        "payload/.maios/kernel/SYSTEM_KERNEL.md",
        "payload/.maios/kernel/COMPETENCE_CULTIVATION_PROTOCOL.md",
        "payload/.maios/kernel/PROJECT_META_FACULTY.json",
        "payload/.maios/kernel/PROJECT_META_FACULTY_CROSSWALK.json",
        "payload/.maios/kernel/PROJECT_ENTITY_PROFILE.json",
        "payload/.maios/kernel/AUTONOMOUS_ENTRY_CONTRACT.json",
        "payload/.maios/kernel/PROJECT_KERNEL_FAMILY_CONTRACT.json",
        "payload/.maios/REPOKERNEL_PROJECTION.json",
        "payload/.maios/competences/INDEX.json",
        "payload/.maios/schemas/RESULTANT_READBACK.schema.json",
        "payload/.maios/state/OPERATING_STATE.json",
        "payload/skills/maios-project-system/SKILL.md",
        "payload/skills/maios-start-new-project/SKILL.md",
        "payload/skills/maios-start-existing-project/SKILL.md",
        "payload/skills/maios-project-context/SKILL.md",
        "payload/skills/maios-project-competence-formation/SKILL.md",
        "payload/skills/maios-project-host-adaptation/SKILL.md",
    }
    actual_names = {
        path.relative_to(package_dir).as_posix() for path in distribution_files(package_dir)
    }
    missing = sorted(required - actual_names)
    if missing:
        errors.append("missing required distribution files: " + ", ".join(missing))
    manifest: dict[str, Any] = {}
    family_contract = project_kernel_family_contract(root)
    projection = read_json(root / "release" / "PROJECTION.json")
    project_version = projection.get("version")
    entry_contract = autonomous_entry_contract(
        root, family_contract, project_version
    )
    try:
        manifest = read_json(package_dir / "MANIFEST.json")
        if manifest.get("schema") != MANIFEST_SCHEMA:
            errors.append("unsupported distribution manifest schema")
        if manifest.get("version") != project_version:
            errors.append(f"distribution version is not {project_version}")
        if manifest.get("project_kernel_family_version") != family_contract.get(
            "family_version"
        ):
            errors.append("distribution family version is not bound to its contract")
        if manifest.get("source_identity", {}).get("tree_sha256") != source_tree_digest(root):
            errors.append("manifest source tree identity is stale")
        if manifest.get("distribution_file_count") != len(actual_names):
            errors.append("manifest distribution_file_count is incorrect")
        actual_payload_count = len(
            [path for path in (package_dir / "payload").rglob("*") if path.is_file()]
        )
        if manifest.get("payload_file_count") != actual_payload_count:
            errors.append("manifest payload_file_count is incorrect")
        for flag in (
            "contains_repokernel_source",
            "contains_form_state",
            "contains_private_topology",
            "contains_lifecycle_hooks",
        ):
            if manifest.get(flag) is not False:
                errors.append(f"manifest must set {flag} false")
    except BuildError as exc:
        errors.append(str(exc))

    try:
        source_meta, source_entity, source_receipt = repokernel_projection_inputs(root)
        packaged_receipt = read_json(
            package_dir / "payload" / ".maios" / "REPOKERNEL_PROJECTION.json"
        )
        packaged_meta = read_json(
            package_dir / "payload" / ".maios" / "kernel" / "PROJECT_META_FACULTY.json"
        )
        packaged_entity = read_json(
            package_dir / "payload" / ".maios" / "kernel" / "PROJECT_ENTITY_PROFILE.json"
        )
        packaged_entry_contract = read_json(
            package_dir
            / "payload"
            / ".maios"
            / "kernel"
            / "AUTONOMOUS_ENTRY_CONTRACT.json"
        )
        packaged_crosswalk = read_json(
            package_dir
            / "payload"
            / ".maios"
            / "kernel"
            / "PROJECT_META_FACULTY_CROSSWALK.json"
        )
        packaged_faculty_field = read_json(
            package_dir / "payload" / ".maios" / "kernel" / "FACULTY_FIELD.json"
        )
        expected_meta = composed_project_meta_faculty(source_meta, source_receipt)
        expected_entity = composed_project_entry_profile(
            source_entity, source_receipt, family_contract, entry_contract
        )
        if packaged_receipt != source_receipt:
            errors.append("packaged RepoKernel projection receipt drifted from source")
        if packaged_meta != expected_meta:
            errors.append("packaged Project Meta-Faculty is not the composed source projection")
        if packaged_entity != expected_entity:
            errors.append("packaged Project Entity Profile is not the owner-native translation")
        if packaged_entry_contract != entry_contract:
            errors.append("packaged autonomous entry contract drifted from source")
        errors.extend(
            project_meta_crosswalk_errors(
                packaged_crosswalk,
                packaged_meta,
                packaged_faculty_field,
                package_dir / "payload",
            )
        )
        family_ids = [
            item.get("id") for item in packaged_meta.get("function_families", [])
        ]
        expected_family_ids = family_contract["meta_faculty"][
            "required_function_families"
        ]
        if (
            packaged_meta.get("open_world")
            is not family_contract["meta_faculty"]["open_world"]
            or packaged_meta.get("effect_authority")
            != family_contract["meta_faculty"]["effect_authority"]
            or sorted(family_ids) != sorted(expected_family_ids)
            or None in family_ids
            or len(family_ids) != len(set(family_ids))
        ):
            errors.append("packaged Project Meta-Faculty lost neutral functional coverage")
        if packaged_meta.get("invocation", {}).get("entry") != PACKAGED_SEMANTIC_OWNER:
            errors.append("packaged Project Meta-Faculty does not use the semantic owner")
        if (
            packaged_entity.get("role", {}).get("startup_interview")
            != entry_contract["entry_policy"]["startup_interview"]
        ):
            errors.append("packaged Project Entity Profile lost its current startup relation")
        if (
            packaged_entity.get("schema")
            != family_contract["entry_profile"]["schema"]
            or packaged_entity.get("competence_field", {}).get("selection_model")
            != family_contract["entry_profile"]["selection_model"]
            or any(
                field in packaged_entity
                for field in family_contract["entry_profile"]["forbidden_fields"]
            )
        ):
            errors.append("packaged Project Entity Profile lost its open owner-native relation")
        for catalog in packaged_entity.get("source_catalogs", []):
            installed_path = catalog.get("installed_registry_path")
            source_path = catalog.get("source_registry_path")
            if not isinstance(installed_path, str) or not native(
                package_dir / "payload", installed_path
            ).is_file():
                errors.append("Project Entity Profile contains an unresolved installed catalog")
            if not isinstance(source_path, str) or not native(root, source_path).is_file():
                errors.append("Project Entity Profile contains an unresolved source catalog")
        expected_projection = {
            "plan_id": source_receipt["repokernel"]["plan_id"],
            "receipt": "payload/.maios/REPOKERNEL_PROJECTION.json",
            "project_meta_faculty": "payload/.maios/kernel/PROJECT_META_FACULTY.json",
            "project_entity_profile": "payload/.maios/kernel/PROJECT_ENTITY_PROFILE.json",
            "autonomous_entry_contract": "payload/.maios/kernel/AUTONOMOUS_ENTRY_CONTRACT.json",
            "semantic_owner": f"payload/{PACKAGED_SEMANTIC_OWNER}",
            "startup_interview": entry_contract["entry_policy"][
                "startup_interview"
            ],
            "configuration_state": "deferred_to_first_operator_relation",
        }
        if manifest.get("repokernel_projection") != expected_projection:
            errors.append("distribution manifest does not bind the RepoKernel projection")
    except (BuildError, KeyError, TypeError) as exc:
        errors.append(f"invalid RepoKernel package composition: {exc}")
    try:
        errors.extend(inventory_errors(package_dir))
    except BuildError as exc:
        errors.append(str(exc))

    try:
        adapters = read_json(package_dir / "adapters" / "ADAPTERS.json")
        adapter_ids = [item.get("id") for item in adapters.get("adapters", [])]
        installed_catalog = read_json(
            package_dir / "payload" / ".maios" / "config" / "HOST_ADAPTERS.json"
        )
        installed_ids = [
            item.get("id") for item in installed_catalog.get("adapters", [])
        ]
        if adapter_ids != [
            "generic",
            "codex",
            "claude",
            "opencode",
            "hermes",
            "openclaw",
            "pi",
            "dsh",
        ]:
            errors.append("host adapter ids or order are incorrect")
        if installed_catalog != installed_host_catalog(root):
            errors.append("installed host adapter catalogue drifted from its source")
        if installed_ids != adapter_ids or manifest.get("host_adapters") != adapter_ids:
            errors.append("host adapter projections do not expose one supported id set")
        if adapters.get("semantic_owner") != "payload/skills/maios-project-system/SKILL.md":
            errors.append("host adapters do not point to the one packaged semantic owner")
        semantic_owner = adapters.get("semantic_owner")
        host_adaptation_owner = adapters.get("host_adaptation_owner")
        portable_owners = adapters.get("portable_competence_owners", [])
        if len(portable_owners) != 5 or not all(
            isinstance(item, str) and item.startswith("payload/skills/")
            for item in portable_owners
        ):
            errors.append("portable competence owners are missing or malformed")
        if host_adaptation_owner not in portable_owners:
            errors.append("host-adaptation owner is not a portable competence owner")
        for adapter in adapters.get("adapters", []):
            adapter_id = adapter.get("id")
            if adapter_id == "generic":
                continue
            semantic_projections = [
                item
                for item in adapter.get("projections", [])
                if item.get("source") == semantic_owner
                and isinstance(item.get("destination"), str)
                and item["destination"].endswith("/maios-project-system/SKILL.md")
            ]
            if len(semantic_projections) != 1:
                errors.append(
                    f"host adapter {adapter_id!r} must project the one semantic owner exactly once"
                )
            adaptation_projections = [
                item
                for item in adapter.get("projections", [])
                if item.get("source") == host_adaptation_owner
                and isinstance(item.get("destination"), str)
                and item["destination"].endswith(
                    "/maios-project-host-adaptation/SKILL.md"
                )
            ]
            if len(adaptation_projections) != 1:
                errors.append(
                    f"host adapter {adapter_id!r} must project the host-adaptation owner exactly once"
                )
            if adapter_id == "codex":
                for owner in portable_owners:
                    owner_name = PurePosixPath(owner).parent.name
                    projections = [
                        item
                        for item in adapter.get("projections", [])
                        if item.get("source") == owner
                        and item.get("destination")
                        == f".agents/skills/{owner_name}/SKILL.md"
                    ]
                    if len(projections) != 1:
                        errors.append(
                            f"Codex adapter must project {owner_name!r} exactly once"
                        )
    except BuildError as exc:
        errors.append(str(exc))
    try:
        faculty_field = read_json(
            package_dir / "payload" / ".maios" / "kernel" / "FACULTY_FIELD.json"
        )
        families = faculty_field.get("families", [])
        permanent = [
            item for item in families if item.get("presence") == "permanent_silent"
        ]
        if faculty_field.get("open_world") is not True:
            errors.append("packaged faculty field must remain open_world")
        if len(families) < 12 or len(permanent) != 2:
            errors.append("packaged faculty field lost functional coverage or silent invariants")
    except BuildError as exc:
        errors.append(str(exc))
    try:
        configuration = read_json(
            package_dir / "payload" / "setup" / "CONFIGURATION_STATE.json"
        )
        if configuration.get("effect_authority") != "none":
            errors.append("initial configuration must not grant effect authority")
        competence_index = read_json(
            package_dir / "payload" / ".maios" / "competences" / "INDEX.json"
        )
        represented = competence_index.get("represented")
        expected_represented = {
            "maios-start-new-project",
            "maios-start-existing-project",
            "maios-project-context",
        }
        if not isinstance(represented, dict) or set(represented) != expected_represented:
            errors.append("initial competence index does not represent the startup/context owners")
        else:
            for competence_id, competence in represented.items():
                knowledge_entry = competence.get("knowledge_entry")
                activation = competence.get("activation_relations")
                if not isinstance(knowledge_entry, str) or not isinstance(activation, list) or not activation:
                    errors.append(
                        f"represented competence {competence_id!r} lacks an operable entry or activation relations"
                    )
                    continue
                knowledge_path = package_dir / "payload" / PurePosixPath(knowledge_entry)
                if not knowledge_path.is_file() or knowledge_path.is_symlink():
                    errors.append(
                        f"represented competence {competence_id!r} has no safe packaged knowledge entry"
                    )
        if competence_index.get("active") != {} or competence_index.get("history") != []:
            errors.append("initial competence index must not contain inherited project state")
        operating_state = read_json(
            package_dir / "payload" / ".maios" / "state" / "OPERATING_STATE.json"
        )
        if operating_state.get("schema") != "maios.operating-state.v2":
            errors.append("initial operating state schema is incorrect")
        if (
            operating_state.get("revision") != 0
            or operating_state.get("history") != []
            or operating_state.get("learning_relations") != []
        ):
            errors.append("initial operating state must not contain inherited project state")
    except BuildError as exc:
        errors.append(str(exc))

    integration_source = package_dir / "skills" / "maios-project-integration" / "SKILL.md"
    integration_codex = (
        package_dir / ".agents" / "skills" / "maios-project-integration" / "SKILL.md"
    )
    if integration_source.is_file() and integration_codex.is_file():
        if integration_source.read_bytes() != integration_codex.read_bytes():
            errors.append("distribution integration competence Codex projection drifted")

    forbidden_markers = (
        b".codex\\worktrees",
        b".codex/worktrees",
        b"MAIOS_CLIENT_SETUP",
        b"project_hook_kernel",
        b"hooks.json",
    )
    credential_names = {".env", "id_rsa", "id_ed25519", "credentials.json"}
    legacy_prefixes = (
        ".repokernel/",
        "meta-competences/",
        "assistant/",
        "skills/maios-project-faculty-router/",
        "skills/maios-setup-interviewer/",
        "skills/operate-maios-project-kernel/",
    )
    for path in distribution_files(package_dir):
        relative = path.relative_to(package_dir).as_posix()
        payload_relative = relative.removeprefix("payload/")
        if "__pycache__" in PurePosixPath(relative).parts or path.suffix.lower() in {
            ".pyc",
            ".pyo",
        }:
            errors.append(f"generated bytecode is forbidden in distribution: {relative}")
        if payload_relative.startswith(legacy_prefixes):
            errors.append(f"legacy package owner is forbidden: {relative}")
        if path.name.lower() in credential_names:
            errors.append(f"credential-like file is forbidden: {relative}")
        data = path.read_bytes()
        for marker in forbidden_markers:
            if marker in data:
                errors.append(f"private or contaminated marker in {relative}: {marker!r}")
        if path.suffix.lower() in {".md", ".json", ".py", ".txt"}:
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"text file is not valid UTF-8: {relative}")
    return {
        "schema": "maios.distribution-verification.v2",
        "valid": not errors,
        "errors": errors,
        "package_file_count": len(actual_names),
        "source_tree_sha256": source_tree_digest(root),
    }


def promote_directory(staging: Path, target: Path) -> None:
    if staging.expanduser().is_symlink() or target.expanduser().is_symlink():
        raise BuildError("promotion paths must not be symlinks")
    staging = staging.resolve()
    target = target.resolve()
    if staging.parent != target.parent:
        raise BuildError("staging and target must share a parent for atomic promotion")
    backup = target.with_name(f".{target.name}.previous-{os.getpid()}")
    if backup.exists():
        raise BuildError(f"promotion backup already exists: {backup}")
    if target.exists():
        os.replace(target, backup)
    try:
        os.replace(staging, target)
    except Exception:
        if backup.exists() and not target.exists():
            os.replace(backup, target)
        raise
    if backup.exists():
        shutil.rmtree(backup)
