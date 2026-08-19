#!/usr/bin/env python
"""Post-process the compiled site. Runs after compile.py; idempotent.

compile.py turns the captured Claude Design render into pages. Everything that
has to be *fixed* about that render lives here, so a rebuild never silently
loses it:
  1. real, sourced review quotes (the export shipped invented ones)
  2. responsive layer (the export had inline grids and no breakpoints)
  3. <picture>/WebP + width/height + lazy-loading
  4. Review JSON-LD
"""
import io, os, re, glob, json
from brandcolour import recolour_text
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ROOT = r"R:/Documents/Claude/Projects/DSHandymen"
OUT  = os.path.join(ROOT, "docs")

# ---------------------------------------------------------------- 1. reviews
# Verbatim. Sourced. Nothing invented. A reviewer whose text cannot be sourced
# verbatim is removed rather than reconstructed.
REVIEWS = [
 ("Gary Walters", "via Google",
  "Came out and did my driveway! GREAT SERVICE! He even found a FedEx parcel left in the "
  "driveway that was left earlier that day I didn&#39;t know about."),
 ("Dave Brennan", "via Google",
  "Dave and his staff are very good at what they do. They don&#39;t normally fix snowblowers "
  "but they still took mine and fixed both of them! They are very friendly as well. "
  "I definitely recommend them!"),
 ("Joseph S", "via BBB",
  "Had an emergency with my dishwasher and called DS they came out quickly and loved my "
  "problem excellent communication prompt and professional I will definitely be using them again"),
 ("Ben Osborne", "via Google", "Dave is the best!"),
]

def fix_reviews(path, s):
    figs = [f for f in re.findall(r'<figure\b.*?</figure>', s, re.S) if 'REVIEW PENDING' in f]
    for i, fig in enumerate(figs):
        if i >= len(REVIEWS):
            s = s.replace(fig, '', 1)
            continue
        name, src, text = REVIEWS[i]
        new = re.sub(r'(<blockquote[^>]*>).*?(</blockquote>)',
                     lambda m: m.group(1) + text + m.group(2), fig, flags=re.S)
        new = re.sub(r'<span class="sc-interp">(Ben Osborne|Gary Walters|Dave Brennan|Renee P)</span>',
                     '<span>%s</span>' % name, new)
        new = new.replace('<span class="sc-interp">[unverified]</span>', '<span>%s</span>' % src)
        s = s.replace(fig, new, 1)
    return s

REVIEW_LD = '<script type="application/ld+json">' + json.dumps({
    "@context": "https://schema.org", "@type": "HomeAndConstructionBusiness",
    "@id": "https://dshandymen.com/#business", "name": "DS Handymen, Inc.",
    "review": [{"@type": "Review",
                "author": {"@type": "Person", "name": n},
                "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                "reviewBody": re.sub('&#39;', "'", t)} for n, _, t in REVIEWS]
}, separators=(",", ":")) + '</script>'

# ---------------------------------------------------------------- 2. images
_dims = {}
def dims_for(page_path, src):
    """resolve a page-relative src to a real file and return (w,h)"""
    base = os.path.dirname(page_path)
    p = os.path.normpath(os.path.join(base, src))
    if p in _dims: return _dims[p]
    try:
        with Image.open(p) as im: _dims[p] = im.size
    except Exception: _dims[p] = None
    return _dims[p]

def fix_images(page_path, s):
    idx = [0]
    def repl(m):
        tag = m.group(0); idx[0] += 1
        sm = re.search(r'src="([^"]+)"', tag)
        if not sm: return tag
        src = sm.group(1)
        if not ('width=' in tag and 'height=' in tag):
            d = dims_for(page_path, src)
            if d: tag = tag[:-1].rstrip() + ' width="%d" height="%d">' % d
        # every <img> must carry an alt attribute. These service-card mascots are
        # decorative - the card already names the service - so alt="" is correct,
        # but the attribute itself is mandatory for WCAG.
        if ' alt=' not in tag:
            tag = tag[:-1].rstrip() + ' alt="">'
        if 'loading=' not in tag:
            tag = tag[:-1].rstrip() + ' loading="%s">' % ('eager' if idx[0] <= 2 else 'lazy')
        if 'decoding=' not in tag:
            tag = tag[:-1].rstrip() + ' decoding="async">'
        if idx[0] <= 2 and 'fetchpriority=' not in tag:
            tag = tag[:-1].rstrip() + ' fetchpriority="high">'
        webp = re.sub(r'\.(jpg|jpeg|png)$', '.webp', src, flags=re.I)
        if webp != src:
            real = os.path.normpath(os.path.join(os.path.dirname(page_path), webp))
            if os.path.exists(real):
                # a -sm variant exists only for gallery tiles (see make_thumbs.py).
                # Offering both lets a 1x screen take the tile-sized file while a
                # 2x screen still gets the full-resolution one.
                from PIL import Image as _I
                cands = []
                for suffix in ('-sm', '-md'):
                    v = webp[:-len('.webp')] + suffix + '.webp'
                    vr = os.path.normpath(os.path.join(os.path.dirname(page_path), v))
                    if os.path.exists(vr):
                        cands.append((v, _I.open(vr).width))
                if cands:
                    cands.append((webp, _I.open(real).width))
                    srcset = ', '.join('%s %dw' % c for c in cands)
                    # tiles are a third of a 1240px container less an 18px gap, so
                    # 31vw is closer to the truth than 33vw - and overstating it by
                    # even two pixels makes the browser skip the small file entirely
                    sizes = '(max-width: 760px) 100vw, (max-width: 1024px) 47vw, 31vw'
                    return ('<picture><source srcset="%s" sizes="%s" type="image/webp">%s</picture>'
                            % (srcset, sizes, tag))
                return '<picture><source srcset="%s" type="image/webp">%s</picture>' % (webp, tag)
        return tag
    return re.sub(r'<img\b[^>]*>', repl, s)


# ---------------------------------------------------------------- 3. plain-English labels
# "Pigeon Division" is the team's name and stays on its own page where it is explained.
# In navigation it means nothing to a homeowner, so links say what the work actually is.
NAV_RELABEL = [
    (">Pigeon Division<", ">Design &amp; Remodeling<"),
    (">Meet the Pigeon Division →<", ">See design &amp; remodeling →<"),
]

def relabel_nav(s):
    for a, b in NAV_RELABEL:
        s = s.replace(a, b)
    return s


# ---------------------------------------------------------------- 4. service-area map
MAP_BLOCK = """
<section aria-label="Service area map" style="background:#FFFFFF">
  <div style="max-width:1080px;margin:0 auto;padding:64px 24px 8px">
    <p style="margin:0 0 10px;font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:16px;
       letter-spacing:.2em;text-transform:uppercase;color:#00338D">Where we work</p>
    <h2 style="margin:0 0 10px;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:40px;
       letter-spacing:.01em;text-transform:uppercase;color:#1B2A4A">Across the Southtowns &amp; Western New York</h2>
    <p style="margin:0 0 26px;font-size:17.5px;color:#3D4756;max-width:62ch">
      The shop is on Miriam Avenue in Blasdell, so Hamburg, Blasdell, Orchard Park and Lackawanna are
      right on the route. We cover most of the greater Buffalo area besides &mdash; if you are near
      the ring below, just ask.</p>
    <picture>
      <source media="(max-width: 760px)" srcset="{PREFIX}assets/web/service-area-map-sm.svg" type="image/svg+xml">
    <img class="svc-map" src="{PREFIX}assets/web/service-area-map.svg" alt="Map of Western New York showing the DS Handymen service area centred on Blasdell, covering Hamburg, Orchard Park, Lackawanna and the wider greater Buffalo area, with Lake Erie to the west" loading="lazy" decoding="async" style="width:100%;height:auto;border:1px solid #DCE5EF;border-radius:12px;box-shadow:0 6px 22px rgba(27,42,74,.10)">
    </picture>
    <p style="margin:16px 0 0;font-size:15.5px;color:#5B6779">
      Not on the map? Call the Bear on <a href="tel:+17168030091" style="color:#00338D;font-weight:600">(716) 803-0091</a> &mdash; if we can get there, we will.</p>
  </div>
</section>
"""

def insert_map(path, s, prefix):
    if 'Service area map' in s:
        return s
    block = MAP_BLOCK.replace('{PREFIX}', prefix)
    name = path.replace(chr(92), '/').rstrip('/').split('/')
    is_area_hub = len(name) >= 2 and name[-2] == 'service-area'
    is_home = name[-1] == 'index.html' and name[-2] == 'docs'
    if is_area_hub:
        # straight after the page intro section
        i = s.find('</section>')
        if i > 0:
            return s[:i+10] + block + s[i+10:]
    elif is_home:
        # just before the existing town list
        i = s.find('<section aria-label="Service area"')
        if i > 0:
            return s[:i] + block + s[i:]
    return s


# ---------------------------------------------------------------- 5. design page copy
# The page led with "Now introducing the Pigeon Division" - a private nickname,
# in a stale announcement frame. It leads with the work instead. These entries
# used to name the division; they no longer can, so the lead credits the crew
# that actually does the work.
COPY_FIXES = [
    (">Now introducing the Pigeon Division<", ">Design &amp; Remodeling<"),
    ("Interior & exterior design and construction &mdash; custom design, trim, cabinets, drywall, paint, tile and finish work.",
     "Kitchens, bathrooms, custom trim, cabinets, tile, paint and finish carpentry across the Southtowns "
     "&mdash; by Dave and his crew."),
    ("Now... introducing the Pigeon Division!", "Design &amp; Remodeling"),
    # the ruler is a left-hand rail on desktop but sits above the copy once the
    # grid collapses, so the wording cannot name a direction
    ('that stick on the left is what', 'that stick is what'),
]

def fix_copy(s):
    for a, b in COPY_FIXES:
        s = s.replace(a, b)
    return s


# ---------------------------------------------------------------- 6. quote form
# The export shipped the form with no action and no method - the site's primary
# conversion path silently did nothing. Wired to FormSubmit, which needs no
# account and no API key, just the destination address, and accepts the photo
# upload. Requires ONE activation click in the first confirmation email.
LIVE_BASE = "https://dshenterpriseinc.github.io/dshandymen/"
FORM_ENDPOINT = "https://formsubmit.co/dshandymen@yahoo.com"

FORM_HIDDEN = (
 '<input type="hidden" name="_subject" value="New quote request from dshandymen.com">'
 '<input type="hidden" name="_template" value="table">'
 '<input type="hidden" name="_captcha" value="false">'
 '<input type="hidden" name="_honey" value="">'
 '<input type="hidden" name="_next" value="{NEXT}">'
)

def wire_form(path, s, prefix):
    """Point the quote form at a real endpoint and make it enforce its own fields.

    The design tool emitted a form with correct name= attributes but no action and
    no method, so submitting it did nothing at all. FormSubmit needs no account and
    forwards file attachments, which matters here - people photograph the driveway.
    """
    if '<form' not in s or 'formsubmit.co' in s:
        return s
    s = s.replace('<form style=',
                  '<form action="%s" method="POST" enctype="multipart/form-data" style=' % FORM_ENDPOINT, 1)
    i = s.find('>', s.find('<form')) + 1
    # FormSubmit needs an absolute redirect URL. Until the apex DNS moves this must
    # be the address the site is actually served from, or every submit lands on a 404.
    s = s[:i] + FORM_HIDDEN.replace('{NEXT}', LIVE_BASE + 'thank-you/') + s[i:]

    # the HTML parser alphabetises attributes, so key off name= rather than position
    def add_attr(html, field, attr):
        pat = re.compile('(<(?:input|textarea|select)[^>]* name="' + field + '"[^>]*?)(/?>)')
        key = attr.split('=')[0]
        def f(m):
            return m.group(0) if key in m.group(1) else m.group(1) + ' ' + attr + m.group(2)
        return pat.sub(f, html, count=1)

    # FormSubmit only forwards a file if the field is literally named "attachment"
    s = re.sub('(<input[^>]* )name="photos"',
               lambda m: m.group(1) + 'name="attachment"', s, count=1)

    for field, attr in [('name', 'required'), ('phone', 'required'), ('description', 'required'),
                        ('attachment', 'accept="image/*"'), ('attachment', 'multiple'),
                        ('companyname', 'tabindex="-1"'), ('companyname', 'autocomplete="off"'),
                        ('companyname', 'aria-hidden="true"')]:
        s = add_attr(s, field, attr)
    return s


THANKYOU = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thanks &mdash; we&rsquo;ll be in touch | DS Handymen, Inc.</title>
<meta name="description" content="Thanks for your quote request. Dave will get back to you shortly. Call (716) 803-0091 if it is urgent.">
<meta name="robots" content="noindex">
<link rel="canonical" href="https://dshandymen.com/thank-you/">
<link rel="icon" href="../assets/web/favicon-32.png">
<link rel="preload" href="../assets/fonts/barlow-condensed-700-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="../assets/fonts.css">
<style>
 body{margin:0;min-height:100vh;display:grid;place-items:center;background:#1B2A4A;color:#fff;
      font-family:'Source Sans 3',system-ui,sans-serif;font-size:18px;text-align:center;padding:28px}
 .card{max-width:620px}
 img{width:150px;height:auto;margin-bottom:18px}
 h1{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:clamp(38px,7vw,60px);
    text-transform:uppercase;letter-spacing:.01em;margin:0 0 14px;line-height:1.02}
 p{color:#DCE6F2;margin:0 0 22px;line-height:1.55}
 a.btn{display:inline-block;background:#F5B324;color:#0C1620;text-decoration:none;font-weight:700;
    font-family:'Barlow Condensed',sans-serif;font-size:21px;letter-spacing:.06em;text-transform:uppercase;
    padding:14px 28px;border-radius:4px}
 a.plain{color:#F5B324}
 @media(prefers-reduced-motion:no-preference){img{animation:bob 4s ease-in-out infinite}
   @keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}}
</style></head>
<body><main class="card">
 <img src="../assets/web/mascot-waving.webp" alt="" loading="eager" decoding="async" fetchpriority="high" width="150" height="176">
 <h1>Got it &mdash; thanks.</h1>
 <p>Your request is with Dave. He&rsquo;ll come back to you as soon as he&rsquo;s off the route.<br>
    If it&rsquo;s urgent, just call &mdash; that&rsquo;s always fastest.</p>
 <p><a class="btn" href="tel:+17168030091">Call the Bear &middot; (716) 803-0091</a></p>
 <p><a class="plain" href="../">&larr; Back to the site</a></p>
</main></body></html>
"""

def write_thankyou():
    d = os.path.join(OUT, "thank-you")
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(recolour_text(THANKYOU))

# ---------------------------------------------------------------- run
# ---------------------------------------------------------------- contrast
# Three of these are structural rather than palette tweaks, so they live here as
# named fixes rather than in the generated map.

def scope_footer_links(s):
    """Stop the footer's link colour leaking onto the whole page.

    The footer component shipped its own <helmet> block with a bare `a{...}`
    rule - pale blue links, correct against the near-black footer. Capture lost
    the framework's scoping, so it emitted last and won the cascade for every
    link on the page: body links rendered at 2.18:1 on white and stopped looking
    like links at all.
    """
    return s.replace("body{margin:0} a{color:#9FB1CC}a:hover{color:#FFFFFF}",
                     "body{margin:0} footer a{color:#9FB1CC}footer a:hover{color:#FFFFFF}")


def fix_terracotta(s):
    """White on the Pigeon Division terracotta was 4.22:1. Nudge it to 4.5."""
    return s.replace("rgb(181, 103, 63)", "rgb(168, 95, 58)")


# The sunrooms hero is white type over a bright patio photo; the original scrim
# faded to 15% at the top, leaving the eyebrow at 1.79:1 and the headline at
# 2.09:1. Deepen it - the photo still reads, the type becomes legible.
SCRIM_FIXES = [
    ("linear-gradient(to top, rgba(12, 22, 32, 0.88) 0%, rgba(12, 22, 32, 0.35) 55%, "
     "rgba(12, 22, 32, 0.15) 100%)",
     "linear-gradient(to top, rgba(12, 22, 32, 0.93) 0%, rgba(12, 22, 32, 0.78) 45%, "
     "rgba(12, 22, 32, 0.62) 100%)"),
]


def fix_scrims(s):
    for old, new in SCRIM_FIXES:
        s = s.replace(old, new)
    return s


_CMAP = None


def apply_contrast_map(path, s):
    """Apply the palette moves solved by build/fix_contrast.py.

    Keyed on the literal inline style attribute the colour was declared in, so a
    rebuild reapplies exactly the same swap without needing a browser. Refresh
    with `python build/fix_contrast.py` after any design change.
    """
    global _CMAP
    if _CMAP is None:
        f = os.path.join(ROOT, "build", "contrast_map.json")
        _CMAP = json.load(io.open(f, encoding="utf-8")) if os.path.exists(f) else []
    rel = path.replace(chr(92), "/").split("/docs/")[1]
    for entry in _CMAP:
        if entry["file"] != "docs/" + rel:
            continue
        old = entry["style"]
        new = old
        for a, b in entry["swaps"].items():
            new = new.replace(a, b)
        if new == old:
            continue
        # anchor on the whole attribute value: a short style string is often a
        # substring of a longer one, and an unanchored replace recolours that
        # element too - which is how the reviews footer ended up at 3.06:1
        for q in ('"', chr(39)):
            s = s.replace("style=" + q + old + q, "style=" + q + new + q)
    return s


# ---------------------------------------------------------------- 6. font fallbacks
# The webfonts load with display=swap, which reflowed the whole document when
# they arrived. Naming a metric-matched stand-in ahead of the generic keeps the
# first paint on the same baseline grid as the final one. The @font-face rules
# that define these live in responsive.css.
FONT_STACKS = [
    ('"Barlow Condensed", sans-serif', '"Barlow Condensed", "Barlow Condensed Fallback", sans-serif'),
    ("'Barlow Condensed',sans-serif", "'Barlow Condensed','Barlow Condensed Fallback',sans-serif"),
    ('"Source Sans 3", sans-serif', '"Source Sans 3", "Source Sans 3 Fallback", sans-serif'),
    ("'Source Sans 3',sans-serif", "'Source Sans 3','Source Sans 3 Fallback',sans-serif"),
    ("'Source Sans 3',system-ui,sans-serif", "'Source Sans 3','Source Sans 3 Fallback',system-ui,sans-serif"),
]


def add_font_fallbacks(s):
    if 'Barlow Condensed Fallback", sans-serif' in s or "Barlow Condensed Fallback',sans-serif" in s:
        return s
    for old, new in FONT_STACKS:
        s = s.replace(old, new)
    return s


# ---------------------------------------------------------------- 7. hero video
# The markup carried src="...mp4" *and* preload="metadata", so the browser began
# pulling the mp4 during parse; site.js then swapped in a <source> list and the
# browser fetched the webm too. Every visitor paid for both encodings - 947 KB on
# the home page for one decorative background. Dropping the attribute leaves
# site.js as the single source of truth for which file to fetch.

def slim_hero_video(s):
    def repl(m):
        tag = m.group(0)
        tag = re.sub(r'\s+src="[^"]*"', '', tag)
        tag = re.sub(r'preload="[^"]*"', 'preload="none"', tag)
        if 'preload=' not in tag:
            tag = tag[:-1].rstrip() + ' preload="none">'
        return tag
    return re.sub(r'<video\b[^>]*>', repl, s)


# ---------------------------------------------------------------- 8. honest labels
# A caption audit against the actual photographs turned up five tiles describing
# work the picture does not show. On a contractor's portfolio that is not a
# cosmetic problem - the pressure-washing page was presenting two photographs of
# a mulch bed as a deck "before and after washing".
#
# deck-wash-before/after  are a mulch bed and a barrow of mulch on a driveway
# bar-1 / bar-2           are one deck, bare then stained - there is no bar
# fb-job-06               is a kitchen, captioned as yard work
# fb-job-08               is a lawn regrade, captioned only as "job site"
#
# Each entry rewrites text inside the <figure> that references that file, so a
# caption shared with an unrelated tile elsewhere is left alone.
FIGURE_FIXES = {
    "deck-wash-before": [("Weathered deck before washing", "Fresh mulch going down around the beds"),
                         ("Deck before washing &mdash; grey and weathered",
                          "Fresh mulch going down around the beds"),
                         (">Deck wash<", ">Mulch bed<"),
                         (">Before<", ">During<")],
    "deck-wash-after":  [("Deck after pressure washing", "Mulch delivered and ready to spread"),
                         ("Same deck after washing &mdash; wood grain restored",
                          "Mulch delivered and ready to spread"),
                         (">Deck wash<", ">Mulch delivered<"),
                         (">After<", ">During<")],
    "bar-1":            [("Custom bar build", "Deck build &middot; before stain"),
                         ("Custom-built bar", "New deck boards down, before stain"),
                         (">Custom bar<", ">Deck build<"),
                         (">After<", ">Before stain<")],
    "bar-2":            [("Finished custom bar", "The same deck once it was stained"),
                         ("Custom bar &middot; finished", "Deck build &middot; stained")],
    "fb-job-06":        [('alt="Yard work"', 'alt="Kitchen remodel, cabinets and range"'),
                         (">Yard work<", ">Kitchen remodel<")],
    "fb-job-08":        [('alt="Work in progress"', 'alt="Lawn regraded and reseeded"'),
                         (">Job site<", ">Yard work<")],
}


def fix_figure_labels(s):
    def repl(m):
        fig = m.group(0)
        for name, subs in FIGURE_FIXES.items():
            if name + "." not in fig:
                continue
            for old, new in subs:
                fig = fig.replace(old, new)
        return fig
    return re.sub(r"<figure\b.*?</figure>", repl, s, flags=re.S)


# ---------------------------------------------------------------- 9. pressure washing
# The "Real jobs, real grime" section promised "every photo below is our crew's
# work" and then showed two photographs of a mulch bed as a deck before and
# after washing, alongside a clip-art badge among the real photographs.
#
# Two genuine shots were sitting unused in the asset folder, and both happen to
# be better than a pair anyway: each catches the job half finished, so the dirty
# and the clean are in the same frame.
PW_SWAPS = [
    ("assets/gallery/deck-wash-before", "assets/gallery/patio-3",
     "Concrete patio half washed, the clean half bright against the grime",
     "Patio, half done"),
    ("assets/gallery/deck-wash-after", "assets/gallery/pressure-washing",
     "Washing a wooden fence, the stripe already done showing the bare grain",
     "Fence, half done"),
]


def fix_pressure_washing(path, s, prefix):
    if "pressure-washing" not in path.replace(chr(92), "/").split("/docs/")[1]:
        return s
    for old, new, alt, cap in PW_SWAPS:
        if prefix + new + "." in s:
            continue                        # already swapped on a previous pass
        for ext in (".webp", ".jpg"):
            s = s.replace(prefix + old + ext, prefix + new + ext)
        s = re.sub(r'alt="[^"]*"(?=[^>]*' + re.escape(new) + r'\.jpg)', 'alt="%s"' % alt, s)
        # the caption sits in the same <figure> as the image we just swapped in
        def cap_repl(m, _new=new, _cap=cap):
            fig = m.group(0)
            if _new + "." not in fig:
                return fig
            return re.sub(r"(<figcaption[^>]*>)[^<]*(</figcaption>)",
                          lambda c: c.group(1) + _cap + c.group(2), fig)
        s = re.sub(r"<figure\b.*?</figure>", cap_repl, s, flags=re.S)

    # the swapped-in files are a different shape, so the old width/height would
    # now describe the wrong aspect ratio and reintroduce layout shift
    for _, new, _, _ in PW_SWAPS:
        d = dims_for(path, prefix + new + ".jpg")
        if d:
            s = re.sub(r'(<img\b[^>]*' + re.escape(new) + r'\.jpg"[^>]*?)width="\d+" height="\d+"',
                       lambda m, _d=d: m.group(1) + 'width="%d" height="%d"' % _d, s)

    # a clip-art badge does not belong in a strip captioned "every photo below
    # is our crew's work"
    s = re.sub(r"<picture>(?:(?!</picture>).)*power-washing(?:(?!</picture>).)*</picture>",
               "", s, flags=re.S)
    return s


# ---------------------------------------------------------------- 10. header badge
# The header logo on all 21 pages was logo-badge-white-knockout, which had been
# cut from the concept sheet's black panel and kept a slab of that black along
# one side, plus a clipped ring. The full-colour badge is the actual brand mark,
# has clean edges, and carries more contrast against the navy header anyway.

def fix_header_badge(s):
    """Put the emblem badge on every mark.

    The build inherited two different badges - a charcoal-ringed "Home Repair &
    Snow Services" disc in the header and a monochrome version in the footer -
    and neither was the mark Dave actually likes. The sheet 01 emblem is: teal
    shirt, gold bars, tan inner ring, "Snow & Home Services". It needs no
    recolour, being from the same teal sheet the mascots come from, and its gold
    keeps it legible on the near-black footer as well as the navy header.

    Runs before fix_images so the <picture> wrapper is built around the name that
    actually ships - getting that order wrong previously shipped a 499 KB png.
    """
    for old_name in ('logo-badge-white-knockout', 'logo-badge-primary', 'logo-badge-dark'):
        s = s.replace(old_name, 'logo-badge-teal')
    return s


# ---------------------------------------------------------------- 11. brand hue
# The captures are fixed JSON and came back in navy, so the site cannot simply be
# re-exported in teal - the rotation has to live in the build. Run last, after
# every other colour decision including the contrast map, and because it holds
# relative luminance exactly, each ratio the map solved for survives it.

def to_brand_teal(s):
    return recolour_text(s)


# ---------------------------------------------------------------- 12. the Bird's page
# Design & Remodeling was the odd one out: a centred hero on flat cream while
# every other page opens left-aligned on dark with footage behind it. Cream also
# meant the hero video had to sit under a 90% scrim to keep the type legible,
# which washed the clip out to almost nothing.
#
# So the hero now matches the rest of the site - dark ground, headline top left,
# the standard directional scrim that is heaviest under the text and lightest on
# the right where the footage can be seen. The drafting grid is not lost; it
# moves down to the band underneath, which is where it can be a texture rather
# than something fighting a video.
#
# Colours here are the pre-rotation navy values the other service heroes use, so
# to_brand_teal lands this page on exactly the same teal as its siblings.

HERO_FIXES = [
    # centred cream panel -> left-aligned dark hero
    ('max-width: 1080px; margin: 0px auto; padding: 96px 24px 88px; text-align: center;',
     'max-width: 1240px; margin: 0px auto; padding: 84px 24px 76px; text-align: left;'),
    # the badge leads the column instead of floating centre
    ('width: 180px; height: 180px; object-fit: contain; display: block; margin: 0px auto 10px;',
     'width: 118px; height: 118px; object-fit: contain; display: block; margin: 0px 0px 18px;'),
    # eyebrow, headline and lead take the dark-hero palette
    ('letter-spacing: 0.24em; text-transform: uppercase; color: rgb(138, 128, 120);',
     'letter-spacing: 0.24em; text-transform: uppercase; color: rgb(245, 179, 36);'),
    ('line-height: 1.04; letter-spacing: 0.05em; text-transform: uppercase; color: rgb(44, 74, 107);',
     'line-height: 1.04; letter-spacing: 0.05em; text-transform: uppercase; color: rgb(255, 255, 255);'),
    ('margin: 0px auto; font-size: 20px; font-weight: 300; color: rgb(92, 83, 72); max-width: 52ch;',
     'margin: 0px; font-size: 20px; font-weight: 300; color: rgb(201, 212, 230); max-width: 46ch;'),
]

# the drafting grid, moved to the band below the hero
GRID_BELOW = ('background:'
              ' repeating-linear-gradient(0deg, rgba(44,74,107,.06) 0px, rgba(44,74,107,.06) 1px, transparent 1px, transparent 32px),'
              ' repeating-linear-gradient(90deg, rgba(44,74,107,.06) 0px, rgba(44,74,107,.06) 1px, transparent 1px, transparent 32px),'
              ' repeating-linear-gradient(0deg, rgba(44,74,107,.14) 0px, rgba(44,74,107,.14) 1px, transparent 1px, transparent 160px),'
              ' repeating-linear-gradient(90deg, rgba(44,74,107,.14) 0px, rgba(44,74,107,.14) 1px, transparent 1px, transparent 160px),'
              ' rgb(239, 231, 220);')


def style_design_page(path, s):
    if 'design-remodeling' not in path.replace(chr(92), '/'):
        return s

    # hero: plain dark ground. The photograph and the grid both come off - the
    # video is the background now, and two textures behind one headline is one
    # too many.
    i = s.find('<section', s.find('<body>'))
    j = s.find('>', i)
    if i > 0 and 'repeating-linear-gradient' in s[i:j]:
        # keep the positioning add_hero_video established - without it the scrim
        # resolves against the viewport and greys out the whole page
        s = s[:i] + '<section style="position:relative;overflow:hidden;background: rgb(12, 22, 32);"' + s[j:]

    for old, new in HERO_FIXES:
        s = s.replace(old, new, 1)

    # the band below the hero picks up the drafting grid
    s = s.replace('<section style="background: rgb(239, 231, 220);">',
                  '<section style="' + GRID_BELOW + '">', 1)

    # the gallery keeps its own cream band so it still reads as a section
    i = s.find('>The work<')
    if i > 0:
        j = s.rfind('<section', 0, i)
        if j > 0 and 'background' not in s[j:s.find('>', j) + 1]:
            s = s[:j] + '<section style="background: rgb(250, 247, 243);"' + s[j + 8:]
    return s


# ---------------------------------------------------------------- 14. hero video
# Each service page gets the clip that matches what it sells, behind its hero,
# the way the home page already works. Silent and looping - they carry no audio
# track at all, so they cannot make noise even if something re-enables it.
#
# Two shapes of hero exist. Most are a solid-coloured section with the content
# straight inside, so the video and a scrim go in as the first two children and
# the content is lifted above them. Sunrooms already layers a photograph and a
# gradient absolutely, so the video slots between the two and inherits the
# gradient it already had as its scrim.

HERO_VIDEO = {
    'snow-plowing': 'snow-plowing',
    'pressure-washing': 'pressure-washing',
    'landscaping': 'landscaping',
    'handyman-remodeling': 'handyman-remodeling',
    'house-clearance': 'house-clearance',
    'sunrooms-patio-enclosures': 'sunrooms-patio-enclosures',
    'services': 'services',
    # registered ahead of its footage: add_hero_video skips any page whose clip is
    # not on disk yet, so this switches itself on the moment the file is encoded
    'design-remodeling': 'design-remodeling',
}


def _vid_tag(prefix, slug):
    return ('<video class="hero-vid" aria-hidden="true" muted loop playsinline preload="none"'
            ' poster="%sassets/video/hero-%s-poster.jpg"'
            ' data-src="%sassets/video/hero-%s.mp4"></video>' % (prefix, slug, prefix, slug))


# The sunrooms page sold three-season rooms and Helios retractable glass over a
# four-up of: a bare concrete slab, a poolside slab, a slab being pressure-washed
# with the washer and hose in shot, and a cinder-block garden bench. Not one of
# them showed an enclosure, and the first was captioned "Patio enclosure project".
#
# Dave has exactly one photograph of the finished product - patio-cover - and it
# was being spent as a hero backdrop underneath a video, where it read as a shed
# in somebody's back yard. It leads the grid instead, full width, and the two
# honest patio shots follow as what an enclosure gets built on. The pressure
# washer belongs to another service and the bench to none.
#
# Runs before fix_images so the srcset is built around the files that ship.
SUNROOM_PHOTOS = [
    ('patio-1', 'patio-cover', 'Covered patio enclosure built by DS Handymen', True),
    ('patio-2', 'patio-1', 'The concrete patio an enclosure gets built on', False),
    ('patio-3', 'patio-2', 'Poolside patio, ready for a three-season room', False),
]


def fix_sunroom_photos(f, s):
    if 'sunrooms-patio-enclosures' not in f.replace(chr(92), '/'):
        return s
    s = re.sub(r'<img[^>]*bench[^>]*>', '', s)
    for old, new, alt, wide in SUNROOM_PHOTOS:
        w, h = Image.open(os.path.join(ROOT, 'site-export', 'assets', 'gallery', new + '.jpg')).size

        def swap(m, old=old, new=new, alt=alt, wide=wide, w=w, h=h):
            tag = m.group(0).replace(old + '.', new + '.')
            tag = re.sub(r'alt="[^"]*"', 'alt="' + alt + '"', tag)
            tag = re.sub(r'width="\d+"', 'width="%d"' % w, tag)
            tag = re.sub(r'height="\d+"', 'height="%d"' % h, tag)
            if wide:
                if 'style="' in tag:
                    tag = tag.replace('style="', 'style="grid-column: 1 / -1;', 1)
                else:
                    tag = tag[:-1].rstrip() + ' style="grid-column: 1 / -1">'
            return tag

        s = re.sub(r'<img[^>]*' + old + r'\.[a-z]+[^>]*>', swap, s, count=1)
    return s


def add_hero_video(path, s, prefix):
    rel = path.replace(chr(92), '/').split('/docs/')[1]
    page = rel.split('/')[0]
    slug = HERO_VIDEO.get(page)
    if not slug or '<video class="hero-vid"' in s:
        return s
    if not os.path.exists(os.path.join(OUT, 'assets', 'video', 'hero-%s.mp4' % slug)):
        return s          # footage not cut yet; leave the hero alone rather than 404

    body = s.index('<body>')
    m = re.compile(r'<section\b[^>]*>').search(s, body)
    if not m:
        return s
    open_tag, at = m.group(0), m.end()
    vid = _vid_tag(prefix, slug)

    # The layered kind: the export put a photograph behind the hero with a
    # gradient over it, from before there was any footage. The video paints at
    # 55%, so the photograph does not sit behind it - it shows through it, as a
    # second unrelated scene mixed into the first. On sunrooms that read as a
    # shed and a back yard behind a three-season room.
    #
    # So the photograph goes and the video takes its place, under the gradient
    # that is already there. The section then needs the dark ink every other
    # hero sits on: it was relying on the photograph to be its background, and
    # a 55% video over white washes out instead of darkening.
    pic = re.compile(r'</picture>').search(s, at, at + 4000)
    if pic and 'position: absolute; inset: 0px' in s[at:at + 4000]:
        start = s.rfind('<picture', at, pic.start())
        if start < 0:
            return s[:pic.end()] + vid + s[pic.end():]
        s = s[:start] + vid + s[pic.end():]
        if 'background' not in open_tag and 'style="' in open_tag:
            fixed = open_tag.replace('style="', 'style="background: rgb(10, 23, 26); ', 1)
            s = s[:m.start()] + fixed + s[m.end():]
        return s

    # The plain kind: video, scrim, then lift the content above them. The section
    # MUST be a positioning context first - without it the scrim resolves against
    # the viewport and greys out the whole page below the hero, which is exactly
    # what happened the first time this shipped.
    if 'position:relative' not in open_tag.replace(' ', ''):
        if 'style="' in open_tag:
            fixed = open_tag.replace('style="', 'style="position:relative;overflow:hidden;', 1)
        else:
            fixed = open_tag[:-1].rstrip() + ' style="position:relative;overflow:hidden">'
        s = s[:m.start()] + fixed + s[m.end():]
        at = m.start() + len(fixed)

    nxt = re.compile(r'<div\b([^>]*)>').search(s, at)
    scrim = '<div class="hero-scrim"></div>'
    out = s[:at] + vid + scrim + s[at:]
    if nxt:
        shift = len(vid) + len(scrim)
        a, b = nxt.start() + shift, nxt.end() + shift
        tag = out[a:b]
        if 'style="' in tag:
            tag = tag.replace('style="', 'style="position:relative;z-index:2;', 1)
        else:
            tag = tag[:-1] + ' style="position:relative;z-index:2">'
        out = out[:a] + tag + out[b:]
    return out


# ---------------------------------------------------------------- 15. mobile header
# The header is sticky and, on a 390px phone, was 238px tall - seven nav links
# wrapping onto three rows took 28% of the screen and kept it, on every page,
# forever. It gets a toggle below 760px: the bar stays compact and the nav opens
# on demand. The button is injected here rather than in the capture because the
# design tool never produced one.

MENU_BTN = (
    '<button class="menu-btn" type="button" aria-expanded="false" aria-controls="mainnav" '
    'aria-label="Menu">'
    '<span class="menu-bars" aria-hidden="true"><i></i><i></i><i></i></span>'
    '<span class="menu-word">Menu</span>'
    '</button>')


def add_mobile_nav(s):
    if 'class="menu-btn"' in s or '<nav aria-label="Main"' not in s:
        return s
    s = s.replace('<nav aria-label="Main"', '<nav id="mainnav" aria-label="Main"', 1)
    i = s.find('<nav id="mainnav"')
    return s[:i] + MENU_BTN + s[i:]


# ---------------------------------------------------------------- 16. the Pigeon Division
# Dave no longer works with Nichole Pigeon, so the division and both references
# to a partnership come out entirely - name, credentials, mascot, badge, video
# and chat persona. The work itself stays: he and his crew do the interior and
# finish side themselves, so every mention is rewritten to say that rather than
# deleted, and Design & Remodeling remains a service with its own page.
#
# Nichole's RIT credential and her crew's 40 years are hers, not the company's,
# so those claims are removed rather than reassigned - repointing someone else's
# qualifications at Dave would be a lie in his shop window.

PIGEON_COPY = [
    # the eyebrow above the page title. It framed this work as a separate outfit
    # under the DS Handymen name, which is the whole thing that has ended.
    ('>A division of DS Handymen, Inc.<', '>Interior work by Dave and his own crew<'),
    ("Want a designer's eye on the finish? That's the Bird. "
     '<a href="../design-remodeling/">Meet the Pigeon Division</a>.',
     "Want a designer's eye on the finish? See "
     '<a href="../design-remodeling/">Design & Remodeling</a>.'),
    # ---- home: the two-temperaments block
    ('aria-label="The Bear and the Bird"', 'aria-label="Inside and out"'),
    ('>One company, two temperaments<', '>One crew, inside and out<'),
    ('>The Bear & the Bird work together<', '>Outside the house, and inside it<'),
    ('<strong style="color: rgb(255, 255, 255);">The Bird</strong> is Nichole Pigeon &mdash; '
     'RIT Design School graduate leading the Pigeon Division, our interior & exterior design and '
     'construction arm. Trim, cabinets, tile, paint, finish work.',
     '<strong style="color: rgb(255, 255, 255);">Inside</strong> it is the same crew. Trim, '
     'cabinets, tile, paint and finish carpentry &mdash; held to the standard of everything else '
     'with his name on it.'),
    ('>Meet the Pigeon Division &rarr;<', '>See design & remodeling &rarr;<'),
    ('>Meet the Pigeon Division<', '>See design & remodeling<'),

    # ---- about
    ('&hellip;and the Bird', '&hellip;and inside the house'),
    ('In recent years the company grew a second temperament: the Pigeon Division, led by Nichole '
     'Pigeon, an RIT Design School graduate whose crew brings 40+ years of collective experience '
     'to design, trim, cabinets, tile, paint and finish work.',
     'In recent years the company grew inwards as well as outwards. Dave and his crew take on '
     'interior and exterior construction too &mdash; design, trim, cabinets, tile, paint and '
     'finish work.'),
    ("The Bear handles the weather. The Bird handles the details. The Bear and the Bird work "
     "together &mdash; one company, one phone number.",
     'The Bear handles the weather. The same crew handles the details &mdash; one company, one '
     'phone number, one standard.'),

    # ---- design & remodeling
    ('&mdash; by our <strong>Pigeon Division</strong>, led by Nichole Pigeon.',
     '&mdash; by Dave and his crew.'),
    ('>The partnership<', '>The standard<'),
    ('"The Bear and the Bird work together to bring you expanded Interior and Exterior Design and '
     'Construction services."',
     '"The same crew that clears your driveway finishes your kitchen."'),
    ("Same company, same phone number, same free estimate &mdash; with a designer's eye on "
     "everything you'll see and touch when the work is done.",
     "Same company, same phone number, same free estimate &mdash; and the same care on everything "
     "you'll see and touch when the work is done."),
    ('>Who leads it<', '>Who does it<'),
    ('>Nichole Pigeon</h2>', '>Dave and his crew</h2>'),
    ('After years of collaborating, DS Handymen, Inc. welcomed Nichole Pigeon and her crew to lead '
     'an expanded interior and exterior construction division. A graduate of the Rochester '
     'Institute of Technology (RIT) Design School, Nichole carries an outstanding reputation for '
     'the pride she takes in her work.',
     'DS Handymen has taken on interior and exterior construction alongside the outside work for '
     'years now. It is the same crew either way &mdash; the one Dave has built up over sixteen '
     'years in business and fifty in Hamburg.'),
    ('Her premium crew brings over 40 years of collective experience to custom design, trim work, '
     'cabinets, drywall, paint, tile and finish work &mdash; plus exterior projects.',
     'Custom design, trim work, cabinets, drywall, paint, tile and finish work &mdash; plus '
     'exterior projects. Free estimate, same as everything else.'),

    # ---- services
    ("Outside work is the Bear's. Design and finish work is the Bird's. Same company, same phone "
     "number, same free estimate.",
     'Outside work and inside work &mdash; same crew either way. Same company, same phone number, '
     'same free estimate.'),
    # the design card sat opposite the handyman card under the two-sides framing.
    # Both are interior work now, so the label has to separate them on what a
    # visitor is actually choosing between: a repair or a remodel.
    (">The Bird's side<", '>Kitchens &amp; baths<'),

    # ---- handyman & remodeling
    ('&mdash; with the Pigeon Division on design and finish',
     '&mdash; design and finish included'),

    # ---- contact
    ('plowing, washing, fixing, building, and the Pigeon Division',
     'plowing, washing, fixing, building and remodeling'),

    # ---- quote form. The value is what lands in Dave's inbox, so it has to read
    # plainly on its own line of an email.
    ('>Pigeon Division (design & finish)<', '>Design & remodeling<'),
    ('value="Pigeon Division (design & finish)"', 'value="Design & remodeling"'),
]

# the duo artwork and the division badge both go; the Bear on a ladder is the
# honest picture of who does this work now
PIGEON_ART = [
    ('mascot-bear-and-bird-duo', 'mascot-ladder-drill'),
    ('mascot-pigeon-blueprint', 'mascot-tool-belt'),
    ('mascot-pigeon-standing', 'mascot-tool-belt'),
    ('bird-pose-brush', 'mascot-tool-belt'),
    ('bird-pose-plans', 'mascot-tool-belt'),
    ('bird-pose-tape', 'mascot-tool-belt'),
    ('bird-pose-roller', 'mascot-tool-belt'),
    ('bird-pose-stand', 'mascot-tool-belt'),
    ('bird-pose-tools', 'mascot-tool-belt'),
    ('bird-pose-turn', 'mascot-tool-belt'),
    ('alt="The Bird with a paintbrush"', 'alt="Dave and his crew handle the finish work"'),
    ('alt="The Bird with rolled plans"', 'alt="Dave and his crew handle the finish work"'),
    ('logo-pigeon-division', 'logo-badge-teal'),
    ('alt="The Bear and the Bird together"', 'alt="The Bear at work on an interior fit-out"'),
    ('alt="The Bear and the Bird &mdash; the two sides of DS Handymen"',
     'alt="The Bear on the ladder, mid fit-out"'),
    ('alt="The Bear and the Bird, side by side"', 'alt="The Bear on the ladder, mid fit-out"'),
    ('alt="The Pigeon Division badge"', 'alt="DS Handymen, Inc."'),
]


# Every service card carried the same eyebrow, "The Bear's side". It only ever
# meant anything against a second side that no longer exists, so six identical
# labels now say nothing six times. Each card gets the label a visitor scanning
# the grid would actually use.
CARD_EYEBROWS = [
    ('Snow Plowing', 'Winter'),
    ('Landscaping', 'Spring to fall'),
    ('Pressure Washing', 'Exterior'),
    ('Handyman &amp; Remodeling', 'Inside the house'),
    ('Handyman & Remodeling', 'Inside the house'),
    ('House Clearance', 'Clear-outs'),
    ('Sunrooms &amp; Patio Enclosures', 'Helios dealer'),
    ('Sunrooms & Patio Enclosures', 'Helios dealer'),
]
OLD_EYEBROW = ">The Bear's side<"


def relabel_service_cards(s):
    """Rewrite each card eyebrow to match the heading that follows it."""
    out, i = [], 0
    while True:
        j = s.find(OLD_EYEBROW, i)
        if j < 0:
            out.append(s[i:])
            break
        ahead = s[j:j + 2400]
        label = None
        for heading, text in CARD_EYEBROWS:
            k = ahead.find('>' + heading + '<')
            if k > 0:
                label = text
                break
        out.append(s[i:j])
        out.append('>' + label + '<' if label else OLD_EYEBROW)
        i = j + len(OLD_EYEBROW)
    return ''.join(out)


# The design card on the services grid was drawn in the second mascot's warm
# palette so it would read as the other outfit's card. It is Dave's own work now
# and sits in a row of six teal siblings, where a lone beige tile just looks like
# a mistake. Measured off the House Clearance card next to it.
#
# Runs after to_brand_teal, not before: these are the colours on the built page,
# and a rotation applied afterwards would move only one side of the pair.
DESIGN_CARD_COLOURS = [
    ('background: rgb(246, 242, 237)', 'background: rgb(242, 249, 250)'),
    ('rgb(232, 223, 212)', 'rgb(218, 235, 239)'),
    ('rgb(164, 92, 56)', 'rgb(0, 65, 79)'),
]


def normalise_design_card(f, s):
    if 'services' + os.sep + 'index.html' not in f and 'services/index.html' not in f:
        return s
    for old, new in DESIGN_CARD_COLOURS:
        s = s.replace(old, new)
    return s


def retire_pigeon_division(s):
    for old, new in PIGEON_COPY:
        s = s.replace(old, new)
    for old, new in PIGEON_ART:
        s = s.replace(old, new)
    # the chat widget on this page is the Bear now, like everywhere else
    s = s.replace('<chat-widget persona="bird">', '<chat-widget persona="design">')
    s = relabel_service_cards(s)
    return s


def main():
    css = io.open(os.path.join(ROOT, "build", "responsive.css"), encoding="utf-8").read()
    n = 0
    for f in sorted(glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True)):
        s = io.open(f, encoding="utf-8").read()
        orig = s
        if 'REVIEW PENDING' in s:
            s = fix_reviews(f, s)
            if '"@type":"Review"' not in s:
                s = s.replace("</head>", REVIEW_LD + "\n</head>", 1)
        depth = f.replace(chr(92), '/').split('/docs/')[1].count('/')
        prefix = '../' * depth
        s = retire_pigeon_division(s)
        s = fix_header_badge(s)
        # both of these rename image files, and must land before fix_images so
        # the srcset it builds names the new files and only variants that exist
        s = fix_pressure_washing(f, s, prefix)
        s = fix_sunroom_photos(f, s)
        if '<picture>' not in s:
            s = fix_images(f, s)
        s = add_hero_video(f, s, prefix)
        s = relabel_nav(s)
        s = fix_copy(s)
        s = add_mobile_nav(s)
        s = scope_footer_links(s)
        s = fix_terracotta(s)
        s = fix_scrims(s)
        s = add_font_fallbacks(s)
        s = slim_hero_video(s)
        s = fix_figure_labels(s)
        s = style_design_page(f, s)
        s = to_brand_teal(s)      # last: every colour decision is made by now
        # after the rotation, not before: the map is measured on the built page,
        # so its keys are the final colours. Applying it to pre-rotation markup
        # matched nothing and silently undid every fix it had solved.
        s = apply_contrast_map(f, s)
        # after the contrast map, not before: the map solved that eyebrow against
        # the beige it used to sit on, and would put the warm colour straight back
        s = normalise_design_card(f, s)
        s = insert_map(f, s, '../'*depth)
        s = wire_form(f, s, '../'*depth)
        if 'Responsive layer' not in s:
            # display:contents promotes a picture's children to grid/flex items, and
            # that includes <source>, which Chrome does not give display:none. Every
            # photo grid was laying out with an invisible item in every other cell.
            head_css = "picture{display:contents}picture>source{display:none}"
            s = s.replace("</head>", "<style>" + head_css + chr(10) + css + "</style>" + chr(10) + "</head>", 1)
        if s != orig:
            io.open(f, "w", encoding="utf-8").write(s); n += 1
    # site.js holds the seasonal background colours and chat-widget.js a full
    # persona palette, both in navy. compile.py copies them in fresh every build,
    # so recolouring the built copies leaves the sources untouched.
    # The service-area map is generated straight into docs/ by make_map.py with
    # its own palette constants, and is referenced as an image rather than inlined,
    # so the page-level rotation never reaches it. Safe to re-run: the brand hue
    # sits outside the blue window, so a second pass is a no-op.
    for extra in ('site.js', 'chat-widget.js', os.path.join('assets', 'web', 'service-area-map.svg')):
        jp = os.path.join(OUT, extra)
        if os.path.exists(jp):
            t = io.open(jp, encoding='utf-8').read()
            io.open(jp, 'w', encoding='utf-8').write(recolour_text(t))

    write_thankyou()
    print("  post-processed %d pages" % n)

    # report
    tot = miss_d = miss_l = pend = miss_a = 0
    for f in glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
        # the injected stylesheet has a comment mentioning <img>, which the tag
        # regex below would happily count as a real image missing every attribute
        s = re.sub("<style[^>]*>.*?</style>|<script[^>]*>.*?</script>", "", s, flags=re.S)
        pend += s.count("REVIEW PENDING")
        for t in re.findall(r'<img\b[^>]*>', s):
            tot += 1
            if not ('width=' in t and 'height=' in t): miss_d += 1
            if 'loading=' not in t: miss_l += 1
            if ' alt=' not in t: miss_a += 1
    print("  imgs %d | missing dims %d | missing loading %d | missing alt %d | review placeholders %d"
          % (tot, miss_d, miss_l, miss_a, pend))

if __name__ == "__main__":
    main()
