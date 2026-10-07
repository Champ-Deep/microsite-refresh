#!/usr/bin/env python3
"""Agent readiness audit for a page, a handoff folder, or a live URL.

Checks what scrapers, crawlers, AI search bots and browser agents actually get.

  python3 agent_audit.py page.html                 # one built page
  python3 agent_audit.py ./handoff/                # a whole handoff package (pages + robots + llms.txt + sitemap)
  python3 agent_audit.py https://www.example.com/  # a live site: also fetches as each AI bot

Exit code 1 when any FAIL is found. Standard library only, plus Playwright for the
JS vs no-JS comparison (skipped with a WARN when Playwright is missing).
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser

BOTS = {
    "GPTBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
    "OAI-SearchBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)",
    "ChatGPT-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
    "ClaudeBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
    "Claude-User": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +Claude-User@anthropic.com)",
    "PerplexityBot": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    "Googlebot": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
}
BROWSER_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
AI_TOKENS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
             "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "meta-externalagent", "CCBot"]
GENERIC_LINKS = {"click here", "here", "read more", "learn more", "more", "link", "this"}

results = []


def rep(level, check, detail=""):
    results.append((level, check, detail))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = ""
        self.meta = {}
        self.links = []
        self.canonical = None
        self.h = []
        self.landmarks = set()
        self.imgs_no_alt = 0
        self.jsonld = []
        self.forms = []
        self.inputs_unlabelled = 0
        self.labels_for = set()
        self.input_ids = []
        self.text = []
        self._stack = []
        self._cur_a = None
        self._cur_h = None
        self._in_ld = False
        self._ld = ""
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "html":
            self.lang = a.get("lang")
        if tag in ("script", "style", "template", "noscript"):
            if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
                self._in_ld, self._ld = True, ""
            else:
                self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k.lower()] = a.get("content", "")
        if tag == "link" and "canonical" in (a.get("rel") or ""):
            self.canonical = a.get("href")
        if re.fullmatch(r"h[1-6]", tag):
            self._cur_h = [int(tag[1]), ""]
        if tag in ("main", "nav", "header", "footer"):
            self.landmarks.add(tag)
        if a.get("role") in ("main", "navigation", "banner", "contentinfo"):
            self.landmarks.add({"main": "main", "navigation": "nav", "banner": "header", "contentinfo": "footer"}[a["role"]])
        if tag == "img" and a.get("alt") is None:
            self.imgs_no_alt += 1
        if tag == "a":
            self._cur_a = [a.get("href", ""), a.get("aria-label", ""), ""]
        if tag == "form":
            self.forms.append({"toolname": a.get("toolname"), "tooldescription": a.get("tooldescription"), "action": a.get("action")})
        if tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        if tag in ("input", "select", "textarea") and (a.get("type") or "text") not in ("hidden", "submit", "button", "file"):
            self.input_ids.append((a.get("id"), a.get("aria-label") or a.get("aria-labelledby")))

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template", "noscript"):
            if self._in_ld and tag == "script":
                self._in_ld = False
                self.jsonld.append(self._ld)
            elif self._skip:
                self._skip -= 1
        if tag == "title":
            self._in_title = False
        if self._cur_h and re.fullmatch(r"h[1-6]", tag):
            self.h.append((self._cur_h[0], " ".join(self._cur_h[1].split())))
            self._cur_h = None
        if tag == "a" and self._cur_a:
            self.links.append(self._cur_a)
            self._cur_a = None

    def handle_data(self, d):
        if self._in_ld:
            self._ld += d
            return
        if self._skip:
            return
        if self._in_title:
            self.title += d
        if self._cur_h:
            self._cur_h[1] += d
        if self._cur_a:
            self._cur_a[2] += d
        self.text.append(d)


def words(s):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'.,%$-]*", s))


def audit_html(html, label, rendered_words=None):
    p = Page()
    p.feed(html)
    raw_text = " ".join(" ".join(p.text).split())
    n = words(raw_text)
    tag = f"[{label}] "

    rep("PASS" if p.lang else "FAIL", tag + "html lang", p.lang or "missing <html lang>")
    t = p.title.strip()
    rep("PASS" if 10 <= len(t) <= 65 else ("WARN" if t else "FAIL"), tag + "title", f"{len(t)} chars: {t[:70]}")
    d = p.meta.get("description", "")
    rep("PASS" if 70 <= len(d) <= 170 else ("WARN" if d else "FAIL"), tag + "meta description", f"{len(d)} chars")
    rep("PASS" if p.canonical else "FAIL", tag + "canonical", p.canonical or "missing")
    og = [k for k in ("og:title", "og:description", "og:image", "og:type") if k in p.meta]
    rep("PASS" if len(og) == 4 else "WARN", tag + "Open Graph", f"{len(og)}/4 ({', '.join(og) or 'none'})")
    if "noindex" in p.meta.get("robots", ""):
        rep("FAIL", tag + "meta robots", "noindex set")

    h1 = [h for h in p.h if h[0] == 1]
    rep("PASS" if len(h1) == 1 else "FAIL", tag + "one H1 in the HTML", f"{len(h1)} found" + (f": {h1[0][1][:60]}" if h1 else ""))
    jumps = [f"h{a[0]}>h{b[0]}" for a, b in zip(p.h, p.h[1:]) if b[0] > a[0] + 1]
    rep("PASS" if not jumps else "WARN", tag + "heading order", "ok" if not jumps else "skips: " + ", ".join(jumps[:5]))
    missing = {"main", "nav", "footer"} - p.landmarks
    rep("PASS" if not missing else "FAIL", tag + "landmarks", "ok" if not missing else "missing " + ", ".join(sorted(missing)))
    rep("PASS" if n >= 250 else "FAIL", tag + "content in raw HTML (what non-JS crawlers read)", f"{n} words")
    if rendered_words:
        ratio = n / max(rendered_words, 1)
        rep("PASS" if ratio >= 0.8 else "FAIL", tag + "no-JS vs JS content", f"{n} raw / {rendered_words} rendered words ({ratio:.0%}). Under 80% means crawlers miss content.")
    rep("PASS" if not p.imgs_no_alt else "FAIL", tag + "img alt", f"{p.imgs_no_alt} images without alt")
    bad = [x for x in p.links if not x[1] and " ".join(x[2].split()).lower() in GENERIC_LINKS]
    empty = [x for x in p.links if not x[1] and not x[2].strip()]
    rep("PASS" if not bad and not empty else "WARN", tag + "link text", f"{len(bad)} generic, {len(empty)} empty (icon links need aria-label)")
    unl = [i for i in p.input_ids if not ((i[0] and i[0] in p.labels_for) or i[1])]
    rep("PASS" if not unl else "FAIL", tag + "form fields labelled", f"{len(unl)} unlabelled fields")

    types = []
    for blob in p.jsonld:
        try:
            data = json.loads(blob)
        except Exception as e:
            rep("FAIL", tag + "JSON-LD parses", str(e)[:80])
            continue
        items = data.get("@graph", [data]) if isinstance(data, dict) else data
        for it in items:
            ty = it.get("@type") if isinstance(it, dict) else None
            types += ty if isinstance(ty, list) else [ty]
            if isinstance(it, dict) and it.get("@type") == "FAQPage":
                for q in it.get("mainEntity", []):
                    qn = (q.get("name") or "").strip()
                    if qn and qn.lower() not in raw_text.lower():
                        rep("FAIL", tag + "FAQ schema matches visible copy", f"question not on page: {qn[:60]}")
    types = [t for t in types if t]
    need = {"Organization", "WebSite"}
    rep("PASS" if need <= set(types) else "FAIL", tag + "JSON-LD Organization + WebSite", ", ".join(types) or "no JSON-LD")
    rep("PASS" if {"Service", "Product", "Offer"} & set(types) else "WARN", tag + "JSON-LD for the offer (Service, Product or Offer)", "")
    rep("PASS" if "FAQPage" in types or "faq" not in raw_text.lower() else "WARN", tag + "FAQPage schema when the page has questions", "")

    if p.forms:
        wm = [f for f in p.forms if f["toolname"] and f["tooldescription"]]
        rep("PASS" if wm else "WARN", tag + "WebMCP toolname/tooldescription on a form", f"{len(wm)}/{len(p.forms)} forms declare a tool")
    else:
        rep("WARN", tag + "primary action is a real <form>", "no <form> in the HTML; agents cannot find the action")
    return p


def rendered_word_count(target):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        rep("WARN", "JS render comparison", "playwright not installed (pip install playwright); skipped")
        return None, None
    url = target if re.match(r"https?://", target) else pathlib.Path(target).resolve().as_uri()
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        out = []
        for js in (True, False):
            ctx = b.new_context(java_script_enabled=js, viewport={"width": 1280, "height": 900})
            pg = ctx.new_page()
            pg.goto(url, wait_until="networkidle", timeout=45000)
            out.append(words(pg.evaluate("document.body ? document.body.innerText : ''")))
            ctx.close()
        b.close()
    return out


def fetch(url, ua=BROWSER_UA, accept=None):
    h = {"User-Agent": ua}
    if accept:
        h["Accept"] = accept
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), ""
    except Exception as e:
        return 0, {}, str(e)


def check_robots(text, label):
    lines = [l.split("#")[0].strip() for l in text.splitlines()]
    groups, cur = {}, []
    for l in lines:
        if not l:
            continue
        k, _, v = l.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            if cur and cur[-1][1]:
                cur = []
            cur.append([v, []])
            for g in cur:
                groups.setdefault(g[0].lower(), g[1])
        elif k in ("allow", "disallow") and cur:
            for g in cur:
                g[1].append((k, v))
                groups[g[0].lower()] = g[1]
    blocked = []
    for t in AI_TOKENS:
        rules = groups.get(t.lower(), groups.get("*", []))
        if ("disallow", "/") in rules and ("allow", "/") not in rules:
            blocked.append(t)
    rep("PASS" if not blocked else "FAIL", f"[{label}] robots.txt lets AI bots in (policy: allow all)", "blocked: " + ", ".join(blocked) if blocked else "all AI tokens allowed")
    rep("PASS" if re.search(r"(?im)^sitemap:", text) else "FAIL", f"[{label}] robots.txt points to sitemap", "")


def check_llms(text, label):
    ok = text.lstrip().startswith("# ") and re.search(r"(?m)^> ", text) and re.search(r"\]\(https?://", text)
    rep("PASS" if ok else "FAIL", f"[{label}] llms.txt format (H1, > summary, linked sections)", f"{len(text)} chars")


def audit_folder(d):
    d = pathlib.Path(d)
    pages = sorted(d.rglob("*.html"))
    for f in ("robots.txt", "llms.txt", "sitemap.xml"):
        rep("PASS" if (d / f).exists() else "FAIL", f"[package] {f} present", "")
    if (d / "robots.txt").exists():
        check_robots((d / "robots.txt").read_text(), "package")
    if (d / "llms.txt").exists():
        check_llms((d / "llms.txt").read_text(), "package")
    for p in pages:
        md = p.with_suffix(".md")
        rep("PASS" if md.exists() else "WARN", f"[{p.name}] markdown twin", md.name if md.exists() else "missing (or enable Cloudflare Markdown for Agents)")
        rw = rendered_word_count(str(p))
        audit_html(p.read_text(), p.name, rw[0] if rw and rw[0] else None)


def audit_url(url):
    base = re.match(r"https?://[^/]+", url).group(0)
    st, hd, html = fetch(url)
    rep("PASS" if st == 200 else "FAIL", "[live] browser fetch", f"HTTP {st}")
    for name, ua in BOTS.items():
        s, h, body = fetch(url, ua)
        challenge = bool(re.search(r"cf-chl|challenge-platform|Just a moment", body or ""))
        lvl = "PASS" if s == 200 and not challenge and words(body) > 50 else "FAIL"
        rep(lvl, f"[live] fetch as {name}", f"HTTP {s}, {len(body)} bytes" + (", bot challenge page" if challenge else ""))
    s, h, md = fetch(url, accept="text/markdown")
    ct = (h.get("Content-Type") or h.get("content-type") or "")
    rep("PASS" if "markdown" in ct else "WARN", "[live] Accept: text/markdown returns markdown", ct or f"HTTP {s}. Turn on Cloudflare Markdown for Agents or serve a .md twin.")
    for f in ("robots.txt", "llms.txt", "sitemap.xml"):
        s, h, body = fetch(base + "/" + f)
        rep("PASS" if s == 200 and body.strip() else "FAIL", f"[live] /{f}", f"HTTP {s}")
        if f == "robots.txt" and s == 200:
            check_robots(body, "live")
        if f == "llms.txt" and s == 200:
            check_llms(body, "live")
    rw = rendered_word_count(url)
    audit_html(html, "live", rw[0] if rw and rw[0] else None)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    t = sys.argv[1]
    if re.match(r"https?://", t):
        audit_url(t)
    elif pathlib.Path(t).is_dir():
        audit_folder(t)
    else:
        rw = rendered_word_count(t)
        audit_html(pathlib.Path(t).read_text(), pathlib.Path(t).name, rw[0] if rw and rw[0] else None)
    order = {"FAIL": 0, "WARN": 1, "PASS": 2}
    for lvl, c, d in sorted(results, key=lambda r: order[r[0]]):
        print(f"  [{lvl}] {c}" + (f"  ({d})" if d else ""))
    f = sum(1 for r in results if r[0] == "FAIL")
    w = sum(1 for r in results if r[0] == "WARN")
    print(f"\n  {f} fail  {w} warn  {len(results) - f - w} pass")
    print("  Agent-ready means zero FAIL. Fix and re-run before handoff.")
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
