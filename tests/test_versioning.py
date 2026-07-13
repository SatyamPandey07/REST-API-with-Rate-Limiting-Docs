from fastapi import status
from app.config import settings

def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data

def test_deprecation_headers_default(client):
    response = client.get("/api/v1/health")
    assert response.headers.get("X-API-Deprecated") == "false"
    assert "Sunset" not in response.headers

def test_deprecation_headers_active(client):
    # Enable deprecation
    settings.API_V1_DEPRECATED = True
    settings.API_V1_SUNSET = "Wed, 11 Nov 2026 00:00:00 GMT"
    
    try:
        response = client.get("/api/v1/health")
        assert response.headers.get("X-API-Deprecated") == "true"
        assert response.headers.get("Sunset") == "Wed, 11 Nov 2026 00:00:00 GMT"
    finally:
        # Restore defaults
        settings.API_V1_DEPRECATED = False
        settings.API_V1_SUNSET = ""
