import asyncio
import inspect
import logging
import os
from collections.abc import Awaitable, Callable, Set
from typing import Any

from aiogram import BaseMiddleware, Router
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.types import CallbackQuery, Message, TelegramObject
from fluent.runtime import FluentLocalization

from src.bot.constants import DIALOG_I18N_FORMAT_KEY
from src.bot.logging_ import logger


# noinspection PyMethodMayBeStatic
class LogAllEventsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        r = await handler(event, data)
        finish_time = loop.time()
        duration = finish_time - start_time
        try:
            # get to `aiogram.dispatcher.event.TelegramEventObserver.trigger` method
            frame = inspect.currentframe()
            frame_info = inspect.getframeinfo(frame)
            while frame is not None:
                if frame_info.function == "trigger":
                    _handler = frame.f_locals.get("handler")
                    if _handler is not None:
                        _handler: HandlerObject
                        record = self._create_log_record(_handler, event, data, duration=duration)
                        logger.handle(record)
                    break
                frame = frame.f_back
                frame_info = inspect.getframeinfo(frame)
        finally:
            del frame
        return r

    def _create_log_record(
        self, handler: HandlerObject, event: TelegramObject, data: dict[str, Any], *, duration: float | None = None
    ) -> logging.LogRecord:
        callback = handler.callback
        func_name = callback.__name__
        pathname = inspect.getsourcefile(callback)
        lineno = inspect.getsourcelines(callback)[1]

        event_type = type(event).__name__
        username = event.from_user.username
        user_string = f"User @{username}<{event.from_user.id}>" if username else f"User <{event.from_user.id}>"

        if isinstance(event, Message):
            message_text = f"{event.text[:50]}..." if len(event.text) > 50 else event.text
            msg = f"{user_string}: [{event_type}] `{message_text}`"
        elif isinstance(event, CallbackQuery):
            msg = f"{user_string}: [{event_type}] `{event.data}`"
        else:
            msg = f"{user_string}: [{event_type}]"

        if duration is not None:
            msg = f"Handler `{func_name}` took {int(duration * 1000)} ms: {msg}"

        record = logging.LogRecord(
            name="src.bot.bot.middlewares.LogAllEventsMiddleware",
            level=logging.INFO,
            pathname=pathname,
            lineno=lineno,
            msg=msg,
            args=(),
            exc_info=None,
            func=func_name,
        )
        record.relativePath = os.path.relpath(record.pathname)
        return record


# That middleware used specifically for aiogram_dialog,
# since it does not support usual aiogram i18n
class DialogI18nMiddleware(BaseMiddleware):
    def __init__(
        self,
        l10ns: dict[str, FluentLocalization],
        default_lang: str,
    ):
        super().__init__()
        self.l10ns = l10ns
        self.default_lang = default_lang

    async def __call__(
        self,
        handler: Callable[
            [Message | CallbackQuery, dict[str, Any]],
            Awaitable[Any],
        ],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        lang = self.default_lang
        if hasattr(event, "from_user") and event.from_user:
            lang = event.from_user.language_code

        l10n = self.l10ns.get(lang, self.l10ns[self.default_lang])
        data[DIALOG_I18N_FORMAT_KEY] = l10n.format_value

        return await handler(event, data)

    def setup(
        self: BaseMiddleware,
        router: Router,
        exclude: Set[str] | None = None,
    ) -> BaseMiddleware:
        """
        Register middleware for all events in the Router
        """
        if exclude is None:
            exclude = set()
        exclude_events = {"update", *exclude}
        for event_name, observer in router.observers.items():
            if event_name in exclude_events:
                continue
            observer.outer_middleware(self)
        return self
