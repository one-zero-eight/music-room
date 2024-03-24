from src.bot.routers.booking import router as router_bookings
from src.bot.routers.registration import router as router_registration
from src.bot.routers.schedule import router as router_image_schedule
from src.bot.routers.admin import router as router_admin

routers = [
    router_bookings,
    router_registration,
    router_image_schedule,
    router_admin,
]
