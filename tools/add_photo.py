#!/usr/bin/env python3
"""Convert a wine photo into photos/NNN.webp and photos/NNN-thumb.webp.

usage: python3 tools/add_photo.py <image> <wine id>
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
FULL_MAX = 700
THUMB_MAX = 320


def save(img, max_side, path, quality):
    copy = img.copy()
    copy.thumbnail((max_side, max_side), Image.LANCZOS)
    copy.save(path, "WEBP", quality=quality, method=6)
    return copy.size


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.strip())
    src, wine_id = Path(sys.argv[1]), int(sys.argv[2])
    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    full = ROOT / "photos" / ("%03d.webp" % wine_id)
    thumb = ROOT / "photos" / ("%03d-thumb.webp" % wine_id)
    print(full.relative_to(ROOT), save(img, FULL_MAX, full, 80))
    print(thumb.relative_to(ROOT), save(img, THUMB_MAX, thumb, 75))
    print('"photo_url": "photos/%03d.webp",' % wine_id)
    print('"photo_thumbnail_url": "photos/%03d-thumb.webp",' % wine_id)


if __name__ == "__main__":
    main()
