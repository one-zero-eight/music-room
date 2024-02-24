from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ParticipantStatus(StrEnum):
    FREE = "free"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LORD = "lord"

    def max_hours_to_book_per_day(self) -> Optional[int]:
        if self == ParticipantStatus.FREE:
            return 2
        elif self == ParticipantStatus.JUNIOR:
            return 2
        elif self == ParticipantStatus.MIDDLE:
            return 3
        elif self == ParticipantStatus.SENIOR:
            return 4
        elif self == ParticipantStatus.LORD:
            return 15
        return None

    def max_hours_to_book_per_week(self) -> Optional[int]:
        if self == ParticipantStatus.FREE:
            return 4
        elif self == ParticipantStatus.JUNIOR:
            return 5
        elif self == ParticipantStatus.MIDDLE:
            return 8
        elif self == ParticipantStatus.SENIOR:
            return 10
        elif self == ParticipantStatus.LORD:
            return 150
        return None


class CreateParticipant(BaseModel):
    name: Optional[str] = None
    alias: Optional[str] = None
    email: str
    phone_number: Optional[str] = None
    telegram_id: Optional[str] = None
    status: ParticipantStatus = ParticipantStatus.FREE
    need_to_fill_profile: bool


class FillParticipantProfile(BaseModel):
    name: str
    alias: str
    phone_number: str


class ViewParticipant(BaseModel):
    id: int
    name: Optional[str] = None
    alias: Optional[str] = None
    email: str
    phone_number: Optional[bytes] = None
    telegram_id: Optional[str] = None
    status: ParticipantStatus
    need_to_fill_profile: bool

    model_config = ConfigDict(from_attributes=True)
