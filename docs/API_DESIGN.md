# TaskFlow API: API Design Document

This document outlines the architectural and engineering design philosophies governing the **TaskFlow API**. It explains key decisions regarding REST endpoints, versioning systems, security controls, and error conventions.

---

## 🔗 REST Endpoint Conventions

TaskFlow API follows standard REST (Representational State Transfer) conventions to provide predictable and logical routing for developers:

### 1. HTTP Methods
- **`GET`**: Retrieve resources (read-only). List views support pagination (`page`, `page_size`) and dynamic query filters.
- **`POST`**: Create new resources. Returns `201 Created` on success.
- **`PUT`**: Modify existing resources. Performs updates on individual projects or tasks.
- **`DELETE`**: Remove resources. Returns `204 No Content` on successful execution.

### 2. Resource Hierarchy
Tasks are scoped under projects conceptually. In the URL mapping, flat paths are utilized (`/tasks` and `/projects`) to keep endpoints short, but validation ensures a task can only be created or updated if its associated `project_id` exists and belongs to the authenticated user.

---

## 🚫 Error Handling Strategy

To ensure client integrations are straightforward and uniform, the API returns a consistent error response envelope format for all client-side and server-side errors:

### Error Envelope Schema
```json
{
  "detail": "Error explanation string details here."
}
```

### Common HTTP Status Codes
- **`400 Bad Request`**: Business logic constraints failed (e.g. duplicating a project name, or assigning a task to a project owned by another user).
- **`401 Unauthorized`**: Authentication is missing, has expired, or the JWT signature is invalid.
- **`404 Not Found`**: Returned if a resource does not exist **or** if it belongs to another user. This prevents resource enumeration attacks and keeps resource existence confidential.
- **`422 Unprocessable Entity`**: Client sent values that failed validation bounds (e.g. negative pages, page_size too large, or missing body fields).
- **`429 Too Many Requests`**: Client requests exceeded rate limits.

---

## 🌐 API Versioning Strategy

TaskFlow API uses **URL-based versioning** (prefixed with `/api/v1/`) rather than header-based or parameter-based versioning.

### Rationale
- **Discoverability**: Easy for developer onboarding; paths are explicit in documentation, cURL examples, and browsers.
- **CDN Caching**: Versioned URLs prevent caching pollution across API upgrades since paths are physically distinct, avoiding the need for complex `Vary: Accept-Version` proxy configurations.

### Deprecation & Sunset Support
When migrating endpoints, version retirement uses standardized HTTP response headers:
- `X-API-Deprecated: true`: Injected into responses once the version is marked for deprecation.
- `Sunset: <HTTP-date>`: Declares the official retirement date for the deprecated version, giving clients time to migrate.

---

## 🛡️ Rate Limiting Architecture

The API limits request volumes using `slowapi` backed by a shared Redis key-value store. 

### Limit Tiers
- **Authentication (`5/minute`)**: Strict limits on `/auth/register` and `/auth/login` scoped by client IP address to prevent dictionary/brute-force password guessing.
- **Writes (`30/minute`)**: Moderate limits on `POST`, `PUT`, `DELETE` scoped to the authenticated user's email.
- **Reads (`100/minute`)**: Generous limits on list and detail queries scoped to the authenticated user's email.

### Key Resolution Rules
1. If the request has a valid JWT Authorization Bearer header, the key is resolved to `user:<email>` (preventing users from bypassing limits by switching IPs).
2. For unauthenticated requests (like registration or invalid tokens), the key falls back to `ip:<get_remote_address>`.
