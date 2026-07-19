import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "product_acceptance_manifest.json"
REQUIRED_CAPABILITIES = {
    "runtime_operations",
    "system_settings",
    "access_roles_invitations_mail",
    "recipe_ownership_publication_variants",
    "project_preparation_shopping_equipment",
    "actor_aware_audit",
    "consolidated_russian_exports",
    "central_alcohol_prohibition",
}
ALLOWED_STATUSES = {"acceptance_candidate", "feature_frozen"}


def fail(message: str) -> None:
    raise SystemExit(f"Product acceptance manifest invalid: {message}")


def require_mapping(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        fail(f"{field} must be an object")
    return value


def require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{field} must be a non-empty string")
    return value


def require_string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        fail(f"{field} must be a non-empty list")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(require_string(item, f"{field}[{index}]"))
    return result


def validate_evidence(path_value: str, capability_id: str) -> None:
    path = ROOT / path_value
    if not path.is_file():
        fail(f"evidence for {capability_id} does not exist: {path_value}")


def main() -> None:
    try:
        manifest = require_mapping(
            json.loads(MANIFEST_PATH.read_text(encoding="utf-8")),
            "manifest",
        )
    except (OSError, json.JSONDecodeError) as error:
        fail(str(error))

    if manifest.get("schema_version") != 1:
        fail("schema_version must be 1")
    alembic_head = require_string(manifest.get("alembic_head"), "alembic_head")
    if alembic_head != "h10021":
        fail("alembic_head must be h10021")

    status = require_string(manifest.get("status"), "status")
    if status not in ALLOWED_STATUSES:
        fail(f"unsupported status: {status}")

    architecture = require_mapping(manifest.get("architecture"), "architecture")
    if architecture.get("deployment_model") != "local_single_club":
        fail("deployment_model must remain local_single_club")
    if architecture.get("application_shape") != "modular_monolith":
        fail("application_shape must remain modular_monolith")
    if architecture.get("multi_tenancy") != "prohibited":
        fail("multi_tenancy must remain prohibited")
    if architecture.get("microservices") != "prohibited":
        fail("microservices must remain prohibited")

    raw_capabilities = manifest.get("accepted_capabilities")
    if not isinstance(raw_capabilities, list):
        fail("accepted_capabilities must be a list")
    capability_ids: set[str] = set()
    for index, raw_capability in enumerate(raw_capabilities):
        capability = require_mapping(
            raw_capability,
            f"accepted_capabilities[{index}]",
        )
        capability_id = require_string(
            capability.get("id"),
            f"capability[{index}].id",
        )
        if capability_id in capability_ids:
            fail(f"duplicate capability: {capability_id}")
        capability_ids.add(capability_id)
        evidence = require_string_list(
            capability.get("evidence"),
            f"capability[{capability_id}].evidence",
        )
        for evidence_path in evidence:
            validate_evidence(evidence_path, capability_id)

    missing = REQUIRED_CAPABILITIES - capability_ids
    unexpected = capability_ids - REQUIRED_CAPABILITIES
    if missing:
        fail(f"missing required capabilities: {sorted(missing)}")
    if unexpected:
        fail(f"unexpected release capabilities: {sorted(unexpected)}")

    require_string_list(
        manifest.get("deferred_non_blocking_scope"),
        "deferred_non_blocking_scope",
    )
    require_string_list(
        manifest.get("feature_freeze_rules"),
        "feature_freeze_rules",
    )

    commands = require_mapping(
        manifest.get("acceptance_commands"),
        "acceptance_commands",
    )
    for command_name in ("manifest", "backend", "browser"):
        require_string(
            commands.get(command_name),
            f"acceptance_commands.{command_name}",
        )

    migration = (
        ROOT
        / "backend"
        / "alembic"
        / "versions"
        / "h10021_enforce_alcohol_prohibition.py"
    )
    if not migration.is_file():
        fail("h10021 migration file is missing")

    active_task = (
        ROOT
        / "docs"
        / "tasks"
        / "active"
        / "TH-0092-product-acceptance-feature-freeze.md"
    )
    closed_task = (
        ROOT
        / "docs"
        / "tasks"
        / "closed"
        / "TH-0092-product-acceptance-feature-freeze.md"
    )
    if status == "acceptance_candidate" and not active_task.is_file():
        fail("candidate status requires active TH-0092 task")
    if status == "feature_frozen":
        if active_task.exists():
            fail("feature_frozen status cannot keep TH-0092 active")
        if not closed_task.is_file():
            fail("feature_frozen status requires closed TH-0092 task")

    print(
        "Product acceptance manifest valid: "
        f"{status}, {len(capability_ids)} accepted capabilities, "
        f"Alembic {alembic_head}."
    )


if __name__ == "__main__":
    main()
