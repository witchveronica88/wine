# Wine

A personal wine-tasting log served by GitHub Pages at https://witchveronica88.github.io/wine/.
The UI is in Korean. Write user-facing text in Korean, matching the tone of the existing records.

## Publishing changes

The owner wants every change live right away: commit and push straight to `main`, without creating branches or pull requests. GitHub Pages deploys `main` within a minute or two.

Browsers may keep the previous `index.html` for up to 10 minutes after a deploy (GitHub Pages sends `max-age=600`), while `data/*.json` is always fetched fresh. So:
- When the shape of a data file changes, the new `index.html` must still read the old shape, and the old shape should keep working for a while (prefer adding fields over renaming or removing them).
- Refreshing: browser pull-to-refresh is blocked (`overscroll-behavior: none`) and the home-screen app has no reload button, so the app has its own pull-to-refresh: pulling down at the top and releasing past 72px reloads a fresh page (same `?r=…` URL as below) and keeps the current bottom tab. Coming back to the app after more than a minute re-fetches `wines.json` and `notes.json` quietly and redraws in place when something changed.
- Old copies of the app: on start and on coming back, the app fetches `index.html?v=…` (no-store) and compares its `<style>` and `<script>` text with its own. If they differ, it reloads a fresh page (at most once per 5 minutes, sessionStorage `wine-stale-reload`). So a phone never stays on an old version for long; you don't need to bump any version number.
- If loading fails, the app reloads itself once at a fresh URL (`?r=…`, guarded by sessionStorage `wine-fresh-reload`), then shows the error screen. 기록 never waits on `notes.json`: if only the notes fail, records still show and the note tabs say so.

## Layout

- `index.html`: the whole app (CSS + vanilla JS, no build step). At startup it loads `data/wines.json` and `data/notes.json` with `fetch`.
- `data/wines.json`: every wine record, shared across devices. This is the source of truth.
- `data/notes.json`: the study-note index. `varietyRows` (품종, `[title, english, summary, aliases, "레드"|"화이트"]`), `regionRows` (산지, `[page, title, subtitle, summary, aliases, country]`) and `basicRows` (사전, `[page, group, title, summary]`; `page` is the `assets/notes/basics/p-NN.webp` number). Keep one note per subject: a grape lives only in 품종, so 사전 has no grape entries.
- `photos/NNN.webp` and `photos/NNN-thumb.webp`: the bottle photo for wine id NNN, zero-padded to 3 digits.
- `assets/notes/<kind>/p-NN.webp`: study-note page images. **Not in the repo yet.** The app keeps each page image hidden until it has actually loaded, so nothing shows (no empty box, no flash) while the files are missing.
- `tools/add_photo.py`: converts a photo into the two webp files.
- `tools/check.py`: validates `data/wines.json`. Run it before every commit.

Records saved from the in-app form exist only in that browser's localStorage (`wine-local-v2`: `{added, edited, deleted}` layered over the repo data). They never reach the repo by themselves.

## 입력 규칙 (Adding a wine)

A record has two kinds of information: what the owner tells you (내 기록) and what you research (조사). Never mix them: research never goes into the owner's fields, and the owner's fields are never invented.

### What the owner sends

Only the photo and the date are needed. The owner can copy this template (it is also in README.md):

```
사진: 라벨 앞면 (뒷면이 있으면 같이)
마신 날: 2026-10-21
마신 곳:
별점: 5점 만점, 0.5 단위
한줄평:
메모: 함께 먹은 음식, 같이 마신 사람 등
산 곳·가격:
```

If something is missing, leave the field empty. Don't ask again for optional fields.

### What you fill in

Read the label first (name, producer, vintage, region, alcohol, volume), then research the rest. Prefer sources for the same vintage; when you have to use another vintage or a general source, say so once in `basis_note`. Convert foreign prices to KRW and record the date in `exchange_rate_date`.

### Fields, by where they show

Every record has exactly these fields, in this order (`tools/check.py` enforces it). Empty text is `""`, an unknown number is `null`.

| section | field | rule |
| --- | --- | --- |
| 병 정보 (label) | `id` | integer, next free id (`python3 tools/check.py` prints it) |
| | `name` | as printed on the label |
| | `producer` | Korean name, then the original in brackets: `케이머스 빈야드(Caymus Vineyards)` |
| | `country`, `region` | Korean. Use the names in `data/notes.json` so they link (see "Links from a wine to its notes") |
| | `grapes` | Korean names with percentages when known: `카베르네 소비뇽 85% · 시라 10% · 카르메네르 5%` |
| | `vintage` | `"2023"`, or `""` for NV / unknown |
| | `wine_type` | `red`, `white`, `sparkling`, `rose`, `orange`, `dessert` or `fortified` |
| | `alcohol_percent`, `volume_ml` | `"13.5%"`, `750` |
| | `photo_url`, `photo_thumbnail_url` | `photos/NNN.webp`, `photos/NNN-thumb.webp` (made by `tools/add_photo.py`) |
| 내 기록 (owner) | `consumed_date` | `YYYY-MM-DD`, required |
| | `place` | where it was drunk, short: `JW 메리어트 홍콩 라운지` |
| | `rating` | stars × 2 (1–10), or `null` |
| | `my_comment` | the owner's one-line review, in their words |
| | `personal_notes` | the owner's memo (food, company, situation) |
| | `price_krw`, `purchase_place` | what the owner paid and where, or `null` / `""` |
| 시음 노트 (research) | `aroma`, `taste`, `finish`, `food_pairing` | one to three plain sentences each, ending in "~다." No source talk inside the text |
| | `sweetness`, `acidity`, `tannin`, `body`, `finish_intensity` | 1–5, or `null` |
| | `basis_note` | one sentence when the tasting text isn't from this vintage: `향·맛은 다른 빈티지 자료 기준이다.` |
| 점수 (research) | `scores` | list of `{source, vintage, score, ratingCount, note}`, all strings. `vintage` is a year, `통산` or `미상` |
| 구매 판단 (research) | `buy_verdict` | lines starting with `• `. Line 1: one sentence on whether it is worth buying and at what price, ending in "~다." Each following line: one piece of evidence (one price with its KRW conversion, or one reason) |
| | `exchange_rate_date` | `YYYY-MM-DD` the prices were converted at, or `null` |
| 조사 메모 (research) | `info_notes` | `• ` lines, one fact each (producer story, vineyard, vintage, method, serving). Don't repeat the 병 정보 |
| system | `created_at`, `updated_at` | ISO timestamps. Bump `updated_at` on every edit |

### Steps

1. `python3 tools/check.py` for the next id.
2. Look at the photo, crop to the bottle if needed, then `python3 tools/add_photo.py <image> <id>`.
3. Add the record to `data/wines.json` (sorted by `id`, 2-space indent, `ensure_ascii=False`). If a grape or region has no study note, add one (see "Links from a wine to its notes").
4. `python3 tools/check.py` must say `ok`. Its warnings list grapes and regions with no note; add notes for them unless they are minor blend parts.
5. Commit the JSON and the photos together and push to `main`.

Never paste base64 images into JSON or HTML.

Editing a record that a device has also edited locally: the device keeps showing its own copy until the user taps "원래 기록으로 되돌리기" at the bottom of the opened wine.

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

Width: content and the fixed bottom tab bar share one maximum width, `--content-max` (720px, same as classic), centered. Phones fill the screen. Anything fixed or sticky (bottom tab bar, pill-tab row, sticky titles) must line up with the content edges; check at 360px, a 800px portrait tablet and a 1280px landscape tablet.

### Screen title (화면 맨 위 제목)

- Every screen starts with the same small centered title in `.brand-row`: "와인 노트", `--fs-l` bold, with a thin double-line decoration on both sides. About 12px above and below.
- The title is not sticky. It scrolls away and only the tab row stays at the top.
- There is no in-app add, edit or delete. The owner asks Claude, and Claude changes `data/wines.json` (and `photos/`) in the repo. An opened wine only shows "원래 기록으로 되돌리기" / "이 기기에서 지우기" for leftover device-only changes from before.

### Fold cards (카드 규칙)

Both main screens follow the card rules shared with the classic and princess repos (classic is the reference).

Common:
- A row of pill tabs under the search box, sticky at the top and scrollable sideways. The selected tab is scrolled into view.
- Below it, one card (`.fold-card`) with no head: full-width rows separated by thin lines, at least 44px tall. Gray group labels (`--fs-s` bold) split the rows.
- No repeated information. A count already shown on a pill is not shown again (no count badge), there is no card title that repeats the picked pill, and no one-line descriptions or "검색 결과" captions. Before adding a label, caption or count, check that the same thing isn't already on screen.
- Cards: radius `--card-radius` (16px), padding `--card-pad` (20px), 16px between cards. One accent color. Pill shapes only for tabs and filter chips.
- Every color is a `:root` token with a dark-mode value.

와인 기록:
- Tabs are the wine-type filters (전체, 레드, 화이트 …) with counts, plain text with no colored dots.
- Sorted by date (최근 마신 순), each year is its own card (`wineCardsHTML`), 16px apart, newest year first. Each card starts with a gray year label row ("2026년"); the first card's label row also holds the sort menu on the right (최근 마신 순 · 이름 순; 평점 높은 순 appears only once some wine has a rating). Other sorts show one card with no year label.
- Wine rows follow the princess book rows: a small photo (40×56, 4px corners, light shadow), the name (`--fs-m` bold), one gray line (type · vintage · country), and on the right the date with ＋ under it. Rows sit inside the card with dividers, not in separate boxes. No colored type dots anywhere, and no grape list or tasting text in the row.
- Sorted by date, the row date is month.day (the card already says the year). Other sorts show a short year (26.10.5).
- Tapping a row opens it in place (first level: full-width title background + accent bar, sticky under the tab row). There is no separate detail page. Only one wine and one inner section are open at a time. A link from a study note switches to 와인 기록, clears the filters and search, opens that wine and scrolls to it.

Bottom tabs: 기록 · 품종 · 산지 · 사전 (4 tabs). The app opens on 기록 (a pull-to-refresh keeps the current tab). Each tab keeps its own scroll position while the app is open.

Search (통합 검색): every tab has the same search box ("와인, 품종, 산지, 개념 검색"), and it always searches everything at once. While there is a query, the pill row and the tab's card are replaced by one card per kind that has hits, in tab order, each starting with a gray label ("와인 기록 · 2병", "품종 · 3종", "산지 · 1곳", "사전 · n개"). Search also looks inside the note details. Rows in the results open in place like everywhere else. Clearing the box or switching bottom tabs ends the search.

품종 · 산지 · 사전 (note tabs, `noteTabs` in `index.html`):
- The pill row holds the groups of that tab with counts: 품종 = 전체 · 레드 · 화이트 (split by the `whiteVarieties` list); 산지 = 전체 · countries in note order (`regionCountry`, from the note page number); 사전 = 전체 · 종류 · 맛과 향 · 마시기 · 용어 (the `group` in each `basicRows` entry). The group comes from the row itself (variety color, region country); `whiteVarieties` and `regionCountry` in `index.html` are only fallbacks for an older notes.json.
- One level of note ＋ rows. Under 전체, a gray group label (like the year label in 와인 기록) starts each group.
- Switching bottom tabs closes the open note.
- Only one note is open at a time. Opening a note from a wine record switches to its tab, picks its group pill, opens the note and scrolls to it.
- A collapsed note row shows only the name (`--fs-m`, bold) and a short gray summary (`--fs-s`: English name, record count). Never put the note text in a collapsed row; it shows at the top of the opened row.
- Opened state: ＋ becomes －, the title color stays the same, only the title row gets `--disclosure-bg` across the full card width, a 3px `--accent` bar runs down the left edge of the opened range, and the title sticks just under the pill row (`--stick`). Tapping a stuck title to fold scrolls back to that title.
- An opened note shows, in order: the details in the label-column format (see the common format below), starting with the row's `summary` as the first item (label 특징 for 품종 · 산지, 뜻 for 사전), then the wines I've had with this grape or region (only when there are any), newest first. No heading: each row is the date (`--fs-s` gray, 84px column) then the wine name (`--fs-m` regular, `--accent` color so it reads as a link), and rows are divided by lines that run the full card width. No photo, no vintage, no bold, no arrow. The last row's line is the next note's line, so there is never a double line.
- Note details live in `data/notes.json` → `details.<kind>.<title>` as `[label, text]` pairs. 품종: 향 · 구조 · 산지 · 음식. 산지: 환경 · 품종 · 스타일 · 정보. 사전: 설명 · 정보. Keep labels short (one word, two or three syllables) and don't reuse 특징 or 뜻, which are taken by the summary. One or two plain sentences each, ending in "~다." When adding a note, add its details too.

### Links from a wine to its notes

- In 지역 and 품종 facts the text stays as written, and only the part that names a note is shown in `--accent` color (no bold, no icon). Tapping it opens that note in its tab. Example: "토카이(토카이-헤저여)" → only "토카이" is colored.
- Matching (`matchNotesInText`) checks each note's title, English name and aliases, ignoring spaces, "·", "-", "/" and brackets. When names overlap the longer one wins ("쁘띠 시라" beats "시라"), and each note is linked once, at its first appearance. The same matching decides which wines an opened note lists.
- Links go both ways and everywhere text is shown (`linkAllNotes`): every 품종, 산지 and 사전 name found in a note's 특징/뜻 and details, and in a wine's 한줄평, 내 메모, 시음 노트, 구매 판단 and 조사 메모, is colored the same way and opens its note. Rules:
  - A note never links to itself, and within one block (one opened note, or one opened wine section) each note is linked only at its first appearance, so the text doesn't turn all green.
  - Overlaps: the longer name wins; at equal length an exact note title beats an alias, then 품종/산지 beat 사전 (so "샴페인" opens the 사전 note, not 샹파뉴 via its alias).
  - Names shorter than two characters (사전 "색") are never matched.
  - 지역 and 품종 facts keep their own matching above (one kind each).
- Every grape and region in `data/wines.json` should link. When a new wine brings a grape or region with no note, add the note (row + details) to `data/notes.json`; when it is only a different spelling ("카버네 소비뇽", "비우라"), add an alias instead. Don't add an alias that names a wider area than the note ("토스카나" is not 키안티).

### 펼친 내용의 공통 서식 (노트 · 와인)

An opened note and an opened wine use the same pieces, so the same kind of text always looks the same:

- **One-line summary** at the top of an opened wine: the owner's rating and `my_comment` (nothing when the owner gave neither), `--fs-m` regular, 16px above the next part. A note has no separate summary line: its `summary` is the first label-column item (특징 / 뜻).
- **Label column** — one format for every labelled piece, prose or short fact: the label sits in a 64px left column (`--fs-s` gray bold, `word-break: keep-all` in case a longer label ever comes back), the content on the right in `--fs-m` regular, first lines on the same baseline, 16px between items, no dividers, no boxes.
  - Text items (`textItemsHTML`, `.text-items`): note summary + details and the wine's 시음 노트.
  - Short facts (`.wine-facts`): the wine's basic facts (생산자, 도수 …), 6px apart.
- Anything inside an item stays in the right column in regular weight. The wine's 구조 item holds thin bars (6px) with gray `--fs-s` regular names (당도 · 산도 · 타닌 · 바디 · 여운) and gray numbers, so they never look like item labels.
- **Bullets** (`.note-list`): one fact per bullet, accent markers.
- Same idea, same label in both places: 구조 (note text / wine bars) and 음식 (note text / wine `food_pairing`). Use these names; don't say 페어링 in one place and 음식 in another.

### 와인 안쪽 내용 (펼친 와인)

Every opened wine uses the same order. Skip any part that has no data.

1. Bottle photo (`photo_url`), with pinch zoom.
2. 내 평가: the owner's ★ rating and `my_comment` on one line (the one-line summary format above). Shown only when the owner gave them. This spot is for the owner's own words; the researched buy verdict lives in 구매 판단.
3. Basic facts, always visible: short facts in the label-column format above, no dividers. Order: 생산자 · 지역 · 품종 · 도수 · 용량 · 마신 날 · 마신 곳 · 구매 (price · place). 나라 and 빈티지 are left out because the sticky wine row above already shows type · vintage · country. 지역 and 품종 link to their study notes. Short facts only, never prose.
4. Inner ＋ rows, closed by default, in this order:
   - 내 메모 (`personal_notes`)
   - 시음 노트: label-column items in this order: 향 · 맛 · 구조 (the 당도 · 산도 · 타닌 · 바디 · 여운 bars) · 여운 · 음식 (`food_pairing`), then `basis_note` as one gray `--fs-s` line
   - 점수: one divider row per score: the source (`--fs-m` bold) on the left and the score (`--fs-m` bold, accent) on the right, then one gray `--fs-s` line "vintage · count · note". No big numbers.
   - 구매 판단: the first line of `buy_verdict` (regular weight), the rest as bullets, then a gray "YYYY.MM.DD 환율 기준" line
   - 조사 메모 (`info_notes`) as bullets
   A collapsed inner row shows only its title (no counts or item lists). Inner rows follow the inner-level opened style: full-width background with the outer bar redrawn, sticky under the wine row, content indented 14px behind a 2px gray guide line.
5. No 수정 · 삭제 buttons. Only a leftover device-only change shows a small "원래 기록으로 되돌리기" or "이 기기에서 지우기" at the bottom.

- New information goes into one of the sections above, never a new box. If a new kind of section is really needed, add it as another inner ＋ row and list it here.
