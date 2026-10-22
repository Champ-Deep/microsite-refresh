---
name: campaign-landing
description: "Use when building a SPAN Global Services paid-campaign landing page (Google Ads, LinkedIn, retargeting) for a data offer such as an install base, a users list or a competitor book. Builds a three-fold, four-field conversion page from site.json: SPAN brand system, headline variants per ad group, work-email gate, a provider market map (treemap, pin and compare), cited sources, dossier card, an objection rail with a visual answer per question, and the halftone wordmark footer. Opt-in sibling of refresh-site and venture-story, not a replacement for either."
---

# Campaign Landing

A SPAN-branded landing page for one paid offer. The example is the PEO and EOR install base page (October 2026). The page is built from `site.json` so copy, counts and sources live in data and the HTML is never hand-edited.

## Route and scope

Choose this for a single-offer page behind an ad click: one headline (with `?hl=` variants per ad group), one form, one proof section, one FAQ. Keep `refresh-site` for full microsites with a catalog and the verification hero, and `venture-story` for corporate homepages. The brand system is SPAN only (green, teal, navy; Montserrat and Inter). For another Champions brand copy the skill and swap the tokens in `template.html`; do not add a colour engine.

## Files

| File | Purpose |
|---|---|
| `examples/span-peo-eor/site.json` | Every string, count, source and tracking id on the page |
| `examples/span-peo-eor/logo.png` | Real transparent SPAN logo, inlined at build |
| `template.html` | The page with `{{tokens}}`; all CSS and JS inline |
| `build.py` | Standard-library build: validates, escapes, computes bar widths, guards dashes |
| `tests/test_build.py` | Build boundary tests |
| `THIRD_PARTY.md` | The three 21st.dev components this page ports |

## Build

```bash
python3 build.py examples/span-peo-eor --out /abs/path/artifact.html
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Python 3.10+ only. No Node, no network. The output opens from disk, with two exceptions it declares: Google Fonts, and the favicon service used by the sources stack (a globe icon replaces any favicon that fails).

## Contract

- `headlines.default` plus `headlines.variants`: append `?hl=key` to the final URL per ad group. Google forbids trademarks in ad text; the page may name providers.
- `compare.left` and `compare.right`: `total`, named `items`, and `otherLabel`. The build derives the "all other" tile as total minus items and fails if items exceed the total, then precomputes share of book, share of all and rank for every tile. The page lays the two books out as regions whose widths follow the totals, and squarifies each region into provider tiles (area = contacts). Click pins a tile and the navy strip shows count, share, rank; hovering another tile shows the ratio; the strip button writes the pinned provider into the form. `compare.strip` holds every strip label.
- `form`: four fields (name, work email, phone, install base). Company is derived from the email domain in the payload. The free-mail list in the template rejects personal addresses client side; mirror it at the real endpoint. `form.specific` is the option that reveals the provider field; chart rows fill it.
- `hero.sources` and `account.sources`: each figure on the page needs a row here (domain, HTTPS url, title, snippet). No numbered citation marks anywhere.
- `faq.items`: exactly five, each with `q`, a one-line `lead`, `detail`, a `visual` (`calls`, `sources`, `renewal`, `sample`, `roles`) and its `visualData`. The rail on the left is a tablist; the panel shows the visual above the answer. `faq.ask` is the navy card at the foot of the rail. The five visuals are fixed layouts in `build.py` fed by `visualData`; add a new kind there, do not inline markup in site.json.
- `dossier`: illustrative only. The footer line must say the record is invented.
- `tracking`: `conversionLabel` ships as a placeholder; set it before launch. The form handler logs the payload and flips to the thanks state; wire the real POST at the `FORM ENDPOINT` comment in the template.

## Gates

1. `python3 -m unittest discover -s tests`.
2. `visual-verify` `audit.py` at 390 and 1440 (zero FAIL; the Inter warning is the brand body font), `shoot.py` with `?static=1` so reveals and bars render without scrolling, then open the shots.
3. Console probes, not screenshots, for the interactive parts: tile areas per region sum to 1.0 and no two tiles overlap; a hover previews a tile in the strip, a click pins it, hovering a second tile shows the ratio, clicking the pinned tile again clears; the strip button fills the provider field (or the segment for an "all other" tile); tabs switch panes and arrow keys move focus; the sources stack opens; the footer canvas draws dots at both widths. On 390 tiles under 46px render as `i`, not `button`, so they never fail tap-target checks.
4. Form probes: free-mail address rejected, empty provider rejected when `form.specific` is chosen, valid submit reaches the thanks state.
5. `no-ai-slop` Gate on every string in `site.json`.

## Lessons

- A static page has no React to install into. Port 21st.dev components to vanilla CSS and JS, keep the behaviour, credit the id in a CSS comment and in `THIRD_PARTY.md`.
- A compare slider over two lists is a curtain, not a comparison: every position shows the same numbers with one side cropped. When the only facts are counts, put share, rank and ratio on screen (treemap plus a stat strip) instead of an interaction that hides half the data.
- Treemap tiles are border-box: a tile shorter than its padding renders at the padding height and overlaps its neighbour. Zero the padding on tiles too small to label, and probe for overlaps, not just for areas summing to one.
- A `.faq article{background:#fff}` rule beats `.faq__ask{background:navy}` on specificity and ships white text on white. Scope the override (`.faq .faq__ask`) and let the contrast audit catch the rest.
- The halftone word must be fitted to the footer height as well as the width, or on wide screens the glyph box is taller than the footer and the word reads as noise. Keep dots at reduced alpha behind real DOM text.
- `scrollIntoView` with smooth scrolling drifts under Playwright; set `scroll-behavior:auto` before measuring or the probe blames the page for a frame that was still moving.
