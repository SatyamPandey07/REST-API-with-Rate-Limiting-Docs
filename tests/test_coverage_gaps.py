import pytest
from unittest.mock import MagicMock
from jose import jwt
from datetime import timedelta
from fastapi import status
from app.config import settings
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

# 1. app/security.py coverage tests
def test_verify_password_corrupted_hash():
    # Calling verify_password with a non-bcrypt corrupted hash will raise an exception in bcrypt,
    # catching it and returning False (covering lines 18-19 of security.py)
    assert verify_password("plain", "corruptedhash") is False

def test_create_access_token_custom_expires():
    # Pass a custom timedelta to create_access_token (covering line 24 of security.py)
    expires = timedelta(minutes=5)
    token = create_access_token(data={"sub": "custom@example.com"}, expires_delta=expires)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "custom@example.com"
    assert "exp" in payload


# 2. app/dependencies.py coverage tests
def test_get_current_user_missing_sub(db):
    # Create a token signed correctly but with sub claim missing (covering line 21 of dependencies.py)
    token = jwt.encode({"not_sub": "value"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(Exception) as exc_info:
        get_current_user(token=token, db=db)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Could not validate credentials"

def test_get_current_user_invalid_signature(db):
    # Create a token signed with an invalid key to trigger JWTError (covering lines 23-24 of dependencies.py)
    token = jwt.encode({"sub": "test@example.com"}, "wrong_key", algorithm=settings.ALGORITHM)
    with pytest.raises(Exception) as exc_info:
        get_current_user(token=token, db=db)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user_nonexistent_user(db):
    # Token has sub claim with email that is not in database (covering line 28 of dependencies.py)
    token = jwt.encode({"sub": "nonexistent@example.com"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(Exception) as exc_info:
        get_current_user(token=token, db=db)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


# 3. app/limiter.py coverage tests
def test_rate_limit_key_func_invalid_token_exception(client):
    # Make request with an invalid Bearer token format to trigger JWT decode exception inside
    # rate_limit_key_func, verifying it falls back to IP address (covering lines 18-19 of limiter.py)
    headers = {"Authorization": "Bearer invalid_token_format_fails_decode"}
    response = client.get("/api/v1/health", headers=headers)
    assert response.status_code == status.HTTP_200_OK


# 4. app/main.py coverage tests
def test_health_check_database_unhealthy_exception(client, monkeypatch):
    # Mock db.execute to raise an Exception to cover database unhealthy path (covering lines 41-42 of main.py)
    def mock_execute(*args, **kwargs):
        raise Exception("Database connection failure simulation")
        
    # We will override db dependency temporarily or patch sessionLocal. By patching
    # main's db session connectivity we can trigger this cleanly.
    from sqlalchemy.orm import Session
    monkeypatch.setattr(Session, "execute", mock_execute)
    
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["database"] == "unhealthy"


# 5. app/routers/projects.py coverage tests
def test_update_project_duplicate_name(auth_client):
    # Create two projects
    auth_client.post("/api/v1/projects/", json={"name": "Project A"})
    res2 = auth_client.post("/api/v1/projects/", json={"name": "Project B"})
    project_b_id = res2.json()["id"]
    
    # Try to rename Project B to Project A (covering line 176 of projects.py)
    response = auth_client.put(f"/api/v1/projects/{project_b_id}", json={"name": "Project A"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Project with this name already exists"

def test_delete_project_not_found(auth_client):
    # Delete a non-existent project (covering line 216 of projects.py)
    response = auth_client.delete("/api/v1/projects/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 6. app/routers/tasks.py coverage tests
def test_update_task_not_found(auth_client):
    # Update a non-existent task (covering line 175 of tasks.py)
    response = auth_client.put("/api/v1/tasks/9999", json={"title": "Ghost"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_task_description_and_project_migration(auth_client):
    # Create two projects
    p1 = auth_client.post("/api/v1/projects/", json={"name": "Proj 1"})
    p2 = auth_client.post("/api/v1/projects/", json={"name": "Proj 2"})
    p1_id = p1.json()["id"]
    p2_id = p2.json()["id"]
    
    # Create task under Project 1
    t = auth_client.post("/api/v1/tasks/", json={"title": "Task 1", "project_id": p1_id})
    t_id = t.json()["id"]
    
    # Update description and change task's project to Project 2 (covering line 197 and line 191 of tasks.py)
    response = auth_client.put(f"/api/v1/tasks/{t_id}", json={
        "description": "Updated Task Description",
        "project_id": p2_id
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == "Updated Task Description"
    assert data["project_id"] == p2_id

def test_update_task_invalid_project_id(auth_client):
    p1 = auth_client.post("/api/v1/projects/", json={"name": "Proj X"})
    p1_id = p1.json()["id"]
    t = auth_client.post("/api/v1/tasks/", json={"title": "Task X", "project_id": p1_id})
    t_id = t.json()["id"]
    
    # Attempt to transfer task to non-existent project (covering lines 186-190 of tasks.py)
    response = auth_client.put(f"/api/v1/tasks/{t_id}", json={"project_id": 9999})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Project not found"

def test_delete_task_not_found(auth_client):
    # Delete a non-existent task (covering line 233 of tasks.py)
    response = auth_client.delete("/api/v1/tasks/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
