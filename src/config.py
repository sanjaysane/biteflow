"""Environment-driven configuration. All secrets come from env vars —
nothing is hardcoded. See .env.example for the full list."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


@dataclass
class Settings:
    whatsapp_token: str = field(default_factory=lambda: _get("WHATSAPP_TOKEN"))
    whatsapp_phone_number_id: str = field(
        default_factory=lambda: _get("WHATSAPP_PHONE_NUMBER_ID")
    )
    whatsapp_api_version: str = field(
        default_factory=lambda: _get("WHATSAPP_API_VERSION", "v21.0")
    )
    webhook_verify_token: str = field(
        default_factory=lambda: _get("WEBHOOK_VERIFY_TOKEN")
    )
    database_url: str = field(default_factory=lambda: _get("DATABASE_URL"))
    locales_dir: str = field(default_factory=lambda: _get("LOCALES_DIR", "locales"))
    default_language: str = field(
        default_factory=lambda: _get("DEFAULT_LANGUAGE", "en")
    )
    cook_allowlist: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        raw = _get("COOK_ALLOWLIST")
        if raw:
            object.__setattr__(
                self, "cook_allowlist", tuple(p.strip() for p in raw.split(",") if p.strip())
            )

    @property
    def whatsapp_api_base(self) -> str:
        return f"https://graph.facebook.com/{self.whatsapp_api_version}"


settings = Settings()
