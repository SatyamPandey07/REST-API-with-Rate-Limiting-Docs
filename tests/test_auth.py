from fastapi import status

def test_register_user(client):
    response = client.post("/auth/register", json={"email": "newuser@example.com", "password": "securepassword"})
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data

def test_register_user_duplicate_email(client):
    client.post("/auth/register", json={"email": "duplicate@example.com", "password": "pass"})
    response = client.post("/auth/register", json={"email": "duplicate@example.com", "password": "pass"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Email already registered"

def test_login_user_success(client):
    # Register user first
    client.post("/auth/register", json={"email": "loginuser@example.com", "password": "mypassword"})
    
    # Login via OAuth2 Form URL-encoded data
    response = client.post("/auth/login", data={"username": "loginuser@example.com", "password": "mypassword"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_invalid_credentials(client):
    client.post("/auth/register", json={"email": "loginuser2@example.com", "password": "mypassword"})
    
    # Try logging in with wrong password
    response = client.post("/auth/login", data={"username": "loginuser2@example.com", "password": "wrongpassword"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid credentials"
