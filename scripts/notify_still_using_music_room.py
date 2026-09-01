"""
One-off broadcast.

Ask every non-banned user whether they still want to use the music room, via a Yes/No
inline-keyboard poll -- but skip anyone with an active or still-upcoming booking
(time_end >= now), since they're obviously still using it. Everyone else gets the poll
and is immediately marked `is_using_music_room=False`; answering "Yes" (or making a new
booking) flips it back to True, otherwise they stay excluded from /users/export.

Users skipped because they have an active booking don't need the poll, but they still
get the Russian-full-name reminder if their stored profile name is in English -- they'd
otherwise never receive it (they're never asked the poll, so src/bot/routers/poll.py's
"Yes" handler, which is the other place this reminder fires, never runs for them).

Usage:
    uv run python scripts/notify_still_using_music_room.py            # send messages
    uv run python scripts/notify_still_using_music_room.py --dry-run  # just list targets
    uv run python scripts/notify_still_using_music_room.py --delay 0.2
"""

import argparse
import asyncio
import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))

from aiogram import Bot  # noqa: E402
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter  # noqa: E402

from src.bot import constants  # noqa: E402
from src.bot.routers.poll import build_still_using_keyboard  # noqa: E402
from src.bot.validators import is_english_name  # noqa: E402
from src.config import api_settings, bot_settings  # noqa: E402
from src.repositories.bookings.repository import booking_repository  # noqa: E402
from src.repositories.users.repository import user_repository  # noqa: E402
from src.schemas import UserStatus  # noqa: E402
from src.storage.sql import SQLAlchemyStorage  # noqa: E402


def setup_storage() -> SQLAlchemyStorage:
    if api_settings is None or bot_settings is None:
        raise SystemExit("`api_settings` and `bot_settings` must both be present in settings.yaml")
    storage = SQLAlchemyStorage.from_url(api_settings.db_url)
    user_repository.update_storage(storage)
    booking_repository.update_storage(storage)
    return storage


async def has_active_booking(user_id: int, now: datetime.datetime) -> bool:
    bookings = await booking_repository.get_user_bookings(user_id)
    return any(booking.time_end >= now for booking in bookings)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--delay", type=float, default=0.1, help="seconds between messages (default: 0.1)")
    parser.add_argument("--dry-run", action="store_true", help="only print who would be messaged")
    args = parser.parse_args()

    now = datetime.datetime.now()

    storage = setup_storage()
    bot = Bot(token=bot_settings.bot_token.get_secret_value())

    async def send(telegram_id: int, text: str, **kwargs) -> bool:
        try:
            await bot.send_message(telegram_id, text, **kwargs)
        except TelegramRetryAfter as exc:
            await asyncio.sleep(exc.retry_after)
            await bot.send_message(telegram_id, text, **kwargs)
        except TelegramForbiddenError:
            return False
        return True

    notified = name_reminded = skipped_banned = skipped_active_booking = failed = 0
    try:
        users = await user_repository.get_all_users()
        print(f"{len(users)} users total ({'dry run' if args.dry_run else 'live'})")

        for user in users:
            if user.status == UserStatus.BANNED:
                skipped_banned += 1
                continue

            if await has_active_booking(user.id, now):
                skipped_active_booking += 1
                if is_english_name(user.name):
                    if args.dry_run:
                        print(
                            f"  would remind to switch name to Russian (active booking): "
                            f"user_id={user.id} telegram_id={user.telegram_id} name={user.name!r}"
                        )
                        name_reminded += 1
                        continue
                    try:
                        sent = await send(user.telegram_id, constants.russian_name_reminder_message)
                    except Exception as exc:  # noqa: BLE001 - keep going through the rest of the users
                        print(f"  failed: user_id={user.id} telegram_id={user.telegram_id}: {exc}")
                        failed += 1
                        continue
                    if not sent:
                        print(f"  blocked by user: user_id={user.id} telegram_id={user.telegram_id}")
                        failed += 1
                        continue
                    print(f"  name-reminded: user_id={user.id} telegram_id={user.telegram_id} name={user.name!r}")
                    name_reminded += 1
                    await asyncio.sleep(args.delay)
                continue

            if args.dry_run:
                print(
                    f"  would notify (and mark is_using_music_room=False): "
                    f"user_id={user.id} telegram_id={user.telegram_id} name={user.name!r}"
                )
                notified += 1
                continue

            await user_repository.set_is_using_music_room(user_id=user.id, value=False)

            try:
                sent = await send(
                    user.telegram_id,
                    constants.still_using_poll_message,
                    reply_markup=build_still_using_keyboard(),
                )
            except Exception as exc:  # noqa: BLE001 - keep going through the rest of the users
                print(f"  failed: user_id={user.id} telegram_id={user.telegram_id}: {exc}")
                failed += 1
                continue
            if not sent:
                print(f"  blocked by user: user_id={user.id} telegram_id={user.telegram_id}")
                failed += 1
                continue

            print(f"  notified: user_id={user.id} telegram_id={user.telegram_id} name={user.name!r}")
            notified += 1
            await asyncio.sleep(args.delay)
    finally:
        await bot.session.close()
        await storage.close_connection()

    verb = "would notify" if args.dry_run else "notified"
    name_verb = "would name-remind" if args.dry_run else "name-reminded"
    print(
        f"\nDone. {verb}={notified}, {name_verb}={name_reminded}, skipped (banned)={skipped_banned}, "
        f"skipped (active booking)={skipped_active_booking}, failed={failed}"
    )


if __name__ == "__main__":
    asyncio.run(main())
