import datetime
from typing import Any

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.kbd import Back, Button, Group, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format

from src.bot import constants
from src.bot.api import api_client
from src.bot.routers.booking import router
from src.bot.routers.booking.states import CreateBookingStates
from src.bot.routers.booking.widgets.calendar import CustomCalendar
from src.bot.routers.booking.widgets.time_range import TimeRangeWidget


@router.message(any_state, Command("create_booking"))
@router.message(any_state, F.text == constants.create_booking_message)
async def start_booking(_message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        CreateBookingStates.choose_date,
        mode=StartMode.NEW_STACK,
    )


async def on_date_selected(
    _callback: CallbackQuery,
    _widget,
    dialog_manager: DialogManager,
    selected_date: datetime.date,
):
    dialog_manager.dialog_data["selected_date"] = selected_date.isoformat()
    await dialog_manager.next()


async def on_time_confirmed(callback: CallbackQuery, _button: Button, dialog_manager: DialogManager):
    date_string: str = dialog_manager.dialog_data["selected_date"]
    date: datetime.datetime = datetime.datetime.fromisoformat(date_string)

    chosen_timeslots = time_selection_widget.get_selected_time_points(dialog_manager)

    if len(chosen_timeslots) != 2:
        await callback.message.answer("You must choose both start and end time")
        return
    start, end = chosen_timeslots
    success, error = await api_client.book(callback.from_user.id, date, start, end)

    if success:
        date_text = date.strftime("%B %d")
        timeslot_text = f"{start.isoformat(timespec='minutes')} - {end.isoformat(timespec='minutes')}"
        text = f"You have successfully booked on <b>{date_text}, {timeslot_text}</b>."
        await callback.message.answer(text, parse_mode="HTML")
        await dialog_manager.done()
    else:
        await callback.message.answer(f"Error occurred: {error}")
        widget = dialog_manager.find("time_selection")
        widget.reset(dialog_manager)
        await dialog_manager.switch_to(CreateBookingStates.choose_date)


async def clear_selection(callback: CallbackQuery, _button: Button, dialog_manager: DialogManager):
    widget = dialog_manager.find("time_selection")
    widget.reset(dialog_manager)


def generate_timeslots(start_time: datetime.time, end_time: datetime.time, interval: int) -> list[datetime.time]:
    """
    Generate timeslots from start_time to end_time with interval
    :param start_time: start time
    :param end_time: end time
    :param interval: interval in minutes
    :return: list of timeslots
    """
    timeslots = []
    current_time = start_time
    while current_time <= end_time:
        timeslots.append(current_time)
        current_time = (
            datetime.datetime.combine(datetime.datetime.today(), current_time) + datetime.timedelta(minutes=interval)
        ).time()
    return timeslots


date_selection = Window(
    Const("Please select a date:"),
    CustomCalendar(id="calendar", on_click=on_date_selected),
    Cancel(Const("❌")),
    state=CreateBookingStates.choose_date,
)

time_selection_widget = TimeRangeWidget(
    timepoints=generate_timeslots(datetime.time(7, 0), datetime.time(23, 00), 30),
    id="time_selection",
)


async def getter_for_time_selection(dialog_manager: DialogManager, event_from_user: User, **_kwargs) -> dict:
    dialog_data: dict = dialog_manager.dialog_data
    date: str = dialog_data["selected_date"]
    data: dict[str, Any] = {"selected_date": date}
    hours = await api_client.get_remaining_daily_hours(event_from_user.id, date)
    weekly_hours = await api_client.get_remaining_weekly_hours(event_from_user.id, date)
    hours = min(hours, weekly_hours)
    data["remaining_daily_hours"] = hours
    data["remaining_daily_hours_hours"] = int(hours)
    data["remaining_daily_hours_minutes"] = int((hours - data["remaining_daily_hours_hours"]) * 60)
    user = await api_client.get_me(event_from_user.id)
    data["status_of_user"] = "???" if user is None else user.status
    _, data["daily_bookings"] = await api_client.get_daily_bookings(date)
    return data


time_selection = Window(
    Format(
        "Please select a time slot for <b>{dialog_data[selected_date]}</b>." + " \u200D" * 53 + "\n"
        "You have <b>{remaining_daily_hours_hours:0.0f}h {remaining_daily_hours_minutes:0.0f}m</b> free.\n"
        "Your status is <b>{status_of_user}</b>.\n"
        "🟢 - booked by you\n"
        "🔴 - booked by someone else\n"
    ),
    Group(time_selection_widget, width=4),
    Row(
        Back(Const("🔙"), on_click=clear_selection),
        Button(Const("✅"), id="done", on_click=on_time_confirmed),
    ),
    getter=getter_for_time_selection,
    state=CreateBookingStates.choose_time,
    parse_mode="HTML",
)

dialog = Dialog(date_selection, time_selection)

router.include_router(dialog)
