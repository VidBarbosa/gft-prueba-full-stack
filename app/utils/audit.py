from typing import Any, Optional
from datetime import datetime
from app.db import get_db

COLLECTION = "audit_logs"

async def log_event(action: str, user_id: Optional[str], actor: str, details: dict[str, Any] | None = None):
    db = await get_db()
    await db[COLLECTION].insert_one({
        "ts": datetime.utcnow(),
        "action": action,
        "user_id": user_id,
        "actor": actor,
        "details": details or {}
    })
