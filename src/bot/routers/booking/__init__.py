from aiogram import Router

from src.bot.filters import FilledProfileFilter

router = Router()

router.message.filter(FilledProfileFilter())

import src.bot.routers.booking.create_booking_routes  # noqa
import src.bot.routers.booking.my_bookings_routes  # noqa
