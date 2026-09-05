"""Fail if locales/en.json, es.json, hi.json don't share the exact same key
set, or if any key holds a different number of {placeholders} across
languages (a classic cause of runtime KeyError in translated strings).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ("en", "es", "hi")
PH = re.compile(r"\{(\w+)\}")


def main() -> None:
    tables = {}
    for lang in LOCALES:
        with open(ROOT / "locales" / f"{lang}.json", encoding="utf-8") as fh:
            tables[lang] = json.load(fh)
    keys = [set(t) for t in tables.values()]
    if not (keys[0] == keys[1] == keys[2]):
        for lang in LOCALES:
            missing = (keys[0] | keys[1] | keys[2]) - keys[LOCALES.index(lang)]
            if missing:
                print(f"{lang}.json missing keys: {sorted(missing)}", file=sys.stderr)
        sys.exit("locale keys diverged")
    bad = []
    for key in keys[0]:
        ph = {lang: set(PH.findall(str(tables[lang][key]))) for lang in LOCALES}
        if not (ph["en"] == ph["es"] == ph["hi"]):
            bad.append((key, ph))
    if bad:
        for key, ph in bad:
            print(f"placeholder mismatch on {key}: {ph}", file=sys.stderr)
        sys.exit("locale placeholders diverged")
    print(f"locales OK: {len(keys[0])} keys × 3 languages, placeholders consistent")


if __name__ == "__main__":
    main()
