# BTG Pactual – Funds API

**Stack**: FastAPI · MongoDB (Motor) · Redis (SlowAPI) · JWT Bearer · structlog · Pytest · Postman
**Infra opcional**: Docker Compose (mongo/redis/postgres) · Scripts de backup/restore/rollback · Seeds diarios

> **Objetivo**: Plataforma para que clientes gestionen sus **fondos de inversión** sin asesor — **suscripción**, **cancelación**, **historial**, y **notificación** (email/SMS).

---

## ✨ Highlights

* **/api/v1** versionado, **CORS**, **TrustedHost**, **GZip**, y **security headers**.
* **Auth JWT** por **Bearer** (sin cookies): login entrega `access_token` + **datos mínimos de usuario**.
* **Rate limiting** por endpoint con **SlowAPI + Redis** (e.g., register `5/min`, login `30/min`).
* **Auditoría** en Mongo (`audit_logs`): `USER_REGISTERED`, `LOGIN_SUCCESS`, `LOGIN_FAILED`, `LOGOUT`, `SUBSCRIBE`, `CANCEL`.
* **Logs JSON** con `structlog` + **access logs** por request.
* **Seeds / Backup / Restore** (Mongo y Postgres) y **restauración diaria** programable.
* **SQL Parte 2**: schema, tablas, constraints, FKs, seeds ricos, query solicitada, cleanup y rollback.
* **Tests** de negocio (pytest + httpx ASGITransport).
* **Postman** lista para ejecutar con manejo automático del token.

---

## 🗺️ Arquitectura

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

**draw\.io** (editable): `docs/architecture_enterprise.drawio` (incluido).

**Puntos clave**

* **JWT Bearer** (sin cookies) → compatible con Swagger/Postman y servicios externos.
* **SlowAPI + Redis** → rate limit por endpoint y clave de usuario/IP.
* **Audit trail** en `audit_logs` para trazabilidad completa.
* **Logs JSON** → agregables por ELK/Datadog.
* **Parametrización** por `.env` → fácil swap **dev/prod**.

---

## 🚀 Run local

```bash
cp .env.example .env
docker compose up -d mongo redis postgres        # postgres solo para Parte 2 (SQL)
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/seed_all.py
uvicorn app.main:app --reload
```

* Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
* Healthcheck: `GET /healthz`

> **Windows – bcrypt**: si ves `AttributeError: module 'bcrypt' has no attribute '__about__'`
>
> ```
> pip install "bcrypt==3.2.2"
> ```
>
> o:
>
> ```
> pip install -U passlib "bcrypt>=4.1.2"
> ```

---

## 🔐 Autenticación & Autorización

* **Login** (`POST /api/v1/auth/login`) devuelve:

  ```json
  {
    "access_token": "<JWT>",
    "token_type": "bearer",
    "user": { "id": "...", "email": "...", "full_name": "...", "role": "user" }
  }
  ```
* Usa `Authorization: Bearer <JWT>` en todas las llamadas protegidas.
* **Roles**: `user`, `admin` (preparado para perfilar futuros endpoints; los tests usan `user`).
* **Cifrado**: contraseñas con `passlib[bcrypt]`. JWT HS256 con expiración configurable.

---

## 📈 Rate limit

* `POST /api/v1/auth/register`: **5/min**
* `POST /api/v1/auth/login`: **30/min**
* Se puede extender por endpoint; configurable por `.env`.

---

## 🧾 Auditoría y logging

* **Auditoría**: inserciones en `audit_logs` con `user_id`, `event_type`, `ip`, `ts`, `payload`.
* **Access logs**: middleware registra cada request/response en JSON (`method`, `path`, `status`, `duration_ms`).
* **Errores de dominio**: manejados de forma central con mensajes claros (p.ej., saldo insuficiente).

---

## 💼 Reglas de negocio (Parte 1)

* **Monto inicial** del cliente: **COP 500.000** al registrarse.
* **Transacción con ID único** para cada suscripción/cancelación.
* Cada **fondo** tiene **monto mínimo** de vinculación.
* **Cancelar** devuelve el valor al saldo del cliente.
* **Saldo insuficiente** → mensaje:

  > `No tiene saldo disponible para vincularse al fondo <Nombre del fondo>`
* **Notificaciones** por preferencia (`email`/`sms`) al suscribirse:

  * En local, **stubs**: impresiones o logs simulando entrega (pluggable).

**Fondos (semilla en Mongo):**

| ID | Nombre                         | Mínimo  | Categoría |
| -- | ------------------------------ | ------- | --------- |
| 1  | FPV\_BTG\_PACTUAL\_RECAUDADORA | 75.000  | FPV       |
| 2  | FPV\_BTG\_PACTUAL\_ECOPETROL   | 125.000 | FPV       |
| 3  | DEUDAPRIVADA                   | 50.000  | FIC       |
| 4  | FDO-ACCIONES                   | 250.000 | FIC       |
| 5  | FPV\_BTG\_PACTUAL\_DINAMICA    | 100.000 | FPV       |

---

## 🧪 Flujos (cURL / Postman / Swagger)

### Registrar

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"u@test.com","full_name":"User Test","password":"Secret123!","notify_channel":"email","notify_destination":"u@test.com"}'
```

### Login (copiar `access_token`)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"u@test.com","password":"Secret123!"}'
```

### Listar fondos

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/funds
```

### Suscribirse a fondo (ej: `fund_id=2`, monto 125000)

```bash
curl -X POST http://localhost:8000/api/v1/subscriptions/2 \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"amount":125000}'
```

### Historial

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/transactions
```

### Cancelar (usa el `id` de la transacción de suscripción)

```bash
curl -X POST http://localhost:8000/api/v1/subscriptions/<tx_id>/cancel \
  -H "Authorization: Bearer <token>"
```

> **Postman**: importa `postman/BTG.postman_collection.json`.
> El flujo de `Login` guarda automáticamente `{{token}}` que usan el resto de requests.

---

## 🗃️ Modelo de datos (NoSQL – Mongo)

**Colecciones**

* `users` (id, email, full\_name, password\_hash, role, balance, notify\_channel, notify\_destination, created\_at)
* `funds` (id, name, min\_amount, category)
* `transactions` (id, user\_id, fund\_id, fund\_name, type=\[SUBSCRIPTION|CANCELLATION], amount, created\_at, correlation\_id)
* `audit_logs` (id, user\_id, event\_type, ip, path, payload, ts)

**Indices sugeridos**: `users.email`, `transactions.user_id`, `funds.id`, `audit_logs.ts`.

---

## 🧰 Seeds / Backup / Restore (Mongo)

* **Semilla completa**: `python scripts/seed_all.py`
* **Reseteo diario** (backup → cleanup → seed): `python scripts/seed_daily.py`

  * Windows Task Scheduler o cron (instrucciones incluidas en script).
* **Scripts de mantenimiento**:

  * `scripts/mongo_backup.py`, `scripts/mongo_restore.py`, `scripts/mongo_cleanup.py`

---

## 🗄️ Parte 2 – SQL (PostgreSQL)

**Objetivo**

* Crear schema, tablas, constantes y FKs.
* Cargar datos de prueba (sucursales, productos, clientes, disponibilidad, visitas, inscripciones).
* **Query solicitada**:
  “Obtener los **nombres** de los **clientes** que tienen inscrito **algún producto** disponible **solo** en las **sucursales que visitan**.”

> Incluyo **dos interpretaciones útiles** y seeds para ambas.
>
> * *Exclusiva*: el producto **solo** está disponible en las sucursales que visita el cliente.
> * *Cobertura de visitas*: el producto está disponible **en todas** las sucursales que visita (aunque exista en otras).

**Archivos** (en `sql/`):

* `00_schema.sql` → `CREATE SCHEMA btg` + `TYPE btg.tipo_producto`.
* `01_tables.sql` → `cliente`, `sucursal`, `producto`, `disponibilidad`, `inscripcion`, `visitan` + FKs.
* `02_seed.sql` → dataset de prueba **coherente** para ambas lecturas.
* `03_query.sql` → versión *exclusiva* (por defecto, la más estricta) o *cobertura* (alternativa).
* `04_cleanup_safe.sql` → limpieza segura (mantiene estructura).
* `05_drop_schema.sql` → drop total del schema.

**Runner Python** (multiplataforma, sin `psql`):

* `scripts/run_all_sql.py` → procesa `\i sql/...` y ejecuta todo con `psycopg2`.
* **Backup/Restore/Rollback** en Python:

  * `scripts/backup_pg.py`
  * `scripts/restore_pg.py`
  * `scripts/rollback_pg.py`

**Ejecutar todo**:

```bash
# Variables (si difieren de docker-compose)
export PGHOST=localhost PGPORT=5432 PGUSER=btg PGPASSWORD=btg123 PGDATABASE=BTG

# Correr todo
python -m scripts/run_all_sql.py

# Backup / Restore / Rollback
python -m scripts/backup_pg.py
python -m scripts/restore_pg.py ./pg_backups/BTG_backup_YYYYmmddTHHMMSSZ.sql
python -m scripts/rollback_pg.py
```

**Resultado esperado** (con el seed ajustado para *exclusiva*):
La query devuelve clientes para los que **existe al menos un producto inscrito** cuyo conjunto de sucursales que lo ofrecen está **contenido exclusivamente** en las sucursales que el cliente visita.

---

## ✅ Requisitos de la prueba – Checklist

**Parte 1 – Fondos (80%)**

* [x] **Suscribirse** a un nuevo fondo (`POST /api/v1/subscriptions/{fund_id}`)
* [x] **Cancelar** una suscripción actual (`POST /api/v1/subscriptions/{tx_id}/cancel`)
* [x] **Historial** de transacciones (`GET /api/v1/transactions`)
* [x] **Notificación** (email/SMS stub) al suscribirse
* [x] **Reglas**:

  * [x] Monto inicial COP **500.000** por usuario
  * [x] **ID único** por transacción y correlación sub/cancel
  * [x] **Mínimo por fondo** validado
  * [x] **Devolución** de saldo en cancelación
  * [x] **Saldo insuficiente** → mensaje requerido
* [x] **Tecnología**: Python **FastAPI**
* [x] **Modelo NoSQL**: colecciones + índices + auditoría
* [x] **API REST**: endpoints, excepciones, **Clean Code**, **Tests**
* [x] **Seguridad**: JWT, roles preparados, rate limit, headers, TrustedHost
* [x] **Despliegue**: docker-compose + guía para IaC (ver **Sugerencias AWS** abajo)
* [x] **Arquitectura + diagrama**: incluido (`docs/architecture_enterprise.drawio`)
* [x] **Postman**: `postman/BTG.postman_collection.json`

**Parte 2 – SQL (20%)**

* [x] **Schema** + **tablas** + **constantes** + **FKs**
* [x] **Seeds**
* [x] **Query solicitada**
* [x] **Cleanup/Drop**, **Backup/Restore/Rollback**
* [x] **Runner** en Python (sin `psql` obligatorio)

---

## 🧪 Tests

* `pytest -q`
* Tests cubren: registro, login, listar fondos, suscripción, cancelación, historial, validaciones de negocio (mínimos/saldo), auditoría y rate-limit (happy path + errores).

---

## 🪪 Seguridad y Mantenibilidad

* **JWT** HS256 con expiración (configurable) y `iss` fijo.
* **Headers** endurecidos: `X-Content-Type-Options`, `X-Frame-Options`, etc.
* **CORS**: whitelist por entorno (`ALLOWED_ORIGINS`).
* **TrustedHost**: whitelist de hosts (`ALLOWED_HOSTS`).
* **Rate-limiting**: defensa contra fuerza bruta/dDoS local.
* **Validación** DTO/Pydantic (inputs sanitizados).
* **Clean Code**: capas (routes → services → repositories → db), DTOs, excepciones de dominio, use-cases claros.
* **Observabilidad**: structlog JSON + auditoría en `audit_logs`.

---

## ☁️ Despliegue (sugerido en AWS)

> **Opcional** — Referencia de cómo lo haría en producción:

* **API**: Lambda + API Gateway (ASGI con Mangum) o ECS/Fargate.
* **MongoDB**: Atlas (VPC peering) o DocumentDB (si aplica).
* **Redis**: ElastiCache (Redis).
* **Secrets**: AWS Secrets Manager / SSM Parameter Store.
* **IaC**:

  * **Serverless Framework** (CloudFormation) — plantilla `serverless.yml` con stages (`dev`, `prod`), variables por entorno, función Lambda, API Gateway, IAM, logs, alarms.
  * o **Terraform**: módulos para VPC, SGs, Lambda/ECS, API GW, Secrets, SG attached, etc.
* **CI/CD**: GitHub Actions → build, tests, seguridad (bandit), deploy por branch/tag.
* **Monitoreo**: CloudWatch logs + alarms (p95 latency, 5xx).

---

## 🧭 Troubleshooting

* **HTTP 400 en tests** con `base_url="http://test"` → TrustedHost bloquea host `test`.
  Solución: `base_url="http://localhost"` o agrega `test` a `ALLOWED_HOSTS` en `.env`.
* **bcrypt en Windows** → ver nota arriba.
* **Rate limit** → 429 si excedes; en `.env` puedes usar `RATE_LIMIT_STORAGE_URL=memory://` en tests.

---

## 🧩 Carpeta del proyecto (guía)

```
app/
  main.py
  api_v1.py
  routes/ (auth, funds, subscriptions, transactions)
  services/
  domain/ (models, schemas, repositories)
  security.py
  db.py
  auth.py
  rate_limit.py
  middleware.py
  utils/ (exceptions, notifications stubs)
docs/
  architecture_enterprise.drawio
postman/
  BTG.postman_collection.json
scripts/
  seed_all.py
  seed_daily.py
  (Mongo) mongo_backup.py, mongo_restore.py, mongo_cleanup.py
db_tools/
  run_all_sql.py
  backup_pg.py
  restore_pg.py
  rollback_pg.py
sql/
  00_schema.sql
  01_tables.sql
  02_seed.sql
  03_query.sql
  04_cleanup_safe.sql
  05_drop_schema.sql
tests/
  test_flow.py
  test_business.py
.env.example
docker-compose.yml
requirements.txt
README.md
```

---

## 🔭 Valor agregado

* **Versionado** de API (`/api/v1`) y estructura limpia por capas.
* **Rate limiting** con Redis, endpoint-level.
* **Auditoría** detallada en Mongo.
* **Logs JSON** y access logs estandarizados.
* **Seeds/backup/restore/rollback** **en Python** (multi-OS, sin depender de `psql` si no quieres).
* **Runner** de SQL que **expande `\i`** como `psql`.
* **Restauración diaria** automatizable.
* **Seguridad**: headers, CORS, TrustedHost, validación estricta, DTOs, JWT correcto.
* **Guía de despliegue AWS** (Serverless/Terraform) y CI/CD propuesto.

---

**© David Barbosa – BTG Pactual – 14/09/2025**
