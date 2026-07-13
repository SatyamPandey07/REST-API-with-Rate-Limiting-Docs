from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.limiter import limiter

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_task(
    request: Request,
    task: schemas.TaskCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new task.

    Creates a task item under the specified project. The parent project must exist and belong to the active authenticated user.

    - **task**: Title, optional description, project ID target, and optional status (default 'Todo').
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **201 Created**: Task created successfully.
    - **400 Bad Request**: If the target `project_id` does not exist or belongs to another user.
    - **401 Unauthorized**: If request token is missing, expired, or invalid.
    - **429 Too Many Requests**: If requests exceed the write rate limit of 30 requests/minute.
    """
    # Verify project exists and belongs to current_user
    project = db.query(models.Project).filter(
        models.Project.id == task.project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not found"
        )
    new_task = models.Task(
        title=task.title,
        description=task.description,
        status=task.status,
        project_id=task.project_id,
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=schemas.PaginatedTaskResponse)
@limiter.limit("100/minute")
def get_tasks(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve tasks (paginated and filtered).

    Returns a paginated list of tasks owned by the authenticated user. Optionally filters by task status or project ID.

    - **page**: Page index (must be >= 1).
    - **page_size**: Record counts per page (must be between 1 and 100).
    - **status**: Filter by status string (e.g. 'Todo', 'InProgress', 'Completed').
    - **project_id**: Filter by target project database ID.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **200 OK**: List of tasks and metadata retrieved. Page requests beyond actual counts return empty data `[]`.
    - **401 Unauthorized**: If request is unauthenticated or has an invalid token.
    - **422 Unprocessable Entity**: If parameters (`page <= 0`, `page_size <= 0`, or `page_size > 100`) fail bounds validation.
    - **429 Too Many Requests**: If client requests exceed the read rate limit of 100 requests/minute.
    """
    query = db.query(models.Task).filter(models.Task.user_id == current_user.id)
    
    if status is not None:
        query = query.filter(models.Task.status == status)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)
        
    total_count = query.count()
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    offset = (page - 1) * page_size
    data = query.offset(offset).limit(page_size).all()
    
    return {
        "data": data,
        "pagination": {
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    }

@router.get("/{task_id}", response_model=schemas.TaskResponse)
@limiter.limit("100/minute")
def get_task(
    request: Request,
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve task details.

    Returns the specified task's properties. The task must belong to the active user.

    - **task_id**: Database identifier of the target task.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **200 OK**: Task details retrieved.
    - **401 Unauthorized**: If request token is missing, expired, or invalid.
    - **404 Not Found**: If the task does not exist or belongs to another user.
    - **429 Too Many Requests**: If client requests exceed 100 requests/minute.
    """
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=schemas.TaskResponse)
@limiter.limit("30/minute")
def update_task(
    request: Request,
    task_id: int, 
    task_update: schemas.TaskUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Update task details.

    Modifies properties (title, description, status). If `project_id` is updated, verifies the new project belongs to the user.

    - **task_id**: Database identifier of the target task.
    - **task_update**: Object containing properties to modify.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **200 OK**: Task details modified and returned.
    - **400 Bad Request**: If the new `project_id` does not exist or is owned by another user.
    - **401 Unauthorized**: If request token is missing, expired, or invalid.
    - **404 Not Found**: If the task does not exist or is owned by another user.
    - **429 Too Many Requests**: If client requests exceed the write rate limit of 30 requests/minute.
    """
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify project exists and belongs to current_user if updating project_id
    if task_update.project_id is not None:
        project = db.query(models.Project).filter(
            models.Project.id == task_update.project_id,
            models.Project.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project not found"
            )
        task.project_id = task_update.project_id

    # Update other fields
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status

    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def delete_task(
    request: Request,
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a task.

    Deletes the task from the database.

    - **task_id**: Database identifier of the target task.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **204 No Content**: Deletion succeeded.
    - **401 Unauthorized**: If request token is missing, expired, or invalid.
    - **404 Not Found**: If the task does not exist or is owned by another user.
    - **429 Too Many Requests**: If client requests exceed the write rate limit of 30 requests/minute.
    """
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    db.delete(task)
    db.commit()
    return None
