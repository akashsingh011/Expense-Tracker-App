from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.wallet import WalletResponse
from app.services.wallet_service import get_wallet_balance


router = APIRouter(
    prefix="/wallet",
    tags=["Wallet"],
)


@router.get("/balance", response_model=WalletResponse,)
def wallet_balance_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user),):
    return get_wallet_balance(
        db=db,
        user_id=current_user.id,
    )