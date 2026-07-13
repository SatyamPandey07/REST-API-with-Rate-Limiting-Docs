# TaskFlow API

[![Continuous Integration](https://github.com/SatyamPandey07/REST-API-with-Rate-Limiting-Docs/actions/workflows/ci.yml/badge.svg)](https://github.com/SatyamPandey07/REST-API-with-Rate-Limiting-Docs/actions/workflows/ci.yml)

A robust task and project management REST API built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Pydantic. This repository serves as a step-by-step showcase of modern production API architecture, built incrementally across 8 planned Pull Requests.

---

## 🚀 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database**: [PostgreSQL](https://www.postgresql.org/) via Docker
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Data Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Testing**: [pytest](https://docs.pytest.org/)

---

## 🛠️ Setup Instructions

### 1. Prerequisites
Ensure you have the following installed:
- Python 3.9+
- Docker & Docker Compose

### 2. Configure Environment
Create a virtual environment and install the dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Spin up PostgreSQL Database
Start the local Postgres instance in the background using Docker Compose:
```bash
docker compose up -d
```

### 4. Run Migrations
Run Alembic migrations to construct the database schema:
```bash
alembic upgrade head
```

### 5. Run the Application
Start the Uvicorn development server:
```bash
uvicorn app.main:app --reload --port 8000
```
Once started, you can access the interactive Swagger API documentation at **[http://localhost:8000/docs](http://localhost:8000/docs)**, and the alternative ReDoc specification view at **[http://localhost:8000/redoc](http://localhost:8000/redoc)**.

For detailed guidelines on the system design, error envelopes, and rate limit tiers, read the **[API Design Guide](docs/API_DESIGN.md)**.
You can also import the pre-configured **[Postman Collection](docs/postman_collection.json)** to test the versioned API endpoints.

---

## 🔑 Authentication

All endpoints under `/projects` and `/tasks` are protected by JWT Bearer Token authentication. Here is how to use them:

### 1. Register a User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypassword"}'
```

### 2. Log in to Get an Access Token
Since the endpoint supports the standard OAuth2 Password flow, send credentials as form data:
```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=user@example.com" \
  -F "password=mypassword"
```
Response:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### 3. Access Protected Endpoints
Pass the token in the `Authorization` header as a Bearer token:
```bash
curl -X GET http://localhost:8000/projects/ \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## 🔢 Pagination & Filtering

List endpoints for both Projects and Tasks support pagination parameters. Additionally, Tasks support filtering by project and status.

### 1. Pagination Parameters
- `page`: The page number (ge=1, default=1).
- `page_size`: Number of records to return (ge=1, le=100, default=20). Requesting > 100 results will reject the call with `422 Unprocessable Entity`.

```bash
curl -X GET "http://localhost:8000/tasks/?page=1&page_size=5" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```
Response envelope structure:
```json
{
  "data": [
    {
      "id": 1,
      "title": "Task 1",
      "status": "Todo",
      "project_id": 2,
      "user_id": 1,
      "created_at": "2026-07-13T20:56:47Z"
    }
  ],
  "pagination": {
    "total_count": 1,
    "page": 1,
    "page_size": 5,
    "total_pages": 1
  }
}
```

### 2. Filtering Tasks
Filter tasks by `status` or `project_id`:
```bash
curl -X GET "http://localhost:8000/tasks/?status=Todo&project_id=2" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```

---

## 🛡️ Rate Limiting

To maintain service stability, prevent brute-force attacks, and protect resources from abuse, TaskFlow API implements distinct rate-limiting tiers using `slowapi` and Redis.

### Tiers & Limits Table

| Endpoint Type | Applied Route | Rate Limit | Scope / Key | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST /auth/register`<br>`POST /auth/login` | **5 / minute** | Client IP | Protects user accounts from automated brute-force attacks and prevents registration spam. |
| **Write** | `POST`, `PUT`, `DELETE` on `/projects` & `/tasks` | **30 / minute** | Authenticated User (JWT)<br>*(IP fallback)* | Prevents database write-locking, resource bloat, and spam creation of projects or tasks. |
| **Read** | `GET` on `/projects` & `/tasks` | **100 / minute** | Authenticated User (JWT)<br>*(IP fallback)* | Allows generous read bandwidth to retrieve data, lists, and paginated information. |

### Error Response & Retry
When a client exceeds the limit, the API returns HTTP **`429 Too Many Requests`** along with a **`Retry-After`** header indicating the number of seconds to wait before retrying:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 48

{
  "detail": "Rate limit exceeded: 5 per 1 minute"
}
```

---

## 🌐 API Versioning

TaskFlow API uses **URL-based versioning** (prefixed with `/api/v1/`) to manage endpoints.

### Why URL-based over Header-based versioning?
- **Ease of Consumption**: URL-based versioning is highly discoverable, visually clean, and straightforward for consumers to test directly in their browsers, postman, or copy-paste curl commands without configuring custom headers.
- **Caching Simplicity**: Proxies, CDNs, and browser caches natively cache separate URLs without needing custom `Vary` header configuration, ensuring higher caching performance.

### ⚠️ Deprecation & Sunset Mechanism
To facilitate smooth transitions when introducing new versions, TaskFlow API implements a native deprecation mechanism via HTTP response headers:
- `X-API-Deprecated: true` (alerting clients that the active endpoint is deprecated).
- `Sunset: <Date>` (indicating the exact end-of-life timestamp for the deprecated version).

#### Example Response Headers (Deprecated Endpoint)
```http
HTTP/1.1 200 OK
Content-Type: application/json
X-API-Deprecated: true
Sunset: Wed, 11 Nov 2026 00:00:00 GMT
```

### Hypothetical Version Upgrade (v2 Migration)
When a future `/api/v2/` version is released (e.g., changing schemas or authentication mechanisms):
1. The new routers will be mounted under `/api/v2/`.
2. The `/api/v1/` endpoints will continue to function normally but will start returning `X-API-Deprecated: true` and the `Sunset` header.
3. Consumers have until the `Sunset` date to transition their request prefixes from `/api/v1/` to `/api/v2/` without breaking production clients.

---

## 🧪 Running Tests

Unit tests are executed in isolation using an in-memory SQLite database. You do not need the Docker Compose database running to run tests.

Execute the test suite using `pytest`:
```bash
pytest
```

---

## 🛠️ Continuous Integration & Test Coverage

TaskFlow API uses **GitHub Actions** for CI, running on every push and pull request.

### CI Workflow Steps
1. Spins up sidecar services for **PostgreSQL** and **Redis**.
2. Checks out code and installs dependencies.
3. Runs Alembic migrations (`alembic upgrade head`) to verify schema initialization.
4. Executes the full `pytest` suite with `pytest-cov` reporting.
5. Fails the build if overall test coverage drops below the **95%** threshold.

### Coverage Commands
Run tests locally with code coverage tracking:
```bash
pytest --cov=app --cov-report=term-missing
```
Currently, the codebase maintains **99% test coverage**.

---

## 🗺️ Roadmap (Incremental API Build Plan)

This project is being built incrementally across 8 sequential Pull Requests to showcase clean design progression:

*   **[PR #1: Core CRUD Scaffolding (Current)]**
    *   Basic Project & Task models and schema setup.
    *   Full CRUD endpoints with proper HTTP status codes.
    *   Docker database scaffolding and initial Alembic migrations setup.
    *   Fully isolated pytest suite using SQLite.
*   **[PR #2: Authentication & Authorization]**
    *   User registration and secure password hashing.
    *   OAuth2 JWT Bearer Token authorization flows.
    *   Scoped resource ownership (users only modify their own tasks).
*   **[PR #3: REST API Rate Limiting]**
    *   Integrating token bucket/sliding window rate-limiting middleware.
    *   Custom rate-limit configurations per endpoint.
*   **[PR #4: REST API Versioning]**
    *   Supporting multiple API versions (e.g. `/api/v1/` and `/api/v2/`).
*   **[PR #5: Advanced Pagination, Sorting & Filtering]**
    *   Custom query parameter filters for tasks (by status, projects, etc.).
    *   Cursor-based and limit-offset pagination.
*   **[PR #6: Logging & Observability]**
    *   Structured JSON logging middleware and performance metrics tracking.
*   **[PR #7: Multi-stage Docker & Production Setup]**
    *   Optimized production Dockerfile build and config profiles.
*   **[PR #8: CI/CD Deployment Pipeline]**
    *   Automated GitHub Actions workflow for testing, linting, and cloud deploy.
