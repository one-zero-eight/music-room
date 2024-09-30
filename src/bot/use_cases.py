import asyncio
import datetime
from src.schemas.booking import ViewBooking
from src.bot.api import api_client
from aiogram import Bot


class NotificationUseCase:
    async def notify_user_about_booking(self, bot: Bot, booking: ViewBooking, user_id: int) -> None:
        now_datetime = datetime.datetime.now()
        seconds_to_wait = (booking.time_start - now_datetime - datetime.timedelta(hours=1)).seconds
        await asyncio.sleep(seconds_to_wait)
        status, _ = await api_client.get_booking_by_id(booking.id)
        if status:
            await bot.send_message(user_id, "Don't forget about your booking! It will start in an hour")

    async def get_user_id_and_telegram_id(self, bookings: dict) -> dict:
        user_ids = [booking["user_id"] for booking in bookings]
        users = await api_client.get_users(user_ids)
        if users is None:
            return dict()
        user_id_to_telegram_id = dict()
        for user in users:
            user_id_to_telegram_id[user["id"]] = user["telegram_id"]
        return user_id_to_telegram_id

    async def notify_users_about_upcoming_bookings(self, bot: Bot) -> None:
        status, weekly_bookings = await api_client.get_weekly_bookings(datetime.datetime.now().date())
        if not status:
            return
        user_id_to_telegram_id = await self.get_user_id_and_telegram_id(weekly_bookings)
        now_datetime = datetime.datetime.now()
        for booking in weekly_bookings:
            booking = ViewBooking(**booking)
            if booking.time_start - datetime.timedelta(hours=1) >= now_datetime:
                asyncio.create_task(
                    self.notify_user_about_booking(bot, booking, user_id_to_telegram_id[booking.user_id])
                )


notification_use_case = NotificationUseCase()
