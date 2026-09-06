from datetime import date, datetime, timezone

from sqlalchemy import ( CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text,)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Fund(Base):
    __tablename__ = "funds"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="ck_funds_amount_positive",
        ),
        Index(
            "ix_funds_user_date",
            "user_id",
            "date",
        ),
        Index(
            "ix_funds_user_source_type",
            "user_id",
            "source_type",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="other",
    )

    note: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="funds",
    )