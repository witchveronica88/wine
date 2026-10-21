#!/usr/bin/env python3
"""Validate data/wines.json (and its links to data/notes.json) before committing.

usage: python3 tools/check.py

Problems stop the commit (exit 1). Warnings are things to look at but may be fine.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"red", "white", "sparkling", "rose", "orange", "dessert", "fortified"}
TASTE = ["sweetness", "acidity", "tannin", "body", "finish_intensity"]
# every record has exactly these fields, in this order (see CLAUDE.md "입력 규칙")
FIELDS = [
    "id", "name", "producer", "country", "region", "grapes", "vintage", "wine_type", "alcohol_percent", "volume_ml",
    "photo_url", "photo_thumbnail_url",
    "consumed_date", "place", "rating", "my_comment", "personal_notes", "price_krw", "purchase_place",
    "aroma", "taste", "finish", "food_pairing", *TASTE, "basis_note",
    "scores", "buy_verdict", "exchange_rate_date", "info_notes",
    "created_at", "updated_at",
]
REQUIRED = ["id", "name", "wine_type", "consumed_date", "created_at", "updated_at"]
CAVEAT = re.compile(r"(빈티지\s*자료|기술\s*자료|자료(를)?\s*기준)")
SEPARATORS = r"[\s·.,()\-_/]"


def norm(text):
    return re.sub(SEPARATORS, "", str(text).lower())


def note_names(notes):
    """kind -> list of normalized names (title, English name, aliases)."""
    varieties = [n for r in notes["varietyRows"] for n in [r[0], r[1], *r[3]]]
    regions = [n for r in notes["regionRows"] for n in [r[1], r[2], *r[4]]]
    return {"grapes": [norm(n) for n in varieties if len(norm(n)) > 1],
            "region": [norm(n) for n in regions if len(norm(n)) > 1]}


def unlinked_grapes(text, names):
    parts = re.split(r"[,·:]|\s{2,}", re.sub(r"\(.*?\)|\d+(?:[.,]\d+)?\s*%", " ", text))
    out = []
    for part in parts:
        word = norm(part)
        if len(word) > 1 and not any(n in word for n in names) and not re.search(r"베이스와인|아수담금|비율|미확인|기준", word):
            out.append(part.strip())
    return out


def main():
    wines = json.loads((ROOT / "data" / "wines.json").read_text(encoding="utf-8"))
    notes = json.loads((ROOT / "data" / "notes.json").read_text(encoding="utf-8"))
    names = note_names(notes)
    problems, warnings = [], []
    seen = set()
    for wine in wines:
        label = "#%s %s" % (wine.get("id", "?"), wine.get("name", "(no name)"))
        missing = [k for k in FIELDS if k not in wine]
        unknown = [k for k in wine if k not in FIELDS]
        if missing:
            problems.append("%s: missing fields %s" % (label, missing))
        if unknown:
            problems.append("%s: unknown fields %s" % (label, unknown))
        for key in REQUIRED:
            if not wine.get(key):
                problems.append("%s: %s is required" % (label, key))
        if not isinstance(wine.get("id"), int):
            problems.append("%s: id must be an integer" % label)
        elif wine["id"] in seen:
            problems.append("%s: duplicate id" % label)
        seen.add(wine.get("id"))
        if wine.get("wine_type") not in TYPES:
            problems.append("%s: wine_type must be one of %s" % (label, sorted(TYPES)))
        for key in TASTE:
            value = wine.get(key)
            if value is not None and value not in (1, 2, 3, 4, 5):
                problems.append("%s: %s must be 1-5 or null" % (label, key))
        rating = wine.get("rating")
        if rating is not None and rating not in range(1, 11):
            problems.append("%s: rating is stars x 2 (1-10) or null" % label)
        for key in ("photo_url", "photo_thumbnail_url"):
            path = wine.get(key)
            if path and str(path).startswith("data:"):
                problems.append("%s: %s must be a file in photos/, not a data URI" % (label, key))
            elif path and not (ROOT / path).is_file():
                problems.append("%s: %s not found: %s" % (label, key, path))
        verdict = [line for line in str(wine.get("buy_verdict") or "").split("\n") if line.strip()]
        if not verdict:
            problems.append("%s: buy_verdict needs at least the verdict line" % label)
        elif not re.match(r"^• .+다\.$", verdict[0]):
            problems.append("%s: buy_verdict first line must be '• … 다.' (one buy/don't-buy sentence)" % label)
        for key in ("aroma", "taste"):
            if CAVEAT.search(str(wine.get(key) or "")):
                problems.append("%s: %s mentions its source; put that in basis_note" % (label, key))
        if wine.get("region") and not any(n in norm(wine["region"]) for n in names["region"]):
            warnings.append("%s: region has no study note: %s" % (label, wine["region"]))
        for grape in unlinked_grapes(str(wine.get("grapes") or ""), names["grapes"]):
            warnings.append("%s: grape has no study note: %s" % (label, grape))
    for line in warnings:
        print("warning:", line)
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print("ok: %d wines, next id %d" % (len(wines), max(seen) + 1))


if __name__ == "__main__":
    main()
