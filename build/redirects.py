import io, os
OUT = r"R:/Documents/Claude/Projects/DSHandymen/docs"
# The design export shipped a /pigeon-division/ URL. Nothing links to it, the
# site has not gone live on the real domain yet, so there is no inbound traffic
# to preserve - and the point of the change was that the name goes.
REDIRECTS = {}
TPL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=%(to)s">
<link rel="canonical" href="https://dshandymen.com/%(canon)s">
<meta name="robots" content="noindex">
<title>Moved | DS Handymen, Inc.</title>
<style>body{font-family:'Source Sans 3',system-ui,sans-serif;background:#1B2A4A;color:#fff;display:grid;place-items:center;min-height:100vh;margin:0;text-align:center;padding:24px}a{color:#F5B324}</style>
</head>
<body><div><p>This page has moved.</p><p><a href="%(to)s">Continue &rarr;</a></p></div>
<script>location.replace('%(to)s');</script></body></html>
"""
for frm, to in REDIRECTS.items():
    d = os.path.join(OUT, frm); os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
        TPL % {"to": to, "canon": to.replace("../", "")})
    print("  redirect %s -> %s" % (frm, to))
