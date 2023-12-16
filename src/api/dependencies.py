from typing import Annotated, TypeVar, Union, Callable, ClassVar, Hashable

from fastapi import Depends

from src.repositories.auth.abc import AbstractAuthRepository
from src.repositories.bookings.abc import AbstractBookingRepository
from src.repositories.participants.abc import AbstractParticipantRepository
from src.storage.sql import AbstractSQLAlchemyStorage

T = TypeVar("T")

CallableOrValue = Union[Callable[[], T], T]


class Dependencies:
    providers: ClassVar[dict[type, CallableOrValue]] = {}

    @classmethod
    def register_provider(cls, key: type[T] | Hashable, provider: CallableOrValue):
        cls.providers[key] = provider

    @classmethod
    def f(cls, key: type[T] | Hashable) -> T:
        """
        Get shared dependency by key (f - fetch)
        """
        if key not in cls.providers:
            if isinstance(key, type):
                # try by classname
                key = key.__name__

                if key not in cls.providers:
                    raise KeyError(f"Provider for {key} is not registered")

            elif isinstance(key, str):
                # try by classname
                for cls_key in cls.providers.keys():
                    if cls_key.__name__ == key:
                        key = cls_key
                        break
                else:
                    raise KeyError(f"Provider for {key} is not registered")

        provider = cls.providers[key]

        if callable(provider):
            return provider()
        else:
            return provider

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


BOOKING_REPOSITORY_DEPENDENCY = Annotated[AbstractBookingRepository, Depends(Dependencies.get_booking_repository)]
AUTH_REPOSITORY_DEPENDENCY = Annotated[AbstractAuthRepository, Depends(Dependencies.get_auth_repository)]
