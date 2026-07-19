from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "release_readiness_manifest.json"
ACCEPTANCE_PATH = ROOT / "docs" / "product_acceptance_manifest.json"
REQUIRED_WORKFLOWS = {
    "Product Acceptance",
    "Quality",
    "Document Quality",
    "Guided Release Acceptance",
    "Operator Docs",
    "Docker Release Runtime",
}
REQUIRED_CHECKLIST_HEADINGS = {
    "## 1. Prerequisites",
    "## 2. Configuration and secrets",
    "## 3. Backup",
    "## 4. Upgrade and migration",
    "## 5. Health verification",
    "## 6. LAN access",
    "## 7. Product smoke acceptance",
    "## 8. Rollback boundary",
    "## 9. Operator sign-off",
}
ALLOWED_STATUSES = {"release_candidate", "release_ready", "released"}
TAG_PATTERN = re.compile(r"^v\d+\.\d+\.\d+$")
COMMIT_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise SystemExit(f"Release readiness manifest invalid: {message}")


def require_mapping(value: object, field: str) -> dict[str, Any]:
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


def read_json(path: Path, field: str) -> dict[str, Any]:
    try:
        return require_mapping(json.loads(path.read_text(encoding="utf-8")), field)
    except (OSError, json.JSONDecodeError) as error:
        fail(str(error))


def require_file(path_value: str, field: str) -> Path:
    path = ROOT / path_value
    if not path.is_file():
        fail(f"{field} does not exist: {path_value}")
    return path


def main() -> None:
    manifest = read_json(MANIFEST_PATH, "manifest")
    acceptance = read_json(ACCEPTANCE_PATH, "acceptance manifest")

    if manifest.get("schema_version") != 1:
        fail("schema_version must be 1")
    if manifest.get("product") != "TourHub":
        fail("product must be TourHub")

    status = require_string(manifest.get("status"), "status")
    if status not in ALLOWED_STATUSES:
        fail(f"unsupported status: {status}")

    previous_revision = require_string(
        manifest.get("previous_alembic_revision"), "previous_alembic_revision"
    )
    final_revision = require_string(manifest.get("final_alembic_head"), "final_alembic_head")
    if previous_revision != "h10020" or final_revision != "h10021":
        fail("migration boundary must remain h10020 -> h10021")

    cycle = require_string_list(manifest.get("migration_cycle"), "migration_cycle")
    if cycle != ["h10020", "h10021", "h10020", "h10021"]:
        fail("migration_cycle must be h10020 -> h10021 -> h10020 -> h10021")

    if acceptance.get("status") != "feature_frozen":
        fail("Product Acceptance must remain feature_frozen")
    if acceptance.get("alembic_head") != "h10021":
        fail("Product Acceptance Alembic head must remain h10021")

    tag = require_string(manifest.get("release_tag"), "release_tag")
    if TAG_PATTERN.fullmatch(tag) is None:
        fail("release_tag must use vMAJOR.MINOR.PATCH")

    release_commit_sha: str | None = None
    if status == "released":
        release_commit_sha = require_string(
            manifest.get("release_commit_sha"), "release_commit_sha"
        )
        if COMMIT_SHA_PATTERN.fullmatch(release_commit_sha) is None:
            fail("release_commit_sha must be a lowercase 40-character commit SHA")
    elif manifest.get("release_commit_sha") is not None:
        fail("release_commit_sha is allowed only when status is released")

    pyproject = tomllib.loads((ROOT / "backend" / "pyproject.toml").read_text(encoding="utf-8"))
    backend_version = require_string(pyproject.get("project", {}).get("version"), "backend version")
    if tag != f"v{backend_version}":
        fail(f"release_tag {tag} must match backend version {backend_version}")

    workflows = set(require_string_list(manifest.get("required_workflows"), "required_workflows"))
    if workflows != REQUIRED_WORKFLOWS:
        fail(
            "required_workflows must be exactly "
            + ", ".join(sorted(REQUIRED_WORKFLOWS))
        )

    external_services = manifest.get("external_runtime_services")
    if external_services != []:
        fail("external_runtime_services must be an empty list")

    checklist_path = require_file(
        require_string(manifest.get("deployment_checklist"), "deployment_checklist"),
        "deployment_checklist",
    )
    release_notes_path = require_file(
        require_string(manifest.get("release_notes_source"), "release_notes_source"),
        "release_notes_source",
    )
    require_file(
        require_string(manifest.get("acceptance_manifest"), "acceptance_manifest"),
        "acceptance_manifest",
    )
    require_file(
        require_string(manifest.get("migration_verifier"), "migration_verifier"),
        "migration_verifier",
    )
    require_file(
        require_string(manifest.get("final_workflow"), "final_workflow"),
        "final_workflow",
    )

    checklist = checklist_path.read_text(encoding="utf-8")
    missing_headings = sorted(
        heading for heading in REQUIRED_CHECKLIST_HEADINGS if heading not in checklist
    )
    if missing_headings:
        fail(f"deployment checklist is missing headings: {missing_headings}")

    for required_reference in (
        "docker-compose.release.yml",
        "docs/INSTALLATION.md",
        "docs/UPDATING.md",
        "scripts/db/backup-tourhub.sh",
        "scripts/db/restore-tourhub.sh",
        "docs/PRODUCT_ACCEPTANCE.md",
    ):
        if required_reference not in checklist:
            fail(f"deployment checklist does not reference {required_reference}")

    release_notes = release_notes_path.read_text(encoding="utf-8")
    if tag not in release_notes:
        fail(f"release notes must name {tag}")
    if "h10021" not in release_notes:
        fail("release notes must name Alembic h10021")
    if "FEATURE FROZEN" not in release_notes:
        fail("release notes must preserve the FEATURE FROZEN decision")

    active_task = (
        ROOT
        / "docs"
        / "tasks"
        / "active"
        / "TH-0093-final-migration-release-readiness.md"
    )
    closed_task = (
        ROOT
        / "docs"
        / "tasks"
        / "closed"
        / "TH-0093-final-migration-release-readiness.md"
    )
    if status == "release_candidate" and not active_task.is_file():
        fail("release_candidate requires active TH-0093")
    if status in {"release_ready", "released"}:
        if active_task.exists():
            fail(f"{status} cannot keep TH-0093 active")
        if not closed_task.is_file():
            fail(f"{status} requires closed TH-0093")

    release_detail = f", release commit {release_commit_sha}" if release_commit_sha else ""
    print(
        "Release readiness manifest valid: "
        f"{status}, {tag}, {previous_revision} -> {final_revision}, "
        f"{len(workflows)} exact-head workflows{release_detail}."
    )


if __name__ == "__main__":
    main()
