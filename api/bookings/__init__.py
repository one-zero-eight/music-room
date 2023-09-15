__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# Register all schemas and routes
# import schemas.booking  # noqa: E402, F401
import api.bookings.routes  # noqa: E402, F401
