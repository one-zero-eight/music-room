from starlette.background import BackgroundTasks

from api.auth import router
from api.auth.service import generate_temporary_code, send_email
from api.dependencies import AUTH_REPOSITORY_DEPENDENCY, PARTICIPANT_REPOSITORY_DEPENDENCY
from api.exceptions import InvalidCode, UserExists


@router.post("/registration")
async def registration(background_task: BackgroundTasks, email: str, auth_repository: AUTH_REPOSITORY_DEPENDENCY):
    if await auth_repository.is_user_registered(email):
        raise UserExists()
    else:
        code = generate_temporary_code()
        await auth_repository.save_code(email, code)
        background_task.add_task(await send_email(email, code))


@router.post("/validate_code")
async def validate_code(email: str, code: str, auth_repository: AUTH_REPOSITORY_DEPENDENCY,
                        participant_repository: PARTICIPANT_REPOSITORY_DEPENDENCY):
    if await auth_repository.is_code_valid(email, code):
        participant_repository.create()
    else:
        raise InvalidCode()
