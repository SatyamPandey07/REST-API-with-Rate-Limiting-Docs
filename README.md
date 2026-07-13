# TaskFlow API

[![Continuous Integration](https://github.com/SatyamPandey07/REST-API-with-Rate-Limiting-Docs/actions/workflows/ci.yml/badge.svg)](https://github.com/SatyamPandey07/REST-API-with-Rate-Limiting-Docs/actions/workflows/ci.yml)

A robust task and project management REST API built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, and Pydantic. This repository serves as a showcase of modern production API architecture, featuring structured request logging, JWT auth boundaries, pagination/filtering indexes, slowapi Redis rate limiting, URL-based API versioning, and continuous integration pipeline automation.

---

## 📖 Problem Statement

Modern web architectures require performant, secure, and easily maintainable backend services. Building APIs that scale cleanly from day one requires solving common architectural issues:
- **Loose boundaries**: Exposing internal database objects or resource scopes directly to requests.
- **Uncontrolled request rates**: Vulnerability to scrapers, dictionary brute-forcing, and denial-of-service.
- **Vague documentation**: Out-of-date or placeholder specs that confuse consumers.
- **Resource bottlenecks**: Expensive queries on large database tables and unoptimized container runtimes.

TaskFlow API solves these problems by establishing a clean-layered REST API with JWT authorization boundaries, granular rate limits, URL versioning, 99% test coverage, and optimized containerized builds.

---

## 🎨 System Architecture

```mermaid
graph TD
    Client[Client Browser / cURL]
    Proxy[Nginx Proxy / API Gateway]
    FastAPI[FastAPI Application]
    RateLimiter[Redis Rate Limit Store]
    DB[(PostgreSQL Database)]
    TestDB[(SQLite Test DB)]

    Client -->|HTTP Request| Proxy
    Proxy -->|Forward /api/v1| FastAPI
    FastAPI -->|Check Token / IP Limits| RateLimiter
    FastAPI -->|Query / Mutate| DB
    FastAPI -.->|Test Context Run| TestDB
```

---

## 🚀 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (Local dev & CI services)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Schemas & Validation**: [Pydantic v2](https://docs.pydantic.dev/)
- **Rate Limiting**: [SlowAPI](https://github.com/laurentS/slowapi) with [Redis](https://redis.io/) backend
- **CI/CD**: [GitHub Actions](https://github.com/features/actions) with [pytest-cov](https://pytest-cov.readthedocs.io/)

---

## ⚙️ Setup Instructions

### 1. Local Development Setup
Ensure you have Python 3.12 installed:
```bash
# Clone the repository
git clone https://github.com/SatyamPandey07/REST-API-with-Rate-Limiting-Docs.git
cd REST-API-with-Rate-Limiting-Docs

# Initialize virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Dev Services via Docker Compose
TaskFlow API uses PostgreSQL and Redis for local dev:
```bash
# Spin up database and cache containers
docker-compose up -d
```

### 3. Run Alembic Migrations
```bash
alembic upgrade head
```

### 4. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

Once started, you can access the interactive Swagger API documentation at **[http://localhost:8000/docs](http://localhost:8000/docs)**, and ReDoc specification view at **[http://localhost:8000/redoc](http://localhost:8000/redoc)**.

For detailed guidelines on the system design, error envelopes, and rate limit tiers, read the **[API Design Guide](docs/API_DESIGN.md)**.
You can also import the pre-configured **[Postman Collection](docs/postman_collection.json)** to test versioned endpoints.

---

## 🖥️ Web Dashboard (Layman GUI)

The project includes an interactive single-page application (SPA) Web Dashboard located in the `frontend/` directory. It is designed with a modern glassmorphic interface to allow non-technical users to access and use the TaskFlow API directly in their browser.

### Dashboard Preview
![TaskFlow Web GUI Dashboard Preview](docs/assets/taskflow_dashboard_mockup.png)

### Features:
- **Authentication**: Easy sign up and sign in interface. Tokens are safely persisted in `localStorage`.
- **Project Board**: Create, list, edit, and delete projects. Selecting a project dynamically loads its associated tasks.
- **Task Management**: Create tasks, edit descriptions, toggle status values (`Todo` &rarr; `InProgress` &rarr; `Completed`), and delete items.
- **Real-time API Telemetry**: Displays health status (database connection tracking), rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After`), and API version warning headers (`X-API-Deprecated`, `Sunset`).

### 🧪 Testing the Application (Step-by-Step for Laymen)
Here is how you can use and test the application end-to-end:
1. **Initialize a User Account**:
   - Click the **Create Account** tab.
   - Input your email (e.g. `user@example.com`) and a password (e.g. `password123`), then submit the form. You will see a success toast notification.
2. **Authenticate (Sign In)**:
   - Click the **Sign In** tab, input the same credentials, and submit.
   - The UI will immediately load your profile and transition to the primary board view.
3. **Manage Projects**:
   - In the left sidebar under **Projects**, click the `+` button.
   - Enter a name (e.g. `Marketing Campaign`) and description, then click **Create**.
   - Click on the newly created project in the list to open it.
4. **Organize Tasks**:
   - Click the **+ Add Task** button in the main board header.
   - Enter a task title (e.g. `Draft Press Release`) and click **Add Task**.
   - Use the **Toggle Status** button on the task card to progress it from `Todo` &rarr; `In Progress` &rarr; `Completed`.
   - Filter your board by tasks status using the dynamic filters bar.
5. **Monitor Telemetry**:
   - Inspect the **API Telemetry** panel on the right sidebar to watch backend rate limits, health indicators, and API deprecation warning headers in real time.

### Running the Web GUI:
1. Ensure the TaskFlow API backend is running (`uvicorn app.main:app --port 8000`).
2. Simply open `frontend/index.html` in any web browser, or serve it using a lightweight local server:
   ```bash
   # Using Python's built-in HTTP server
   python3 -m http.server 3000 --directory frontend/
   ```
3. Open **[http://localhost:3000](http://localhost:3000)** in your browser. Configure the backend URL at the top if running on a custom port.

---

## 🐳 Production Container Build

For production environments, the application includes a secure, optimized multi-stage `Dockerfile`:
```bash
# Build the production Docker image
docker build -t taskflow-api:latest .

# Run the container locally (overriding DB/Redis environment credentials)
docker run -p 8000:8000 \
  -e SECRET_KEY="your_production_secret" \
  -e DATABASE_URL="postgresql://postgres:postgres@host.docker.internal:5432/taskflow" \
  -e REDIS_URL="redis://host.docker.internal:6379/0" \
  taskflow-api:latest
```

### Production Security & Optimization Details:
- **Multi-Stage Isolation**: Build tools (gcc, headers) are isolated in a temporary builder stage. The final runner stage only copies the compiled virtual environment.
- **Non-Privileged Execution**: Runs under a secure system user context (`runuser` UID 10001) instead of `root` to mitigate container escape risks.
- **Python Optimizations**: Executed with `PYTHONUNBUFFERED=1` to ensure logger outputs are immediately written to stdout/stderr.

---

## 📊 Observability & Metrics

TaskFlow API implements structured request-profiling logging. Every API request is logged in key-value JSON format to stdout:
```json
{"method": "POST", "path": "/api/v1/projects/", "status_code": 201, "duration_ms": "14.50ms"}
```

In a full production deployment, we would configure a metrics collector (like Prometheus) to scrape and aggregate these parameters. The key metrics to monitor include:

| Metric | What it Measures | Why it Matters |
|---|---|---|
| **Request Volume (RPM)** | Total HTTP requests per minute. | Detects traffic surges, client spam, or drops in service visibility. |
| **Error Rate (%)** | Ratio of 5xx server responses to total requests. | Serves as the primary indicator of service health degradation or database timeouts. |
| **p50 Latency** | Median response duration (50% of requests are faster). | Measures typical user experience under normal conditions. |
| **p90 / p99 Latency** | The 90th and 99th percentile response times. | Highlights tail latency outliers. Essential for detecting thread locking, connection pool exhaustion, or unindexed database queries. |

---

## 🚀 Scaling to 10x Capacity

To scale TaskFlow API from hundreds of requests to **10x capacity**, we would execute the following scaling roadmap:

### 1. Offload Rate Limiting to API Gateway
Instead of rate limiting requests at the application level (which consumes Python CPU cycles and connection pool handles), we would offload rate limiting to a dedicated reverse-proxy or API Gateway layer (like Kong, Nginx, or Cloudflare).

### 2. Database Read Replicas
Since task and project management systems typically experience read-heavy traffic (e.g. users fetching boards vs creating tasks), we would configure a PostgreSQL primary cluster for writes and route all `GET` read queries to multiple read-only database replicas.

### 3. Caching via Redis
We would implement a caching layer using Redis for frequently queried resources (like list views of projects and active task collections) with cache invalidation policies (TTL or event-driven invalidation on project updates) to bypass database lookups entirely.

### 4. Async Task Processing
Offload heavy or non-blocking processes (such as sending email notifications, generating project PDF reports, or cleaning deleted project tasks) to asynchronous queue workers (using Celery or ARQ) to ensure HTTP responses are returned immediately without blocking the event loop.

---

## 🧪 Running Tests & CI

Unit tests are executed in isolation using an in-memory SQLite database.

```bash
# Execute local test suite with coverage
pytest --cov=app --cov-report=term-missing
```

Currently, the codebase maintains **99% test coverage**. The continuous integration pipeline strictly enforces a **95% coverage threshold**.
