import sys, pathlib, asyncio, datetime
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.db import get_db
from bson import json_util

async def main():
    db = await get_db()
    backup = {}
    for col in ["users","funds","transactions","audit_logs"]:
        backup[col] = [d async for d in db[col].find({})]
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    import os
    os.makedirs("backups", exist_ok=True)
    with open(f"backups/mongo_backup_{ts}.json","w",encoding="utf-8") as f:
        f.write(json_util.dumps(backup))
    # limpieza
    for col in ["users","funds","transactions","audit_logs"]:
        await db[col].delete_many({})
    print("✅ Limpieza realizada; backup guardado en backups/")

if __name__ == "__main__":
    asyncio.run(main())
