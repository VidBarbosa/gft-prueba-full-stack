import sys, pathlib, asyncio
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.db import get_db
from app.domain.models import Fund
from app.domain.repositories import FundRepository

FUNDS = [
    Fund(id="1", name="FPV_BTG_PACTUAL_RECAUDADORA", min_amount=75000, category="FPV"),
    Fund(id="2", name="FPV_BTG_PACTUAL_ECOPETROL",   min_amount=125000, category="FPV"),
    Fund(id="3", name="DEUDAPRIVADA",                min_amount=50000, category="FIC"),
    Fund(id="4", name="FDO-ACCIONES",                min_amount=250000, category="FIC"),
    Fund(id="5", name="FPV_BTG_PACTUAL_DINAMICA",    min_amount=100000, category="FPV"),
]

async def main():
    db = await get_db()
    repo = FundRepository(db)
    await repo.upsert_many(FUNDS)
    print("✅ Fondos cargados")

if __name__ == "__main__":
    asyncio.run(main())
