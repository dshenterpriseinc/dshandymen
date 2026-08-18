#!/usr/bin/env python
"""Compile the captured Claude Design render into a deployable static site."""
import json, io, os, re, shutil, glob
from bs4 import BeautifulSoup

ROOT = r"R:/Documents/Claude/Projects/DSHandymen"
CAP  = os.path.join(ROOT, "build", "captured")
SRC  = os.path.join(ROOT, "site-export")
OUT  = os.path.join(ROOT, "docs")

SITE   = "https://dshandymen.com"
PHONE  = "(716) 803-0091"
TEL    = "+17168030091"

# page -> (url path, <title>, meta description)
PAGES = {
 "Home":               ("",                              "Snow Plowing & Home Services | Hamburg NY | DS Handymen",
                        "Snow plowing, pressure washing, landscaping and home repair across Hamburg, Blasdell and Orchard Park. BBB A+ accredited, insured, family run since 2009."),
 "Services":           ("services/",                     "Our Services | DS Handymen, Inc. | Southtowns NY",
                        "Snow plowing, landscaping, pressure washing, handyman and remodeling, house clearance and sunrooms across the Buffalo Southtowns. Free estimates."),
 "SnowPlowing":        ("snow-plowing/",                 "Snow Plowing in Hamburg & Blasdell NY | DS Handymen, Inc.",
                        "Residential driveway and commercial lot plowing across the Southtowns. Seasonal contracts or one-off visits, two trucks on route. $20 off for referrals. Get on the list."),
 "Landscaping":        ("landscaping/",                  "Landscaping & Yard Care | Hamburg NY | DS Handymen, Inc.",
                        "Mowing, mulching, planting, trimming, raking and gutter clean-outs across Hamburg, Blasdell, Orchard Park and Lackawanna. Free estimates."),
 "PressureWashing":    ("pressure-washing/",             "Pressure Washing Hamburg NY | Siding & Decks | DS Handymen",
                        "Pressure washing for driveways, siding, decks, roofs, sidewalks and pool decks. If it's outside and it's dirty, we can help you out. Serving the Southtowns."),
 "HandymanRemodeling": ("handyman-remodeling/",          "Handyman & Remodeling | Hamburg & Blasdell NY | DS Handymen, Inc.",
                        "Windows, basements, kitchens, flooring, drywall, decks and three-season rooms. Big jobs, small jobs, we do it all. BBB A+ accredited since 2009."),
 "HouseClearance":     ("house-clearance/",              "House & Estate Clearance | Attics, Garages | DS Handymen, Inc.",
                        "Attic, garage and full estate clear-outs across the Southtowns. It can be overwhelming figuring out where to start - we start. Free estimates."),
 "Sunrooms":           ("sunrooms-patio-enclosures/",    "Sunrooms & Patio Enclosures | Hamburg NY | DS Handymen",
                        "Three-season rooms plus Helios retractable glass sunrooms and patio enclosures. A trained dealer and installer serving Hamburg and Western New York."),
 "PigeonDivision":     ("design-remodeling/",            "Design & Remodeling | Kitchens, Tile & Trim | DS Handymen",
                        "Kitchen and bathroom remodels, custom trim, cabinets, tile and finish carpentry across the Buffalo Southtowns. Led by Nichole Pigeon, RIT Design School."),
 "About":              ("about/",                        "About Dave Schultz | DS Handymen, Inc. | Hamburg NY",
                        "Dave Schultz has lived in Hamburg for 50 years and has run DS Handymen since 2009. BBB Accredited with an A+ rating, fully insured, locally owned."),
 "Gallery":            ("gallery/",                      "Before & After Gallery | Real Jobs | DS Handymen, Inc.",
                        "Real before and after photos of kitchens, bathrooms, basements, decks, siding and landscaping completed across the Buffalo Southtowns."),
 "Reviews":            ("reviews/",                      "Customer Reviews | 4.7 Stars | DS Handymen, Inc. Hamburg NY",
                        "What Southtowns homeowners say about DS Handymen, Inc. Rated 4.7 stars, BBB Accredited with an A+ rating since 2021."),
 "ServiceArea":        ("service-area/",                 "Service Area | Hamburg & the Southtowns | DS Handymen",
                        "DS Handymen serves Hamburg, Blasdell, Orchard Park, Lackawanna and the wider Buffalo Southtowns - see the map of everywhere the trucks reach."),
 "HamburgNY":          ("service-area/hamburg-ny/",      "Handyman & Snow Plowing in Hamburg, NY | DS Handymen, Inc.",
                        "Dave's hometown - 50 years and counting. Snow plowing, landscaping, pressure washing and home repair throughout Hamburg, New York."),
 "BlasdellNY":         ("service-area/blasdell-ny/",     "Handyman & Snow Plowing in Blasdell, NY | DS Handymen, Inc.",
                        "Home base - the shop is on Miriam Avenue. Snow plowing, landscaping, pressure washing and home repair throughout Blasdell, New York."),
 "OrchardParkNY":      ("service-area/orchard-park-ny/", "Handyman & Snow Plowing in Orchard Park, NY | DS Handymen, Inc.",
                        "Bills country. Snow plowing, landscaping, pressure washing and home repair throughout Orchard Park, New York. Free estimates."),
 "LackawannaNY":       ("service-area/lackawanna-ny/",   "Handyman & Snow Plowing in Lackawanna, NY | DS Handymen, Inc.",
                        "From the Basilica to the lakeshore. Snow plowing, landscaping, pressure washing and home repair throughout Lackawanna, New York."),
 "GiftCertificates":   ("gift-certificates/",            "Gift Certificates | Give the Gift of Time | DS Handymen, Inc.",
                        "DS Handymen gift certificates in $100, $250 and $500, good toward any service. Give someone a day of freedom from yard work."),
 "Quote":              ("quote/",                        "Get a Free Quote | Send Photos | DS Handymen, Inc.",
                        "Send a photo of the driveway, deck or room and get a straight answer. Free estimates across Hamburg, Blasdell, Orchard Park and Lackawanna."),
 "Contact":            ("contact/",                      "Contact DS Handymen, Inc. | (716) 803-0091 | Blasdell NY",
                        "Call the Bear at (716) 803-0091. DS Handymen, Inc., 135 Miriam Avenue, Suite 1, Blasdell, NY 14219. Free estimates, fully insured."),
 "NotFound":           ("404",                           "Page Not Found | DS Handymen, Inc.",
                        "That page could not be found. Head back to the home page, or call the Bear at (716) 803-0091 and we will point you the right way."),
}

LINKMAP = {f"{k}.dc.html": ("/" if v[0] == "" else "/" + v[0]) for k, v in PAGES.items()}
LINKMAP["NotFound.dc.html"] = "/404.html"

RESPONSIVE_CSS = io.open(os.path.join(ROOT,"build","responsive.css"),encoding="utf-8").read()

HOVER_CSS = """
picture{display:contents}
/* ---- interaction states (re-created; the design tool bound these in JS) ---- */
a,button{transition:background-color .18s ease,color .18s ease,border-color .18s ease,box-shadow .18s ease,transform .18s ease}
a[style*="background: #00338D"]:hover{background:#00276B !important;color:#fff !important}
a[style*="background: #FFFFFF"]:hover,a[style*="background: #fff"]:hover{background:#F4F8FB !important;color:#00276B !important}
a[style*="border: 2px solid rgba(255,255,255"]:hover{border-color:#fff !important;color:#fff !important}
a[style*="background: #B5673F"]:hover{background:#8F4E2D !important;color:#fff !important}
a[style*="background: #1B2A4A"]:hover{background:#00338D !important;color:#fff !important}
article:hover,figure[style*="border"]:hover,a[style*="border-radius: 8px"]:hover{box-shadow:0 10px 24px rgba(27,42,74,.14);color:#0C1620}
header a:hover{color:#fff}
/* ---- focus visibility (WCAG 2.2 AA) ---- */
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid #F5B324;outline-offset:2px;border-radius:2px}
.skip-link{position:absolute;left:-9999px;top:0;z-index:9999;background:#1B2A4A;color:#fff;padding:12px 18px;font-weight:700}
.skip-link:focus{left:8px;top:8px}
@media(prefers-reduced-motion:reduce){*{animation:none !important;transition:none !important;scroll-behavior:auto !important}}
"""

def rel_prefix(url):
    """"" -> ""  |  "services/" -> "../"  |  "service-area/hamburg-ny/" -> "../../" """
    if url in ("", "404"):
        return ""
    return "../" * url.rstrip("/").count("/") + "../"

def clean_body(html, prefix):
    soup = BeautifulSoup(html, "lxml")
    # unwrap the framework's own wrappers
    for sel in ["#dc-root", ".sc-host", "x-dc"]:
        for el in soup.select(sel):
            el.unwrap()
    # strip framework bookkeeping attributes
    for el in soup.find_all(True):
        for a in list(el.attrs):
            if a.startswith(("data-dc", "data-sc", "sc-")) or a in ("ref", "hint-placeholder-count", "hint-placeholder-val", "style-hover"):
                del el.attrs[a]
    # drop the framework's inline component source (dead weight, ~6KB/page)
    for sc in soup.find_all("script"):
        if not sc.get("src") and sc.get("type") != "application/ld+json":
            sc.decompose()
    # rewrite internal links + asset paths
    for el in soup.find_all(["a", "img", "video", "source", "link", "script"]):
        for attr in ("href", "src"):
            v = el.get(attr)
            if not v:
                continue
            if v in LINKMAP:
                t = LINKMAP[v].lstrip("/")
                el[attr] = (prefix + t) if t else (prefix if prefix else "./")
            elif v.startswith("assets/"):
                el[attr] = prefix + v
    # lxml wraps any fragment in its own <html><body>. The page template supplies
    # those, so decoding the whole soup nests a second pair inside the document.
    node = soup.body or soup
    return node.decode_contents(formatter="html5").strip()

def page_styles(head_html):
    """keep the design's own <style> and font <link>, drop the framework placeholder CSS."""
    soup = BeautifulSoup(head_html, "lxml")
    out = []
    for st in soup.find_all("style"):
        css = st.decode_contents()
        if ".sc-placeholder" in css or "sc-dc-streaming" in css:
            continue
        out.append("<style>" + css + "</style>")
    for ln in soup.find_all("link"):
        if ln.get("rel") and "stylesheet" in ln.get("rel"):
            out.append(str(ln))
    return "\n".join(out)

LD_LOCAL = json.dumps({
  "@context":"https://schema.org","@type":"HomeAndConstructionBusiness",
  "@id": SITE + "/#business","name":"DS Handymen, Inc.","alternateName":"DS Handymen",
  "url": SITE, "telephone": PHONE, "email":"dshandymen@yahoo.com",
  "logo": SITE + "/assets/web/logo-badge-primary.png",
  "image": SITE + "/assets/photos/beforeafter-siding-windows-AFTER.jpg",
  "description":"Snow plowing, landscaping, pressure washing, handyman and remodeling services across the Buffalo Southtowns. Family run since 2009.",
  "foundingDate":"2009-11-01",
  "address":{"@type":"PostalAddress","streetAddress":"135 Miriam Avenue, Suite 1","addressLocality":"Blasdell","addressRegion":"NY","postalCode":"14219","addressCountry":"US"},
  "geo":{"@type":"GeoCoordinates","latitude":42.7959,"longitude":-78.8253},
  "areaServed":[{"@type":"City","name":n} for n in ["Hamburg","Blasdell","Orchard Park","Lackawanna","West Seneca","East Aurora"]],
  "priceRange":"$$",
  "aggregateRating":{"@type":"AggregateRating","ratingValue":"4.7","reviewCount":"13"},
  "sameAs":["https://www.facebook.com/dshandymen",
            "https://www.bbb.org/us/ny/blasdell/profile/handyman/ds-handymen-inc-0041-236007251"]
}, separators=(",", ":"))

SERVICE_LD = {
 "SnowPlowing":("Snow Plowing","Residential driveway and commercial lot snow plowing, seasonal contracts or one-off visits."),
 "Landscaping":("Landscaping","Mowing, mulching, planting, trimming, raking and gutter clean-outs."),
 "PressureWashing":("Pressure Washing","Pressure washing for driveways, siding, decks, roofs, sidewalks and pool decks."),
 "HandymanRemodeling":("Handyman and Remodeling","Windows, basements, kitchens, flooring, drywall, decks and three-season rooms."),
 "HouseClearance":("House Clearance","Attic, garage and full estate clear-outs."),
 "Sunrooms":("Sunroom Installation","Three-season rooms and Helios retractable glass sunrooms and patio enclosures."),
 "PigeonDivision":("Interior and Exterior Design and Construction","Custom design, trim, cabinets, drywall, paint, tile and finish work."),
}

def build_head(name, url, title, desc, prefix=""):
    canon = SITE + "/" + url if url != "404" else SITE + "/404.html"
    blocks = ['<script type="application/ld+json">' + LD_LOCAL + "</script>"]
    if name in SERVICE_LD:
        sname, sdesc = SERVICE_LD[name]
        blocks.append('<script type="application/ld+json">' + json.dumps({
            "@context":"https://schema.org","@type":"Service","name":sname,"description":sdesc,
            "serviceType":sname,"provider":{"@id":SITE+"/#business"},
            "areaServed":[{"@type":"City","name":n} for n in ["Hamburg","Blasdell","Orchard Park","Lackawanna"]],
            "url":canon}, separators=(",",":")) + "</script>")
    crumb = [{"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"}]
    if url not in ("", "404"):
        crumb.append({"@type":"ListItem","position":2,"name":title.split("|")[0].strip(),"item":canon})
        blocks.append('<script type="application/ld+json">' + json.dumps(
            {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":crumb},
            separators=(",",":")) + "</script>")
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#1B2A4A">
<meta property="og:type" content="website">
<meta property="og:site_name" content="DS Handymen, Inc.">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/web/og-share.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{prefix}assets/web/favicon-32.png">
<link rel="apple-touch-icon" href="{prefix}assets/web/favicon-32.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
""" + "\n".join(blocks)

def main():
    os.makedirs(OUT, exist_ok=True)
    # remove only generated html, never fight the OS over locked asset dirs
    for f in glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True):
        try: os.remove(f)
        except OSError: pass
    shutil.copytree(os.path.join(SRC, "assets"), os.path.join(OUT, "assets"), dirs_exist_ok=True)
    shutil.copy(os.path.join(SRC, "chat-widget.js"), os.path.join(OUT, "chat-widget.js"))
    shutil.copy(os.path.join(ROOT, "build", "site.js"), os.path.join(OUT, "site.js"))

    written = []
    for name, (url, title, desc) in PAGES.items():
        f = os.path.join(CAP, name + ".json")
        if not os.path.exists(f):
            print("  !! missing capture:", name); continue
        d = json.load(io.open(f, encoding="utf-8"))
        prefix = rel_prefix(url)
        body = clean_body(d["body"], prefix)
        styles = page_styles(d["head"])
        html = (
            "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
            + build_head(name, url, title, desc, prefix) + "\n"
            + styles + "\n<style>" + HOVER_CSS + "</style>\n</head>\n<body>\n"
            + '<a class="skip-link" href="#main">Skip to main content</a>\n'
            + body.rstrip()
            + '\n<script src="' + prefix + 'chat-widget.js" defer></script>\n'
            + '<script src="' + prefix + 'site.js" defer></script>\n'
            + "</body>\n</html>\n"
        )
        dest = os.path.join(OUT, "404.html") if url == "404" else os.path.join(OUT, url, "index.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        io.open(dest, "w", encoding="utf-8").write(html)
        written.append((name, dest.replace(OUT, "").replace("\\", "/"), len(html)))
    for n, p, s in written:
        print(f"  {n:20} -> {p:42} {s//1024}KB")
    print(f"\n{len(written)} pages written")

if __name__ == "__main__":
    main()
