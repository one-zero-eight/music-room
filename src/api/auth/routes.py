import random

from fastapi import HTTPException
from starlette.background import BackgroundTasks

from src.api.auth import router
from src.exceptions import InvalidCode, UserExists
from src.repositories.auth.repository import auth_repository
from src.repositories.participants.repository import participant_repository
from src.repositories.smtp.repository import smtp_repository
from src.schemas import CreateParticipant, ParticipantStatus


def _generate_auth_code() -> str:
    # return random 6-digit code
    return str(random.randint(100_000, 999_999))


@router.post("/registration")
async def registration(background_task: BackgroundTasks, email: str):
    if await auth_repository.is_user_registered(email, telegram_id=None):
        raise UserExists()
    else:
        code = _generate_auth_code()
        await auth_repository.save_code(email, code)
        message = smtp_repository.render_verification_message(email, code)
        # smtp.send(message, email)
        background_task.add_task(smtp_repository.send, message, email)


@router.get("/is_user_exists")
async def is_user_exists(email: str = None, telegram_id: str = None) -> bool:
    return await auth_repository.is_user_registered(email, telegram_id)


@router.get("/is_need_to_fill_profile")
async def is_need_to_fill_profile(telegram_id: str):
    is_registered = await auth_repository.is_user_registered(telegram_id=telegram_id)
    if not is_registered:
        raise HTTPException(status_code=404, detail="User not found")
    participant_id = await participant_repository.get_participant_id(telegram_id)
    return await participant_repository.is_need_to_fill_profile(participant_id)


@router.post("/validate_code")
async def validate_code(
    email: str,
    code: str,
    telegram_id: str,
):
    if await auth_repository.is_code_valid(email, code):
        await auth_repository.delete_code(email)
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
