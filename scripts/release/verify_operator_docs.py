from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FRAGMENTS = {
    "README.md": [
        "docs/INSTALLATION.md",
        "docs/DOCKER_RELEASE.md",
        "docs/UPDATING.md",
        "docker-compose.release.yml",
        "scripts/db/backup-tourhub.sh",
        "scripts/db/restore-tourhub.sh",
    ],
    "docs/INSTALLATION.md": [
        "docker compose -f docker-compose.release.yml",
        "/api/v1/health",
        "/healthz",
        "alembic current",
        "COMPOSE_FILE=docker-compose.release.yml",
        "backup-tourhub.sh",
        "postgres18_cluster_data",
    ],
    "docs/DOCKER_RELEASE.md": [
        "frontend/Dockerfile.release",
        "docker-compose.release.yml",
        "build --pull",
        "up -d --wait --wait-timeout 180",
        "/api/v1/health",
        "/healthz",
        "COMPOSE_FILE=docker-compose.release.yml",
        "down --volumes",
        "Docker Release Runtime",
    ],
    "docs/UPDATING.md": [
        "git pull --ff-only",
        "docker compose -f docker-compose.release.yml build --pull backend frontend",
        "run --rm --entrypoint alembic backend upgrade head",
        "COMPOSE_FILE=docker-compose.release.yml",
        "restore-tourhub.sh",
        "docker compose -f docker-compose.release.yml down --volumes",
        "/healthz",
    ],
}

LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def check_required_fragments(errors: list[str]) -> None:
    for relative_path, fragments in REQUIRED_FRAGMENTS.items():
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"Missing required file: {relative_path}")
            continue
        content = path.read_text(encoding="utf-8")
        for fragment in fragments:
            if fragment not in content:
                errors.append(f"{relative_path} is missing required fragment: {fragment}")


def check_relative_links(errors: list[str]) -> None:
    for relative_path in REQUIRED_FRAGMENTS:
        source = ROOT / relative_path
        if not source.is_file():
            continue
        content = source.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(content):
            target = raw_target.split("#", maxsplit=1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (source.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"Broken relative link in {relative_path}: {raw_target}")


def main() -> int:
    errors: list[str] = []
    check_required_fragments(errors)
    check_relative_links(errors)

    required_files = [
        ROOT / "docker-compose.release.yml",
        ROOT / "frontend/Dockerfile.release",
        ROOT / "frontend/nginx.release.conf",
        ROOT / "scripts/db/backup-tourhub.sh",
        ROOT / "scripts/db/restore-tourhub.sh",
        ROOT / "scripts/release/verify_docker_runtime.py",
    ]
    for path in required_files:
        if not path.is_file():
            errors.append(f"Missing operator file: {path.relative_to(ROOT)}")

    if errors:
        print("Operator documentation verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Operator documentation verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
