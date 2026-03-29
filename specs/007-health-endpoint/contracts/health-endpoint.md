# Health Endpoint Contract

**Feature**: 007-health-endpoint  
**Date**: 2026-03-29

## 1. Endpoint Contract

| Method | Path | Authentication | Rate Limiting | Documentation Visibility |
|--------|------|----------------|---------------|--------------------------|
| GET | `/api/v1/health/` | `AllowAny` | Exempt | Public schema and internal schema |

## 2. Response Contract

### 2.1 Healthy Result

| Condition | HTTP Status | Body |
|-----------|-------------|------|
| Application can handle requests normally | `200` | `{"status":"healthy"}` |

### 2.2 Non-Healthy Result

| Condition | HTTP Status | Body |
|-----------|-------------|------|
| Application is starting, stopping, or otherwise cannot handle requests normally | `503` | `{"status":"unhealthy"}` |

## 3. Scope Contract

1. The endpoint reports only application-process health.
2. Database, cache, message broker, third-party API, and other dependency checks are out of scope.
3. External dependency failures alone MUST NOT cause `/api/v1/health/` to report `unhealthy`.
4. The response body MUST contain only the `status` field and no extra metadata.
5. Responses MUST NOT expose dependency names, dependency diagnostics, or internal failure details.

## 4. Routing And Schema Contract

1. The endpoint MUST be registered via `health.urls.api_v1_urlpatterns`.
2. Main `afrourban/urls.py` MUST include that route through `api_urlpatterns` under `/api/`.
3. `afrourban/api_schema.py` MUST classify `/api/v1/health/` as a public endpoint.
4. Regenerated public and internal OpenAPI artifacts MUST both contain `/api/v1/health/`.

## 5. Logging Contract

Each request evaluation SHOULD emit one structured log event containing, at minimum:

- `message` or event name for the health check
- `outcome`
- `http_status`
- `method`
- `path`
- `request_user_id` when present, otherwise `null`

The event SHOULD use `health_check_evaluated` as its structured event name.
The contract MUST NOT log dependency diagnostics, secrets, or unnecessary internal detail.
