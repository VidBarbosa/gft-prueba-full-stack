# Arquitectura

```mermaid
flowchart LR
  UA[Usuario/API Client] -->|HTTPS| GW[FastAPI / Uvicorn]
  subgraph App
    GW --> MW[Middlewares\nSecurity/CORS/GZip/AccessLog]
    MW --> R[Routers /api/v1/*]
    R --> S[Services (Domain)]
    S --> Repo[(Repositories)]
    R --> Auth[Auth (JWT Bearer)]
    R --> RL[Rate Limiter (SlowAPI)]
    MW --> Log[Structlog JSON]
  end
  Repo --> MDB[(MongoDB)]
  RL --> REDIS[(Redis)]
  Log --> AUDIT[(MongoDB audit_logs)]
```
**Puntos clave**
- **JWT Bearer** Compatible con Swagger/Postman.
- **SlowAPI + Redis** para rate limiting por endpoint.
- **Audit trail** en `audit_logs`.
- **Logs JSON** a stdout para observabilidad.
- Seeds, backups y restauración programable.
