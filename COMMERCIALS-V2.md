# DS Handymen — 20 Commercials, V2 (corrected slate)
### Supersedes COMMERCIALS.md. Built from client feedback + Veo prompting research.

## WHAT CHANGED AND WHY

| Feedback | Fix |
|---|---|
| "Plowing a street is no good — nobody pays to plow a street" | **Every plowing spot is now a residential DRIVEWAY** (long driveways fine), with a garage/house clearly in frame so the job reads as paid residential work |
| "The hammer suddenly turned into a drill — that was weird" | Veo responds to explicit negatives. Every prompt now ends with `no morphing, no warping, no objects transforming into other objects`. One continuous action per clip, no internal cuts |
| "He wasn't actually fixing anything" | Every spot is now a **real DS Handymen job with a visible before → after outcome**: a sagging shelf made level, a door hung, gutters secured, drywall patched, tile laid |
| "A little longer" | Each spot is now **two chained 8s scenes** (A + B) + a longer end card ≈ **21–22s**, instead of 14.6s |
| "Love the pressure-washed house one" | Pressure washing gets **three** spots and leads the campaign |

## PROMPT TEMPLATE (use verbatim — this is the quality lever)

> **[STYLE]** commercial, 8 seconds. **[SETTING]**.
> **THE BEAR:** a friendly muscular cartoon polar bear mascot wearing a deep navy work
> shirt — white fur, black nose, warm confident expression. He is the ONLY character in the
> entire video.
> **ACTION** (one single continuous action, no cuts): **[ACTION WITH A CLEAR OUTCOME]**.
> **CAMERA:** [shot size + move]. **LIGHT:** [lighting].
> **NEGATIVE:** no humans, no people, no faces, no text, no letters, no numbers, no logos,
> no watermarks, no morphing, no warping, no objects transforming into other objects, no
> duplicate limbs, no jump cuts, no background shifting, no floating tools.

Repeat the **THE BEAR** block *verbatim* in Scene B of every spot — that is what stops the
character drifting between the two halves.

---

## THE 20

### PLOWING — driveways only, never streets

**01 · LAKE EFFECT** *(photoreal)* — **A:** bear in a navy pickup with a yellow plow pushes a
clean bank of snow down a **long residential driveway**, two-car garage ahead, house lit
warm. **B:** wide shot of the finished driveway, clean pavement corner to corner, snow
banked neatly at the edges.

**02 · GET ON THE LIST** *(Pixar 3D)* — **A:** heavy snow falling on a buried driveway, the
garage barely visible. **B:** the bear's plow truck finishes the last pass and he leans out
the window with a satisfied nod at the cleared driveway.

**03 · DON'T GET STUCK** *(flat 2D cartoon)* — **A:** a car's wheels spin uselessly at the top
of a snowed-in driveway. **B:** the bear's plow clears a path to the road and the car rolls
out freely.

### PRESSURE WASHING — the campaign lead

**04 · THE STRIPE** *(photoreal macro)* — **A:** bear's paws sweep the wand across filthy
concrete, revealing one clean stripe. **B:** pull back to the whole driveway, half filthy,
half brilliant.

**05 · WASH AWAY WINTER** *(Pixar 3D)* — **A:** bear washes a grimy, algae-streaked two-storey
house, water arcing. **B:** the finished house, siding bright and clean, bear proud in frame.
*(Client favourite — lead spot.)*

**06 · DECK REBORN** *(photoreal)* — **A:** bear washes a grey weathered deck, grime lifting.
**B:** the finished deck, warm clean wood grain, furniture back in place.

### HANDYMAN — real jobs with real outcomes

**07 · THE SAGGING SHELF** *(retro 1950s cartoon)* — **A:** a wall shelf hangs crooked, one
bracket pulled loose from the wall. **B:** bear fits a new bracket, sets the shelf level, and
places a book on it — it stays put. *(Replaces the incoherent original.)*

**08 · HANGING THE DOOR** *(Pixar 3D)* — **A:** bear lifts a new interior door into an empty
frame. **B:** he sets the hinge pin and swings it — it closes cleanly.

**09 · GUTTER PATROL** *(photoreal)* — **A:** bear on a ladder lifts a new gutter section
against the fascia. **B:** he drives the last screw and water runs clean through the
downspout.

**10 · WINDOW SWAP** *(flat 2D cartoon)* — **A:** old drafty window, visible cold draft lines.
**B:** bear seats the new window and the draft lines vanish, interior glows warm.

**11 · DRYWALL PATCH** *(Pixar 3D)* — **A:** a ragged hole in a bedroom wall. **B:** bear
smooths the final pass of compound — a flat, seamless, paint-ready wall.

### LANDSCAPING

**12 · PERFECT STRIPES** *(anime)* — **A:** bear mows an overgrown lawn, clippings flying.
**B:** wide reveal of immaculate alternating mown stripes.

**13 · MULCH DAY** *(tilt-shift miniature)* — **A:** bear barrows mulch to a tired flower bed.
**B:** the finished bed, dark fresh mulch, crisp edges.

**14 · FALL CLEAN-UP** *(photoreal)* — **A:** bear rakes heavy autumn leaves into a pile on a
lawn. **B:** the cleared lawn, bagged leaves stacked neatly at the kerb.

### HOUSE CLEARANCE

**15 · ATTIC RESCUE** *(claymation)* — **A:** bear carries boxes out of a crammed attic.
**B:** the attic empty, swept, daylight through the vent.

### SUNROOMS

**16 · THREE-SEASON ROOM** *(photoreal)* — **A:** bear pulls a tarp away from a new
glass-walled sunroom. **B:** slow push through the glass, golden hour, autumn trees.

### PIGEON DIVISION — the Bird leads these

**17 · FINISH CARPENTRY** *(Pixar 3D)* — **A:** the pigeon fits crown moulding along a
ceiling. **B:** the finished room, crisp trim, warm designer lighting.

**18 · TILE BACKSPLASH** *(photoreal)* — **A:** pigeon sets a tile into fresh adhesive.
**B:** the finished backsplash behind a clean countertop.

### BRAND

**19 · BEAR & BIRD** *(flat 2D)* — **A:** split screen, bear hauling lumber / pigeon laying
tile. **B:** the divider slides away into one finished room, both characters together.

**20 · GO BILLS** *(bold 2D cartoon)* — **A:** bear clears a driveway in a red-white-and-blue
scarf on game day. **B:** he raises both paws in triumph, snow confetti.

---

## ENDINGS — three variants under test

Per client request, testing alternatives to the single static card:

- **END-A · Static card** (built, working) — navy, badge, tagline, URL, phone, towns, trust
- **END-B · Animated badge sting** — generated 3D badge assembly, ffmpeg text composited over
- **END-C · In-world ending** — the spot's own final shot held, with text composited over it,
  so the branding never leaves the world of the commercial

Text is **always** composited in ffmpeg, never generated — Veo cannot render legible type.

## AUDIT GATE — every spot must pass before acceptance

1. Bear on-model: white fur, **navy work shirt**, correct proportions
2. **No humans** anywhere, including background
3. **No morphing** — tools and objects stay the same object throughout
4. The job is **real and completed** — a visible before → after
5. Plowing is a **driveway**, never a street
6. No garbled generated text anywhere in frame
7. Scene A and Scene B match in character, lighting and palette
8. End card: phone and URL correct and legible

Any failure → regenerate with a corrected prompt.
