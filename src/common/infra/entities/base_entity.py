from datetime import datetime
from uuid import UUID  # Tipo Python

from sqlalchemy import func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, registry

table_registry = registry()


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):  # pyright: ignore[reportUnsafeMultipleInheritance]
    # This connects the base to your specific registry
    registry = table_registry  # pyright: ignore[reportUnannotatedClassAttribute]


class BaseEntity(Base):
    __abstract__ = True  # pyright: ignore[reportUnannotatedClassAttribute]
    # Usamos server_default para chamar a função nativa do Postgres 18
    # init=False retira o id do construtor User(name="...")
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("uuidv7()"), init=False)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), nullable=False, onupdate=func.now())
    status: Mapped[bool] = mapped_column(init=False, default=True, nullable=False)
