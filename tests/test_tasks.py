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
    # Missing project_id
    response = auth_client.post("/tasks/", json={"title": "Task C"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_tasks_paginated(auth_client):
    p_res = auth_client.post("/projects/", json={"name": "Project Y"})
    project_id = p_res.json()["id"]
    auth_client.post("/tasks/", json={"title": "T1", "project_id": project_id})
    auth_client.post("/tasks/", json={"title": "T2", "project_id": project_id})
    auth_client.post("/tasks/", json={"title": "T3", "project_id": project_id})

    # Fetch page 1 size 2
    response = auth_client.get("/tasks/?page=1&page_size=2")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert "data" in res_data
    assert "pagination" in res_data
    assert len(res_data["data"]) == 2
    
    pagination = res_data["pagination"]
    assert pagination["total_count"] == 3
    assert pagination["page"] == 1
    assert pagination["page_size"] == 2
    assert pagination["total_pages"] == 2

def test_get_tasks_filtering(auth_client):
    p_res1 = auth_client.post("/projects/", json={"name": "Project P1"})
    project_id1 = p_res1.json()["id"]
    p_res2 = auth_client.post("/projects/", json={"name": "Project P2"})
    project_id2 = p_res2.json()["id"]

    # Create 3 tasks with different statuses and project_ids
    auth_client.post("/tasks/", json={"title": "Task 1", "status": "Todo", "project_id": project_id1})
    auth_client.post("/tasks/", json={"title": "Task 2", "status": "InProgress", "project_id": project_id1})
    auth_client.post("/tasks/", json={"title": "Task 3", "status": "Todo", "project_id": project_id2})

    # Filter by status "Todo"
    res_status = auth_client.get("/tasks/?status=Todo")
    assert res_status.status_code == status.HTTP_200_OK
    assert len(res_status.json()["data"]) == 2

    # Filter by project_id1
    res_project = auth_client.get(f"/tasks/?project_id={project_id1}")
    assert res_project.status_code == status.HTTP_200_OK
    assert len(res_project.json()["data"]) == 2

    # Filter by status "Todo" AND project_id1
    res_both = auth_client.get(f"/tasks/?status=Todo&project_id={project_id1}")
    assert res_both.status_code == status.HTTP_200_OK
    assert len(res_both.json()["data"]) == 1
    assert res_both.json()["data"][0]["title"] == "Task 1"

def test_get_tasks_page_out_of_bounds(auth_client):
    p_res = auth_client.post("/projects/", json={"name": "Project Y"})
    project_id = p_res.json()["id"]
    auth_client.post("/tasks/", json={"title": "T1", "project_id": project_id})

    # Page 10 out of bounds
    response = auth_client.get("/tasks/?page=10&page_size=2")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"] == []
    assert response.json()["pagination"]["total_count"] == 1
    assert response.json()["pagination"]["total_pages"] == 1

def test_get_tasks_validation_errors(auth_client):
    response = auth_client.get("/tasks/?page=0&page_size=20")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = auth_client.get("/tasks/?page=1&page_size=-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = auth_client.get("/tasks/?page=1&page_size=101")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

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

    response = auth_client.get(f"/tasks/{other_task.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
