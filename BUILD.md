# Handoff: Claude Design → Claude Code

## Step 1 — Export from Claude Design (10 seconds, you must click it)
Open the project, then:

**Share  →  Export  →  Project HTML  →  "Every project file, zipped. Instant and free."**

> There is **no "Open in Claude Code" button.** Don't keep looking for one.
> `/design-sync` (the two-way Design↔Code bridge) only works on **design-system** projects —
> component libraries. This is a regular 23-page design project, so it isn't reachable that way.
> Verified: `DesignSync list_projects` returns only "Broadsheet" and "Adjustly Design System".
> The zip is the supported handoff. It's instant and free.

## Step 2 — Unzip to
`R:\Documents\Claude\Projects\DSHandymen\site-export\`

## Step 3 — Start Claude Code in the project folder and paste this
---
Build the production DS Handymen website.

WORKING DIR: R:\Documents\Claude\Projects\DSHandymen

INPUTS:
- site-export/        The Claude Design output (23 pages). This is the visual target.
- DESIGN.md           The full creative + build brief. The spec of record.
- assets/11_WEB_READY/    Logos, favicons, mascot cutouts, chat avatars (transparent PNGs)
- assets/12_PHOTOS_CURATED/   19 real job photos, descriptively named
- assets/10_FINAL_commercials/  Finished :15-:25 mascot commercials
- assets/audio/       His real Buffalo radio ad
- assets/06_job_photos_fb/ + 07_job_photos_other/   195 more real photos

TASK:
1. Read DESIGN.md in full first. Where the export and DESIGN.md disagree, DESIGN.md wins on
   facts (phone, towns, offers, hierarchy) and the export wins on layout and visual design.
2. Turn the export into a real static site: shared header/footer, clean URLs per the §9
   architecture, no duplicated markup across 23 files.
3. Wire the REAL assets in. The export references filenames; make them resolve to the actual
   files. Convert to WebP/AVIF with fallbacks, add explicit width/height, lazy-load below fold,
   write descriptive alt text naming service + town.
4. Both chat assistants: scripted intent-matching, no API keys in client code, the Bear<->Bird
   handoff working, keyboard accessible, prefers-reduced-motion respected.
5. Quote form on a static-compatible handler (Formspree/Web3Forms) with photo upload + honeypot.
6. Add JSON-LD: LocalBusiness sitewide, Service per service page, FAQPage from the chat corpus.
   AggregateRating ONLY as 4.7 / 13.
7. sitemap.xml, robots.txt, canonicals, 404, CNAME for dshandymen.com.
8. 301 map from every dhenterprise.com/DJS/* URL to its new equivalent.

HARD RULES:
- The ONLY phone number anywhere is (716) 803-0091.
- Never ship anything from assets/99_stock_DO_NOT_USE/.
- Budget: LCP < 2.0s on 4G, CLS < 0.05, JS < 100KB gzipped. No jQuery/Bootstrap/page builder.
- WCAG 2.2 AA.
- Do not invent licence numbers, warranties, prices or review counts.

DEPLOY:
GitHub Pages, repo dshenterpriseinc/dshandymen, branch main, custom domain dshandymen.com,
Enforce HTTPS on.
BLOCKER: local gh is authed as `redtopatfunnyfarm` which has PULL-ONLY access to that repo.
Fix that (sign in as dshenterpriseinc, or add the account as a collaborator) before first push.

Start by reading DESIGN.md and site-export/, then show me a build plan before writing code.
---

## Quote form

The quote form posts to FormSubmit (`postprocess.py` → `wire_form`), which needs no
account and forwards photo attachments straight to `dshandymen@yahoo.com`.

**One-time activation is required.** The very first submission triggers a confirmation
email to `dshandymen@yahoo.com` with an activation link. Until Dave clicks it, nothing
is delivered. Send one test submission, then have him click the link.

`LIVE_BASE` at the top of `postprocess.py` drives the post-submit redirect (`_next`).
It must be the address the site is actually served from — change it to
`https://dshandymen.com/` at the same time the DNS cutover happens, or submissions will
bounce to a 404.

## Audits

Four checkers live in `build/`. None runs as part of `build.sh` — they each drive
a headless browser and take a minute or two — so run them after a change that
could plausibly affect what they measure.

```bash
python build/audit_contrast.py   # WCAG 2.2 AA contrast, judged on rendered pixels
python build/audit_a11y.py       # tap targets, labels, landmarks, duplicate ids, focus
python build/audit_images.py     # images larger than the box they render in
python build/audit_perf.py       # per-page transfer weight, FCP, LCP, CLS
```

All four should come back clean. As of the last run: 0 contrast failures, 0
accessibility issues, heaviest page 1.2 MB, worst LCP 232 ms, worst CLS 0.004.

### Fixers

These rewrite things, so they are separate from the read-only audits:

```bash
python build/fix_contrast.py     # solves contrast failures -> build/contrast_map.json
python build/optimize_images.py  # downscales assets to twice their rendered size
python build/make_thumbs.py      # -sm/-md variants for gallery tiles (srcset)
python build/fetch_fonts.py      # re-pulls the self-hosted woff2 files
```

`fix_contrast.py` rebuilds twice on purpose: once with the map cleared so it sees
the raw compiled colours, then once more to apply what it solved. Re-run it after
any change to the palette, the imagery behind text, or the page layout — the map
is keyed on exact inline style strings and goes stale silently.

### Fonts

Both faces are self-hosted under `docs/assets/fonts/` and preloaded. The
metric-matched fallbacks in `responsive.css` are tuned to how each face is
actually used, not to a generic sample — Barlow Condensed is display type and
nearly always uppercase, where it runs 67.5% of Arial's width against the 77% a
mixed-case string suggests. To re-measure after a font change, load a page and
run in the console:

```js
await document.fonts.ready;
const c = document.createElement('canvas').getContext('2d');
const w = (f, s, wt) => { c.font = (wt||400) + ' 100px ' + f; return c.measureText(s).width; };
const S = 'SERVICES DESIGN & REMODELING GALLERY REVIEWS ABOUT FREE QUOTE';
w('"Barlow Condensed"', S, 700) / w('Arial', S, 700);   // -> size-adjust
```

`ascent-override` and `descent-override` are the font's own ascent and descent
(from `measureText().fontBoundingBoxAscent` / `Descent` at 100px) divided by that
size-adjust, so the line box keeps the real font's height.

## A note on the shell

Heredocs in this environment collapse backslash escapes, so a `\b` written into
a Python regex through one arrives as a literal backspace character (0x08) and
the pattern silently never matches. It cost several confusing debugging rounds.
Write Python files with an editor, or build backslashes with `chr(92)`.
