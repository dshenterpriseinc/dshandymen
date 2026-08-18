# dshandymen.com

Website for **DS Handymen, Inc.** — Dave Schultz, Blasdell / Hamburg, NY.
Snow plowing · landscaping · pressure washing · handyman & remodeling · house clearance ·
sunrooms · and the **Pigeon Division** (interior & exterior design and finish work).

📞 (716) 803-0091 · BBB Accredited A+ · Serving Blasdell, Hamburg, Orchard Park, Lackawanna

---

## 🟢 LIVE

### **https://dshenterpriseinc.github.io/dshandymen/**

Served by GitHub Pages from `main` → `/docs` over HTTPS with a valid GitHub certificate.
All 25 routes and assets verified 200.

**To move it to dshandymen.com:** point the DNS (see `DNS-SETUP.md`), then
`git mv docs/CNAME.pending docs/CNAME`, push, and tick **Enforce HTTPS**.
Every path on the site is relative, so the identical build serves correctly from either
address — no rebuild required.

### Verified live
| | |
|---|---|
| Routes | 25/25 → 200 · 0 broken links · 0 broken images |
| HTTPS | valid certificate, TLS verify 0, ~90ms response |
| Structured data | 49 JSON-LD blocks, all valid (LocalBusiness · Service · BreadcrumbList · Review) |
| Reviews | 4 verbatim, sourced from Google/BBB, each labelled with its source |
| Responsive | 375px → **0px** overflow · 768px → 2-col · 1440px → 3-col |
| First paint | ~187 KB · JS 25 KB of a 100 KB budget |
| Images | 153 tags, all with width/height + loading; WebP via `<picture>` |
| Chat | Bear + Bird, handoff verified working on nested pages |
| A11y | skip link · focus-visible · 44px targets · reduced-motion honoured |

## Build
```bash
bash build/build.sh      # compile.py + postprocess.py -> docs/
```
`site-export/` is the design **source**; `docs/` is the compiled site. The pipeline is
idempotent — every fix (real reviews, responsive layer, WebP, dimensions, lazy-loading)
is applied by `postprocess.py`, so rebuilds never silently regress.

## Layout
| Path | What |
|---|---|
| `DESIGN.md` | **The spec of record.** Creative concept, hard facts, assets, chat corpus, architecture. |
| `BUILD.md` | Paste-in prompt for Claude Code. |
| `site-export/` | Claude Design output — 23 pages + the assets the site actually uses. |
| `assets/11_WEB_READY/` | Logos, favicons, mascot cutouts, chat avatars. |
| `assets/12_PHOTOS_CURATED/` | 19 real job photos, descriptively named. |
| `COMMERCIALS-V2.md` · `PROGRESS.md` | Mascot commercial slate and production ledger. |

Heavy source material (195 raw job photos, the finished commercials, generation scenes, and
quarantined stock) stays local — see `.gitignore`.

## Audit — 2026-08-18
✅ 23 pages · 38 asset refs, **0 missing** · **0 broken** internal links · 49 images, **all** with
alt text · one `<h1>` per page · form controls labelled · Season Engine (4 states) implemented ·
both chat assistants present with Bear↔Bird handoff · only phone anywhere is (716) 803-0091 ·
rating stated honestly as 4.7★ / 13 · `prefers-reduced-motion` respected

### Hero video — optimised 2026-08-18
Trimmed to 8s of pure action (branded end cards removed — they read as a mistake behind hero
copy), audio stripped, re-encoded. **17 MB → 3.0 MB MP4 (-82%)**, with WebM alternates and
poster frames. Serve: `<video muted autoplay loop playsinline preload="none" poster="…-poster.jpg">`
with WebM first, MP4 fallback.

❌ No JSON-LD on any page · no `sitemap.xml`, `robots.txt`, `CNAME` · no Blog or Privacy page ·
Bird chat avatars not yet bundled (falls back to the division badge)

## Next
1. Compile `site-export/` → static HTML with clean URLs
2. Source the real review quotes
3. Add JSON-LD, sitemap, robots, CNAME
4. Enable GitHub Pages on `main`, custom domain `dshandymen.com`, **Enforce HTTPS**
   *(the old host's certificate expired 14 Jul 2026 — visitors currently get a "Not Secure" warning)*
