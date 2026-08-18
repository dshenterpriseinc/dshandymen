# site-export/ — Claude Design output, extracted

**This is NOT deployable HTML.** Do not push it to GitHub Pages as-is.

## What the format actually is
The `.dc.html` files are Claude Design's own component format, not static HTML:
- `<x-dc>` wrapper, `<helmet>` for head content
- `<dc-import name="SiteHeader">` for shared components
- `{{ mustache }}` bindings, `<sc-for>` loops, `<sc-if>` conditionals
- non-standard attributes like `style-hover="..."`
- React-style class components with `state` / `renderVals()` embedded at the bottom of each page
- all of it interpreted at runtime by **`support.js` (69 KB)**

**All content is present** — copy, service blurbs, town notes and the season data all live in the
`renderVals()` block at the bottom of each page. Nothing was lost in export. It just needs
compiling to real static HTML.

## 🚨 FIXED BEFORE YOU TOUCH IT — fabricated testimonials
The export shipped **8 invented review quotes attributed to 4 real, named people**
(Ben Osborne, Gary Walters, Dave Brennan, Renee P), rendered as `<blockquote>` with 5-star
ratings, plus invented job/town attributions — **with no disclaimer anywhere on the page.**
The design chat claimed they were "flagged on the page." They were not.

Those names are real people from Dave's Birdeye listing. Publishing words they never said,
next to their names, as endorsements is not a style problem — it is fabricated testimony, it
breaches FTC endorsement rules, and it would put his BBB A+ standing at risk.

**All 8 have been replaced with `[REVIEW PENDING …]` markers** so they cannot ship silently.
The names are retained because they are real; the words are gone.

➡️ **Before launch:** pull the verbatim text of each review from Google / BBB / Facebook and
paste it in. If a quote can't be sourced verbatim, delete that reviewer entirely.
The `4.7★ / 13 reviews` figure is accurate and can stay.

## What's in here
- 23 `.dc.html` pages + `SiteHeader` / `SiteFooter` components
- `assets/web/` (22) — real logos, favicon, mascot cutouts, all 6 Bear chat avatars
- `assets/photos/` (19) — the curated real job photos
- `assets/gallery/` (39) — gallery set
- `assets/video/` (4) — `hero-winter / thaw / green / leaffall.mp4`, the Season Engine sources
- `assets/audio/radio-ad.mp3` — his real Buffalo radio spot
- `chat-widget.js` (17 KB) — the Bear/Bird assistants
- `_ds/broadsheet-…/` — the Broadsheet design-system manifest

## Verified clean
- Only phone number anywhere: **(716) 803-0091** (26 display + 29 `tel:`)
- Rating stated correctly as **4.7★ / 13 reviews**, not inflated
- No files from `99_stock_DO_NOT_USE`
- `prefers-reduced-motion` handled in the base stylesheet

## Still to confirm during the build
- Bird chat avatars — only the 6 Bear states are bundled; Bird falls back to the division badge
- The Season Engine reads live date; confirm the no-JS/server-rendered fallback per DESIGN.md §6①
