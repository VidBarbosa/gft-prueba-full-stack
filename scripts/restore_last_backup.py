import sys, pathlib, asyncio, json, os
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.db import get_db
from bson import json_util
from pathlib import Path

def last_backup():
    p = Path("backups")
    if not p.exists():
        return None
    xs = sorted(p.glob("mongo_backup_*.json"))
    return str(xs[-1]) if xs else None

async def main():
    path = last_backup()
    if not path:
        print("No hay backups para restaurar.")
        return
    with open(path,"r",encoding="utf-8") as f:
        data = json_util.loads(f.read())
    db = await get_db()
    for col in ["users","funds","transactions","audit_logs"]:
        await db[col].delete_many({})
        if data.get(col):
            await db[col].insert_many(data[col])
    print(f"✅ Restaurado desde {path}")

if __name__ == "__main__":
    asyncio.run(main())
