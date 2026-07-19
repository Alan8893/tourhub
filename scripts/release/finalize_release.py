from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "docs" / "release_readiness_manifest.json"
DEFAULT_EVIDENCE = ROOT / "final-release-tag-evidence.json"


def _request_json(
    url: str,
    token: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tourhub-final-release-readiness",
    }
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {}


def _write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _latest_runs_by_name(
    runs: list[dict[str, Any]],
    sha: str,
) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for run in runs:
        if run.get("head_sha") != sha or run.get("event") != "push":
            continue
        name = run.get("name")
        if isinstance(name, str) and name not in latest:
            latest[name] = run
    return latest


def _wait_for_workflows(
    api_url: str,
    repository: str,
    token: str,
    sha: str,
    required: list[str],
    poll_seconds: int,
    max_attempts: int,
) -> dict[str, dict[str, Any]]:
    query = urllib.parse.urlencode(
        {"head_sha": sha, "event": "push", "per_page": 100}
    )
    runs_url = f"{api_url}/repos/{repository}/actions/runs?{query}"

    for attempt in range(1, max_attempts + 1):
        payload = _request_json(runs_url, token)
        raw_runs = payload.get("workflow_runs", [])
        if not isinstance(raw_runs, list):
            raise RuntimeError("GitHub Actions response did not contain workflow_runs")
        latest = _latest_runs_by_name(raw_runs, sha)

        failed = {
            name: latest[name].get("conclusion")
            for name in required
            if name in latest
            and latest[name].get("status") == "completed"
            and latest[name].get("conclusion") != "success"
        }
        if failed:
            raise RuntimeError(f"Required exact-head workflows failed: {failed}")

        missing = [name for name in required if name not in latest]
        pending = [
            name
            for name in required
            if name in latest and latest[name].get("status") != "completed"
        ]
        if not missing and not pending:
            return {name: latest[name] for name in required}

        print(
            f"Waiting for exact-head workflows ({attempt}/{max_attempts}); "
            f"missing={missing}, pending={pending}",
            flush=True,
        )
        if attempt < max_attempts:
            time.sleep(poll_seconds)

    raise TimeoutError(
        "Required exact-head workflows did not all complete successfully"
    )


def resolve_release_tag_policy(
    manifest: dict[str, Any],
    current_sha: str,
) -> tuple[str, bool]:
    status = manifest.get("status")
    if status == "release_ready":
        return current_sha, True
    if status == "released":
        release_commit_sha = manifest.get("release_commit_sha")
        if not isinstance(release_commit_sha, str) or not release_commit_sha:
            raise ValueError("released manifest requires release_commit_sha")
        return release_commit_sha, False
    raise ValueError("manifest status must be release_ready or released")


def _ensure_tag(
    api_url: str,
    repository: str,
    token: str,
    tag: str,
    expected_sha: str,
    *,
    allow_create: bool,
) -> str:
    encoded_tag = urllib.parse.quote(tag, safe="")
    ref_url = f"{api_url}/repos/{repository}/git/ref/tags/{encoded_tag}"
    try:
        existing = _request_json(ref_url, token)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
    else:
        existing_sha = existing.get("object", {}).get("sha")
        if existing_sha != expected_sha:
            raise RuntimeError(
                f"Tag {tag} points to {existing_sha}, not published commit {expected_sha}"
            )
        return "already_present" if allow_create else "verified_immutable"

    if not allow_create:
        raise RuntimeError(f"Published release tag {tag} is missing")

    _request_json(
        f"{api_url}/repos/{repository}/git/refs",
        token,
        method="POST",
        payload={"ref": f"refs/tags/{tag}", "sha": expected_sha},
    )
    return "created"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or verify the TourHub release tag after exact-head gates."
    )
    parser.add_argument("--sha", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--poll-seconds", type=int, default=20)
    parser.add_argument("--max-attempts", type=int, default=90)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    repository = os.environ.get("GITHUB_REPOSITORY")
    api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    if not token or not repository:
        raise SystemExit("GITHUB_TOKEN and GITHUB_REPOSITORY are required")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("release_tag") != args.tag:
        raise SystemExit("Requested tag does not match release readiness manifest")
    required = manifest.get("required_workflows")
    if not isinstance(required, list) or not all(
        isinstance(item, str) for item in required
    ):
        raise SystemExit("required_workflows must be a list of workflow names")

    try:
        expected_tag_sha, allow_create = resolve_release_tag_policy(
            manifest,
            args.sha,
        )
    except ValueError as error:
        raise SystemExit(str(error)) from error

    evidence: dict[str, Any] = {
        "schema_version": 1,
        "status": "running",
        "release_status": manifest.get("status"),
        "repository": repository,
        "validated_commit_sha": args.sha,
        "release_commit_sha": expected_tag_sha,
        "release_tag": args.tag,
        "required_workflows": required,
    }
    try:
        runs = _wait_for_workflows(
            api_url,
            repository,
            token,
            args.sha,
            required,
            args.poll_seconds,
            args.max_attempts,
        )
        evidence["workflow_runs"] = {
            name: {
                "id": run.get("id"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "html_url": run.get("html_url"),
            }
            for name, run in sorted(runs.items())
        }
        tag_result = _ensure_tag(
            api_url,
            repository,
            token,
            args.tag,
            expected_tag_sha,
            allow_create=allow_create,
        )
        evidence["tag_result"] = tag_result
        evidence["status"] = "success"
        _write_evidence(args.evidence, evidence)
        print(
            f"Release tag {args.tag} {tag_result} at published commit "
            f"{expected_tag_sha}; validated head {args.sha}."
        )
    except Exception as error:
        evidence["status"] = "failure"
        evidence["error"] = {
            "type": type(error).__name__,
            "message": str(error),
        }
        _write_evidence(args.evidence, evidence)
        raise


if __name__ == "__main__":
    main()
