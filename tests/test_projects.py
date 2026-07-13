from fastapi import status
from app import models, security

def test_create_project(auth_client):
    response = auth_client.post("/projects/", json={"name": "Alpha Project", "description": "Description A"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Alpha Project"
    assert "id" in data

def test_create_project_unauthorized(client):
    response = client.post("/projects/", json={"name": "Alpha Project"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_project_validation_error(auth_client):
    response = auth_client.post("/projects/", json={"description": "Invalid"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_duplicate_project_name(auth_client):
    auth_client.post("/projects/", json={"name": "Beta Project"})
    response = auth_client.post("/projects/", json={"name": "Beta Project"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Project with this name already exists"

def test_get_projects(auth_client):
    auth_client.post("/projects/", json={"name": "P1"})
    auth_client.post("/projects/", json={"name": "P2"})
    response = auth_client.get("/projects/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_get_project_by_id(auth_client):
    res = auth_client.post("/projects/", json={"name": "P3"})
    project_id = res.json()["id"]

    response = auth_client.get(f"/projects/{project_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "P3"

def test_get_project_not_found(auth_client):
    response = auth_client.get("/projects/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project not found"

def test_update_project(auth_client):
    res = auth_client.post("/projects/", json={"name": "P4", "description": "Old Desc"})
    project_id = res.json()["id"]

    response = auth_client.put(f"/projects/{project_id}", json={"name": "P4 Updated", "description": "New Desc"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "P4 Updated"
    assert data["description"] == "New Desc"

def test_update_project_not_found(auth_client):
    response = auth_client.put("/projects/999", json={"name": "Ghost"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_project(auth_client):
    res = auth_client.post("/projects/", json={"name": "P5"})
    project_id = res.json()["id"]

    response = auth_client.delete(f"/projects/{project_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_res = auth_client.get(f"/projects/{project_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

def test_project_isolation(auth_client, db):
    # Create another user in DB
    other_user = models.User(email="other@example.com", hashed_password=security.hash_password("pass"))
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    # Create a project owned by other_user
    other_project = models.Project(name="Other Project", user_id=other_user.id)
    db.add(other_project)
    db.commit()
    db.refresh(other_project)

    # Attempt to retrieve other_user's project using auth_client (logged in as test@example.com)
    # Expected: 404 Not Found to prevent leaking presence
    response = auth_client.get(f"/projects/{other_project.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
