from fastapi import status

def test_create_project(client):
    response = client.post("/projects/", json={"name": "Alpha Project", "description": "Description A"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Alpha Project"
    assert "id" in data

def test_create_project_validation_error(client):
    # Missing required 'name' field
    response = client.post("/projects/", json={"description": "Invalid"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_create_duplicate_project_name(client):
    client.post("/projects/", json={"name": "Beta Project"})
    response = client.post("/projects/", json={"name": "Beta Project"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Project with this name already exists"

def test_get_projects(client):
    client.post("/projects/", json={"name": "P1"})
    client.post("/projects/", json={"name": "P2"})
    response = client.get("/projects/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_get_project_by_id(client):
    res = client.post("/projects/", json={"name": "P3"})
    project_id = res.json()["id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "P3"

def test_get_project_not_found(client):
    response = client.get("/projects/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Project not found"

def test_update_project(client):
    res = client.post("/projects/", json={"name": "P4", "description": "Old Desc"})
    project_id = res.json()["id"]

    response = client.put(f"/projects/{project_id}", json={"name": "P4 Updated", "description": "New Desc"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "P4 Updated"
    assert data["description"] == "New Desc"

def test_update_project_not_found(client):
    response = client.put("/projects/999", json={"name": "Ghost"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_project(client):
    res = client.post("/projects/", json={"name": "P5"})
    project_id = res.json()["id"]

    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify not found
    get_res = client.get(f"/projects/{project_id}")
    assert get_res.status_code == status.HTTP_404_NOT_FOUND
