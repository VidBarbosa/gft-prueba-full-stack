from fastapi import APIRouter
from app.routes import auth as auth_routes
from app.routes import funds as funds_routes
from app.routes import subscriptions as subs_routes
from app.routes import transactions as txs_routes

api_router = APIRouter()
api_router.include_router(auth_routes.router)
api_router.include_router(funds_routes.router)
api_router.include_router(subs_routes.router)
api_router.include_router(txs_routes.router)
