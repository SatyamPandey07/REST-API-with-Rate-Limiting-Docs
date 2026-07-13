from fastapi import FastAPI, APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.routers import projects, tasks, auth
from app.database import get_db
from app.config import settings
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter, custom_rate_limit_exceeded_handler

app = FastAPI(
    title="TaskFlow API",
    description="A task and project management REST API built with FastAPI.",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# Centralized versioned router
v1_router = APIRouter(prefix="/api/v1")

# Uptime monitoring health endpoint (unauthenticated)
@v1_router.get("/health", tags=["health"])
@limiter.limit("100/minute")
def health_check(request: Request, db: Session = Depends(get_db)):
    try:
        # Run a simple query to verify database connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    return {
        "status": "healthy",
        "database": db_status
    }

# Register routers under /api/v1 prefix
v1_router.include_router(auth.router)
v1_router.include_router(projects.router)
v1_router.include_router(tasks.router)

app.include_router(v1_router)

# Deprecation and Sunset headers HTTP middleware
@app.middleware("http")
async def add_deprecation_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/v1"):
        if settings.API_V1_DEPRECATED:
            response.headers["X-API-Deprecated"] = "true"
            if settings.API_V1_SUNSET:
                response.headers["Sunset"] = settings.API_V1_SUNSET
        else:
            response.headers["X-API-Deprecated"] = "false"
    return response
