import re

# One Cyrillic word, hyphens allowed inside it (e.g. "Иванова-Петрова"), no Latin letters or digits.
_RU_WORD = r"[А-Яа-яЁё]+(?:-[А-Яа-яЁё]+)*"
# A Russian full name: at least two space-separated Cyrillic words (first name + last name).
RUSSIAN_NAME_RE = re.compile(rf"^{_RU_WORD}(?: {_RU_WORD})+$")
_CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def is_russian_name(text: str | None) -> bool:
    if not text:
        return False
    normalized = re.sub(r"\s+", " ", text.strip())
    return RUSSIAN_NAME_RE.fullmatch(normalized) is not None


def is_english_name(text: str | None) -> bool:
    """A name written with Latin letters and not a single Cyrillic one."""
    return bool(text) and _LATIN_RE.search(text) is not None and _CYRILLIC_RE.search(text) is None
