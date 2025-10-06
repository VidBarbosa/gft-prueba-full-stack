from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

async def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_uri)
    return _client

async def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        client = await get_client()
        _db = client[settings.mongo_db]
    return _db
