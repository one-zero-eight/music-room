from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.sql.__mixin__ import IdMixin
from src.storage.sql.models import Base

if TYPE_CHECKING:
    from src.storage.sql.models.booking import Booking


class User(Base, IdMixin):
    __tablename__ = "user"
    name: Mapped[str] = mapped_column(nullable=True)
    alias: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="free")
    telegram_id: Mapped[int] = mapped_column(nullable=True, default="null")

    booking: Mapped[list["Booking"]] = relationship(back_populates="user")
