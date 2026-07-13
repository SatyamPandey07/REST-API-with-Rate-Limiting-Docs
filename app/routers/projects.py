from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app.limiter import limiter

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.post("/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
def create_project(
    request: Request,
    project: schemas.ProjectCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new project.

    Initializes a project scoped exclusively to the authenticated user.

    - **project**: Name and optional description of the project.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model extracted from JWT claims.

    **Possible HTTP status returns:**
    - **201 Created**: Project created successfully.
    - **400 Bad Request**: If a project with the same name already exists for the active user.
    - **401 Unauthorized**: If request is unauthenticated or the token is expired/invalid.
    - **429 Too Many Requests**: If client requests exceed the write rate limit of 30 requests/minute.
    """
    # Check duplicate project name within the scope of the current user
    db_project = db.query(models.Project).filter(
        models.Project.name == project.name,
        models.Project.user_id == current_user.id
    ).first()
    if db_project:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists"
        )
    new_project = models.Project(
        name=project.name,
        description=project.description,
        user_id=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=schemas.PaginatedProjectResponse)
@limiter.limit("100/minute")
def get_projects(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve all projects (paginated).

    Returns a list of projects owned by the authenticated user enveloped in pagination metadata.

    - **page**: Page index (must be >= 1).
    - **page_size**: Record counts per page (must be between 1 and 100).
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **200 OK**: List of projects and metadata retrieved. Page requests beyond actual counts return empty data `[]`.
    - **401 Unauthorized**: If request is unauthenticated or has an invalid token.
    - **422 Unprocessable Entity**: If bounds parameters (`page <= 0`, `page_size <= 0`, or `page_size > 100`) fail validation checks.
    - **429 Too Many Requests**: If client requests exceed the read rate limit of 100 requests/minute.
    """
    query = db.query(models.Project).filter(models.Project.user_id == current_user.id)
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

@router.get("/{project_id}", response_model=schemas.ProjectDetailResponse)
@limiter.limit("100/minute")
def get_project(
    request: Request,
    project_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve detailed project information.

    Returns the specified project's properties and includes the associated nested task array.

    - **project_id**: Database identifier of the target project.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **200 OK**: Project details retrieved.
    - **401 Unauthorized**: If request token is missing, expired, or invalid.
    - **404 Not Found**: If the project does not exist, or belongs to another user (to avoid leaking resource existence).
    - **429 Too Many Requests**: If client requests exceed 100 requests/minute.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return project

@router.put("/{project_id}", response_model=schemas.ProjectResponse)
@limiter.limit("30/minute")
def update_project(
    request: Request,
    project_id: int, 
    project_update: schemas.ProjectUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Update project details.

    Modifies the project's title and description. Validates name uniqueness if modified.

    - **project_id**: Database identifier of the target project.
    - **project_update**: Object containing properties to modify.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **200 OK**: Project details modified and returned.
    - **400 Bad Request**: If changing the name conflicts with an existing project of the active user.
    - **401 Unauthorized**: If request token is missing, expired, or invalid.
    - **404 Not Found**: If the project does not exist, or belongs to another user.
    - **429 Too Many Requests**: If client requests exceed the write rate limit of 30 requests/minute.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project_update.name is not None:
        if project_update.name != project.name:
            existing = db.query(models.Project).filter(
                models.Project.name == project_update.name,
                models.Project.user_id == current_user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project with this name already exists"
                )
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description

    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def delete_project(
    request: Request,
    project_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a project.

    Deletes the project and cascades deletions to all associated Tasks.

    - **project_id**: Database identifier of the target project.
    - **db**: Database session dependency.
    - **current_user**: Authenticated User model.

    **Possible HTTP status returns:**
    - **204 No Content**: Deletion succeeded.
    - **401 Unauthorized**: If request token is missing, expired, or invalid.
    - **404 Not Found**: If the project does not exist, or belongs to another user.
    - **429 Too Many Requests**: If client requests exceed the write rate limit of 30 requests/minute.
    """
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    db.delete(project)
    db.commit()
    return None
