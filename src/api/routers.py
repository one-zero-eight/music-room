from src.api.auth.routes import router as router_auth
from src.api.bookings.routes import router as router_booking
from src.api.users.routes import router as router_users
from src.api.root.routes import router as router_root

routers = [router_root, router_users, router_booking, router_auth]

__all__ = ["routers", *routers]
