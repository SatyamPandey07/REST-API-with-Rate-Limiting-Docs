from fastapi import status
from app.limiter import limiter

def test_rate_limiting_auth_endpoint(client):
    limiter.reset()

    for i in range(5):
        response = client.post(
            "/api/v1/auth/register",
            json={"email": f"rate_user_{i}@example.com", "password": "password123"}
        )
        assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "rate_user_5@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "detail" in response.json()
    assert "Rate limit exceeded" in response.json()["detail"]

    assert "Retry-After" in response.headers
    retry_after = int(response.headers["Retry-After"])
    assert retry_after > 0

    limiter.reset()

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "rate_user_5@example.com", "password": "password123"}
    )
    assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
