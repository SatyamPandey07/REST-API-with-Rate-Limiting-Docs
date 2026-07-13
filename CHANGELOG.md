# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Interactive single-page application (SPA) Web Dashboard in `frontend/` (HTML/CSS/JS) built with a dark glassmorphic design system.
- Configured CORS (`CORSMiddleware`) in the FastAPI backend application to permit cross-origin requests from the browser frontend.
- Multi-stage, secure production `Dockerfile` running under non-privileged system user context (`runuser` UID 10001).
- Structured JSON-formatted request logging middleware tracking HTTP method, path, status, and duration.
- GitHub Actions CI workflow config at `.github/workflows/ci.yml` running on pushes/pull requests.
- Integrated sidecar PostgreSQL and Redis database containers inside CI pipeline environment.
- Configured code test coverage reporting via `pytest-cov`, strictly enforcing a minimum threshold of **95%**.
- Comprehensive unit test file `tests/test_coverage_gaps.py` targeting edge cases to reach **99%** code coverage.
- Comprehensive OpenAPI documentation enhancements for FastAPI, including detailed docstrings on all routers and tags grouping (Auth, Projects, Tasks, Health).
- Detailed description and realistic request/response validation examples on all Pydantic schemas.
- Automation script `scripts/generate_postman.py` compiling a complete v2.1.0 Postman collection saved at `docs/postman_collection.json`.
- Comprehensive design guide at `docs/API_DESIGN.md` detailing architectural routing, versioning, security, and error handling.
- Explicit URL-based API versioning prefixing all endpoints with `/api/v1/`.
- Dynamic deprecation detection HTTP middleware injecting `X-API-Deprecated` and `Sunset` response headers based on app configurations.
- Unauthenticated uptime health check endpoint at `GET /api/v1/health` verifying database connectivity.
- Rate limiting capability using the `slowapi` library integrated with a Redis backend.
- Local development Docker-compose configured with a Redis database instance.
- Specialized rate limits per client type:
  - Auth endpoints (`/auth/register`, `/auth/login`): Stricter limit of 5 requests/minute per client IP.
  - Read endpoints (`GET`): Generous limit of 100 requests/minute per authenticated user.
  - Write endpoints (`POST`, `PUT`, `DELETE`): Moderate limit of 30 requests/minute per authenticated user.
- Per-authenticated-user rate limit keys mapped from JWT sub claim, falling back to client IP for unauthenticated requests.
- Custom rate-limit exceeded handler returning standard HTTP 429 response along with client `Retry-After` header.
- Unit tests validating rate limiter blocks, headers, and window reset intervals.
