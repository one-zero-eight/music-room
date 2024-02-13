from src.api.auth import router as router_auth
from src.api.bookings import router as router_booking
from src.api.participants import router as router_participants
from src.api.root import router as router_root

routers = [router_root, router_participants, router_booking, router_auth]

__all__ = ["routers", *routers]
