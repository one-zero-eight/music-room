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
    email: Mapped[str] = mapped_column(unique=True)
    status: Mapped[str] = mapped_column(default="free")
    phone_number: Mapped[str] = mapped_column()

    booking: Mapped[List["Booking"]] = relationship(back_populates="participant")


class PotentialUser(Base):
    __tablename__ = "potential_user"

    email: Mapped[str] = mapped_column(primary_key=True, unique=True)
    # phone_number: Mapped[str] = mapped_column(unique=True)
    code: Mapped[str] = mapped_column()
    code_expiration: Mapped[datetime.datetime] = mapped_column()
