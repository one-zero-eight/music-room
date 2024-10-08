import datetime
from src.schemas.booking import ViewBooking
from src.repositories.users.repository import user_repository
from src.repositories.bookings.repository import booking_repository
from src.api.bot_client import tg_bot_client


class NotificationUseCase:
    async def get_user_id_and_telegram_id(self, bookings: list[ViewBooking]) -> dict:
        user_ids = [booking.user_id for booking in bookings]
        users = await user_repository.get_multiple_users(user_ids)
        if users is None:
            return dict()
        user_id_to_telegram_id = dict()
        for user in users:
            user_id_to_telegram_id[user.id] = user.telegram_id
        return user_id_to_telegram_id

    async def notify_users_about_upcoming_bookings(self) -> None:
        daily_bookings = await booking_repository.get_daily_bookings(datetime.datetime.now().date())
        user_id_to_telegram_id = await self.get_user_id_and_telegram_id(daily_bookings)
        now_datetime = datetime.datetime.now()
        for booking in daily_bookings:
            notification_time = booking.time_start - datetime.timedelta(hours=1)
            if datetime.timedelta(seconds=0) <= notification_time - now_datetime < datetime.timedelta(seconds=60):
                await tg_bot_client.notify_user_about_booking(user_id_to_telegram_id[booking.user_id], booking)


notification_use_case = NotificationUseCase()
