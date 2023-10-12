from typing import Annotated

from fastapi import Depends

from src.repositories.auth.abc import AbstractAuthRepository
from src.repositories.bookings.abc import AbstractBookingRepository
from src.repositories.participants.abc import AbstractParticipantRepository
from src.storage.sql import AbstractSQLAlchemyStorage


class Dependencies:
    _storage: "AbstractSQLAlchemyStorage"
    _participant_repository: "AbstractParticipantRepository"
    _booking_repository: "AbstractBookingRepository"
    _auth_repository: "AbstractAuthRepository"

    @classmethod
    def get_storage(cls) -> "AbstractSQLAlchemyStorage":
        return cls._storage

    @classmethod
    def set_storage(cls, storage: "AbstractSQLAlchemyStorage"):
        cls._storage = storage

    @classmethod
    def get_participant_repository(cls) -> "AbstractParticipantRepository":
        return cls._participant_repository

    @classmethod
    def set_participant_repository(cls, participant_repository: "AbstractParticipantRepository"):
        cls._participant_repository = participant_repository

    @classmethod
    def get_booking_repository(cls) -> "AbstractBookingRepository":
        return cls._booking_repository

    @classmethod
    def set_booking_repository(cls, booking_repository: "AbstractBookingRepository"):
        cls._booking_repository = booking_repository

    @classmethod
    def get_auth_repository(cls) -> "AbstractAuthRepository":
        return cls._auth_repository

    @classmethod
    def set_auth_repository(cls, auth_repository: "AbstractAuthRepository"):
        cls._auth_repository = auth_repository


STORAGE_DEPENDENCY = Annotated[AbstractSQLAlchemyStorage, Depends(Dependencies.get_storage)]
PARTICIPANT_REPOSITORY_DEPENDENCY = Annotated[
    AbstractParticipantRepository, Depends(Dependencies.get_participant_repository)
]

BOOKING_REPOSITORY_DEPENDENCY = Annotated[AbstractBookingRepository, Depends(Dependencies.get_booking_repository)]
AUTH_REPOSITORY_DEPENDENCY = Annotated[AbstractAuthRepository, Depends(Dependencies.get_auth_repository)]
