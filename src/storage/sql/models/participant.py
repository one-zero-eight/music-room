import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.sql.__mixin__ import IdMixin
from src.storage.sql.models import Base

if TYPE_CHECKING:
    from src.storage.sql.models.booking import Booking


class Participant(Base, IdMixin):
    __tablename__ = "participant"
    name: Mapped[str] = mapped_column(nullable=True)
    alias: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    status: Mapped[str] = mapped_column(nullable=False, default="free")
    telegram_id: Mapped[str] = mapped_column(nullable=True, default="null")
    phone_number: Mapped[bytes] = mapped_column(nullable=True)
    need_to_fill_profile: Mapped[bool] = mapped_column(nullable=False)

    booking: Mapped[List["Booking"]] = relationship(back_populates="participant")


class PotentialUser(Base, IdMixin):
    __tablename__ = "potential_user"

    email: Mapped[str] = mapped_column()
    code: Mapped[str] = mapped_column()
    code_expiration: Mapped[datetime.datetime] = mapped_column()
