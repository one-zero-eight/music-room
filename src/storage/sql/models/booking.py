import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.sql.__mixin__ import IdMixin
from src.storage.sql.models import Base

if TYPE_CHECKING:
    from src.storage.sql.models.participant import Participant


class Booking(Base, IdMixin):
    __tablename__ = "booking"
    participant_id: Mapped[int] = mapped_column(ForeignKey("participant.id"))
    participant: Mapped["Participant"] = relationship(
        "Participant",
        back_populates="booking",
        lazy="joined",
    )
    participant_alias: AssociationProxy[str] = association_proxy("participant", "alias")
    time_start: Mapped[datetime.datetime] = mapped_column(DateTime)
    time_end: Mapped[datetime.datetime] = mapped_column(DateTime)
