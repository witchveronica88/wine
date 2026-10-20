# Wine

A personal wine-tasting log served by GitHub Pages at https://witchveronica88.github.io/wine/.
The UI is in Korean. Write user-facing text in Korean, matching the tone of the existing records.

## Publishing changes

The owner wants every change live right away: commit and push straight to `main`, without creating branches or pull requests. GitHub Pages deploys `main` within a minute or two.

## Layout

- `index.html`: the whole app (CSS + vanilla JS, no build step). At startup it loads `data/wines.json` and `data/notes.json` with `fetch`.
- `data/wines.json`: every wine record, shared across devices. This is the source of truth.
- `data/notes.json`: the study-note index (varieties, regions, basics).
- `photos/NNN.webp` and `photos/NNN-thumb.webp`: the bottle photo for wine id NNN, zero-padded to 3 digits.
- `assets/notes/<kind>/p-NN.webp`: study-note page images. **Not in the repo yet**, so the app shows an "image unavailable" box for them.
- `tools/add_photo.py`: converts a photo into the two webp files.
- `tools/check.py`: validates `data/wines.json`. Run it before every commit.

Records saved from the in-app form exist only in that browser's localStorage (`wine-local-v2`: `{added, edited, deleted}` layered over the repo data). They never reach the repo by themselves.

## Adding a wine

1. Find the next id. `python3 tools/check.py` prints it.
2. If there is a photo, run `python3 tools/add_photo.py <image> <id>`. Open the image first and crop it to the bottle if needed.
3. Add an object to `data/wines.json`. Keep the file sorted by `id` and use 2-space indent with `ensure_ascii=False`.
4. Run `python3 tools/check.py`.
5. Commit the JSON and the photos together and push to `main`.

Never paste base64 images into JSON or HTML.

### Record fields

| field | notes |
| --- | --- |
| `id` | integer, unique, increasing |
| `name` | label name, usually as printed on the bottle |
| `producer`, `country`, `region`, `grapes` | Korean text. `region` and `grapes` are matched against the study notes, so use the Korean names found in `data/notes.json` where possible |
| `grapes_label` | optional short grape name for the list row, when `grapes` is long |
| `vintage` | string such as `"2023"` |
| `wine_type` | `red`, `white`, `sparkling`, `rose`, `orange`, `dessert` or `fortified` |
| `consumed_date` | `YYYY-MM-DD`, the day it was drunk (required) |
| `volume_ml` | number or null |
| `alcohol_percent` | string such as `"13.5%"` |
| `aroma`, `taste`, `finish`, `food_pairing` | tasting prose |
| `sweetness`, `acidity`, `tannin`, `body`, `finish_intensity` | 1–5 or null |
| `scores` | list of `{source, vintage, score, ratingCount, note}`, all strings |
| `buy_verdict` | bullet lines (`• ...`) separated by `\n`. The first line is the verdict headline |
| `info_notes` | research bullets in the same format |
| `exchange_rate_date` | `YYYY-MM-DD` that prices in `buy_verdict` were converted at, or null |
| `price_krw`, `purchase_place` | what the owner paid, or null / "" |
| `rating` | the owner's stars × 2 (2–10), or null. Only fill it in when the owner gives a rating |
| `personal_notes` | the owner's own memo. Never invent it |
| `basis_note` | optional caveat shown under the aroma and taste text, e.g. `"다른 빈티지 자료 기준"` |
| `photo_url`, `photo_thumbnail_url` | `photos/NNN.webp` / `photos/NNN-thumb.webp`, or null |
| `created_at`, `updated_at` | ISO timestamps. Bump `updated_at` when editing a record |

Editing a record that a device has also edited locally: the device keeps showing its own copy until the user taps "원래 기록으로 되돌리기" on the detail page.

## Checking the app

```sh
python3 -m http.server 8765   # then open http://localhost:8765/
```

`fetch` does not work from `file://`, so always use a local server.

## Font size

- The base body text size is 16px. Never make body text smaller than 16px.
- Use sizes below 16px only for secondary text such as dates, labels and captions.
