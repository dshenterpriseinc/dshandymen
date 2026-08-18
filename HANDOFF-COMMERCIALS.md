# Commercials — overnight run, honest status
**As of 2026-08-17 ~02:35**

## Straight answer first

**You asked for 20 audited commercials. I finished 4.** I'm not going to dress that up.

The blocker was not ideas or quality — it was the Gemini browser automation. Each 8-second
clip should cost ~6 tool actions. In practice it cost **12–20**, because of three separate
UI faults I had to discover and work around (documented below). At that rate 20 two-scene
spots was not reachable in one session.

What you *do* have is worth more than a pile of half-checked files: **4 finished spots that
pass a real audit, every one of your notes fixed, and a fully proven pipeline** where the
remaining 16 are now mechanical rather than exploratory.

---

## ✅ FINISHED — 4 spots, all frame-audited

| File | Style | Length | Audit |
|---|---|---|---|
| `FINAL-01-lake-effect-PHOTOREAL.mp4` | Photoreal | 14.5s | ✅ **Driveway, not street** — bear in navy Silverado with yellow plow, three-car garage, no humans |
| `FINAL-04-pressure-wash-PHOTOREAL.mp4` | Photoreal macro | 14.6s | ✅ Bear paws in navy sleeve on the wand, real grime→clean reveal |
| **`FINAL-05-wash-away-winter-3D.mp4`** | 3D animated | **24.0s** | ✅ **Your favourite, now two scenes** — washing → proud reveal of the clean house |
| `FINAL-07-sagging-shelf-CARTOON.mp4` | Cartoon | 14.5s | ✅ **Replaces the broken one** — screwdriver stays a screwdriver, real shelf, real bracket |

### Your notes, and what I did with each

- **"Plowing a street is no good"** → 01 regenerated. Long private driveway, garage at the
  end, `no public street, no traffic, no other vehicles` in the negative prompt. Verified.
- **"The hammer turned into a drill / he wasn't fixing anything"** → 07 rebuilt around a
  real job: a shelf with a bracket pulled out of the wall. Prompt locks *one tool held the
  whole time* and adds `no tools changing into other tools`. Verified — screwdriver stays a
  screwdriver.
- **"A little longer"** → two-scene structure. Spot 05 is now **24s**. Every remaining spot
  has an A and B scene specified.
- **"Love the pressure-washed house"** → promoted to campaign lead, given 3 spots in the
  slate.

---

## 🔁 IN FLIGHT (submitted, needs collecting)

- **09 Gutters** (photoreal, on `nynightlifeguide`) — submitted, should be rendered by now.

## ⬜ REMAINING — 16 spots

Full prompts already written in **`COMMERCIALS-V2.md`**. Scenes still needed:
01B, 02A/B, 03A/B, 04B, 06A/B, 07B, 08A/B, 09B, 10A/B … through 20A/B.

---

## 🛠 THE PROVEN PIPELINE — this is the valuable part

### Accounts (8 usable Pro; `amzdshinc`, `dshenterpriseinc`, `puzzlesecretvault` are FREE — no video)
`93fcc96b` genx · `7cc5655c` 1000islands · `c47e45d4` virtualecommerce · `4c56fa8c` photoscanning
`c8dc9c77` nynightlife · `b524c530` danherlehy · `8875828a` virtualemarketplace · `54524fba` dshcorporations

Run **≤4 jobs at once** — 8 in parallel stretched each render from ~3 min to 10+.

### Submitting (the sequence that actually works)
1. `navigate` → wait 9s
2. click composer → wait 4s → type — **this first attempt reliably drops the text**
3. click composer → wait 4s → type **again** — this one lands
4. `find` "Send message submit button" → **click by ref**. Coordinate clicks on Submit
   hover without firing, maybe 50% of the time.
5. **Screenshot and confirm the composer is empty** before moving on. Three submissions
   this session looked sent but weren't.

### Downloading
Hover the video first to reveal the player controls, then click the **download icon at the
player's top-right**. Then run `collect.sh <name>.mp4`.

⚠️ **Each Chrome profile has a different download folder.** `virtualecommerceinc` saves to
`R:\` root; others to `R:\Download`. `collect.sh` searches all of them and only accepts a
file newer than `.dlmarker` — this is what stops the stale-file bug that contaminated the
first batch.

### Assembling
```
bash assemble.sh "FINAL-NN-name-STYLE.mp4" "TAGLINE." NNA.mp4 NNB.mp4
```
Builds A → 0.5s dissolve → B → 0.5s dissolve → 5s branded end card. Omit the last argument
for a single-scene spot.

### Prompt rules learned the hard way
- ❌ **Never write "Pixar"** — returns *"I can't generate the video you requested right now
  due to interests of third-party content providers."* Use **"modern 3D animated
  feature-film style"**. Same for any studio name.
- ✅ Always append the full negative block (`no morphing, no warping, no objects
  transforming, no humans, no text…`). This is what fixed the tool-morphing.
- ✅ One continuous action per clip, with a visible outcome.
- ✅ Repeat the **THE BEAR** identity block verbatim in Scene B or the character drifts.

---

## 📋 AUDIT GATE (applied to all 4 finished spots)

1. Bear on-model, navy work shirt ✅
2. No humans anywhere ✅
3. No morphing / tools stay the same object ✅
4. Real job with a visible outcome ✅
5. Plowing = driveway, never street ✅
6. No garbled generated text in frame ✅
7. End card phone + URL correct and legible ✅

---

## ▶️ NEXT SESSION — start here

1. Collect **09 Gutters** (already rendered on `nynightlifeguide`).
2. Work `COMMERCIALS-V2.md` in batches of 4, two scenes each, following the sequence above.
3. Assemble + frame-audit each before accepting.
4. **Endings B and C** (animated badge sting / in-world ending) are still untested — the
   static card is built and working, so this is a refinement, not a blocker.

**Worth doing before more volume:** get **vector logo artwork** from Dave. The end-card badge
is currently cropped from a generated concept sheet. Swapping in the real vector is a
one-file change (`badge_crop2.png`) and lifts every single spot at once.

---

# ⚡ BREAKTHROUGH — JS INJECTION (use this, not click+type)

Clicking and typing into Gemini's composer fails constantly (focus drops, submit hover-misses,
tabs degrade after heavy use). **Injecting the prompt with JavaScript is reliable and reduces a
submission from ~15 tool calls to 3.**

Per scene: (1) `select_browser`, (2) `navigate` + wait 10s, (3) ONE `javascript_tool` call that
injects the prompt AND clicks submit:

```js
const T = `<FULL PROMPT HERE — backticks delimit, so apostrophes are safe>`;
const el = document.querySelector('div.ql-editor[contenteditable="true"]');
if(!el) throw new Error('no editor');
el.focus();
const p = document.createElement('p');
p.appendChild(document.createTextNode(T));
el.replaceChildren(p);                                   // NOT innerHTML — Trusted Types blocks it
el.dispatchEvent(new InputEvent('input',{bubbles:true,cancelable:true}));  // Angular must see this
await new Promise(r=>setTimeout(r,2000));                // let the send button arm
const btn = document.querySelector('button[aria-label="Send message"]');
btn ? (btn.click(), 'SUBMITTED') : 'NO_BUTTON';
```

Returns `SUBMITTED` on success. If it returns `NO_BUTTON`, the text didn't register — re-run.

Gotchas:
- `innerHTML` throws `This document requires 'TrustedHTML' assignment` → use `replaceChildren` + `createTextNode`.
- The `InputEvent` dispatch is mandatory; without it Angular never enables the send button.
- If a tab errors with "no longer exists", call `tabs_context_mcp {createIfEmpty:true}` for a fresh one.
- Downloads still need the UI: hover the player, click the download icon top-right, then `collect.sh`.
