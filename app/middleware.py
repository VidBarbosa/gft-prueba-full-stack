from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
import uuid
from app.logging import log

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        return response

class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        import time as _t
        start = _t.perf_counter()
        try:
            response = await call_next(request)
        except Exception as e:
            duration = (_t.perf_counter() - start) * 1000
            log.info("access", status=500, duration_ms=round(duration,2), path=request.url.path, method=request.method, error=str(e))
            raise
        duration = (_t.perf_counter() - start) * 1000
        log.info("access", status=response.status_code, duration_ms=round(duration,2), path=request.url.path, method=request.method)
        return response
