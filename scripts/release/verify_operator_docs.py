from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FRAGMENTS = {
    "README.md": [
        "docs/INSTALLATION.md",
        "docs/UPDATING.md",
        "scripts/db/backup-tourhub.sh",
        "scripts/db/restore-tourhub.sh",
    ],
    "docs/INSTALLATION.md": [
        "docker compose up -d --build",
        "/api/v1/health",
        "alembic current",
        "backup-tourhub.sh",
        "postgres18_cluster_data",
    ],
    "docs/UPDATING.md": [
        "git pull --ff-only",
        "docker compose build --pull backend frontend",
        "alembic backend upgrade head",
        "restore-tourhub.sh",
        "docker compose down --volumes",
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

    required_scripts = [
        ROOT / "scripts/db/backup-tourhub.sh",
        ROOT / "scripts/db/restore-tourhub.sh",
    ]
    for script in required_scripts:
        if not script.is_file():
            errors.append(f"Missing operator script: {script.relative_to(ROOT)}")

    if errors:
        print("Operator documentation verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Operator documentation verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
