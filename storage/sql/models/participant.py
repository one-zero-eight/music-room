import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sql.__mixin__ import IdMixin
from storage.sql.models.base import Base

if TYPE_CHECKING:
    from storage.sql.models.booking import Booking


class Participant(Base, IdMixin):
    __tablename__ = "participant"
    name: Mapped[str] = mapped_column()
    alias: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column(default="free")
    # max_hours_per_day: Mapped[int] = mapped_column()
    # max_hours_per_week: Mapped[int] = mapped_column()

    booking: Mapped[List["Booking"]] = relationship(back_populates="participant")