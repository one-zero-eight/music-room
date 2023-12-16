from starlette.background import BackgroundTasks

from src.api.auth import router
from src.api.auth.service import generate_temporary_code, send_email
from src.api.dependencies import Dependencies
from src.exceptions import InvalidCode, UserExists
from src.schemas import CreateParticipant


@router.post("/registration")
async def registration(background_task: BackgroundTasks, email: str):
    auth_repository = Dependencies.get_auth_repository()

    if await auth_repository.is_user_registered(email, telegram_id=None):
        raise UserExists()
    else:
        code = await generate_temporary_code()
        await auth_repository.save_code(email, code)
        background_task.add_task(await send_email(email, code))


@router.get("/is_user_exists")
async def is_user_exists(email: str = None, telegram_id: str = None) -> bool:
    auth_repository = Dependencies.get_auth_repository()
    if await auth_repository.is_user_registered(email, telegram_id):
        return True
    return False


@router.post("/validate_code")
async def validate_code(
    email: str,
    code: str,
    telegram_id: str,
):
    auth_repository = Dependencies.get_auth_repository()
    participant_repository = Dependencies.get_participant_repository()

    if await auth_repository.is_code_valid(email, code):
        participant = CreateParticipant(
            email=email,
            need_to_fill_profile=True,
            status="free",
            telegram_id=telegram_id,
        )
        created = await participant_repository.create(participant)
        return created
    else:
        raise InvalidCode()
