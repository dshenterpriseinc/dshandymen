# DS Handymen, Inc. — Master Design Brief
### Handoff document for Claude Design → Claude Code → GitHub Pages

**Prepared:** 2026-08-16
**Client:** DS Handymen, Inc. — Dave Schultz ("The Bear"), Blasdell / Hamburg, NY
**Target rating:** 9.8/10. This is not a template job. Read the whole brief.

---

## 0. THE ONE-LINE BRIEF

> Build the website for a 16-year-old, BBB A+ rated Western New York home-services
> company whose single greatest untapped asset is a **polar bear mascot named The Bear**
> and his design-side counterpart, **The Pigeon** — and make it the most characterful,
> trustworthy, fastest-loading contractor site in Erie County.

---

## 1. URGENT CONTEXT (read before designing)

The current site is in a genuine emergency state. This is *why* the rebuild matters,
and it shapes several decisions below.

| Problem | Detail | Consequence |
|---|---|---|
| **SSL certificate expired** | Let's Encrypt cert expired **14 Jul 2026** | Every visitor since has hit a full-page red "Your connection is not private" interstitial. Effectively **zero** web leads for a month. |
| **Wrong home** | Live site is `dhenterprise.com/DJS/` — a subfolder of an unrelated domain. `dshandymen.com` merely forwards to it. | 16 years of brand equity and SEO accruing to the wrong domain. |
| **WordPress 5.2.21** | Released 2019. ~7 years of unpatched CVEs. `xmlrpc.php` and the REST API fully open. | The entire 272-file media library was downloadable unauthenticated, no login. Compromise risk is high. |
| **Near-name domain for sale** | `dshandyman.com` (singular) is parked on GoDaddy, actively listed for sale. | Any competitor can buy his near-name. |
| **Thin reputation** | 4.7★ from only **13 reviews** after 16 years. | Competitors with 100+ reviews outrank him in the map pack. |
| **Public hit counter** | Homepage widget displays "Users Today: 1 · Users Yesterday: 0". | Actively broadcasts that nobody visits. **Do not reproduce.** |

**Decisions already made by the client:**
- Domain: point **dshandymen.com** at GitHub Pages (free auto-renewing SSL — permanently fixes the cert problem).
- Strategy: **balanced year-round hub** with a seasonal hero, not a single-service site.
- Brand: **go all-in on the Bear & Bird.**
- Leads: **quote form with photo upload.**
- Plus: an **animated 3D mascot chatbot** (spec in §8).

---

## 2. THE BUSINESS — VERIFIED FACTS

Use these exactly. Anything marked `[CONFIRM]` must be checked with Dave before launch.

**Identity**
- Legal name: **DS Handymen, Inc.** (note: *Handymen*, plural, and *Inc.*)
- Owner: **Dave Schultz** — lifelong Hamburg NY resident, **50 years** in the area
- Known as: **"The Bear"** — used publicly in his own copy ("Call the Bear today")
- Founded: **1 November 2009** (16 years)
- **BBB Accredited since 26 March 2021 · A+ rating** — this is his single strongest trust signal and is currently buried
- Insured `[CONFIRM licence # / carrier]`

**Contact**
- Phone: **(716) 803-0091** — primary conversion path; he is a phone-first business
- Email: `dshandymen@yahoo.com` → **recommend migrating to `dave@dshandymen.com`** `[CONFIRM]`
- Address: **135 Miriam Avenue, Suite 1, Blasdell, NY 14219**
  - Also on record: PO Box 2111, Blasdell NY 14219 · and `253 S Shore Dr` on Birdeye
  - ⚠️ **NAP inconsistency across directories is hurting local SEO. Pick ONE canonical address and use it byte-identically everywhere.** `[CONFIRM which]`
- Hours: Birdeye says "24/7" `[CONFIRM real hours + storm-response expectations]`

**Service area:** His own 2025/26 plowing ad names four towns explicitly —
**Blasdell · Hamburg · Orchard Park · Lackawanna**. Treat those as confirmed and build
their location pages first. Likely extensions: West Seneca, East Aurora, the wider
**Southtowns** / Erie County. `[CONFIRM the extensions + any radius limit]`

**Payment & offers** (all found on his own graphics, none on his website):
- **Venmo accepted** — `david schultz@dshandymeninc`
- **Gift certificates: $100 / $250 / $500**, redeemable against any service
- **$20 referral coupon** on seasonal plowing
- **10% off for Veterans, Seniors and Teachers** `[CONFIRM still live]`

**Reputation:** 4.7★ / 13 reviews (Birdeye, aggregating Google). Named reviewers whose
wording can be quoted with permission: Ben Osborne, Gary Walters, Dave Brennan, Renee P.

---

## 3. SERVICES (the full, real list)

Grouped as they should appear in the IA:

**❄️ Snow & Winter** — *the Bear's signature*
- Residential driveway plowing · commercial parking lots
- Seasonal contracts **or** one-off plows · two trucks on route
- **$20 referral coupon** for any seasonal referral
- Existing voice: *"Lake effect snow? No problem!"* · *"Don't get stuck — get plowed!"* · *"We'll clear your way."*

**🌿 Landscaping & Yard**
- Mowing, mulching, planting, trimming
- Raking, gutter clean-outs, winter protection for trees & shrubs
- Seasonal maintenance schedules

**💦 Pressure / Power Washing**
- Driveways, siding, decks, roofs, sidewalks, pool decks
- Existing voice: *"If it's outside and it's dirty, we can help you out."* · *"Wash away winter."*

**🔨 Handyman & Remodeling**
- Window replacement · basement remodeling · kitchen upgrades · flooring · drywall
- **Three-season room** construction
- Deck refinishing · outdoor bar construction

**📦 House Clearance** *(newer, under-marketed — give it a real page)*
- Attics, garages, full estate clear-outs
- Strong emotional copy already exists: *"It can be overwhelming figuring out where to start."*

**🏛️ Helios Retractable Glass Sunrooms & Patio Enclosures**
- Trained, authorised dealer + installer (partner: heliossolutionsusa.com)
- Highest-ticket offering — deserves a premium page

**🕊️ The Pigeon Division — Interior & Exterior Design and Construction**
- Led by **Nichole Pigeon**, graduate of **Rochester Institute of Technology (RIT) Design School**
- Crew has **40+ years collective experience**
- Custom design, trim work, cabinets, drywall, paint, tile, finish work, exterior projects
- Existing tagline: *"The Bear and the Bird work together."* ← **this is the brand. Build on it.**

---

## 4. BRAND STRATEGY — THE BEAR & THE BIRD

This is the creative core. Every competitor in the Southtowns is a name-plus-truck-photo.
DS Handymen has **two characters and a story**, and currently wastes both.

**The narrative:**
> **The Bear** does the heavy work — plowing, washing, hauling, building. Strong,
> dependable, shows up in a blizzard.
> **The Bird** makes it beautiful — design, trim, cabinets, tile, finish.
> Two halves of one company. *Muscle and craft.*

**Tone of voice:** Plain-spoken Western New York. Warm, a little funny, never corporate.
Dave already writes this way — *"Go Bills!"*, *"Call the Bear"*, *"Don't get stuck — get plowed."*
**Preserve his voice.** Do not sand it into agency copy.

**Guardrails:** the humour must never undercut credibility on high-ticket pages.
Bear-forward and playful on plowing/washing; Bird-forward and restrained on
Pigeon Division / Helios sunrooms.

---

## 5. VISUAL IDENTITY

### 5.0 ⚠️ WHAT HE IS ACTUALLY DOING NOW (Facebook audit, Aug 2026)

**The website is years behind his real brand.** His Facebook page shows a much stronger,
deeper, more current identity that the old WordPress site never adopted. **Follow Facebook,
not the website.**

Verified from `facebook.com/dshandymen` (635 followers · "SNOW PLOWING / PRESSURE WASHING
HOMES / LANDSCAPE" · Landscape Company):

- **His current logo is already a circular badge.** Dark charcoal ring, muscular polar bear
  standing **arms crossed** in a dark work shirt, `DS HANDYMEN INC.` curved along the top,
  `SNOW PLOWING · 716-803-0091 · LANDSCAPING` curved along the bottom. It is on his
  **truck doors** (photographed on a black 3500 HD) and is his profile picture.
- **The palette is deep, not teal.** Navy, royal blue, charcoal, crisp white, red accents.
  The 2022 teal logo on the website is the outdated one.
- **Buffalo Bills fandom is a genuine brand pillar**, not a throwaway. He posts
  Bills-themed bear graphics — including a **"GO BILLS! SUPER BOWL CHAMPS 2026!"** bear in
  a Bills uniform — and a 2021 "Bear in the hot tub" graphic offering **10% off for
  Veterans, Seniors and Teachers** with the bear in a Bills jersey.
- **His snow plowing ad** is a blue Chevy with a V-plow: *"SERVICING THE BLASDELL ·
  HAMBURG · ORCHARD PARK · LACKAWANNA"* / *"GET ON THE LIST NOW"* / *"RELIABLE &
  PROFESSIONAL SERVICE · FULLY INSURED."* ← **use this confirmed town list.**
- He runs **Memorial Day / holiday** posts with a red-and-navy shield lockup — he shows up
  for civic moments. Worth reflecting in the brand's warmth.
- A snow-depth-ruler infographic: *"Get ready for LOTS of snow!"* / *"PLEASE GIVE SNOWPLOW
  DRIVERS A BREAK!"* — proof he already thinks in useful, shareable graphics. **The site
  should have a homepage module in exactly this spirit.**

**Also surfaced, and missing from his website entirely:**
- **Venmo accepted** — `david schultz@dshandymeninc`
- **Gift certificates** at **$100 / $250 / $500**, usable on any service
  ("the gift of time" — a genuinely good seasonal offer that deserves its own page)
- **10% discount for Veterans, Seniors and Teachers** `[CONFIRM still live]`

### 5.1 Mascot — already generated
Four concept sheets are in `assets/00_NEW_brand_concepts/`. The bear was **evolved, not
replaced** — recognisably Dave's bear, with clean vector shapes, bolder line-work, a
stronger silhouette, and the dated 2000s gradients removed.

| File | Contents |
|---|---|
| `concept-sheet-01-bear-evolution.jpg` | First pass — badge · shovel pose · hard-hat + tool-belt · icon. ⚠️ *teal palette, superseded* |
| `concept-sheet-02-service-poses.jpg` | Six service poses: shovelling · plow truck · pressure washer · mower + trimmers · ladder with drill · friendly wave. ⚠️ *recolour to §5.2* |
| `concept-sheet-03-chatbot-3d-avatar.jpg` | Six 3D expressions for the chatbot: neutral · waving · listening · delighted · pointing · thumbs-up. ⚠️ *restyle shirt to navy* |
| **`concept-sheet-04-CORRECTED-deep-navy-palette.jpg`** | ✅ **THE DIRECTION.** Charcoal/navy circular badge with arms-crossed bear · navy-shirt bear with safety-yellow shovel · "LET'S GO BUFFALO!" Bills-pride bear · white knockout badge for dark backgrounds and truck vinyl |
| **`concept-sheet-05-pigeon-division-and-duo.jpg`** | ✅ **THE PIGEON, UNIFIED.** Charcoal "PIGEON DIVISION / DS HANDYMEN INC." badge matching the Bear's · full-body Pigeon with paintbrush and rolled blueprint · **the Bear & Bird duo lockup** · simplified single-colour pigeon icon |

> **The duo lockup in sheet 05 is the single most important asset in this brief.** It is
> the brand story in one image — muscle and craft, side by side, finally in the same visual
> language. Use it on the homepage "Bear & Bird" section (§7.1E) and on the About page.

> ⚠️ **Sheet 04 contains a hallucinated placeholder phone number (`716-555-0123`).**
> The real number is **(716) 803-0091**. Correct it in the final vector artwork.

**Sheet 04's badge is the primary logo lockup** — it matches what's already on his trucks,
works at favicon size, and survives one-colour vinyl.

### 5.2 Palette — CORRECTED to his real current brand

| Role | Colour | Hex | Use |
|---|---|---|---|
| Primary | Deep navy | `#1B2A4A` | Headers, footer, the Bear's work shirt, body text |
| Secondary | Royal blue (Bills) | `#00338D` | Buttons, links, plow truck, Buffalo-pride moments |
| Badge | Charcoal | `#333333` | The badge ring, truck vinyl, heavy UI |
| Accent | Bills red | `#C60C30` | Urgency, seasonal/holiday, sparing highlights |
| Equipment | Safety yellow | `#F5B324` | Plow blades and equipment **only** — never as a UI colour |
| Snow | Off-white | `#F4F8FB` | Section backgrounds |
| Ink | Near-black | `#0C1620` | Maximum-contrast text |

**Red and royal blue together read as Buffalo Bills** — that is deliberate and on-brand for
this business, but keep it to seasonal and civic moments so the core site stays navy and
charcoal. Pigeon Division retains its softer tan / warm grey / terracotta sub-palette.

### 5.3 Typography
- **Display:** a confident condensed sans with slight industrial character
  (Barlow Condensed, Oswald, or similar). Uppercase for section headers.
- **Body:** a highly legible humanist sans (Inter, Source Sans). **17–18px minimum** —
  a meaningful share of his customers are older homeowners.
- Never set body copy below 16px. Never use thin weights on the navy background.

### 5.4 Motifs
Carved-wood sign texture (from the original logo) · snow drifts as section dividers ·
bear paw prints as list bullets · blueprint grid on Pigeon Division pages.
Use these as light seasoning, not wallpaper.

---

## 6. SITE ARCHITECTURE

```
/                          Home — seasonal hero, all services, trust, reviews, quote CTA
/services/                 Overview hub
  /snow-plowing/           ❄️ Seasonal contracts + $20 referral
  /landscaping/            🌿
  /pressure-washing/       💦
  /handyman-remodeling/    🔨
  /house-clearance/        📦
  /sunrooms-patio-enclosures/  🏛️ Helios — premium treatment
  /pigeon-division/        🕊️ Design & construction — premium treatment
/about/                    Dave's story, 50 years in Hamburg, BBB A+, the crew
/gallery/                  Before & after, filterable by service
/reviews/                  Aggregated reviews + prominent "leave a review" CTA
/service-area/             Hub page
  /hamburg-ny/  /blasdell-ny/  /orchard-park-ny/  /west-seneca-ny/  /lackawanna-ny/  /east-aurora-ny/
/quote/                    Main conversion page — form + photo upload
/contact/
/blog/                     "Helpful Tips" — keep the existing WNY seasonal-maintenance angle
404, /privacy/, /sitemap.xml, /robots.txt
```

**Service-area pages must be genuinely differentiated** — real local landmarks, real
neighbourhood names, real job photos from that town. Six near-identical templated pages
is thin content and Google will treat it as such.

---

## 7. PAGE SPECIFICATIONS

### 7.1 Homepage

**A · Sticky header**
Badge logo left · nav centre · **(716) 803-0091 as a tap-to-call button** right, always
visible. On mobile a persistent bottom call bar.

**B · Seasonal hero** — auto-swaps by month (client chose the balanced year-round hub)
- **Nov–Mar:** Bear plowing. *"Lake effect snow? No problem."* → Reserve Your Plow Contract
- **Apr–Jun:** Bear pressure washing. *"Wash away winter."* → Get a Free Quote
- **Jul–Sep:** Bear landscaping / Pigeon remodel. *"Make the most of your outdoor space."*
- **Oct:** Bear with rake. *"Prep for winter today."*

Implement as a small date-based JS swap over pre-rendered content — **the default must be
server-rendered HTML so it works with JS disabled and is fully crawlable.**

**C · Trust bar** — immediately under the hero, above the fold on desktop:
`BBB A+ Accredited` · `Since 2009` · `Fully Insured` · `4.7★ Google` · `Locally Owned, Hamburg NY`

**D · Six service cards** — each with its new Bear pose from sheet 02.

**E · The Bear & The Bird** — the split brand story. Two columns, two characters, two kinds
of work. This is the emotional centre of the page.

**F · Before & After slider** — real job photos, drag-to-compare.

**G · Reviews** — real quotes with names.

**H · Radio ad** — he has a professionally produced Buffalo radio spot sitting unused
(`assets/audio/WLBC_..._DS_Handymen_Incorporated_-_Buffalo_1W002.mp3`). Give it a proper
styled player: *"Hear our radio ad."* Almost no competitor has this.

**I · Service-area map** with linked town pages.

**J · Quote CTA band** → the form.

**K · Footer** — NAP block (schema-marked), hours, services, socials, BBB badge.

### 7.2 Snow Plowing page
Urgency-driven. Season countdown. Residential vs commercial split. Seasonal-contract vs
one-off comparison table. **The $20 referral offer as a real feature, not fine print.**
Reuse the "two trucks on route" credibility line.

### 7.3 Pigeon Division page
Tonal shift: quieter, more editorial, more white space. Lead with Nichole's RIT credential
and the crew's 40 years. Large before/after imagery. This is where high-ticket remodel
leads convert — **do not put a cartoon bear at the top of this page.**

### 7.4 Quote page
Fields: name · email · phone · **service (multi-select)** · property address /
town · timeframe · description · **photo upload (multiple)** · how did you hear about us.
Static-hosting-compatible handler (Formspree / Web3Forms free tier).
Honeypot + rate-limiting. Clear success state with expected response time.

---

## 8. THE MASCOT CHATBOT ("Ask The Bear")

A signature feature. Nothing else in this market has one.

**Presentation**
- Floating circular launcher, bottom-right, using the 3D bear head from sheet 03
- Idle: gentle breathing/bobbing animation; occasional blink
- Attention: after ~20s on a service page, a small speech bubble — *"Need a quote? Ask me."*
- On open: panel with the 3D bear at top, avatar swapping between the six expression states
  (neutral → listening while user types → delighted on success → pointing when linking out)
- Animate with CSS transforms + sprite/state swap. **No heavy 3D engine** — this must not
  cost seconds of load time.

**Behaviour**
- Opens with quick-reply chips: `Snow plowing` · `Get a quote` · `Service area` · `Pricing` · `Talk to Dave`
- **Always** offers the phone number as an escape hatch
- Never invents prices — routes to a quote or a call
- Accessible: keyboard navigable, focus-trapped, ARIA-labelled, respects
  `prefers-reduced-motion` (mascot holds still)

**Pre-loaded Q&A corpus** — built from his real site + Facebook. Ship with these:

| Intent | Answer |
|---|---|
| Who are you? | "I'm the Bear — Dave Schultz's sidekick at DS Handymen. Dave's been fixing, plowing and building around Hamburg for 50 years." |
| What areas do you serve? | Hamburg, Blasdell, Orchard Park, West Seneca, Lackawanna, East Aurora and the wider Southtowns. |
| Are you insured? | Yes — fully insured, and BBB Accredited with an A+ rating since 2021. |
| How long in business? | Since 2009 — 16 years. |
| Do you plow driveways? | Yes, residential driveways and commercial lots. Seasonal contract or one-off. Two trucks on route. |
| How much does plowing cost? | Depends on driveway size and layout — Dave will quote you. Call (716) 803-0091 or send a photo through the quote form. |
| Referral discount? | Refer another seasonal customer and you get **$20 off**. |
| What can you pressure wash? | Driveways, siding, decks, roofs, sidewalks, pool decks. "If it's outside and it's dirty." |
| Do you do kitchens/bathrooms? | Yes — that's the Pigeon Division, led by Nichole Pigeon, an RIT Design School graduate. Custom design, trim, cabinets, drywall, paint, tile, finish. |
| Three-season room / sunroom? | Yes — we build three-season rooms, and we're a trained installer for Helios retractable glass sunrooms and patio enclosures. |
| Can you clear out my attic/garage/estate? | Yes — house clearance is one of our services. |
| Do you do gutters? | Yes — gutter clean-outs as part of seasonal landscaping. |
| Emergency / storm? | Call Dave directly at (716) 803-0091. |
| Free estimates? | Yes — free estimates. |
| How do I book? | Quote form (photos welcome) or call (716) 803-0091. |
| Where are you based? | Blasdell, NY — right in the Southtowns. |
| How can I pay? | Cash, cheque, and **Venmo** — `david schultz@dshandymeninc`. `[CONFIRM cards]` |
| Do you sell gift certificates? | Yes — **$100, $250 or $500**, good toward any service. "Give someone the gift of time." |
| Any discounts? | **10% off for Veterans, Seniors and Teachers**, and **$20 off** for referring a seasonal plowing customer. |
| Go Bills? | "Let's go Buffalo." 🦬 |

`[CONFIRM with Dave: real hours, payment methods, deposit policy, warranty terms,
whether he wants the bot to state any price ranges at all.]`

---

## 8B. VIDEO

Cinematic B-roll clips generated for this project live in `assets/08_video_broll/`.
Each is ~8 seconds, 1080p, silent, no on-screen text or logos — deliberately clean so they
can be cut, looped, trimmed and captioned without fighting baked-in graphics.

| File | Shot |
|---|---|
| `broll-01-snowplow-dawn.mp4` | Pre-dawn blue hour, navy pickup with a safety-yellow plow blade pushing a wall of powder down a suburban Buffalo driveway, headlights through drifting snow |
| `broll-02-pressure-wash-reveal.mp4` | Macro slow-motion — a pressure washer wand revealing a clean stripe across filthy weathered concrete in one satisfying pass |

**How to use them**
- **Homepage hero:** muted, autoplaying, looping background video behind the seasonal
  headline. **Must** be `muted autoplay loop playsinline`, with a static poster image, and
  it must not block LCP — lazy-load the video and paint the poster first.
- Clip 01 heads the **Snow Plowing** page; clip 02 heads **Pressure Washing**.
- Respect `prefers-reduced-motion`: serve the poster frame only, no playback.
- Keep each under ~3 MB and provide a WebM alongside the MP4.
- These are also ready-made **social posts** — the pressure-wash reveal in particular is
  exactly the kind of oddly-satisfying clip that performs on Facebook Reels, and he
  already has an engaged local following there.

**Still to shoot/generate** `[NEXT]`: a landscaping/mowing clip, an interior finish-carpentry
clip for the Pigeon Division, and an animated sting of the badge logo for video end-cards.

> ⚠️ **Real footage beats generated footage for trust.** These clips are excellent as
> atmosphere and section headers, but the *proof* pages — gallery, reviews, before/after —
> must use his real 195 job photos. Consider getting Dave to shoot 30 seconds of phone
> video from an actual plow route this winter; that will outperform anything generated.

---

## 9. ASSETS

All **272** files from the old site are downloaded and sorted in `assets/`:

| Folder | Count | Notes |
|---|---|---|
| `00_NEW_brand_concepts/` | 3 | The new mascot sheets generated for this project |
| `01_logos/` | 18 | Original bear logo, landscape logo, pressure-wash logo, **Pigeon Division (4590×5028)** |
| `02_mascot_bear/` | 5 | Bear plowing, bear in hot tub, groundhog seasonal art |
| `03_trucks/` | 12 | Truck photography, several already cropped as web banners |
| `04_promos/` | 16 | Printable coupons, $15-off, Christmas gift certificate |
| `05_community/` | 1 | Golf tournament (6830×6457) — community-involvement proof |
| `06_job_photos_fb/` | 154 | Real job photos from Facebook — **the gold. Use these heavily.** |
| `07_job_photos_other/` | 41 | More real work, incl. patios, decks, sidewalks |
| `audio/` | 1 | **The Buffalo radio commercial** |
| `99_stock_DO_NOT_USE/` | 24 | iStock images — ⚠️ licence does not demonstrably transfer. **Excluded from the new site.** |

**Rules**
1. **Real job photos over stock, always.** He has 195 of them.
2. Nothing from `99_stock_DO_NOT_USE` ships without a verified licence.
3. Every image: WebP/AVIF with fallback, explicit `width`/`height` (no layout shift),
   lazy-loaded below the fold, descriptive alt text naming the service and town.
4. Many originals are 2048px+ — resize properly; do not ship 2MB heroes.
5. `[CONFIRM]` Dave has permission to publish customer-property before/afters.

---

## 10. TECHNICAL CONSTRAINTS

- **Host:** GitHub Pages, repo `dshenterpriseinc/dshandymen`, branch `main`
- **Static only.** No server, no PHP, no database.
- **Custom domain:** `dshandymen.com` + `www` → CNAME file → enable *Enforce HTTPS*
- ⚠️ **Deploy blocker:** the local `gh` CLI is authenticated as `redtopatfunnyfarm`, which
  currently has **pull-only** access. Either sign in as `dshenterpriseinc` or add the
  other account as a collaborator before the first push.
- **301 the old URLs.** Map every `dhenterprise.com/DJS/*` path to its new equivalent so
  16 years of links don't 404.
- **Performance budget:** LCP < 2.0s on 4G, CLS < 0.05, total JS < 100KB gzipped.
  No jQuery, no Bootstrap, no page builder. Hand-written HTML/CSS + minimal JS.
- **Accessibility:** WCAG 2.2 AA. Real focus states, 4.5:1 contrast, keyboard-navigable
  everything including the chatbot, `prefers-reduced-motion` honoured.

---

## 11. SEO / LOCAL SEARCH

- `LocalBusiness` (or `HomeAndConstructionBusiness`) JSON-LD on every page: canonical NAP,
  geo, opening hours, `areaServed`, `priceRange`, `sameAs` → Facebook + BBB
- `Service` schema per service page · `FAQPage` on pages with FAQs ·
  `AggregateRating` **only** if genuinely sourced
- Unique title + meta description per page, town names in service-area titles
- Descriptive alt text carrying service + town
- `sitemap.xml`, `robots.txt`, canonical tags
- **Off-site actions to hand Dave:** claim/optimise the Google Business Profile, fix the
  NAP inconsistency across BBB/Birdeye/Yelp/Facebook, and run a review drive — going from
  13 to 50+ reviews will move the map pack more than any on-page change.

---

## 12. DO NOT

- ❌ Reproduce the public visitor counter
- ❌ Use dachshund / golden retriever / leprechaun stock photos
- ❌ Sand Dave's voice into generic contractor copy
- ❌ Put the cartoon bear at the top of the Pigeon Division or Helios pages
- ❌ Ship a carousel hero nobody scrolls
- ❌ Auto-play the radio ad
- ❌ Invent licence numbers, warranty terms, prices, or review counts
- ❌ Bury the phone number — it is the primary conversion path

---

## 13. OPEN QUESTIONS FOR DAVE

1. Canonical business address — Miriam Ave, S Shore Dr, or the PO Box?
2. Real business hours, and storm-response availability?
3. Licence number / insurance carrier for the trust bar?
4. Full, exact list of towns served — and any he wants to exclude?
5. Permission to publish customer before/after photos?
6. Move email off `@yahoo.com` to `dave@dshandymen.com`?
7. Does he want to buy the parked `dshandyman.com` (singular) defensively?
8. Any price ranges he's willing to publish, or quote-only?
9. Is the $20 referral offer still live?
10. Is the Helios partnership still active?
11. Who maintains the site after launch?

---

## 14. DEFINITION OF DONE — 9.8/10

1. Loads in under 2 seconds on a phone on 4G in a Hamburg driveway
2. Valid HTTPS, auto-renewing, never expires again
3. A stranger knows in 5 seconds what he does, where, and how to reach him
4. The Bear makes them smile; the BBB A+ badge makes them trust
5. Every photo is real work by his real crew
6. The chatbot answers the top 20 questions without Dave picking up the phone
7. Perfect Lighthouse accessibility score
8. Ranks for "snow plowing Hamburg NY" and siblings within two seasons
9. Dave is proud enough to put the URL on the truck
