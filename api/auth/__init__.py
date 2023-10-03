__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

import api.auth.routes  # noqa: E402, F401
