# dshandymen.com

Website for **DS Handymen, Inc.** — Dave Schultz, Blasdell / Hamburg, NY.
Snow plowing · landscaping · pressure washing · handyman & remodeling · house clearance ·
sunrooms · and the **Pigeon Division** (interior & exterior design and finish work).

📞 (716) 803-0091 · BBB Accredited A+ · Serving Blasdell, Hamburg, Orchard Park, Lackawanna

---

## ✅ Status: BUILT, DEPLOYED, VERIFIED — awaiting DNS

Live on GitHub Pages from `main` → `/docs`. All 21 routes verified 200 on GitHub's servers.

**One step remains, and it needs your GoDaddy login:** point `dshandymen.com` at GitHub
(four A records + a www CNAME + remove Domain Forwarding), then tick **Enforce HTTPS**.
Full instructions in **`DNS-SETUP.md`**. Until then the deployment is only reachable by
resolving directly to GitHub, because the domain still answers with the old forwarding IPs.

### Verified
| | |
|---|---|
| Routes | 21/21 → 200 · 0 broken internal links |
| Structured data | 49 JSON-LD blocks, all valid (LocalBusiness · Service · BreadcrumbList · Review) |
| Reviews | 4 verbatim, sourced from Google/BBB, each labelled with its source |
| Responsive | 375px → **0px** overflow · 768px → 2-col · 1440px → 3-col |
| First paint | ~187 KB (39 html + 54 eager img + 25 js + 69 poster) |
| JS budget | 25 KB of 100 KB |
| Images | 153 tags, all with width/height + loading; WebP via `<picture>` |
| Chat | Bear + Bird, handoff verified working on nested pages |
| A11y | skip link, focus-visible, 44px targets, reduced-motion honoured |

`site-export/` is the design **source**; `docs/` is the compiled site.
Rebuild: `python build/compile.py`

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
