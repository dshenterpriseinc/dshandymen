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
    <img src="{PREFIX}assets/web/service-area-map.svg" alt="Map of Western New York showing the DS Handymen service area centred on Blasdell, covering Hamburg, Orchard Park, Lackawanna and the wider greater Buffalo area, with Lake Erie to the west" width="1000" height="780" loading="lazy" decoding="async" style="width:100%;height:auto;border:1px solid #DCE5EF;border-radius:12px;box-shadow:0 6px 22px rgba(27,42,74,.10)">
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
# in a stale announcement frame (the division launched in Jan 2024). Lead with the
# work, then introduce the team by name.
COPY_FIXES = [
    (">Now introducing the Pigeon Division<", ">Design &amp; Remodeling<"),
    ("Interior & exterior design and construction &mdash; custom design, trim, cabinets, drywall, paint, tile and finish work.",
     "Kitchens, bathrooms, custom trim, cabinets, tile, paint and finish carpentry across the Southtowns "
     "&mdash; by our <strong>Pigeon Division</strong>, led by Nichole Pigeon."),
    # stale "new division" language elsewhere
    ("Now... introducing the Pigeon Division!", "The Pigeon Division"),
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
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
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
<body><div class="card">
 <img src="../assets/web/mascot-waving.png" alt="" loading="eager" decoding="async" fetchpriority="high" width="150" height="176">
 <h1>Got it &mdash; thanks.</h1>
 <p>Your request is with Dave. He&rsquo;ll come back to you as soon as he&rsquo;s off the route.<br>
    If it&rsquo;s urgent, just call &mdash; that&rsquo;s always fastest.</p>
 <p><a class="btn" href="tel:+17168030091">Call the Bear &middot; (716) 803-0091</a></p>
 <p><a class="plain" href="../">&larr; Back to the site</a></p>
</div></body></html>
"""

def write_thankyou():
    d = os.path.join(OUT, "thank-you")
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(THANKYOU)

# ---------------------------------------------------------------- run
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
        if '<picture>' not in s:
            s = fix_images(f, s)
        s = relabel_nav(s)
        s = fix_copy(s)
        depth = f.replace(chr(92),'/').split('/docs/')[1].count('/')
        s = insert_map(f, s, '../'*depth)
        s = wire_form(f, s, '../'*depth)
        if 'Responsive layer' not in s:
            s = s.replace("</head>", "<style>picture{display:contents}\n" + css + "</style>\n</head>", 1)
        if s != orig:
            io.open(f, "w", encoding="utf-8").write(s); n += 1
    write_thankyou()
    print("  post-processed %d pages" % n)

    # report
    tot = miss_d = miss_l = pend = miss_a = 0
    for f in glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True):
        s = io.open(f, encoding="utf-8").read()
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
