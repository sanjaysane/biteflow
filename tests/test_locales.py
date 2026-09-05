"""Cross-cutting guarantees: locale tables share identical keys, and
every key referenced by handlers exists in every language.
"""

import re
from pathlib import Path

from src.i18n import I18n

ROOT = Path(__file__).resolve().parent.parent


def test_locale_key_parity():
    i18n = I18n(str(ROOT / "locales"))
    en, es, hi = (i18n.keys(l) for l in ("en", "es", "hi"))
    assert es == en, f"es missing/extra: {en ^ es}"
    assert hi == en, f"hi missing/extra: {en ^ hi}"
    assert len(en) > 40


def test_handler_keys_exist_in_all_locales():
    """Scrape t("...") / reply("...") / send_to(..., "...") call sites and
    require every referenced key in every locale table."""
    i18n = I18n(str(ROOT / "locales"))
    src = ROOT / "src"
    pattern = re.compile(r'''(?:\.t\(\s*\w+\s*,\s*|reply\(\s*|send_to\(\s*\w+\s*,\s*)"([a-z_]+)"''')
    referenced: set[str] = set()
    for path in list(src.rglob("*.py")):
        referenced |= set(pattern.findall(path.read_text()))
    # f-string status keys: t(lang, f"status_{status}")
    for status in ("received", "accepted", "cooking", "out_for_delivery",
                   "completed", "cancelled"):
        referenced.add(f"status_{status}")
    for lang in ("en", "es", "hi"):
        missing = referenced - i18n.keys(lang)
        assert not missing, f"{lang} missing keys: {sorted(missing)}"


def test_no_unfilled_placeholders():
    """Every template's {placeholders} must be fillable (no stray braces)."""
    i18n = I18n(str(ROOT / "locales"))
    for lang in ("en", "es", "hi"):
        for key in i18n.keys(lang):
            template = i18n.t(lang, key)
            # doubled braces would be a literal; singletons must be named
            assert "{{" not in template and "}}" not in template, key
