__all__ = ["SqlAuthRepository", "auth_repository", "TokenRepository"]

from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from src.config import api_settings
from src.schemas.auth import VerificationResult, VerificationSource
from src.storage.sql import AbstractSQLAlchemyStorage


class SqlAuthRepository:
    storage: AbstractSQLAlchemyStorage

    def update_storage(self, storage: AbstractSQLAlchemyStorage) -> Self:
        self.storage = storage
        return self

    def _create_session(self) -> AsyncSession:
        return self.storage.create_session()


class TokenRepository:
    ALGORITHM = "RS256"

    @classmethod
    def verify_bot_token(cls, auth_token: str) -> VerificationResult:
        if auth_token.endswith(api_settings.bot_token):
            telegram_id = auth_token[: -len(api_settings.bot_token)]
            if telegram_id:
                telegram_id = int(telegram_id.strip(":"))
            else:
                telegram_id = None

            return VerificationResult(success=True, telegram_id=telegram_id, source=VerificationSource.BOT)
        else:
            return VerificationResult(success=False)

    @classmethod
    def verify_api_token(cls, auth_token: str) -> VerificationResult:
        if auth_token == api_settings.api_key:
            return VerificationResult(success=True, source=VerificationSource.API)
        else:
            return VerificationResult(success=False)


auth_repository: SqlAuthRepository = SqlAuthRepository()
