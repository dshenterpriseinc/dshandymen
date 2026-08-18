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
