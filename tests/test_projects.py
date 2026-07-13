from fastapi import status

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

def test_get_projects_paginated(auth_client):
    auth_client.post("/projects/", json={"name": "P1"})
    auth_client.post("/projects/", json={"name": "P2"})
    auth_client.post("/projects/", json={"name": "P3"})

    # Fetch page 1 with size 2
    response = auth_client.get("/projects/?page=1&page_size=2")
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

def test_get_projects_page_out_of_bounds(auth_client):
    auth_client.post("/projects/", json={"name": "P1"})
    
    # Request page 5
    response = auth_client.get("/projects/?page=5&page_size=2")
    assert response.status_code == status.HTTP_200_OK
    res_data = response.json()
    assert res_data["data"] == []
    assert res_data["pagination"]["total_count"] == 1
    assert res_data["pagination"]["total_pages"] == 1

def test_get_projects_validation_errors(auth_client):
    # Invalid page size (0)
    response = auth_client.get("/projects/?page=1&page_size=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid negative page
    response = auth_client.get("/projects/?page=-1&page_size=10")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Page size too large (> 100)
    response = auth_client.get("/projects/?page=1&page_size=101")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

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
