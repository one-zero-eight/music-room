import datetime

from authlib.jose import jwt, JoseError
from sqlalchemy import and_, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.repositories.auth.abc import AbstractAuthRepository
from src.repositories.participants.abc import AbstractParticipantRepository
from src.schemas.auth import VerificationResult, VerificationSource
from src.storage.sql import AbstractSQLAlchemyStorage
from src.storage.sql.models.participant import Participant, PotentialUser


class SqlAuthRepository(AbstractAuthRepository):
    storage: AbstractSQLAlchemyStorage

    def __init__(self, storage: AbstractSQLAlchemyStorage):
        self.storage = storage

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()

    async def is_user_registered(self, email: str, telegram_id: str | None) -> bool:
        async with self._create_session() as session:
            if email is None and telegram_id is None:
                return False
            clauses = []
            if email is not None:
                clauses.append(Participant.email == email)
            if telegram_id is not None:
                clauses.append(Participant.telegram_id == telegram_id)
            query = select(Participant).where(or_(*clauses))
            obj = await session.scalar(query)
            return False if obj is None else True

    async def code_exists(self, email: str) -> bool:
        async with self._create_session() as session:
            query = select(PotentialUser).where(PotentialUser.email == email)
            res = await session.scalar(query)
            return True if res else False

    async def save_code(self, email: str, code: str) -> None:
        async with self._create_session() as session:
            current_datetime = datetime.datetime.now()
            delta = datetime.timedelta(minutes=30)
            new_datetime = current_datetime + delta

            if await self.code_exists(email):
                query = (
                    update(PotentialUser)
                    .where(PotentialUser.email == email)
                    .values(code=code, email=email, code_expiration=new_datetime)
                    .returning(PotentialUser)
                )
            else:
                query = (
                    insert(PotentialUser)
                    .values(code=code, email=email, code_expiration=new_datetime)
                    .returning(PotentialUser)
                )
            await session.scalar(query)
            await session.commit()

    async def delete_code(self, email: str) -> None:
        async with self._create_session() as session:
            query = select(PotentialUser).where(PotentialUser.email == email)
            objs = await session.scalars(query)
            for obj in objs:
                await session.delete(obj)
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


class TokenRepository:
    ALGORITHM = "RS256"

    @classmethod
    async def verify_access_token(cls, auth_token: str) -> VerificationResult:
        from src.api.dependencies import Dependencies

        try:
            payload = jwt.decode(auth_token, settings.JWT_PUBLIC_KEY)
        except JoseError:
            return VerificationResult(success=False)

        user_repository = Dependencies.get(AbstractParticipantRepository)
        user_id: str = payload.get("sub")

        if user_id is None or not user_id.isdigit():
            return VerificationResult(success=False)

        converted_user_id = int(user_id)

        user = await user_repository.get_participant(converted_user_id)

        if user is None:
            return VerificationResult(success=False)

        return VerificationResult(
            success=True, user_id=converted_user_id, source=VerificationSource.USER
        )

    @classmethod
    def create_access_token(cls, user_id: int) -> str:
        access_token = TokenRepository._create_access_token(
            data={"sub": str(user_id)},
            expires_delta=datetime.timedelta(days=1),
        )
        return access_token

    @classmethod
    def _create_access_token(cls, data: dict, expires_delta: datetime.timedelta) -> str:
        payload = data.copy()
        issued_at = datetime.datetime.utcnow()
        expire = issued_at + expires_delta
        payload.update({"exp": expire, "iat": issued_at})
        encoded_jwt = jwt.encode(
            {"alg": cls.ALGORITHM}, payload, settings.JWT_PRIVATE_KEY.get_secret_value()
        )
        return str(encoded_jwt, "utf-8")

    @classmethod
    def verify_bot_token(cls, auth_token: str) -> VerificationResult:
        if auth_token.endswith(settings.BOT_TOKEN):
            user_id = auth_token[: -len(settings.BOT_TOKEN)]
            if user_id:
                user_id = int(user_id.strip(":"))
            else:
                user_id = None

            return VerificationResult(
                success=True, user_id=user_id, source=VerificationSource.BOT
            )
        else:
            return VerificationResult(success=False)
