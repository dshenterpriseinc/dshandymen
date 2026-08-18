# Final step: point dshandymen.com at GitHub Pages

> 🟢 **Live:** https://dshenterpriseinc.github.io/dshandymen/

**The site is built, deployed and serving.** Every route returns 200 from GitHub's servers.
The only thing left is DNS — the domain still points at the old forwarding host.

| | |
|---|---|
| Registrar / DNS | **GoDaddy** (nameservers `ns59/ns60.domaincontrol.com`) |
| Points at today | `15.197.225.128`, `3.33.251.168` (old forwarding, sends traffic to dhenterprise.com) |
| Needs to point at | GitHub Pages |

## In GoDaddy → Domain → DNS → Manage DNS

**1. Delete** the two existing `A` records for `@`.

**2. Add four `A` records** — Name `@`, TTL 600:
```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

**3. Add a `CNAME`** — Name `www`, Value `dshenterpriseinc.github.io`

**4. Remove any Domain Forwarding** on the domain (that's what the current IPs are).

## Then, 10–60 minutes later
Go to **repo → Settings → Pages**. The "DNS Check in Progress" warning clears, and the
**Enforce HTTPS** checkbox becomes available. **Tick it.**

That issues a free auto-renewing Let's Encrypt certificate — which permanently fixes the
problem his old site has had since **14 July 2026**, when its certificate expired and every
visitor started getting a red "Not Secure" interstitial.

## Verify
```
nslookup dshandymen.com          # expect 185.199.108-111.153
curl -I https://dshandymen.com   # expect HTTP/2 200
```

## Already done
- Pages enabled: `main` branch, `/docs` folder
- `CNAME` file committed (`dshandymen.com`) — GitHub already picked it up
- `.nojekyll` so asset folders are served untouched
- 21 routes live, sitemap.xml and robots.txt in place
