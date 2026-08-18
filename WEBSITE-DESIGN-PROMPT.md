# BUILD BRIEF — dshandymen.com
### Hand this to Claude Design. Every asset referenced below already exists on disk.

---

## 0. THE BRIEF IN ONE LINE

> Design and build the website for **DS Handymen, Inc.** — a 16-year-old, BBB A+ rated home
> services company in Blasdell / Hamburg, New York, whose owner Dave Schultz is known locally
> as **"The Bear."** The site must be fast, mobile-first, unmistakably Western New York, and
> built around a mascot brand no competitor can copy.

**Deployment:** static site on **GitHub Pages**, repo `dshenterpriseinc/dshandymen`, custom
domain **dshandymen.com**. No server, no database, no PHP.

---

## 1. NON-NEGOTIABLE FACTS — use these exactly, invent nothing

| | |
|---|---|
| Legal name | **DS Handymen, Inc.** (*Handymen*, plural, with *Inc.*) |
| Owner | **Dave Schultz** — lifelong Hamburg resident, 50 years in the area |
| Known as | **"The Bear"** — he uses this himself ("Call the Bear today") |
| Founded | **1 November 2009** (16 years) |
| Trust | **BBB Accredited, A+ rating**, accredited since 26 March 2021. Fully insured. |
| Phone | **(716) 803-0091** — primary conversion path, he is a phone-first business |
| Email | `dshandymen@yahoo.com` *(recommend `dave@dshandymen.com` — flag, don't invent)* |
| Address | **135 Miriam Avenue, Suite 1, Blasdell, NY 14219** |
| Towns served | **Blasdell · Hamburg · Orchard Park · Lackawanna** (confirmed from his own advertising), plus the wider Southtowns |
| Reviews | **4.7★ from 13 reviews** — do not inflate this number |
| Payment | Cash, cheque, **Venmo: `david schultz@dshandymeninc`** |
| Gift certificates | **$100 / $250 / $500**, redeemable against any service |
| Offers | **$20 off** for referring a seasonal plowing customer · **10% off for Veterans, Seniors and Teachers** |
| Facebook | facebook.com/dshandymen (635 followers) |

> ⚠️ **NEVER print a phone number other than (716) 803-0091.** An earlier AI-generated logo
> contained a fake number (`716-555-0123`); that file is quarantined as
> `logo-badge-primary-PLACEHOLDER-wrong-phone.png` — **do not use it anywhere.**

---

## 2. SERVICES (the real list)

**❄️ Snow plowing** — residential driveways and commercial lots. Seasonal contracts or
one-off. Two trucks on route. *"Don't get stuck — get plowed."* · *"Get on the list now."*

**🌿 Landscaping** — mowing, mulching, planting, trimming, raking, gutter clean-outs,
winter protection for trees and shrubs.

**💦 Pressure washing** — driveways, siding, decks, roofs, sidewalks, pool decks.
*"If it's outside and it's dirty, we can help you out."*

**🔨 Handyman & remodeling** — window replacement, basement remodeling, kitchen upgrades,
flooring, drywall, deck refinishing, three-season rooms, outdoor bars.

**📦 House clearance** — attics, garages, full estate clear-outs. Under-marketed; give it a
real page. His own copy: *"It can be overwhelming figuring out where to start."*

**🏛️ Helios retractable glass sunrooms & patio enclosures** — trained dealer/installer.
Highest ticket; premium treatment.

**🕊️ The Pigeon Division** — interior/exterior design and finish carpentry, led by
**Nichole Pigeon**, a Rochester Institute of Technology (RIT) Design School graduate. Crew has
**40+ years collective experience**: custom design, trim, cabinets, drywall, paint, tile.

---

## 3. THE BRAND IDEA — The Bear and the Bird

This is the creative spine. Every Southtowns competitor is a surname and a truck photo.
DS Handymen has **two characters and a story**:

> **The Bear** does the heavy work — plowing, washing, hauling, building. Shows up in a blizzard.
> **The Bird** makes it beautiful — design, trim, cabinets, tile, finish.
> **Muscle and craft.** Two halves of one company.

Dave already wrote the line himself: *"The Bear and the Bird work together."*

**Voice:** plain-spoken Western New York. Warm, a bit funny, never corporate. Keep his
phrasing — *"Go Bills!"*, *"Call the Bear"*, *"Lake effect snow? No problem."* **Do not sand
it into agency copy.**

**Guardrail:** playful and Bear-forward on plowing/washing. Quiet, editorial and Bird-forward
on the Pigeon Division and Helios sunrooms — **no cartoon bear at the top of those pages.**

---

## 4. VISUAL SYSTEM

### Palette — taken from his current 2025/26 branding, not the old website
| Role | Hex | Use |
|---|---|---|
| Primary navy | `#1B2A4A` | Headers, footer, the Bear's work shirt, body text |
| Royal blue | `#00338D` | Buttons, links, Buffalo-pride moments |
| Charcoal | `#292D33` | Badge ring, truck vinyl, heavy UI |
| Bills red | `#C60C30` | Urgency, seasonal/holiday accents — **sparingly** |
| Safety yellow | `#F5B324` | Plow blades and equipment **only** — never a UI colour |
| Snow | `#F4F8FB` | Section backgrounds |
| Ink | `#0C1620` | Maximum-contrast text |

Red + royal blue together read as Buffalo Bills. That's deliberate and on-brand — but keep it
to seasonal/civic moments so the core site stays navy and charcoal.

### Typography
- **Display:** confident condensed sans with industrial character (Barlow Condensed, Oswald).
  Uppercase section headers.
- **Body:** humanist sans (Inter, Source Sans). **17–18px minimum** — a large share of his
  customers are older homeowners. Never below 16px. No thin weights on navy.

### Motifs
Carved-wood sign texture · snow-drift section dividers · bear paw prints as list bullets ·
blueprint grid on Pigeon Division pages. Seasoning, not wallpaper.

---

## 5. ASSET MANIFEST — everything below is already produced and on disk

### `assets/11_WEB_READY/` — transparent PNGs, drop straight in

**Brand marks**
| File | Use |
|---|---|
| `logo-badge-dark.png` (1024²) | **PRIMARY LOGO.** Charcoal disc, white bear + ring text, transparent outside. No phone number. |
| `logo-badge-white-knockout.png` | White-on-dark variant for navy sections and the footer |
| `logo-pigeon-division.png` | Pigeon Division sub-brand badge |
| `favicon-16/32/48/180/192/512.png` | Favicon + Apple touch + Android |
| `icon-maskable-512.png` | PWA maskable icon (navy safe-zone) |
| `og-share-1200x630.jpg` | Open Graph / Twitter card — correct phone and URL baked in |

**Mascot cutouts — all transparent, all in the corrected navy shirt**
| File | Use |
|---|---|
| `mascot-waving.png` | Homepage hero, 404 page |
| `mascot-shovelling.png` | Snow plowing card |
| `mascot-plow-truck.png` | Snow plowing hero |
| `mascot-pressure-washing.png` | Pressure washing card |
| `mascot-mowing.png` | Landscaping card |
| `mascot-ladder-drill.png` | Handyman card |
| `mascot-bear-shovel-hero.png` | Large hero cut-out |
| `mascot-bear-go-bills.png` | Game-day / seasonal banner **only** |
| `mascot-pigeon-blueprint.png` | Pigeon Division page |
| **`mascot-bear-and-bird-duo.png`** | **The most important asset.** The brand story in one image — use on the homepage "Bear & Bird" section and the About page. |

**Chatbot avatar states** — 512² circular PNGs, same 3D model, swap by state:
`chatbot-neutral` · `chatbot-waving` · `chatbot-listening` · `chatbot-delighted` ·
`chatbot-pointing` · `chatbot-thumbsup`

### `assets/12_PHOTOS_CURATED/` — 19 real job photos, descriptively named
Includes a genuine **before/after pair of the same house** —
`beforeafter-siding-windows-BEFORE.jpg` (yellow, old windows, Bills flag flying) and
`beforeafter-siding-windows-AFTER.jpg` (blue, new siding and windows, hedge cleared).
**Build the homepage before/after slider around this pair.**
Also: kitchen remodel (3 angles), tile backsplash, bathroom vanity, living room, dining room,
finished basement (2), refinished deck, two landscaping beds, window install in progress,
night siding work, two roof "before" shots, and the branded truck.

### `assets/10_FINAL_commercials/` — 9 finished :15–:25 mascot commercials
Photoreal, 3D-animated and cartoon styles. Each ends on a branded card with the correct
phone and URL. Use as **muted, looping hero background video** and as section headers.
Silent by design — never autoplay with sound.

### `assets/audio/` — **his real Buffalo radio commercial** (`WLBC_..._Buffalo_1W002.mp3`)
Almost no competitor has this. Give it a styled player: *"Hear our radio ad."* Never autoplay.

### `assets/06_job_photos_fb/` + `07_job_photos_other/` — 195 more real photos for galleries

> ⚠️ **`assets/99_stock_DO_NOT_USE/`** — 24 iStock files whose licence does not demonstrably
> transfer. **Excluded. Do not ship.**

---

## 6. SITE ARCHITECTURE

```
/                                Home
/services/                       Hub
  /snow-plowing/                 ❄️  seasonal contracts + $20 referral
  /landscaping/                  🌿
  /pressure-washing/             💦
  /handyman-remodeling/          🔨
  /house-clearance/              📦
  /sunrooms-patio-enclosures/    🏛️  premium
  /pigeon-division/              🕊️  premium, design-led
/about/                          Dave, 50 years in Hamburg, BBB A+, the crew
/gallery/                        Before & after, filterable by service
/reviews/                        Reviews + prominent "leave a review" CTA
/service-area/                   Hub
  /hamburg-ny/ /blasdell-ny/ /orchard-park-ny/ /lackawanna-ny/
/gift-certificates/              $100 / $250 / $500 — currently promoted nowhere online
/quote/                          Main conversion page — form + photo upload
/contact/
/blog/                           "Helpful Tips" — WNY seasonal maintenance
404 · /privacy/ · sitemap.xml · robots.txt
```

Service-area pages must be **genuinely differentiated** — real landmarks, real neighbourhood
names, real job photos from that town. Four near-identical templated pages is thin content.

---

## 7. HOMEPAGE SPEC

**A · Sticky header** — badge left, nav centre, **(716) 803-0091 as a tap-to-call button**
right, always visible. Persistent bottom call bar on mobile.

**B · Seasonal hero** — server-rendered default, small date-based JS swap on top:
- **Nov–Mar** Bear plowing. *"Lake effect snow? No problem."* → Reserve Your Plow Contract
- **Apr–Jun** Bear pressure washing. *"Wash away winter."* → Get a Free Quote
- **Jul–Sep** Landscaping / remodel. *"Make the most of your outdoor space."*
- **Oct** Bear with rake. *"Prep for winter today."*

Muted looping commercial behind it, poster frame first, lazy-loaded, must not block LCP.

**C · Trust bar** (above the fold on desktop):
`BBB A+ Accredited` · `Since 2009` · `Fully Insured` · `4.7★ Google` · `Locally Owned, Hamburg NY`

**D · Six service cards** — each with its mascot cutout.

**E · The Bear & The Bird** — the split brand story, two columns, using
`mascot-bear-and-bird-duo.png`. **The emotional centre of the page.**

**F · Before & After slider** — the real siding/windows pair, drag to compare.

**G · Reviews** — real quotes with names (Ben Osborne, Gary Walters, Dave Brennan, Renee P).

**H · Radio ad player** — *"Hear our radio ad."*

**I · Service-area map** with linked town pages.

**J · Quote CTA band** → the form.

**K · Footer** — NAP block (schema-marked), hours, services, socials, BBB badge, Venmo.

### Other pages of note
- **Snow plowing:** urgency-led. Season countdown. Residential vs commercial. Seasonal vs
  one-off comparison table. **The $20 referral as a real feature, not fine print.**
- **Pigeon Division:** quieter, editorial, generous white space. Lead with Nichole's RIT
  credential and 40 years of crew experience. Large before/after imagery.
- **Quote page:** name · email · phone · service (multi-select) · address/town · timeframe ·
  description · **photo upload (multiple)** · how did you hear about us. Static-compatible
  handler (Formspree / Web3Forms). Honeypot + rate limiting. Clear success state.

---

## 8. "ASK THE BEAR" CHATBOT

Signature feature; nothing in this market has one.

- Floating circular launcher bottom-right using `chatbot-neutral.png`
- Idle: gentle breathing/bob, occasional blink. After ~20s on a service page a small bubble:
  *"Need a quote? Ask me."*
- On open: panel with the 3D bear at top, avatar swapping between the six states
  (neutral → listening while typing → delighted on success → pointing when linking out)
- **CSS transforms + sprite swap only. No 3D engine.** Must not cost seconds of load.
- Quick-reply chips: `Snow plowing` · `Get a quote` · `Service area` · `Pricing` · `Talk to Dave`
- **Always** offers the phone number as an escape hatch. **Never invents prices.**
- Keyboard navigable, focus-trapped, ARIA-labelled, honours `prefers-reduced-motion`

**Pre-load this Q&A** (drawn from his real site and Facebook):

| Intent | Answer |
|---|---|
| Who are you? | "I'm the Bear — Dave Schultz's sidekick at DS Handymen. Dave's been fixing, plowing and building around Hamburg for 50 years." |
| Areas served? | Blasdell, Hamburg, Orchard Park, Lackawanna and the wider Southtowns. |
| Insured? | Fully insured, and BBB Accredited with an A+ rating since 2021. |
| How long in business? | Since 2009 — 16 years. |
| Do you plow driveways? | Yes — residential driveways and commercial lots. Seasonal contract or one-off. Two trucks on route. |
| Plowing cost? | Depends on driveway size and layout. Call (716) 803-0091 or send a photo through the quote form. |
| Referral discount? | Refer another seasonal customer and get **$20 off**. |
| What can you pressure wash? | Driveways, siding, decks, roofs, sidewalks, pool decks. "If it's outside and it's dirty." |
| Kitchens / bathrooms? | That's the Pigeon Division — led by Nichole Pigeon, an RIT Design School graduate. |
| Sunroom? | Yes — three-season rooms, and we're a trained installer for Helios retractable glass sunrooms. |
| Clear my attic/garage? | Yes — house clearance is one of our services. |
| Gutters? | Yes — gutter clean-outs, repairs and replacement. |
| Emergency / storm? | Call Dave directly at (716) 803-0091. |
| Free estimates? | Yes. |
| How do I book? | Quote form (photos welcome) or call (716) 803-0091. |
| Where are you based? | Blasdell, NY — right in the Southtowns. |
| How can I pay? | Cash, cheque and **Venmo** — `david schultz@dshandymeninc`. |
| Gift certificates? | **$100, $250 or $500**, good toward any service. "Give someone the gift of time." |
| Discounts? | **10% off for Veterans, Seniors and Teachers**, and **$20 off** for a seasonal plowing referral. |
| Go Bills? | "Let's go Buffalo." 🦬 |

---

## 9. TECHNICAL

- **GitHub Pages**, repo `dshenterpriseinc/dshandymen`, branch `main`
- Custom domain `dshandymen.com` + `www` → `CNAME` file → **Enforce HTTPS**
  *(This permanently fixes his expired-certificate problem — the old cert lapsed 14 Jul 2026
  and every visitor has been hitting a red "Not Secure" interstitial since.)*
- **301 every old URL** from `dhenterprise.com/DJS/*` to its new equivalent — 16 years of links
- **Budget:** LCP < 2.0s on 4G, CLS < 0.05, total JS < 100KB gzipped. Hand-written HTML/CSS +
  minimal JS. No jQuery, no Bootstrap, no page builder.
- **Images:** WebP/AVIF with fallback, explicit `width`/`height`, lazy-load below the fold,
  descriptive alt text naming service + town. Several originals are 2048px+ — resize properly.
- **Accessibility:** WCAG 2.2 AA. Real focus states, 4.5:1 contrast, full keyboard nav
  including the chatbot, `prefers-reduced-motion` honoured.

> ⚠️ **Deploy blocker:** the local `gh` CLI is authenticated as `redtopatfunnyfarm`, which has
> **pull-only** access to that repo. Sign in as `dshenterpriseinc` or add the other account as
> a collaborator before the first push.

---

## 10. SEO / LOCAL SEARCH

- `LocalBusiness` / `HomeAndConstructionBusiness` JSON-LD on every page: canonical NAP, geo,
  hours, `areaServed`, `priceRange`, `sameAs` → Facebook + BBB
- `Service` schema per service page · `FAQPage` where FAQs appear · `AggregateRating` **only**
  if genuinely sourced (4.7 / 13 — do not inflate)
- Unique title + meta description per page; town names in service-area titles
- `sitemap.xml`, `robots.txt`, canonical tags

**Off-site, for Dave (not the build):** claim and optimise the Google Business Profile; fix the
**NAP inconsistency** across BBB / Birdeye / Yelp / Facebook (three different addresses are
live); run a review drive — 13 → 50+ will move the map pack more than any on-page change.

---

## 11. DO NOT

- ❌ Use `logo-badge-primary-PLACEHOLDER-wrong-phone.png` — it carries a fake number
- ❌ Print any phone number other than **(716) 803-0091**
- ❌ Reproduce the old site's public visitor counter ("Users Today: 1")
- ❌ Ship anything from `99_stock_DO_NOT_USE/`
- ❌ Put the cartoon bear atop the Pigeon Division or Helios pages
- ❌ Autoplay the radio ad or any video with sound
- ❌ Sand Dave's voice into generic contractor copy
- ❌ Invent licence numbers, warranties, prices, or review counts
- ❌ Bury the phone number

---

## 12. OPEN QUESTIONS FOR DAVE (flag, don't guess)

1. Canonical address — Miriam Ave, S Shore Dr, or the PO Box? (all three are live somewhere)
2. Real business hours, and storm-response availability?
3. Licence number / insurance carrier for the trust bar?
4. Any towns to add or exclude beyond the confirmed four?
5. Permission to publish customer before/after photos?
6. Move email off `@yahoo.com`?
7. Is the $20 referral still live? The 10% Veterans/Seniors/Teachers discount?
8. Is the Helios partnership still active?
9. Any price ranges he'll publish, or quote-only?

---

## 13. DEFINITION OF DONE

1. Loads under 2s on a phone on 4G in a Hamburg driveway
2. Valid auto-renewing HTTPS that never expires again
3. A stranger knows in 5 seconds what he does, where, and how to reach him
4. The Bear makes them smile; the BBB A+ badge makes them trust
5. Every photo is real work by his real crew
6. The chatbot answers the top 20 questions without Dave picking up the phone
7. Perfect Lighthouse accessibility score
8. Dave is proud enough to put the URL on the truck
