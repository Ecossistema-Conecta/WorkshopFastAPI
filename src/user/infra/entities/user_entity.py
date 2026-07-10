from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.infra.entities import BaseEntity

if TYPE_CHECKING:
    from src.common.infra.entities import EmailLog


class User(BaseEntity):
    __tablename__ = "users"  # pyright: ignore[reportUnannotatedClassAttribute]

    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)

    email_logs_senders: Mapped[list['EmailLog']] = relationship(
        'EmailLog', foreign_keys='[EmailLog.sender_id]', back_populates='sender', default_factory=list
    )
    email_logs_receivers: Mapped[list['EmailLog']] = relationship(
        'EmailLog', foreign_keys='[EmailLog.receiver_id]', back_populates='receiver', default_factory=list
    )
