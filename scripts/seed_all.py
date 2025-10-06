import sys, pathlib, asyncio, uuid
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.db import get_db
from app.security import hash_password
from app.domain.models import Fund, User, Transaction
from app.domain.repositories import FundRepository, UserRepository, TransactionRepository

FUNDS = [
    Fund(id="1", name="FPV_BTG_PACTUAL_RECAUDADORA", min_amount=75000, category="FPV"),
    Fund(id="2", name="FPV_BTG_PACTUAL_ECOPETROL",   min_amount=125000, category="FPV"),
    Fund(id="3", name="DEUDAPRIVADA",                min_amount=50000, category="FIC"),
    Fund(id="4", name="FDO-ACCIONES",                min_amount=250000, category="FIC"),
    Fund(id="5", name="FPV_BTG_PACTUAL_DINAMICA",    min_amount=100000, category="FPV"),
]

USERS = [
    {"email":"user1@test.com","full_name":"User One","password":"Secret123!","notify":"email"},
    {"email":"user2@test.com","full_name":"User Two","password":"Secret123!","notify":"sms","dest":"+573001112233"},
]

async def main():
    db = await get_db()
    funds_repo = FundRepository(db)
    users_repo = UserRepository(db)
    tx_repo = TransactionRepository(db)

    await funds_repo.upsert_many(FUNDS)

    user_ids = {}
    for u in USERS:
        existing = await users_repo.find_by_email(u["email"])
        if existing:
            user_ids[u["email"]] = existing.id
            continue
        uid = str(uuid.uuid4())
        user = User(
            id=uid,
            email=u["email"],
            full_name=u["full_name"],
            password_hash=hash_password(u["password"]),
            role="user",
            balance=500_000,
            notify_channel=u["notify"],
            notify_destination=u.get("dest") or u["email"],
        )
        await users_repo.create(user)
        user_ids[u["email"]] = uid

    u1 = user_ids["user1@test.com"]
    tx1 = Transaction(id=str(uuid.uuid4()), user_id=u1, fund_id="1", fund_name="FPV_BTG_PACTUAL_RECAUDADORA", type="SUBSCRIPTION", amount=100_000)
    await tx_repo.create(tx1)
    await users_repo.update_balance(u1, 400_000)
    tx2 = Transaction(id=str(uuid.uuid4()), user_id=u1, fund_id="1", fund_name="FPV_BTG_PACTUAL_RECAUDADORA", type="CANCELLATION", amount=100_000, related_to=tx1.id)
    await tx_repo.create(tx2)
    await users_repo.update_balance(u1, 500_000)

    print("✅ Seed completo: fondos + usuarios + transacciones demo")

if __name__ == "__main__":
    asyncio.run(main())
