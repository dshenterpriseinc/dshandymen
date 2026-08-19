# DS Handymen Commercials — live progress ledger
# Watchdog "dshandymen-commercials" reads + updates this every 10 min.
# COLLECT FIRST, THEN SUBMIT. Steal any lock older than 20 minutes.

## FINISHED (assembled + frame-audited) — 13 of 20
01 DONE FINAL-01-lake-effect-PHOTOREAL.mp4       14.5s driveway plow
03 DONE FINAL-03-dont-get-stuck-CARTOON.mp4      14.5s car stuck, bear clears it
04 DONE FINAL-04-pressure-wash-PHOTOREAL.mp4     14.6s macro grime->clean
05 DONE FINAL-05-wash-away-winter-3D.mp4         24.0s TWO-SCENE, CLIENT FAVOURITE
06 DONE FINAL-06-deck-reborn-PHOTOREAL.mp4       14.5s deck wash
07 DONE FINAL-07-sagging-shelf-CARTOON.mp4       14.5s shelf bracket repair
08 DONE FINAL-08-hanging-the-door-3D.mp4         14.5s hanging interior door
09 DONE FINAL-09-gutters-PHOTOREAL.mp4           14.5s gutter install
10 DONE FINAL-10-window-swap-CARTOON.mp4         14.5s draft -> new window, warm glow
11 DONE FINAL-11-drywall-patch-3D.mp4            24.0s TWO-SCENE
12 DONE FINAL-12-perfect-stripes-ANIME.mp4       14.5s mowing stripes
14 DONE FINAL-14-fall-cleanup-PHOTOREAL.mp4      14.5s leaves raked, lawn cleared
16 DONE FINAL-16-three-season-room-PHOTOREAL.mp4 24.0s sunroom tarp reveal

All 13 verified present in assets/10_FINAL_commercials/ on 2026-08-18 22:15.

## REMAINING — 7 spots: 02, 13, 15, 17, 18, 19, 20

---

# ⛔ RUN REPORT 2026-08-18 ~21:15–22:15 — ZERO SCENES COLLECTED

**Nothing was collected and nothing was assembled this run.** The previous run's plan —
"the 7 chats will show up in Recents next run, then use the proven click-the-recents-entry
route" — does not work, and I proved why. Read the next section before trying again.

## 🔬 THE RECENTS LAG IS REAL AND IT IS THE WHOLE BLOCKER (proven, not inferred)

I submitted a brand-new video prompt on Daniel Herlehy (chat `ed31be0973cc88a4`) and
confirmed it was generating. **Twenty-five minutes later that chat was absent from that same
account's own Recents list**, and three separate deep-link attempts to `/app/ed31be0973cc88a4`
all bounced to `/app`. This is a self-created control case, so the lag is not speculation:

- A chat is **not reachable by any route** (Recents, deep link, `/search`) for hours after it
  is created — on the very account that owns it.
- `myactivity.google.com/product/gemini` **also lags** — its newest entry was "Yesterday",
  today's prompts were absent — and its rows carry **no chat links**. Dead end, don't retry it.
- Gemini's **Library** page (left nav) *does* show a newest-first media grid with videos, but
  it lags the same way.

### ➡️ THE ONE RULE THAT MATTERS NEXT RUN
**After you submit, STAY IN THAT TAB.** Poll it in place until the video renders, then hover
the player and download it *there*. If you navigate away, switch profiles, or the tab dies,
that render is unrecoverable until the following day. Every scene lost across the last two
runs was lost exactly this way. Submit **one** scene, sit on it, collect it, and only then
submit the next. Four-in-flight across four profiles is what has been destroying the work.

## 🧾 The 7 "rendered but not collected" chats from the previous run — status corrected

The previous ledger listed 6 of these as rendering on profile `c8dc9c77`. **They are not
there.** I scanned that profile's two accounts (NYNightLife Guide `/u/0`, Dan Herlehy `/u/1`)
and none of the 7 chat IDs appear in either Recents list. Decisive evidence: NYNightLife's
Library media grid is newest-first, and it contains **no video newer than 14A** — only today's
pigeon/character *images*. Those six video submissions almost certainly never rendered
(they most likely hit the out-of-quota account the previous run documented).

| Scene | Chat id          | Verdict now |
|-------|------------------|-------------|
| 02A   | e7349ba005c4b358 | not found in any scanned account — resubmitted this run |
| 13A   | 29c5216b5433531f | not found — resubmitted this run |
| 15A   | ea0a98085f71e073 | not found — resubmit attempted, unconfirmed |
| 17A   | 08e4851808915787 | not found (PIGEON, crown moulding) — still needed |
| 18A   | ece253d6ac8998db | not found (PIGEON, tile backsplash) — still needed |
| 19A   | 3b67fbfdb308b3ae | not found (bear + pigeon) — still needed |
| 20A   | 5806406c531f5aad | not found (Go Bills driveway shovel) — still needed |

Treat these 7 IDs as **dead**. Do not spend another run hunting them.

## 📤 SUBMITTED THIS RUN (stranded — try to collect these first next run)

| Scene | Chat id          | Account / profile              | State when last seen |
|-------|------------------|--------------------------------|----------------------|
| 02A   | ed31be0973cc88a4 | Daniel Herlehy / `c47e45d4`    | Stop button present, generating — CONFIRMED |
| 13A   | 8675be49b22ca21f | `8875828a` (Flash)             | Stop button present, generating — CONFIRMED |
| 15A   | —                | Daniel Herlehy / `c47e45d4`    | tab died on the send click, **send unconfirmed** |

Prompts used are the single-scene, self-contained-outcome variants (same shape as the 10A/14A
shipped singles): 02A = final plow pass ending on a fully cleared driveway; 13A = tilt-shift
mulch bed, one rake held throughout; 15A = claymation attic emptied to bare swept floorboards.

## 🗺️ ACCOUNT MAP AS OBSERVED THIS RUN (it rotates — re-verify every single time)

| Profile     | What it served | Tier |
|-------------|----------------|------|
| `c8dc9c77`  | `/u/0` NYNightLife Guide, `/u/1` Dan Herlehy | Pro / Pro |
| `c47e45d4`  | Daniel Herlehy — later rotated to "Tammi"    | Pro / Free |
| `4c56fa8c`  | `/u/0` a Flash-Lite account, `/u/1` Dan Herlehy | Free / Pro |
| `93fcc96b`  | `/u/0` Dan Herlehy, `/u/2` unrelated account | Pro / — |
| `54524fba`  | DSH Corporation, rotated to Dan Herlehy then "dan herlehy" | Pro / Free |
| `8875828a`  | unnamed, Flash — accepted a video job        | usable |
| `7cc5655c`  | **SIGNED OUT ENTIRELY** — shows the Sign-in page. Skip it. | — |

Rotation is worse than previously documented: the served account changes **between page
loads, and again whenever the tab is re-created**. `/u/N` for an index that doesn't exist
silently falls back to `/u/0`, so a "successful" navigate proves nothing — always read the
account name back before and after acting.

## 🛠 MECHANICS LEARNED THIS RUN (save yourself the calls)

1. **A collapsed sidebar means conversation `<a>` elements do not exist**, so any scan that
   reads chat IDs returns empty and looks like a clean "not found". Expand the sidebar first
   (`button[aria-label*="menu"]`, JS click works for *this* button) and confirm you got
   anchors before believing a negative result. This produced two false negatives this run.
2. **`innerWidth === 0` means the tab isn't being rendered** (minimised/background window).
   Screenshots fail with a CDP deserialize error and real clicks are impossible. Abandon that
   profile rather than fighting it.
3. **JS `btn.click()` on the send button genuinely does not send** — confirmed again. Only a
   real `computer` click on the send arrow works. Pressing Return, even twice, did **not**
   send on the accounts I tried, contradicting the previous run's note.
4. **Send-button position:** compute it, don't guess. `getBoundingClientRect()` gives CSS px;
   screenshots are scaled, so multiply by `1568 / innerWidth`. Observed: sidebar expanded
   → x≈1144, collapsed → x≈1048.
5. **Verify a send by screenshot, not by JS.** The DOM check for an empty composer read stale
   for ~10s after a successful send and made a good submit look like a failure.
6. **Tabs die constantly, and most often on the `computer` click immediately after an
   injection.** That single failure mode cost the 15A submission and both collectable renders.
7. Returning raw `href` strings from `javascript_tool` trips a "Cookie/query string data"
   block. Return only the last path segment.

## SCENES ON DISK (assets/09_scenes/)
01A 03A 03B 04A 05A 05B 06A 07A 08A 09A 10A 11A 11B 12A 14A 16A 16B
02A-REJECT-duplicate-bear.mp4        <- do NOT use: second bear head in rear window
UNUSED-pigeon-painting-offmodel.mp4  <- second mascot, retired. Do not ship.
11B is the design-remodeling hero: the Bear skimming a wall in a warm interior. Use 0.0-5.0s;
past ~5s the shot has pushed into a close-up that reads badly behind hero type.

## TAGLINES
plowing "DON'T GET STUCK - GET PLOWED." | washing "IF IT'S OUTSIDE AND IT'S DIRTY, WE CLEAN IT."
handyman "BIG JOBS. SMALL JOBS. WE DO IT ALL."
seasonal plowing (spot 02) "GET ON THE LIST NOW."
10 and 14 shipped with the handyman line (landscaping has no line of its own).

## ▶️ NEXT RUN — do exactly this
1. Try to collect `ed31be0973cc88a4` (02A) and `8675be49b22ca21f` (13A) — by then they should
   finally be in Recents. Expand the sidebar, then click the Recents entry (real click).
2. Then work **one scene at a time**: submit → stay in the tab → poll → download → `collect.sh`
   → `assemble.sh`. Do not batch submissions across profiles again.
3. Remaining after that: 15 and 20. **17/18/19 are cancelled** - they were the design-partner
   spots and that partnership has ended (see below). Do not shoot them.


## THE DESIGN PARTNERSHIP IS OVER (2026-08-18)
Dave no longer works with the outside design outfit. The service stays - **he and his own crew
do the interior work now** - so nothing was deleted from the site except the partner.

What that meant in practice, and what to keep in mind if any of it comes back:

- **`retire_pigeon_division()` in `postprocess.py` (section 16)** does the copy and art swap and
  runs *first*, before every other fix. Two later passes had to be corrected because they ran
  *after* it and put the old content straight back: `fix_copy` rebuilt the design page lead, and
  a `retire_two_object_bird` helper re-pointed an image at the partner's art. If a reference ever
  reappears, look for a later pass reintroducing it before assuming the table missed a string.
- **Specific replacements must sit above generic ones** in `PIGEON_COPY`. A short rule fired
  first, ate half of a longer sentence, and left the tail behind.
- **`normalise_design_card()` runs after `apply_contrast_map`**, not before. The map had solved
  that card's eyebrow against the warm background it used to sit on and kept restoring it.
- **`compile.py` prunes `RETIRED_ASSETS` from `docs/assets` before copying.** `copytree` merges,
  so a deleted image used to ship forever. The list is explicit rather than a tree diff: the
  gallery, the photos, the map and the share images are generated straight into `docs/` and have
  no source in `site-export`, so a diff would delete all of them. It did, once.
- **The chat widget is one character again.** `BIRD_FIG`, `BIRD_KB`, `POSE_SETS.bird`, the second
  `FALLBACK`, `_setPoses` and the whole `_handoff` path are gone. `persona="design"` is still
  read, but it only changes the opening line and the quick questions - same Bear, same art, same
  colours. The design answers now live in `BEAR_KB` above the general rows.
- **Credentials were not transferred.** The partner's design qualification and her crew's years
  were hers; they are deleted, not restated as Dave's. Dave's own - 16 years in business, 50 in
  Hamburg - are what the copy leans on instead.
- **`/pigeon-division/` redirect removed.** Nothing links to it and the site is not live on the
  real domain yet, so there was no inbound traffic to protect.
- New art: `mascot-tool-belt` (hard hat, tool belt, arms folded), cut from `bear-pose-arms` by
  `build_mascot_frames.py`'s `card_cuts()`. It is the card art wherever the partner's was.
- Services cards: six identical "The Bear's side" eyebrows only meant something against a second
  side. Now Winter / Spring to fall / Exterior / Inside the house / Clear-outs / Helios dealer /
  Kitchens & baths.

After: 0 contrast failures, 0 a11y issues, heaviest page 1358 KB, worst LCP 204 ms, worst CLS
0.016, and 0 matches for pigeon|nichole|bird across everything in `docs/`.

## SUNROOMS PAGE (2026-08-18)
The hero layered a photograph under the video. The video paints at 55%, so the photo did not
sit behind it - it showed through it, as a second scene mixed into the first. `add_hero_video`
now removes that photograph on any page shaped like this and gives the section the dark ink the
other heroes sit on; without it a 55% video composites against white and washes out.

The photo grid on that page showed a bare slab, a poolside slab, a slab being pressure-washed
with the washer in shot, and a cinder-block bench - captioned "Patio enclosure project". Dave
has exactly one photograph of a finished enclosure, `patio-cover`, and it was being spent as the
hero backdrop. It leads the grid now, full width, with the two honest patio shots under it.

**Dave needs real sunroom photos.** One is all there is, and it has a garden shed in the
background. Three or four of a finished three-season room, and one of a Helios install, would
carry that page on their own.
