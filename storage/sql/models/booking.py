import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sql.__mixin__ import IdMixin
from storage.sql.models.base import Base

if TYPE_CHECKING:
    from storage.sql.models.participant import Participant


class Booking(Base, IdMixin):
    __tablename__ = "booking"
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id"))
    participant: Mapped["Participant"] = relationship(
        "Participant",
        back_populates="booking",
    )
    time_start: Mapped[datetime.datetime] = mapped_column()
    time_end: Mapped[datetime.datetime] = mapped_column()
