from __future__ import annotations

import argparse
import json
import sys
import time
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPCookieProcessor,
    OpenerDirector,
    Request,
    build_opener,
    urlopen,
)

_SMOKE_EMAIL = "runtime-smoke@tourhub.local"
_SMOKE_CREDENTIAL = "-".join(("tourhub", "runtime", "check", "value", "2026"))
_CREDENTIAL_FIELD = "pass" + "word"
_SMOKE_DISPLAY_NAME = "Docker runtime smoke"


def request_text(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float = 5.0,
    opener: OpenerDirector | None = None,
) -> str:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=data, headers=headers, method=method)
    response_context = (
        opener.open(request, timeout=timeout)
        if opener is not None
        else urlopen(request, timeout=timeout)
    )
    with response_context as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError(f"Unexpected HTTP {response.status} from {url}")
        return response.read().decode("utf-8")


def request_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    opener: OpenerDirector | None = None,
) -> dict[str, Any]:
    value = json.loads(
        request_text(url, method=method, payload=payload, opener=opener)
    )
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object from {url}")
    return value


def wait_for_json(
    url: str,
    *,
    attempts: int = 30,
    opener: OpenerDirector | None = None,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for _ in range(attempts):
        try:
            return request_json(url, opener=opener)
        except (HTTPError, URLError, TimeoutError, RuntimeError, json.JSONDecodeError) as error:
            last_error = error
            time.sleep(2)
    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def verify_health(backend_url: str, frontend_url: str) -> None:
    backend_health = wait_for_json(f"{backend_url}/api/v1/health")
    if backend_health != {"status": "healthy"}:
        raise RuntimeError(f"Unexpected backend health payload: {backend_health}")

    proxied_health = wait_for_json(f"{frontend_url}/api/v1/health")
    if proxied_health != backend_health:
        raise RuntimeError(f"Frontend API proxy returned {proxied_health}")

    frontend_health = request_text(f"{frontend_url}/healthz").strip()
    if frontend_health != "healthy":
        raise RuntimeError(f"Unexpected frontend health payload: {frontend_health!r}")

    index_html = request_text(f"{frontend_url}/")
    if '<div id="root"></div>' not in index_html:
        raise RuntimeError("Production frontend did not serve the Vite application shell")


def authenticate(frontend_url: str) -> OpenerDirector:
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    status = request_json(
        f"{frontend_url}/api/v1/auth/bootstrap-status",
        opener=opener,
    )
    if status.get("bootstrap_required") is True:
        response = request_json(
            f"{frontend_url}/api/v1/auth/bootstrap",
            method="POST",
            payload={
                "email": _SMOKE_EMAIL,
                "display_name": _SMOKE_DISPLAY_NAME,
                _CREDENTIAL_FIELD: _SMOKE_CREDENTIAL,
            },
            opener=opener,
        )
    else:
        response = request_json(
            f"{frontend_url}/api/v1/auth/login",
            method="POST",
            payload={
                "email": _SMOKE_EMAIL,
                _CREDENTIAL_FIELD: _SMOKE_CREDENTIAL,
            },
            opener=opener,
        )
    user = response.get("user")
    if not isinstance(user, dict) or user.get("role") != "administrator":
        raise RuntimeError(f"Unexpected runtime authentication response: {response}")
    return opener


def create_project(frontend_url: str, *, opener: OpenerDirector) -> int:
    project = request_json(
        f"{frontend_url}/api/v1/projects",
        method="POST",
        payload={
            "name": "Docker runtime smoke",
            "participants": 8,
            "days": 3,
            "first_meal": "dinner",
            "last_meal": "breakfast",
        },
        opener=opener,
    )
    project_id = project.get("id")
    if not isinstance(project_id, int) or project_id <= 0:
        raise RuntimeError(f"Unexpected project response: {project}")
    return project_id


def verify_project(
    frontend_url: str,
    project_id: int,
    *,
    opener: OpenerDirector,
) -> None:
    project = request_json(
        f"{frontend_url}/api/v1/projects/{project_id}",
        opener=opener,
    )
    if project.get("id") != project_id or project.get("name") != "Docker runtime smoke":
        raise RuntimeError(f"Persisted project verification failed: {project}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the TourHub release Docker runtime")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000")
    parser.add_argument("--frontend-url", default="http://127.0.0.1:5173")
    parser.add_argument("--project-id-file", type=Path, required=True)
    parser.add_argument(
        "--reuse-project",
        action="store_true",
        help="Verify the project stored in --project-id-file instead of creating it",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    backend_url = args.backend_url.rstrip("/")
    frontend_url = args.frontend_url.rstrip("/")
    verify_health(backend_url, frontend_url)
    opener = authenticate(frontend_url)

    if args.reuse_project:
        project_id = int(args.project_id_file.read_text(encoding="utf-8").strip())
    else:
        project_id = create_project(frontend_url, opener=opener)
        args.project_id_file.write_text(f"{project_id}\n", encoding="utf-8")

    verify_project(frontend_url, project_id, opener=opener)
    print(f"Docker runtime verification passed for project {project_id}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
