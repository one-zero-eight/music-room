__all__ = ["SqlAuthRepository", "auth_repository", "TokenRepository"]

import time
from typing import Self

from authlib.jose import JoseError, JWTClaims, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import api_settings
from src.repositories.innohassle_accounts import innohassle_accounts
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
    def decode_token(cls, token: str) -> JWTClaims:
        now = time.time()
        pub_key = innohassle_accounts.get_public_key()
        payload = jwt.decode(token, pub_key)
        payload.validate_exp(now, leeway=0)
        payload.validate_iat(now, leeway=0)
        return payload

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
    async def verify_user_token(cls, token: str) -> VerificationResult:
        try:
            payload = cls.decode_token(token)
            innohassle_id: str = payload.get("uid")
            if innohassle_id is None:
                return VerificationResult(success=False)
            user_data = await innohassle_accounts.get_user_by_innohassle_id(innohassle_id)
            if user_data is None:
                raise VerificationResult(success=False)
            return VerificationResult(success=True, telegram_id=user_data.telegram.id)
        except JoseError:
            raise VerificationResult(success=False)

    @classmethod
    def verify_api_token(cls, auth_token: str) -> VerificationResult:
        if auth_token == api_settings.api_key:
            return VerificationResult(success=True, source=VerificationSource.API)
        else:
            return VerificationResult(success=False)


auth_repository: SqlAuthRepository = SqlAuthRepository()
