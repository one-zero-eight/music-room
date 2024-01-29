__all__ = ["verify_request"]

from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from src.api.auth.telegram import (
    TelegramWidgetData,
    telegram_webapp_check_authorization,
)
from src.api.dependencies import Dependencies
from src.exceptions import NoCredentialsException, IncorrectCredentialsException
from src.repositories.auth.repository import TokenRepository
from src.repositories.participants.abc import AbstractParticipantRepository
from src.schemas.auth import VerificationResult

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Your JSON Web Token (JWT)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


async def get_access_token(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[str]:
    # Prefer header to cookie
    if bearer:
        return bearer.credentials


async def verify_request(
    bearer: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> VerificationResult:
    """
    Check one of the following:
    - JWT Token with `user_id` in payload sub
    - Bearer token from header with BOT_TOKEN (or `user_id:bot_token`)
    - Bearer token from header with webapp data
    :raises NoCredentialsException: if token is not provided
    :raises IncorrectCredentialsException: if token is invalid
    """

    if not bearer:
        raise NoCredentialsException()

    user_verification_result = await TokenRepository.verify_access_token(
        bearer.credentials
    )
    if user_verification_result.success:
        return user_verification_result

    bot_verification_result = TokenRepository.verify_bot_token(bearer.credentials)
    if bot_verification_result.success:
        # replace telegram_id with user_id
        participant_repository = Dependencies.get(AbstractParticipantRepository)
        telegram_id = str(bot_verification_result.user_id)
        bot_verification_result.user_id = (
            await participant_repository.get_participant_id(telegram_id)
        )
        return bot_verification_result

    try:
        telegram_data = TelegramWidgetData.parse_from_string(bearer.credentials)
    except ValidationError:
        raise IncorrectCredentialsException()

    webapp_verification_result = telegram_webapp_check_authorization(telegram_data)

    if webapp_verification_result.success:
        return webapp_verification_result

    raise IncorrectCredentialsException()
