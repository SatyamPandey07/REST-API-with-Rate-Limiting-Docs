from fastapi import status
from app import models, security

def test_create_task(auth_client):
    # Create project first
    p_res = auth_client.post("/projects/", json={"name": "Project X"})
    project_id = p_res.json()["id"]

    response = auth_client.post("/tasks/", json={"title": "Task A", "description": "Desc A", "project_id": project_id})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Task A"
    assert data["project_id"] == project_id

def test_create_task_unauthorized(client):
    response = client.post("/tasks/", json={"title": "Task B", "project_id": 1})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_task_invalid_project(auth_client):
    response = auth_client.post("/tasks/", json={"title": "Task B", "project_id": 999})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Project not found"

def test_create_task_validation_error(auth_client):
    response = auth_client.post("/tasks/", json={"title": "Task C"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_tasks(auth_client):
    p_res = auth_client.post("/projects/", json={"name": "Project Y"})
    project_id = p_res.json()["id"]
    auth_client.post("/tasks/", json={"title": "T1", "project_id": project_id})
    auth_client.post("/tasks/", json={"title": "T2", "project_id": project_id})

    response = auth_client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2

def test_get_task_by_id(auth_client):
    p_res = auth_client.post("/projects/", json={"name": "Project Z"})
    project_id = p_res.json()["id"]
    t_res = auth_client.post("/tasks/", json={"title": "T3", "project_id": project_id})
    task_id = t_res.json()["id"]

    response = auth_client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "T3"

def test_get_task_not_found(auth_client):
    response = auth_client.get("/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_task(auth_client):
    p_res = auth_client.post("/projects/", json={"name": "Project W"})
    project_id = p_res.json()["id"]
    t_res = auth_client.post("/tasks/", json={"title": "T4", "project_id": project_id})
    task_id = t_res.json()["id"]

    response = auth_client.put(f"/tasks/{task_id}", json={"title": "T4 Updated", "status": "Completed"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "T4 Updated"
    assert data["status"] == "Completed"

def test_delete_task(auth_client):
    p_res = auth_client.post("/projects/", json={"name": "Project V"})
    project_id = p_res.json()["id"]
    t_res = auth_client.post("/tasks/", json={"title": "T5", "project_id": project_id})
    task_id = t_res.json()["id"]

    response = auth_client.delete(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_res = auth_client.get(f"/tasks/{task_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

def test_task_isolation(auth_client, db):
    # Create another user in DB
    other_user = models.User(email="other@example.com", hashed_password=security.hash_password("pass"))
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    # Create a project and task owned by other_user
    other_project = models.Project(name="Other Project", user_id=other_user.id)
    db.add(other_project)
    db.commit()
    db.refresh(other_project)

    other_task = models.Task(title="Other Task", project_id=other_project.id, user_id=other_user.id)
    db.add(other_task)
    db.commit()
    db.refresh(other_task)

    # Attempt to retrieve other_user's task using auth_client (logged in as test@example.com)
    # Expected: 404 Not Found to prevent leaking presence
    response = auth_client.get(f"/tasks/{other_task.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
