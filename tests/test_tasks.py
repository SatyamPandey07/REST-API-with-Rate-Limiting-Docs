from fastapi import status

def test_create_task(client):
    # Create project first
    p_res = client.post("/projects/", json={"name": "Project X"})
    project_id = p_res.json()["id"]

    response = client.post("/tasks/", json={"title": "Task A", "description": "Desc A", "project_id": project_id})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Task A"
    assert data["project_id"] == project_id

def test_create_task_invalid_project(client):
    response = client.post("/tasks/", json={"title": "Task B", "project_id": 999})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Project not found"

def test_create_task_validation_error(client):
    # Missing project_id
    response = client.post("/tasks/", json={"title": "Task C"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_tasks(client):
    p_res = client.post("/projects/", json={"name": "Project Y"})
    project_id = p_res.json()["id"]
    client.post("/tasks/", json={"title": "T1", "project_id": project_id})
    client.post("/tasks/", json={"title": "T2", "project_id": project_id})

    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2

def test_get_task_by_id(client):
    p_res = client.post("/projects/", json={"name": "Project Z"})
    project_id = p_res.json()["id"]
    t_res = client.post("/tasks/", json={"title": "T3", "project_id": project_id})
    task_id = t_res.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "T3"

def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_task(client):
    p_res = client.post("/projects/", json={"name": "Project W"})
    project_id = p_res.json()["id"]
    t_res = client.post("/tasks/", json={"title": "T4", "project_id": project_id})
    task_id = t_res.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"title": "T4 Updated", "status": "Completed"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "T4 Updated"
    assert data["status"] == "Completed"

def test_delete_task(client):
    p_res = client.post("/projects/", json={"name": "Project V"})
    project_id = p_res.json()["id"]
    t_res = client.post("/tasks/", json={"title": "T5", "project_id": project_id})
    task_id = t_res.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND
