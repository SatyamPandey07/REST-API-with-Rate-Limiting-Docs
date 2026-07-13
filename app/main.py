from fastapi import FastAPI
from app.routers import projects, tasks

app = FastAPI(
    title="TaskFlow API",
    description="A task and project management REST API built with FastAPI.",
    version="1.0.0"
)

# Register routers
app.include_router(projects.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "api": "TaskFlow API",
        "version": "1.0.0"
    }
