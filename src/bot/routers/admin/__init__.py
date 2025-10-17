from aiogram import Router

router = Router(name="admin")

import src.bot.routers.admin.admin_routes  # noqa
