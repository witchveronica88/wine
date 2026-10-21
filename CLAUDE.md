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

## Design rules (디자인 규칙)

Text uses exactly four sizes. They are defined as tokens on `:root` in `index.html`, and every `font-size` must use one of these tokens, never a raw px value:

| token | size | use |
| --- | --- | --- |
| `--fs-xl` | 24px | screen titles, big numbers |
| `--fs-l` | 18px | section headings |
| `--fs-m` | 16px | body text, inputs (the base size; body text is never smaller) |
| `--fs-s` | 14px | secondary text: captions, notes, tables, tabs, dates, labels |

Pair each size with its line-height token (`--lh-xl`, `--lh-l`, `--lh-m`, `--lh-s`).

Pages must not scroll sideways at a 360px phone width.

### Screen title (화면 맨 위 제목)

- Each main screen starts with a small centered title in `.brand-row`: "와인 기록" / "와인 노트", `--fs-l` bold, with a thin double-line decoration on both sides. About 12px above and below.
- The title is not sticky. It scrolls away and only the tab row stays at the top.
- There is no in-app "add wine" button or form. The owner sends the details and Claude adds the record to `data/wines.json`. Editing and deleting on the detail page still work (local only).

### Fold cards (카드 규칙)

Both main screens follow the card rules shared with the classic and princess repos (classic is the reference).

Common:
- A row of pill tabs under the search box, sticky at the top and scrollable sideways. The selected tab is scrolled into view.
- Below it, one card (`.fold-card`): a head with the title (`--fs-l`, bold; same size as the screen title for now), a gray pill count badge on the right, a one-line gray description, then a thin line. Under the head, full-width rows separated by thin lines, at least 44px tall.
- Nested ＋ rows (none yet; follow this if one is added): the outer row keeps its full-width title background and the 3px accent bar. An inner opened title row gets `--disclosure-bg` only across the inner width (12px past the text on each side, 8px corners), no accent bar, and a 5px `--surface` box-shadow so text doesn't show around it while sticky. The inner row's content is indented 14px with a 2px `--border` guide line on its left.
- Cards: radius `--card-radius` (16px), padding `--card-pad` (20px), 16px between cards. One accent color. Pill shapes only for tabs, filter chips and badges.
- Every color is a `:root` token with a dark-mode value.

와인 기록:
- Tabs are the wine-type filters (전체, 레드, 화이트 …) with counts. The card title is "모든 와인" or "레드 와인" etc., the badge is the bottle count, and the description line holds the latest date and the sort menu.
- Wine rows (photo, type · vintage, name `--fs-m` bold, country · grape) sit inside the card with dividers, not in separate boxes. When sorted by date, a gray date label starts each day.
- Tapping a row opens the detail page, so these rows have › instead of ＋.

와인 노트:
- Tabs: 레드 품종 · 화이트 품종 · 프랑스 · 이탈리아 · 스페인 · 포르투갈 · 독일 · 오스트리아 · 헝가리 · 신대륙 · 기초 개념 (`noteTabs` in `index.html`). Varieties are split by the `whiteVarieties` list, and regions by country from their note page number (`regionCountry`). When a region note is added to `data/notes.json`, update `regionCountry` too.
- The last tab picked is remembered in localStorage `wine-notes-kind` (falls back to the first tab). Opening a note from a wine record switches to its tab and opens it.
- A collapsed row shows only the name (`--fs-m`, bold) and a short gray summary (`--fs-s`: country for mixed-country tabs, English name, record count). Never put the note text in a collapsed row; it shows at the top of the opened row.
- Opened row: ＋ becomes －, the title color stays the same, only the title row gets `--disclosure-bg`, and a 3px `--accent` bar runs down the left edge of the whole opened range. Content starts 14px below the title row's line. The opened title sticks just under the tab row, and tapping it to fold scrolls back to the title.
- Items inside an opened row (linked wine records) are divider rows, never bordered or filled boxes. Title `--fs-m` bold, date `--fs-s` gray below, vintage `--fs-s` gray on the right.

The detail page is a reading page with always-visible sections, so the fold-card rules don't apply there.
