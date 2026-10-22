---
name: campaign-landing
description: "Use when building a SPAN Global Services paid-campaign landing page (Google Ads, LinkedIn, retargeting) for a data offer such as an install base, a users list or a competitor book. Builds a three-fold, four-field conversion page from site.json: SPAN brand system, headline variants per ad group, work-email gate, a sweepable PEO versus EOR style compare chart, cited sources, dossier card, answer-first FAQ and the halftone wordmark footer. Opt-in sibling of refresh-site and venture-story, not a replacement for either."
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
- `compare.left` and `compare.right`: `total`, named `items`, and `otherLabel`. The build derives the "all other" row as total minus items and fails if items exceed the total. Bars scale to half the chart width per side so the 50/50 state is a butterfly chart; sweeping reveals either side in full.
- `form`: four fields (name, work email, phone, install base). Company is derived from the email domain in the payload. The free-mail list in the template rejects personal addresses client side; mirror it at the real endpoint. `form.specific` is the option that reveals the provider field; chart rows fill it.
- `hero.sources` and `account.sources`: each figure on the page needs a row here (domain, HTTPS url, title, snippet). No numbered citation marks anywhere.
- `faq.items`: exactly five, each with `q`, a one-line `lead` and `detail`. The sixth tile is `faq.ask`, which links to the form.
- `dossier`: illustrative only. The footer line must say the record is invented.
- `tracking`: `conversionLabel` ships as a placeholder; set it before launch. The form handler logs the payload and flips to the thanks state; wire the real POST at the `FORM ENDPOINT` comment in the template.

## Gates

1. `python3 -m unittest discover -s tests`.
2. `visual-verify` `audit.py` at 390 and 1440 (zero FAIL; the Inter warning is the brand body font), `shoot.py` with `?static=1` so reveals and bars render without scrolling, then open the shots.
3. Console probes, not screenshots, for the interactive parts: the range input sets `--p` and the clip; a mouse sweep sets `--p` and leaving resets to 50; a click on either side at 50/50 fills the provider field from that side; all 16 rows align across panes; on 390 every name and count sits clear of the divider (rows stack name over count below 700px); the sources stack opens; the footer canvas draws dots at both widths.
4. Form probes: free-mail address rejected, empty provider rejected when `form.specific` is chosen, valid submit reaches the thanks state.
5. `no-ai-slop` Gate on every string in `site.json`.

## Lessons

- A static page has no React to install into. Port 21st.dev components to vanilla CSS and JS, keep the behaviour, credit the id in a CSS comment and in `THIRD_PARTY.md`.
- The compare slider only reads at 50/50 when each side's labels fit in half the width. Stack name over count below 700px and scale bars to half width, then prove it with a bounding-box probe against the divider.
- A `.faq article{background:#fff}` rule beats `.faq__ask{background:navy}` on specificity and ships white text on white. Scope the override (`.faq .faq__ask`) and let the contrast audit catch the rest.
- The halftone word must be fitted to the footer height as well as the width, or on wide screens the glyph box is taller than the footer and the word reads as noise. Keep dots at reduced alpha behind real DOM text.
- `scrollIntoView` with smooth scrolling drifts under Playwright; set `scroll-behavior:auto` before measuring or the probe blames the page for a frame that was still moving.
