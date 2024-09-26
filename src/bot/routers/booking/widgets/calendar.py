from datetime import datetime, timedelta

import pytz
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.kbd.calendar_kbd import Calendar, CalendarUserConfig


class CustomCalendar(Calendar):
    """
    Calendar widget.

    Used to render keyboard for date selection.
    """

    async def _get_user_config(
        self,
        data: dict,
        manager: DialogManager,
    ) -> CalendarUserConfig:
        """
        User related config getter.

        Override this method to customize how user config is retrieved.

        :param data: data from window getter
        :param manager: dialog manager instance
        :return:
        """
        now = datetime.now(tz=pytz.timezone("Europe/Moscow"))
        min_date = now.date()
        max_date = (now + timedelta(days=7)).date()
        return CalendarUserConfig(max_date=max_date, min_date=min_date)
