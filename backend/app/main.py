from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.expenses import router as expenses_router
from app.api.routes.funds import router as funds_router
from app.api.routes.wallet import router as wallet_router

from app.core.config import settings
from app.core.database import Base, engine

# Import models so SQLAlchemy registers them before create_all
from app.models import Expense, Fund, User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(expenses_router, prefix="/api/v1")
app.include_router(funds_router, prefix="/api/v1")
app.include_router(wallet_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service_name": settings.app_name,
    }