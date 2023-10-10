import datetime

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.auth.abc import AbstractAuthRepository
from storage.sql import AbstractSQLAlchemyStorage
from storage.sql.models import Participant, PotentialUser


class SqlAuthRepository(AbstractAuthRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def is_user_registered(self, email: str) -> bool:
        async with self._create_session() as session:
            query = select(Participant).where(Participant.email == email)
            obj = await session.scalar(query)
            if obj is not None:
                return True
            return False

    async def save_code(self, email: str, code: str) -> None:
        async with self._create_session() as session:
            current_datetime = datetime.datetime.now()
            delta = datetime.timedelta(minutes=30)
            new_datetime = current_datetime + delta

            query = (
                insert(PotentialUser)
                .values(code=code, email=email, code_expiration=new_datetime)
                .returning(PotentialUser)
            )
            await session.scalar(query)
            await session.commit()

    async def is_code_valid(self, email: str, code: str) -> bool:
        async with self._create_session() as session:
            current_datetime = datetime.datetime.now()
            query = select(PotentialUser).where(
                and_(
                    PotentialUser.email == email,
                    PotentialUser.code == code,
                    PotentialUser.code_expiration >= current_datetime,
                )
            )
            obj = await session.scalar(query)
            return False if obj is None else True