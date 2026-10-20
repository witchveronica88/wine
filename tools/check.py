#!/usr/bin/env python3
"""Validate data/wines.json before committing.

usage: python3 tools/check.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"red", "white", "sparkling", "rose", "orange", "dessert", "fortified"}
REQUIRED = ["id", "name", "wine_type", "consumed_date", "created_at", "updated_at"]
TASTE = ["sweetness", "acidity", "tannin", "body", "finish_intensity"]


def main():
    wines = json.loads((ROOT / "data" / "wines.json").read_text(encoding="utf-8"))
    problems = []
    seen = set()
    for i, wine in enumerate(wines):
        label = "#%s %s" % (wine.get("id", "?"), wine.get("name", "(no name)"))
        for key in REQUIRED:
            if not wine.get(key):
                problems.append("%s: missing %s" % (label, key))
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
        if rating is not None and rating not in range(2, 11):
            problems.append("%s: rating is 2-10 (stars x 2) or null" % label)
        for key in ("photo_url", "photo_thumbnail_url"):
            path = wine.get(key)
            if path and str(path).startswith("data:"):
                problems.append("%s: %s must be a file in photos/, not a data URI" % (label, key))
            elif path and not (ROOT / path).is_file():
                problems.append("%s: %s not found: %s" % (label, key, path))
    if problems:
        print("\n".join(problems))
        sys.exit(1)
    print("ok: %d wines, next id %d" % (len(wines), max(seen) + 1))


if __name__ == "__main__":
    main()
