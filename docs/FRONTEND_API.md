# TourHub Frontend API Guide

## API Base URL

The frontend uses the same-origin API path by default:

```text
/api/v1
```

In Docker Compose development, Vite proxies `/api/*` to `http://backend:8000`. This keeps browser requests on the frontend origin and works from `localhost` or another computer on the local network.

Examples:

```text
http://localhost:5173/api/v1/projects
http://<server-ip>:5173/api/v1/projects
```

Do not hardcode `localhost:8000` in browser-facing frontend code. In a remote browser, `localhost` identifies that user's computer, not the TourHub server.

An explicit backend URL can be configured when a reverse proxy or deployment requires it:

```env
VITE_API_URL=https://tourhub.example.test/api/v1
```

Direct cross-origin browser access to the backend also requires the frontend origin in backend CORS settings. The standard Docker Compose workflow avoids that requirement by using the same-origin Vite proxy.

## OpenAPI Specification

FastAPI exposes OpenAPI directly from the backend:

```text
http://localhost:8000/openapi.json
```

Swagger UI:

```text
http://localhost:8000/docs
```

When accessing the server from another computer, replace `localhost` with the server hostname or IP address.

## TypeScript Client Generation

Recommended approach:

```bash
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o src/api/generated
```

Generated client code should not be edited manually.

## Client Update Workflow

1. Backend API changes are merged.
2. Run OpenAPI generation.
3. Review the generated diff.
4. Commit generated client changes.

## API Rules

- Use the `/api/v1` prefix.
- Use the shared frontend API client.
- Do not create feature-local clients with hardcoded origins.
- IDs are UUID strings unless an endpoint contract explicitly uses another type.
- Status values come from workflow enums.
- Frontend should not duplicate backend business rules.

## Current Foundation Endpoints

- `GET /meta` — API metadata and workflow information.
- `GET /health` — service health check.
