__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["Bookings"])

import src.api.bookings.routes  # noqa: E402, F401
