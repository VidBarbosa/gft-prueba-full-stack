from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware

from app.config import settings
from app.api_v1 import api_router
from app.utils.exceptions import domain_error_handler, DomainError
from app.middleware import SecurityHeadersMiddleware, AccessLogMiddleware
from app.logging import configure_logging

# SlowAPI (handler global)
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

docs_url = "/docs" if not settings.disable_docs_in_prod or settings.app_env != "prod" else None
redoc_url = "/redoc" if docs_url else None

openapi_tags = [
    {"name": "auth", "description": "Autenticación con JWT **Bearer**. Login devuelve token y datos mínimos de usuario."},
    {"name": "funds", "description": "Consulta de fondos disponibles (monto mínimo y categoría)."},
    {"name": "subscriptions", "description": "Suscripción a fondos (apertura) y cancelación."},
    {"name": "transactions", "description": "Historial del usuario (aperturas y cancelaciones)."},
    {"name": "meta", "description": "Salud y versión del servicio."}
]

configure_logging()
app = FastAPI(title="BTG Pactual – Funds API", version=settings.app_version, docs_url=docs_url, redoc_url=redoc_url, openapi_tags=openapi_tags)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=[h.strip() for h in settings.allowed_hosts.split(",") if h.strip()])
app.add_middleware(GZipMiddleware, minimum_size=512)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AccessLogMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit handler (limiter se aplica vía decorador por endpoint)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Versioned API
app.include_router(api_router, prefix=settings.api_prefix)

# Meta
@app.get("/healthz", tags=["meta"])
async def healthz():
    return {"status": "ok"}

@app.get("/version", tags=["meta"])
async def version():
    return {"version": settings.app_version, "env": settings.app_env, "prefix": settings.api_prefix}

app.add_exception_handler(DomainError, domain_error_handler)
