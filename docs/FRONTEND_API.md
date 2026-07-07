# TourHub Frontend API Guide

## API Base URL

Development:

```
http://localhost:8000/api/v1
```

## OpenAPI Specification

FastAPI exposes OpenAPI schema at:

```
http://localhost:8000/openapi.json
```

Swagger UI:

```
http://localhost:8000/docs
```

## TypeScript Client Generation

Recommended approach:

```
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o src/api/generated
```

Generated client should not be edited manually.

## Client Update Workflow

1. Backend API changes are merged.
2. Run OpenAPI generation.
3. Review generated diff.
4. Commit generated client changes.

## API Rules

- Use `/api/v1` prefix.
- IDs are UUID strings.
- Status values come from workflow enums.
- Frontend should not duplicate backend business rules.

## Current Foundation Endpoints

- `GET /meta` - API metadata and workflow information.
- `GET /health` - service health check.
