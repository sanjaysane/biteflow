"""Multilingual layer.

- `I18n.t(lang, key, **kwargs)` renders a template with `{placeholders}`.
- Falls back: requested language → English → the key itself (never crashes).
- `resolve_language()` picks the chat language: explicit session override,
  else the user's DB preference, else the configured default.

Locale files live in locales/{en,es,hi}.json and MUST share identical keys;
tests enforce this.
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import SUPPORTED_LANGUAGES


class I18n:
    def __init__(self, locales_dir: str | Path) -> None:
        self._tables: dict[str, dict[str, str]] = {}
        base = Path(locales_dir)
        for lang in SUPPORTED_LANGUAGES:
            path = base / f"{lang}.json"
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise TypeError(f"Locale file {path} must be a JSON object")
            self._tables[lang] = {k: str(v) for k, v in data.items()}

    @property
    def languages(self) -> tuple[str, ...]:
        return tuple(self._tables)

    def keys(self, lang: str = "en") -> set[str]:
        return set(self._tables[lang])

    def t(self, lang: str, key: str, **kwargs) -> str:
        table = self._tables.get(lang) or {}
        template = table.get(key)
        if template is None:
            template = self._tables["en"].get(key, key)
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            # A bad placeholder must never break a chat loop; fall back
            # to the raw template so the failure is visible, not silent.
            return template


def resolve_language(
    user: dict | None, session: dict | None, default: str = "en"
) -> str:
    """Priority: live session override → stored user preference → default."""
    for source in (session, user):
        if source:
            lang = source.get("lang") or source.get("preferred_language")
            if lang in SUPPORTED_LANGUAGES:
                return lang
    return default if default in SUPPORTED_LANGUAGES else "en"
