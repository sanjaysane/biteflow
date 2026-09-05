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
    pattern = re.compile(
        r'''(?:\.t\(\s*\w+\s*,\s*|reply\(\s*|send_to\(\s*\w+\s*,\s*)"([a-z_]+)"'''
    )
    referenced: set[str] = set()
    for path in list(src.rglob("*.py")):
        referenced |= set(pattern.findall(path.read_text()))
    # f-string status keys: t(lang, f"status_{status}")
    for status in (
        "received",
        "accepted",
        "cooking",
        "out_for_delivery",
        "completed",
        "cancelled",
    ):
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


# ── Marathi (mr): declared partial locale with English fallback ──────────
# Policy (see BRIEF.md): en/es/hi keep strict key parity; mr covers the
# customer/prospect-facing demo keys, and I18n.t falls back to English for
# every key mr does not define. This is deliberate, not a parity hole.


def test_mr_is_subset_of_en():
    i18n = I18n(str(ROOT / "locales"))
    assert set(i18n.keys("mr")) <= set(i18n.keys("en")), "mr must not invent keys"


def test_mr_no_empty_strings():
    i18n = I18n(str(ROOT / "locales"))
    for key in i18n.keys("mr"):
        assert i18n.t("mr", key).strip(), f"mr.{key} is empty"


def test_mr_placeholder_parity_for_defined_keys():
    import re

    i18n = I18n(str(ROOT / "locales"))
    en = {k: i18n.t("en", k) for k in i18n.keys("en")}
    for key in i18n.keys("mr"):
        got = set(re.findall(r"\{([a-z_]+)\}", i18n.t("mr", key)))
        want = set(re.findall(r"\{([a-z_]+)\}", en[key]))
        assert got == want, f"mr.{key}: placeholders {got} != en {want}"


def test_mr_falls_back_to_english_for_missing_keys():
    i18n = I18n(str(ROOT / "locales"))
    en_keys = set(i18n.keys("en"))
    mr_keys = set(i18n.keys("mr"))
    missing = sorted(en_keys - mr_keys)
    assert missing, "expected mr to be partial (some keys missing)"
    for key in missing[:25]:
        assert i18n.t("mr", key) == i18n.t("en", key), f"no fallback for {key}"


def test_language_menu_lists_four_languages():
    i18n = I18n(str(ROOT / "locales"))
    for lang in ("en", "es", "hi", "mr"):
        menu = i18n.t(lang, "language_menu")
        assert "4" in menu and "मराठी" in menu, f"{lang} menu missing Marathi"
