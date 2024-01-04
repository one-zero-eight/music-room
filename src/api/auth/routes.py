import random

from starlette.background import BackgroundTasks

from src.api.auth import router
from src.api.dependencies import Dependencies
from src.config import settings
from src.exceptions import InvalidCode, UserExists
from src.repositories.auth.abc import AbstractAuthRepository
from src.repositories.participants.abc import AbstractParticipantRepository
from src.repositories.smtp.repository import SMTPRepository
from src.schemas import CreateParticipant, ParticipantStatus


def _generate_auth_code() -> str:
    # return random 6-digit code
    return str(random.randint(100_000, 999_999))


@router.post("/registration")
async def registration(background_task: BackgroundTasks, email: str):
    auth_repository = Dependencies.get(AbstractAuthRepository)

    if await auth_repository.is_user_registered(email, telegram_id=None):
        raise UserExists()
    else:
        code = _generate_auth_code()
        await auth_repository.save_code(email, code)
        smtp = Dependencies.get(SMTPRepository)
        message = smtp.render_message(settings.REGISTRATION_MESSAGE_TEMPLATE, email, code=code)
        # smtp.send(message, email)
        background_task.add_task(smtp.send, message, email)


@router.get("/is_user_exists")
async def is_user_exists(email: str = None, telegram_id: str = None) -> bool:
    auth_repository = Dependencies.get(AbstractAuthRepository)
    return await auth_repository.is_user_registered(email, telegram_id)


@router.post("/validate_code")
async def validate_code(
    email: str,
    code: str,
    telegram_id: str,
):
    auth_repository = Dependencies.get(AbstractAuthRepository)
    participant_repository = Dependencies.get(AbstractParticipantRepository)

    if await auth_repository.is_code_valid(email, code):
        participant = CreateParticipant(
            email=email,
            need_to_fill_profile=True,
            status=ParticipantStatus.FREE,
            telegram_id=telegram_id,
        )
        created = await participant_repository.create(participant)
        return created
    else:
        raise InvalidCode()
