__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Root"])

import src.api.root.routes  # noqa: E402, F401
