import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.sql.__mixin__ import IdMixin
from src.storage.sql.models import Base

if TYPE_CHECKING:
    from src.storage.sql.models.user import User


class Booking(Base, IdMixin):
    __tablename__ = "booking"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(
        "User",
        back_populates="booking",
        lazy="joined",
    )
    user_alias: AssociationProxy[str] = association_proxy("user", "alias")
    time_start: Mapped[datetime.datetime] = mapped_column(DateTime)
    time_end: Mapped[datetime.datetime] = mapped_column(DateTime)
