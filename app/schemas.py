from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str = Field(
        ...,
        description="The unique name of the project. Scoped per-user.",
        examples=["Acme Website Redesign"]
    )
    description: Optional[str] = Field(
        None,
        description="A detailed description of the project scope and targets.",
        examples=["Redesign corporate homepage with modern aesthetics and responsive layout."]
    )

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        description="New unique name of the project.",
        examples=["Acme Website Redesign v2"]
    )
    description: Optional[str] = Field(
        None,
        description="Updated project description details.",
        examples=["Updated scope to include mobile applications section."]
    )

class ProjectResponse(ProjectBase):
    id: int = Field(
        ...,
        description="Unique database identifier of the project.",
        examples=[12]
    )
    user_id: int = Field(
        ...,
        description="Database identifier of the user who owns this project.",
        examples=[3]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp indicating when the project was created."
    )

    model_config = ConfigDict(from_attributes=True)


# --- Task Schemas ---
class TaskBase(BaseModel):
    title: str = Field(
        ...,
        description="Title representing the task checklist item.",
        examples=["Implement login logic"]
    )
    description: Optional[str] = Field(
        None,
        description="In-depth details about task requirements.",
        examples=["Setup oauth2 password login and return access JWT tokens."]
    )
    status: str = Field(
        "Todo",
        description="Active status of the task. Typical values: 'Todo', 'InProgress', 'Completed'.",
        examples=["InProgress"]
    )

class TaskCreate(TaskBase):
    project_id: int = Field(
        ...,
        description="Database identifier of the project this task belongs to.",
        examples=[12]
    )

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        description="New title for the task.",
        examples=["Refactor login logic"]
    )
    description: Optional[str] = Field(
        None,
        description="Updated requirements description.",
        examples=["Implement direct bcrypt checkpw instead of passlib context."]
    )
    status: Optional[str] = Field(
        None,
        description="Updated task status.",
        examples=["Completed"]
    )
    project_id: Optional[int] = Field(
        None,
        description="Transfer the task to a different project.",
        examples=[14]
    )

class TaskResponse(TaskBase):
    id: int = Field(
        ...,
        description="Unique database identifier of the task.",
        examples=[45]
    )
    project_id: int = Field(
        ...,
        description="Database identifier of the project this task belongs to.",
        examples=[12]
    )
    user_id: int = Field(
        ...,
        description="Database identifier of the user who owns this task.",
        examples=[3]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp indicating when the task was created."
    )

    model_config = ConfigDict(from_attributes=True)


# --- Nested Response Schemas for Detailed Views ---
class ProjectDetailResponse(ProjectResponse):
    tasks: List[TaskResponse] = Field(
        [],
        description="List of tasks associated with this project."
    )

    model_config = ConfigDict(from_attributes=True)


# --- User & Token Schemas ---
class UserCreate(BaseModel):
    email: str = Field(
        ...,
        description="Unique email address for registering/logging in.",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="Secure password. Plaintext is hashed via bcrypt before saving.",
        examples=["securePassword123"]
    )

class UserResponse(BaseModel):
    id: int = Field(
        ...,
        description="Unique database identifier of the user.",
        examples=[3]
    )
    email: str = Field(
        ...,
        description="User email address.",
        examples=["user@example.com"]
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp indicating when the user account was registered."
    )

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="Signed JWT access token for authorization.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        "bearer",
        description="The type of token returned.",
        examples=["bearer"]
    )

class TokenData(BaseModel):
    email: Optional[str] = Field(
        None,
        description="Subject email decoded from the JWT token.",
        examples=["user@example.com"]
    )


# --- Pagination Schemas ---
class PaginationMetadata(BaseModel):
    total_count: int = Field(
        ...,
        description="Total matching records count in database.",
        examples=[23]
    )
    page: int = Field(
        ...,
        description="Current page retrieved.",
        examples=[1]
    )
    page_size: int = Field(
        ...,
        description="Limits on items retrieved per page.",
        examples=[20]
    )
    total_pages: int = Field(
        ...,
        description="Calculated total pages available.",
        examples=[2]
    )

class PaginatedProjectResponse(BaseModel):
    data: List[ProjectResponse] = Field(
        ...,
        description="List of projects matching pagination slice."
    )
    pagination: PaginationMetadata = Field(
        ...,
        description="Pagination metadata details."
    )

class PaginatedTaskResponse(BaseModel):
    data: List[TaskResponse] = Field(
        ...,
        description="List of tasks matching pagination slice."
    )
    pagination: PaginationMetadata = Field(
        ...,
        description="Pagination metadata details."
    )
