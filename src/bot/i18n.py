import os
from typing import Any, Dict, Protocol

from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text
from fluent.runtime import FluentLocalization, FluentResourceLoader

from src.bot.constants import DIALOG_I18N_FORMAT_KEY
from src.bot.middlewares import DialogI18nMiddleware

DEFAULT_LOCALE = "en"
LOCALES = ["en", "ru"]


class Values(Protocol):
    def __getitem__(self, item: Any) -> Any:
        raise NotImplementedError


class I18NFormat(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when)
        self.text = text

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        format_text = manager.middleware_data.get(
            DIALOG_I18N_FORMAT_KEY,
            default_format_text,
        )
        return format_text(self.text, data)


def default_format_text(text: str, data: Values) -> str:
    return text.format_map(data)


def make_i18n_middleware():
    loader = FluentResourceLoader(
        os.path.join(
            os.getcwd(),
            "locales",
            "{locale}",
            "LC_MESSAGES",
        )
    )
    l10ns = {
        locale: FluentLocalization(
            [locale, DEFAULT_LOCALE],
            ["dialog.ftl"],
            loader,
        )
        for locale in LOCALES
    }
    return DialogI18nMiddleware(l10ns, DEFAULT_LOCALE)
