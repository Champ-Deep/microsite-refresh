#!/usr/bin/env python3
"""Build a refreshed microsite page from template + site.json + catalog.json.

  python3 build_site.py <build-dir> [--out <dir>]

Reads <build-dir>/template.html, site.json, catalog.json and writes:
  <out>/artifact.html        body-only page for Artifact preview (no doctype)
  <out>/handoff/index.html   full document with <head> for engineers
  <out>/handoff/index.md     markdown twin for agents
  <out>/handoff/robots.txt, llms.txt, sitemap.xml
Every list in catalog.json is rendered as a real <a href> in the HTML (nav panel,
finder and footer hubs), so crawlers and agents reach any list within two clicks.
"""
import html
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

E = html.escape


def url(base, path):
    return path if path.startswith(("#", "http")) else base + path


def build(d, out):
    d, out = pathlib.Path(d), pathlib.Path(out)
    tpl = (d / "template.html").read_text()
    site = json.loads((d / "site.json").read_text())
    cat = json.loads((d / "catalog.json").read_text())
    B = cat["base"]
    groups = cat["groups"]
    svc = cat["services"]

    # ---------- head ----------
    a = site.get("address") or {}
    graph = [
        dict({"@type": "Organization", "@id": site["domain"] + "/#org", "name": site["name"], "url": site["domain"] + "/",
              "slogan": site.get("tagline", ""), "email": site["email"], "telephone": site["phone"]},
             **({"address": {"@type": "PostalAddress", "streetAddress": a["street"], "addressLocality": a["city"], "addressRegion": a["region"], "postalCode": a["postal"], "addressCountry": a["country"]}} if a.get("street") else {})),
        {"@type": "WebSite", "@id": site["domain"] + "/#site", "name": site["name"], "url": site["domain"] + "/", "publisher": {"@id": site["domain"] + "/#org"}},
        {"@type": "Service", "name": site["offer"]["name"], "description": site["offer"]["description"], "provider": {"@id": site["domain"] + "/#org"},
         "serviceType": site["offer"].get("service_type", "Email verification"), "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "eligibleQuantity": {"@type": "QuantitativeValue", "maxValue": site["offer"]["quantity"], "unitText": "contacts"}}},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in site["faq"]]},
        {"@type": "ItemList", "name": "Email lists by buyer type", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": g["name"], "url": url(B, g["hub"][1]) if g.get("hub") else site["domain"] + "/#lists"} for i, g in enumerate(groups)]},
    ]
    head = "\n".join([
        f'<meta name="description" content="{E(site["description"][:165])}">',
        f'<link rel="canonical" href="{site["domain"]}/">',
        f'<link rel="alternate" type="text/markdown" href="{site["domain"]}/index.md">',
        f'<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{E(site["name"])}: {E(site["offer"].get("og_title", site["offer"]["name"]))}">',
        f'<meta property="og:description" content="{E(site["description"][:200])}">',
        f'<meta property="og:image" content="{site["og_image"]}">',
        f'<meta property="og:url" content="{site["domain"]}/">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>",
    ])

    hint = cat.get("search_hint", "Try a job title, industry or software")

    # ---------- nav mega panel ----------
    def col(g, n=5):
        items = "".join(f'<li><a href="{url(B, p)}">{E(t)}</a></li>' for t, p in g["lists"][:n])
        hub = g.get("hub")
        head_ = (f'<a class="mhead" href="{url(B, hub[1])}">' if hub else '<span class="mhead">') + f'{E(g["name"])}<small>{E(g.get("who", ""))}</small>' + ('</a>' if hub else '</span>')
        more = f'<a class="mall" href="{url(B, hub[1])}">{E(hub[0])} <span aria-hidden="true">&#8594;</span></a>' if hub else (f'<a class="mall" href="#lists">All {len(g["lists"])} {E(g["name"].lower())} lists <span aria-hidden="true">&#8594;</span></a>' if len(g["lists"]) > n else "")
        return f'<div class="mcol">{head_}<ul>{items}</ul>{more}</div>' 
    mega = (
        '<div class="mega" id="mega" data-open="">'
        '<div class="mpanel" data-panel="find">'
        '<div class="msearch"><label class="mono" for="msq">Search lists</label><input id="msq" type="search" placeholder="{E(hint)}" autocomplete="off" data-finder-input>'
        '<p class="hint-s">Or pick who you sell to.</p><a class="mall" href="#lists">See every list on one page <span aria-hidden="true">&#8594;</span></a></div>'
        '<div class="mcols">' + "".join(col(g) for g in groups) + "</div></div>"
        '<div class="mpanel" data-panel="fix"><div class="mcols fixcols">' + col(dict(svc, who="Clean, verify and complete the list you have"), 8) +
        '<div class="mcol mpromo"><span class="hand">Start here</span><b>1,000 contacts verified free</b><p>Drop a CSV and see what will bounce before you send.</p><a class="btn btn-red" href="#top" data-focus-drop><span>Verify my list</span><span class="arr"><i>&#8594;</i><i>&#8594;</i></span></a></div>'
        "</div></div></div>"
    )

    # ---------- finder section ----------
    rail = "".join(f'<button type="button" role="tab" id="t-{g["id"]}" aria-controls="p-{g["id"]}" aria-selected="{"true" if i == 0 else "false"}"><b>{E(g["name"])}</b><small>{E(g["who"])} &middot; {len(g["lists"])}</small></button>' for i, g in enumerate(groups))
    panels = "".join(
        f'<section class="fpanel" id="p-{g["id"]}" role="tabpanel" aria-labelledby="t-{g["id"]}"><h3>{E(g["name"])} {E(cat.get("list_noun", "lists"))}</h3><ul class="flist">'
        + "".join(f'<li><a href="{url(B, p)}">{E(t)}<span class="go" aria-hidden="true">&#8594;</span></a></li>' for t, p in g["lists"])
        + '</ul>' + (f'<a class="mall" href="{url(B, g["hub"][1])}">{E(g["hub"][0])} <span aria-hidden="true">&#8594;</span></a>' if g.get("hub") else '') + '</section>'
        for g in groups)
    lookup = {t: url(B, p) for g in groups for t, p in g["lists"]}
    pills = "".join(f'<a class="pop" href="{lookup[t]}">{E(t)}</a>' for t in cat["popular"] if t in lookup)
    finder = f'''<section class="block finder" id="lists" aria-labelledby="lists-h">
  <div class="wrap">
    <div class="fhead">
      <div><div class="mono">Need a new list instead?</div><h2 id="lists-h" style="margin-top:14px">Find your list in two clicks.</h2></div>
      <div class="fsearch" role="search">
        <label for="fq" class="mono">Who do you sell to?</label>
        <input id="fq" type="search" placeholder="{E(hint)}" autocomplete="off" data-finder-input aria-describedby="fq-hint">
        <div class="results" id="fres" role="listbox" aria-label="Matching lists" hidden></div>
        <p id="fq-hint" class="hint-s">Most searched: </p><div class="pops">{pills}</div>
      </div>
    </div>
    <div class="fbody">
      <div class="rail" role="tablist" aria-label="List categories">{rail}</div>
      <div class="fpanels">{panels}</div>
    </div>
    <p class="cat-note">{E(cat.get("catalog_note", ""))} Not seeing your niche? <a href="#strategist">We build custom lists</a>{E(cat.get("custom_note", ""))}.</p>
  </div>
</section>'''

    foot = '<div><b>Lists</b><ul>' + "".join(f'<li><a href="{url(B, g["hub"][1]) if g.get("hub") else "#lists"}">{E(g["name"])}</a></li>' for g in groups) + '</ul></div>'

    data = {"lists": [{"t": t, "u": url(B, p), "g": g["name"]} for g in groups for t, p in g["lists"]] + [{"t": t, "u": url(B, p), "g": "Fix a list"} for t, p in svc["lists"]],
            "syn": cat["synonyms"]}
    finder_js = "  var FINDER = " + json.dumps(data) + ";\n" + (d / "finder.js").read_text()

    faq_html = "".join(f'<article class="reveal"><h3>{E(q)}</h3><p>{E(ans)}</p></article>' for q, ans in site["faq"])
    tpl = tpl.replace("{{FAQ}}", faq_html).replace("{{NAV_CTA}}", E(site.get("nav_cta", site["offer"]["name"])))
    page = (tpl.replace("{{HEAD}}", head).replace("{{MEGA}}", mega).replace("{{FINDER}}", finder)
            .replace("{{FOOTLISTS}}", foot).replace("{{FINDERJS}}", finder_js))
    page = page.replace("{{LOGO_LIGHT}}", logo_uri(d, site, False)).replace("{{LOGO_DARK}}", logo_uri(d, site, True)).replace("{{LOGO_ALT}}", E(site["name"] + (", " + site["tagline"] if site.get("tagline") else "")))
    page = page.replace("</style>", (d / "extra.css").read_text() + "\n</style>", 1)
    leftovers(page, site, d)
    if re.search("[\\u2013\\u2014]", page):
        sys.exit("dash found in page; fix copy before building")

    out.mkdir(parents=True, exist_ok=True)
    (out / "artifact.html").write_text(page)

    # ---------- handoff package ----------
    h = out / "handoff"
    h.mkdir(exist_ok=True)
    split = page.index("<style>")
    head_part, body_part = page[:split], page[split:]
    style_end = body_part.index("</style>") + len("</style>")
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
           + head_part + body_part[:style_end] + "\n</head>\n<body>\n" + body_part[style_end:] + "\n</body>\n</html>\n")
    (h / "index.html").write_text(doc)
    (h / "index.md").write_text(to_markdown(doc, site))
    (h / "robots.txt").write_text(robots(site))
    (h / "llms.txt").write_text(llms(site, cat))
    urls = [site["domain"] + "/"] + sorted({url(B, g["hub"][1]) for g in groups if g.get("hub")} | {u for u in lookup.values()} | {url(B, p) for _, p in svc["lists"] if not p.startswith("#")})
    (h / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{E(u)}</loc></url>\n" for u in urls) + "</urlset>\n")
    print(f"built {out}/artifact.html and {h}/ ({len(urls)} sitemap urls, {len(lookup)} lists)")


EXAMPLE_MARKERS = ["Email Data Group", "emaildatagroup", "us-dentists-2024", "brightsmile", "Okafor", "Coast Dental", "1,240 US dentists",
                   "DSO owners", "CQ Roll Call", "CA Technologies", "ReachForce", "M Systems", "AllDigital", "Telintel", "Media Center Drive", "800 710 4895"]


def leftovers(page, site, d):
    """Stop the build when copy from the reference site is still on another site's page."""
    if "emaildatagroup" in site["domain"] or "--allow-leftovers" in sys.argv:
        return
    found = sorted({m for m in EXAMPLE_MARKERS if m.lower() in page.lower()})
    if found:
        sys.exit("Reference-site copy still on the page (rewrite it, or pass --allow-leftovers for a draft):\n  " + "\n  ".join(found))


def logo_uri(d, site, dark):
    """Embed the site's own logo. Dark variant recolours near-black ink to light so the tagline stays readable."""
    import base64, io
    f = d / site.get("logo", "logo.png")
    if not f.exists():
        sys.exit(f"logo missing: put the site's real logo at {f} (never draw a substitute)")
    try:
        from PIL import Image
    except ImportError:
        return "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode()
    im = Image.open(f).convert("RGBA")
    if im.width > 560:
        im = im.resize((560, round(im.height * 560 / im.width)), Image.LANCZOS)
    if dark:
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a and max(r, g, b) < 90:
                    px[x, y] = (237, 235, 229, a)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def robots(site):
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User",
            "Google-Extended", "Applebot-Extended", "meta-externalagent", "CCBot"]
    if site.get("robots_policy", "allow-all") == "allow-all":
        body = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)
    else:
        train = {"GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended", "meta-externalagent", "CCBot"}
        body = "".join(f"User-agent: {b}\n{'Disallow' if b in train else 'Allow'}: /\n\n" for b in bots)
    return ("# AI crawlers listed by name so the policy is explicit. Policy: " + site.get("robots_policy", "allow-all") + "\n"
            + body + "User-agent: *\nAllow: /\n\n" + f"Sitemap: {site['domain']}/sitemap.xml\n")


def llms(site, cat):
    B = cat["base"]
    out = [f"# {site['name']}", "", f"> {site['description']}", "",
           site["offer"].get("llms_line", site["offer"]["description"]), "",
           "## Key pages", "", f"- [Home and free verification]({site['domain']}/): drop a list, get a report, verify 1,000 contacts free", f"- [Home as markdown]({site['domain']}/index.md)", ""]
    for g in cat["groups"]:
        out += [f"## {g['name']} {cat.get('list_noun', 'lists')}", ""] + ([f"- [{g['hub'][0]}]({url(B, g['hub'][1])}): {g['who']}"] if g.get("hub") else [])
        out += [f"- [{t}]({url(B, p)})" for t, p in g["lists"]] + [""]
    s = cat["services"]
    out += ["## Data services", ""] + [f"- [{t}]({url(B, p) if not p.startswith('#') else site['domain'] + '/'})" for t, p in s["lists"]] + [""]
    out += ["## Contact", "", f"- Phone: {site['phone']}", f"- Email: {site['email']}", ""]
    return "\n".join(out)


class MD(HTMLParser):
    SKIP = {"script", "style", "svg", "noscript", "template", "button", "select", "input", "label"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.href, self.buf = [], 0, None, ""

    def flush(self, prefix=""):
        t = " ".join(self.buf.split())
        if t:
            self.out.append(prefix + t)
        self.buf = ""

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag in self.SKIP:
            self.skip += 1
        if self.skip:
            return
        if tag in ("h1", "h2", "h3", "p", "li", "div", "section", "tr"):
            self.flush()
        if tag == "a":
            self.href = a.get("href")
            self.buf += " ["
        if tag == "br":
            self.buf += " "

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "a":
            self.buf = self.buf.rstrip() + f"]({self.href or '#'}) "
        if tag in ("h1", "h2", "h3"):
            self.flush("#" * int(tag[1]) + " ")
            self.out.append("")
        elif tag == "li":
            self.flush("- ")
        elif tag in ("p", "div", "section", "tr", "td"):
            self.flush()

    def handle_data(self, d):
        if not self.skip:
            self.buf += d


def to_markdown(doc, site):
    body = doc[doc.index("<body>"):]
    body = re.sub(r'<div class="mega".*?</div></div></div>', "", body, flags=re.S)
    p = MD()
    p.feed(body)
    p.flush()
    lines, prev = [], None
    for l in p.out:
        if l == prev:
            continue
        lines.append(l)
        prev = l
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = re.sub(r"\[\s*\]\([^)]*\)", "", md)
    return f"---\ntitle: {site['name']}\nurl: {site['domain']}/\n---\n\n" + md.strip() + "\n"


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    out = args[args.index("--out") + 1] if "--out" in args else str(pathlib.Path(args[0]) / "dist")
    build(args[0], out)
