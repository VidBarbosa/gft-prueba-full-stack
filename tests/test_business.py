import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from motor.motor_asyncio import AsyncIOMotorClient

@pytest.fixture(autouse=True, scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def _prepare_db():
    from app.config import settings
    client = AsyncIOMotorClient(settings.mongo_uri)
    await client.drop_database(settings.mongo_db)

@pytest.mark.anyio
async def test_full_business_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        # Register
        r = await ac.post("/api/v1/auth/register", json={
            "email":"testuser@test.com","full_name":"TU","password":"Secret123!",
            "notify_channel":"email","notify_destination":"testuser@test.com"
        })
        assert r.status_code in (201, 409)

        # Duplicate registration must 409
        r2 = await ac.post("/api/v1/auth/register", json={
            "email":"testuser@test.com","full_name":"TU","password":"Secret123!",
            "notify_channel":"email","notify_destination":"testuser@test.com"
        })
        assert r2.status_code == 409

        # Bad login
        r = await ac.post("/api/v1/auth/login", json={"email":"testuser@test.com","password":"Wrong!"})
        assert r.status_code == 401

        # Good login
        r = await ac.post("/api/v1/auth/login", json={"email":"testuser@test.com","password":"Secret123!"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Seed funds
        from app.db import get_db
        from app.domain.repositories import FundRepository
        from app.domain.models import Fund
        db = await get_db()
        await FundRepository(db).upsert_many([
            Fund(id="1", name="FPV_BTG_PACTUAL_RECAUDADORA", min_amount=75000, category="FPV"),
            Fund(id="2", name="FPV_BTG_PACTUAL_ECOPETROL",   min_amount=125000, category="FPV"),
            Fund(id="3", name="DEUDAPRIVADA",                min_amount=50000, category="FIC"),
            Fund(id="4", name="FDO-ACCIONES",                min_amount=250000, category="FIC"),
            Fund(id="5", name="FPV_BTG_PACTUAL_DINAMICA",    min_amount=100000, category="FPV"),
        ])

        # List funds
        r = await ac.get("/api/v1/funds", headers=headers)
        assert r.status_code == 200
        funds = r.json()
        assert isinstance(funds, list) and len(funds) >= 5

        # Pick ECOPETROL
        fund = next(f for f in funds if f["id"] == "2")

        # Below minimum
        r = await ac.post(f"/api/v1/subscriptions/{fund['id']}", headers=headers, json={"amount": 1000})
        assert r.status_code == 400
        assert "Monto mínimo" in r.json()["detail"]

        # Over balance
        r = await ac.post(f"/api/v1/subscriptions/{fund['id']}", headers=headers, json={"amount": 999999999})
        assert r.status_code == 400
        assert "No tiene saldo disponible" in r.json()["detail"]

        # Valid subscription
        r = await ac.post(f"/api/v1/subscriptions/{fund['id']}", headers=headers, json={"amount": 125000})
        assert r.status_code == 200
        tx = r.json()
        tx_id = tx["id"]

        # History contains subscription
        r = await ac.get("/api/v1/transactions", headers=headers)
        assert r.status_code == 200
        items = r.json()["items"]
        assert any(t["id"] == tx_id and t["type"] == "SUBSCRIPTION" for t in items)

        # Cancel it
        r = await ac.post(f"/api/v1/subscriptions/{tx_id}/cancel", headers=headers)
        assert r.status_code == 200
        cancel_tx = r.json()
        assert cancel_tx["type"] == "CANCELLATION" and cancel_tx["amount"] == 125000
