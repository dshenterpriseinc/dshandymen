# Switching from the github.io URL to dshandymen.com

The site currently serves at **https://dshenterpriseinc.github.io/dshandymen/** with a valid
GitHub certificate, because `dshandymen.com` still resolves to the old forwarding host.

Every path on the site is **relative**, so the exact same build works at either address —
no rebuild needed when you switch.

## When the DNS in DNS-SETUP.md is done:
```bash
cd "R:\Documents\Claude\Projects\DSHandymen"
git mv docs/CNAME.pending docs/CNAME
git commit -m "Enable custom domain dshandymen.com"
git push
```
Then repo → Settings → Pages → tick **Enforce HTTPS**.

That's it. Canonical URLs already point at `https://dshandymen.com/`, so search engines
have always been told where the real home is and nothing needs re-indexing.
