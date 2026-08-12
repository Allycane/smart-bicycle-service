from sqlalchemy import String, Enum, DateTime, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from database.connection import Base

class MemberModel(Base):
    __tablename__ = "bike_member"

    nickname : Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )
    email : Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    password : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    riding_styles : Mapped[list[str]] = mapped_column(
        JSON,
        nullable=True
    )

    agree_required : Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    agree_marketing : Mapped[bool] = mapped_column(
        Boolean,
        nullable=True
    )

    role : Mapped[str] = mapped_column(
        Enum("USER", "ADMIN", name="member_role"),
        nullable=False,
        default = "USER"
    )

    created_id : Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
