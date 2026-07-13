from fastapi import FastAPI
from app.routers import projects, tasks, auth
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter, custom_rate_limit_exceeded_handler

app = FastAPI(
    title="TaskFlow API",
    description="A task and project management REST API built with FastAPI.",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# Register routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "api": "TaskFlow API",
        "version": "1.0.0"
    }
