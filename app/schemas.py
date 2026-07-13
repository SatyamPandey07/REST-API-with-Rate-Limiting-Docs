from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Todo"

class TaskCreate(TaskBase):
    project_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    project_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    project_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Nested Response Schemas for Detailed Views (Optional but good practice) ---
class ProjectDetailResponse(ProjectResponse):
    tasks: List[TaskResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- User & Token Schemas ---
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


# --- Pagination Schemas ---
class PaginationMetadata(BaseModel):
    total_count: int
    page: int
    page_size: int
    total_pages: int

class PaginatedProjectResponse(BaseModel):
    data: List[ProjectResponse]
    pagination: PaginationMetadata

class PaginatedTaskResponse(BaseModel):
    data: List[TaskResponse]
    pagination: PaginationMetadata
