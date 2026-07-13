from fastapi import Request, Response
from fastapi.responses import JSONResponse
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings

def rate_limit_key_func(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email = payload.get("sub")
            if email:
                return f"user:{email}"
        except Exception:
            pass
    return f"ip:{get_remote_address(request)}"

storage_uri = settings.REDIS_URL if settings.REDIS_URL else "memory://"
limiter = Limiter(key_func=rate_limit_key_func, storage_uri=storage_uri)

def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    retry_after = getattr(exc, "retry_after", 60)
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )
    response.headers["Retry-After"] = str(retry_after)
    return response
