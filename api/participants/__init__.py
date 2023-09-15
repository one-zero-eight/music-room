__all__ = ["router"]

from fastapi import APIRouter

router = APIRouter(prefix="/participants", tags=["Participants"])

# Register all schemas and routes
# import schemas.booking  # noqa: E402, F401
import api.participants.routes  # noqa: E402, F401
