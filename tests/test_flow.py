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
async def test_register_login_list_funds_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        r = await ac.post("/api/v1/auth/register", json={
            "email":"u@test.com","full_name":"User Test","password":"Secret123!",
            "notify_channel":"email","notify_destination":"u@test.com"
        })
        assert r.status_code == 201

        r = await ac.post("/api/v1/auth/login", json={"email":"u@test.com","password":"Secret123!"})
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r = await ac.get("/api/v1/funds", headers=headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
