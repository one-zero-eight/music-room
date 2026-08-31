"""
One-off broadcast.

Ask every user whose stored profile name is written in English (Latin letters, no
Cyrillic) to switch it to Russian -- but only if they actually used the music room
recently, i.e. they have at least one booking whose start time falls within the last
N months (default: 6).

Usage:
    uv run python scripts/notify_english_named_users.py            # send messages
    uv run python scripts/notify_english_named_users.py --dry-run  # just list targets
    uv run python scripts/notify_english_named_users.py --months 3 --delay 0.2
"""

import argparse
import asyncio
import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))

from aiogram import Bot  # noqa: E402
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter  # noqa: E402

from src.bot.validators import is_english_name  # noqa: E402
from src.config import api_settings, bot_settings  # noqa: E402
from src.repositories.bookings.repository import booking_repository  # noqa: E402
from src.repositories.users.repository import user_repository  # noqa: E402
from src.storage.sql import SQLAlchemyStorage  # noqa: E402

MESSAGE = (
    "Привет! Пожалуйста, укажите своё имя в профиле бота музыкальной комнаты на русском "
    "языке (кириллицей). Так администраторам проще сверять списки для доступа в "
    "спортивный комплекс.\n\n"
    "Откройте бота, начните бронирование командой /create_booking и введите своё полное "
    "имя на русском, когда бот попросит.\n\n"
    "— — —\n\n"
    "Hi! Please set your name in the music room bot profile in Russian (Cyrillic "
    "letters). It helps the administrators match the access lists for the sports "
    "complex.\n\n"
    "Open the bot, start a booking with /create_booking and type your full name in "
    "Russian when prompted."
)


def setup_storage() -> SQLAlchemyStorage:
    if api_settings is None or bot_settings is None:
        raise SystemExit("`api_settings` and `bot_settings` must both be present in settings.yaml")
    storage = SQLAlchemyStorage.from_url(api_settings.db_url)
    user_repository.update_storage(storage)
    booking_repository.update_storage(storage)
    return storage


async def has_recent_booking(user_id: int, cutoff: datetime.datetime) -> bool:
    bookings = await booking_repository.get_user_bookings(user_id)
    return any(cutoff <= booking.time_start for booking in bookings)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--months", type=float, default=6, help="look-back window in months (default: 6)")
    parser.add_argument("--delay", type=float, default=0.1, help="seconds between messages (default: 0.1)")
    parser.add_argument("--dry-run", action="store_true", help="only print who would be messaged")
    args = parser.parse_args()

    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=args.months * 30.4375)

    storage = setup_storage()
    bot = Bot(token=bot_settings.bot_token.get_secret_value())

    notified = skipped_name = skipped_no_booking = failed = 0
    try:
        users = await user_repository.get_all_users()
        print(f"{len(users)} users total; look-back since {cutoff:%Y-%m-%d} ({'dry run' if args.dry_run else 'live'})")

        for user in users:
            if not is_english_name(user.name):
                skipped_name += 1
                continue
            if not await has_recent_booking(user.id, cutoff):
                skipped_no_booking += 1
                continue

            if args.dry_run:
                print(f"  would notify: user_id={user.id} telegram_id={user.telegram_id} name={user.name!r}")
                notified += 1
                continue

            try:
                await bot.send_message(user.telegram_id, MESSAGE)
            except TelegramRetryAfter as exc:
                await asyncio.sleep(exc.retry_after)
                await bot.send_message(user.telegram_id, MESSAGE)
            except TelegramForbiddenError:
                print(f"  blocked by user: user_id={user.id} telegram_id={user.telegram_id}")
                failed += 1
                continue
            except Exception as exc:  # noqa: BLE001 - keep going through the rest of the users
                print(f"  failed: user_id={user.id} telegram_id={user.telegram_id}: {exc}")
                failed += 1
                continue

            print(f"  notified: user_id={user.id} telegram_id={user.telegram_id} name={user.name!r}")
            notified += 1
            await asyncio.sleep(args.delay)
    finally:
        await bot.session.close()
        await storage.close_connection()

    verb = "would notify" if args.dry_run else "notified"
    print(
        f"\nDone. {verb}={notified}, skipped (name not English)={skipped_name}, "
        f"skipped (no booking in window)={skipped_no_booking}, failed={failed}"
    )


if __name__ == "__main__":
    asyncio.run(main())
