from api.participants import router as router_participants
from api.bookings import router as router_booking

routers = [router_participants, router_booking]

__all__ = ["routers", *routers]
