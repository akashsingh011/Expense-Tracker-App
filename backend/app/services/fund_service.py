from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.fund import Fund
from app.schemas.fund import FundCreate, FundUpdate

ALLOWED_SOURCE_TYPES = {
    "salary",
    "refund",
    "cash",
    "petty",
    "other",
}

def normalize_source_type(source_type: str) -> str:
    source_type = source_type.strip().lower()

    if source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(
            f"Invalid source_type. Allowed values: "
            f"{', '.join(sorted(ALLOWED_SOURCE_TYPES))}"
        )

    return source_type


def create_fund(db: Session, user_id: int, fund_data: FundCreate,) -> Fund:
    source_type = normalize_source_type(
        fund_data.source_type
    )

    fund = Fund(
        user_id=user_id,
        date=fund_data.date,
        amount=fund_data.amount,
        source_type=source_type,
        note=fund_data.note,
    )

    db.add(fund)
    db.commit()
    db.refresh(fund)

    return fund


def list_funds(db: Session, user_id: int,) -> list[Fund]:
    statement = (
        select(Fund)
        .where(Fund.user_id == user_id)
        .order_by(Fund.date.asc(), Fund.id.asc())
    )

    return list(db.scalars(statement).all())


def get_fund(db: Session, user_id: int, fund_id: int,) -> Fund | None:
    statement = select(Fund).where(
        Fund.id == fund_id,
        Fund.user_id == user_id,
    )

    return db.scalar(statement)


def update_fund(db: Session, user_id: int, fund_id: int, fund_data: FundUpdate,) -> Fund | None:
    fund = get_fund(
        db=db,
        user_id=user_id,
        fund_id=fund_id,
    )

    if fund is None:
        return None

    update_data = fund_data.model_dump(
        exclude_unset=True,
    )

    if "source_type" in update_data:
        update_data["source_type"] = normalize_source_type(
            update_data["source_type"]
        )

    for field, value in update_data.items():
        setattr(fund, field, value)

    db.commit()
    db.refresh(fund)

    return fund


def delete_fund(db: Session, user_id: int, fund_id: int,) -> bool:
    fund = get_fund(
        db=db,
        user_id=user_id,
        fund_id=fund_id,
    )

    if fund is None:
        return False

    db.delete(fund)
    db.commit()

    return True