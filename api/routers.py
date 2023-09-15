from api.participants import router as router_participants

routers = [router_participants]

__all__ = ["routers", *routers]
