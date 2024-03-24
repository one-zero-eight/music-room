from aiogram import Router

router = Router(name="booking")

import src.bot.routers.booking.create_booking_routes  # noqa
import src.bot.routers.booking.my_bookings_routes  # noqa
