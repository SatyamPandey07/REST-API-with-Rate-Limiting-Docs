# TaskFlow API

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
Once started, you can access the interactive Swagger API documentation at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

---

## 🧪 Running Tests

Unit tests are executed in isolation using an in-memory SQLite database. You do not need the Docker Compose database running to run tests.

Execute the test suite using `pytest`:
```bash
pytest
```

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
