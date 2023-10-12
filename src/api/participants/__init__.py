__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/participants", tags=["Participants"])

import src.api.participants.routes  # noqa: E402, F401
