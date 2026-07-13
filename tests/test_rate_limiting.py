from fastapi import status
from app.limiter import limiter

def test_rate_limiting_auth_endpoint(client):
    # Reset the rate limiter storage to start with a clean slate
    limiter.reset()
    
    # The registration route is limited to 5/minute
    # Let's hit it 5 times.
    for i in range(5):
        response = client.post(
            "/auth/register",
            json={"email": f"rate_user_{i}@example.com", "password": "password123"}
        )
        # It should succeed or fail validation, but NOT return 429
        assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS

    # The 6th hit must trigger 429 Too Many Requests
    response = client.post(
        "/auth/register",
        json={"email": "rate_user_5@example.com", "password": "password123"}
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "detail" in response.json()
    assert "Rate limit exceeded" in response.json()["detail"]

    # Verify Retry-After header is present
    assert "Retry-After" in response.headers
    retry_after = int(response.headers["Retry-After"])
    assert retry_after > 0

    # Reset the rate limiter storage to simulate window expiration
    limiter.reset()

    # The next hit should now go through (not return 429)
    response = client.post(
        "/auth/register",
        json={"email": "rate_user_5@example.com", "password": "password123"}
    )
    assert response.status_code != status.HTTP_429_TOO_MANY_REQUESTS
