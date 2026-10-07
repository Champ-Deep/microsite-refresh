#!/usr/bin/env python3
"""Purpose-first navigation check: can a visitor (or an agent) reach every list in 3 clicks or fewer?

  python3 click_depth.py page.html --catalog catalog.json        # built page: every catalog URL must be linked from the page (1 click)
  python3 click_depth.py https://www.example.com/ [--max 3]       # live site: crawls same-domain links breadth first and checks sitemap URLs

Exit code 1 when any target is deeper than --max (default 3) or unreachable.
"""
import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request
from collections import deque

UA = "Mozilla/5.0 (compatible; MicrositeRefreshDepthCheck/1.0)"


def links(html, base):
    out = set()
    for h in re.findall(r'<a\b[^>]*\bhref="([^"#][^"]*)"', html, flags=re.I):
        u = urllib.parse.urljoin(base, h).split("#")[0]
        out.add(u.rstrip("/"))
    return out


def get(u):
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=15) as r:
            if "html" not in r.headers.get("Content-Type", ""):
                return ""
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    mx = int(a[a.index("--max") + 1]) if "--max" in a else 3
    t = a[0]
    if not re.match(r"https?://", t):
        cat = json.loads(pathlib.Path(a[a.index("--catalog") + 1]).read_text())
        B = cat["base"]
        targets = {(B + p if not p.startswith("http") else p).rstrip("/") for g in cat["groups"] for _, p in g["lists"]}
        targets |= {(B + g["hub"][1]).rstrip("/") for g in cat["groups"]}
        found = links(pathlib.Path(t).read_text(), B + "/")
        miss = sorted(targets - found)
        print(f"  {len(targets) - len(miss)}/{len(targets)} lists and hubs linked directly from the page (1 click)")
        for m in miss:
            print(f"  [FAIL] not linked from the page: {m}")
        sys.exit(1 if miss else 0)

    root = t.rstrip("/")
    host = urllib.parse.urlparse(root).netloc
    sm = get(root + "/sitemap.xml") or ""
    targets = {u.rstrip("/") for u in re.findall(r"<loc>([^<]+)</loc>", sm)}
    depth, q = {root: 0}, deque([root])
    while q:
        u = q.popleft()
        if depth[u] >= mx:
            continue
        html = get(u)
        if not html:
            continue
        for v in links(html, u + "/"):
            if urllib.parse.urlparse(v).netloc == host and v not in depth:
                depth[v] = depth[u] + 1
                q.append(v)
        if len(depth) > 3000:
            break
    if not targets:
        print("  [WARN] no sitemap.xml found; reporting crawl only")
    deep = sorted(u for u in targets if u not in depth)
    print(f"  {len(targets) - len(deep)}/{len(targets)} sitemap URLs reachable within {mx} clicks of the home page")
    for u in deep[:200]:
        print(f"  [FAIL] deeper than {mx} clicks or unreachable: {u}")
    sys.exit(1 if deep else 0)


if __name__ == "__main__":
    main()
