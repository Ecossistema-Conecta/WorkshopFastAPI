from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Text

from src.common.infra.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from src.user.infra.entities.user_entity import User


class EmailLog(BaseEntity):
    __tablename__ = "email_log"  # pyright: ignore[reportUnannotatedClassAttribute]

    id_control: Mapped[str | None] = mapped_column(nullable=True)
    receiver_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), nullable=False)
    sender_id: Mapped[UUID | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    sender: Mapped[Optional['User']] = relationship(
        'User', foreign_keys=[sender_id], back_populates='email_logs_senders', init=False
    )
    receiver: Mapped[Optional['User']] = relationship(
        'User', foreign_keys=[receiver_id], back_populates='email_logs_receivers', init=False
    )
