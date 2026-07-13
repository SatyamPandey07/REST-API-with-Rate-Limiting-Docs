from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
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

@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Task).filter(models.Task.user_id == current_user.id).all()

@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
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
def update_task(
    task_id: int, 
    task_update: schemas.TaskUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
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
def delete_task(
    task_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
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
