from src.api.auth import router as router_auth
from src.api.bookings import router as router_booking
from src.api.participants import router as router_participants

routers = [router_participants, router_booking, router_auth]

__all__ = ["routers", *routers]
