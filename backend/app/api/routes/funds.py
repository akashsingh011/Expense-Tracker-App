from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.fund import FundCreate, FundResponse, FundUpdate
from app.services.fund_service import (
    create_fund,
    delete_fund,
    get_fund,
    list_funds,
    update_fund,
)


router = APIRouter(
    prefix="/funds",
    tags=["Funds"],
)


@router.post(
    "",
    response_model=FundResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_fund_endpoint(
    fund_data: FundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_fund(
            db=db,
            user_id=current_user.id,
            fund_data=fund_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[FundResponse],
)
def list_funds_endpoint(
    start_date: date | None = None,
    end_date: date | None = None,
    source_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_funds(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        source_type=source_type,
    )


@router.get(
    "/{fund_id}",
    response_model=FundResponse,
)
def get_fund_endpoint(
    fund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fund = get_fund(
        db=db,
        user_id=current_user.id,
        fund_id=fund_id,
    )

    if fund is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund not found",
        )

    return fund


@router.patch(
    "/{fund_id}",
    response_model=FundResponse,
)
def update_fund_endpoint(
    fund_id: int,
    fund_data: FundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        fund = update_fund(
            db=db,
            user_id=current_user.id,
            fund_id=fund_id,
            fund_data=fund_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if fund is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund not found",
        )

    return fund


@router.delete(
    "/{fund_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_fund_endpoint(
    fund_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = delete_fund(
        db=db,
        user_id=current_user.id,
        fund_id=fund_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fund not found",
        )

    return None