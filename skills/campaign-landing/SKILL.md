---
name: campaign-landing
description: Use when building a SPAN paid-campaign landing page.
---

# Campaign Landing

A SPAN-branded landing page for one paid offer. Examples cover both a count-backed PEO/EOR install base and a count-free MSP sample request. The page is built from site.json; copy, counts and sources stay in data, not hand-edited HTML. The portable entry skill is span-landing-page in Champ-Deep/champ-skills, design/span-landing-page/; this plugin path stays supported as its implementation.

## Route and scope

Choose this for a single-offer page behind an ad click: one headline (with `?hl=` variants per ad group), one form, one proof section, one FAQ. Keep `refresh-site` for full microsites with a catalog and the verification hero, and `venture-story` for corporate homepages. The brand system is SPAN only (green, teal, navy; Montserrat and Inter). For another Champions brand copy the skill and swap the tokens in `template.html`; do not add a colour engine.

## Files

| File | Purpose |
|---|---|
| `examples/span-peo-eor/site.json` | Every string, count, source and tracking id on the page |
| `examples/span-peo-eor/logo.png` | Real transparent SPAN logo, inlined at build |
| `examples/span-msp-us/site.json` | Count-free source-backed MSP offer, optional phone and custom requirements |
| `template.html` | The page with `{{tokens}}`; all CSS and JS inline |
| `build.py` | Standard-library build: validates, escapes, computes bar widths, guards dashes |
| `tests/test_build.py` | Build boundary tests |
| `THIRD_PARTY.md` | Provenance for the selected 21st.dev vanilla ports |

## Build

```bash
python3 build.py examples/span-peo-eor --out /abs/path/artifact.html
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Python 3.10+ only. No Node or network needed for the build. The output opens from disk, with two exceptions it declares: Google Fonts, and the favicon service used by the sources stack (a globe icon replaces any favicon that fails).

## Contract

- `headlines.default` plus `headlines.variants`: append `?hl=key` to the final URL per ad group. Check the current ad-platform trademark policy and the approved campaign before using provider names in ads; a headline variant alone is not legal approval.
- `compare.left` and `compare.right`: `total`, `short` (PEO, EOR), named `items`, and `otherLabel`. The build derives the "all other" tile as total minus items and fails if items exceed the total, then precomputes share of book, share of all, rank and a size tier for every tile. `compare.bento` sets the tiers (`lgAt`, `wideAt` as percent of its own book; the long tail is always `wide`) and every label on the board. One board per book sits side by side (stacked on phones), each sorted by count; colour and a tag carry the book, tile size carries the tier. Boards run 4 columns on desktop because a 2x2 plus 2x1 mix tiles exactly at 4 and never at 3. Tiles drag to reorder (pointer, press and hold on touch, Alt plus arrows), click pins one and every other tile shows its ratio to it, `?hl=<provider>` pins that provider on load, and the navy strip shows count, share, rank and the CTA that writes the provider into the form. `compare.strip` holds every strip label.
- `form`: four primary fields: name, work email, phone and requirement. Preserve optional phone with phoneRequired=false; default is true for the PEO fixture. segmentLabel, providerLabel and providerError distinguish Custom requirements from Which provider. The email domain is only a domain, not verified company identity. Mirror the free-mail filter at a real endpoint. form.specific reveals the conditional field.
- `band`, `clients` and `compare` are optional, as are hero.sources and account.sources. Omit unsupported sections rather than invent counts, refresh dates, customer names, distribution charts or citations. When figures exist, source them beside the claim. No numbered citation marks.
- `faq.items`: exactly five, each with `q`, a one-line `lead`, `detail`, a `visual` (`calls`, `sources`, `renewal`, `sample`, `roles`) and its `visualData`. The rail on the left is a tablist; the panel shows the visual above the answer. `faq.ask` is the navy card at the foot of the rail. The five visuals are fixed layouts in `build.py` fed by `visualData`; add a new kind there, do not inline markup in site.json.
- `dossier`: illustrative only. Clearly label it a schematic layout, not real data. Do not apply Verified to a dummy email or carry legal-compliance badges into an offer without supporting evidence.
- `tracking`: conversionLabel is not a real tracking ID until supplied. The unwired form is a preview, not lead capture: no personal-payload logs, lead conversions or false request-received messages. Wire and verify a real endpoint and tracking before launch. Keep preview feedback explicit that nothing was sent.

## Gates

1. `python3 -m unittest discover -s tests`.
2. `visual-verify` `audit.py` at 390 and 1440 (zero FAIL; the Inter warning is the brand body font), `shoot.py` with `?static=1` so reveals and bars render without scrolling, then open the shots.
3. Console probes, not screenshots, for the interactive parts: no two tiles overlap before or after a drag; a pointer drag lifts (`.held`, scale in the inline transform), reorders, lands with the teal ring and does not pin; a tap pins and a 350ms hold lifts on touch; Alt plus arrow moves the focused tile and Enter pins it; the reset button appears only when the order differs; every unpinned tile shows a ratio chip while one is pinned; `?hl=deel` pins Deel on load; the strip button fills the provider field (or the segment for an "all other" tile); tabs switch panes and arrow keys move focus; the sources stack opens; the footer canvas draws dots at both widths.
4. Form probes: free-mail address rejected, empty provider rejected when `form.specific` is chosen, valid submit reaches the thanks state.
5. `no-ai-slop` Gate on every string in `site.json`.

## Lessons

- A static page has no React to install into. Port 21st.dev components to vanilla CSS and JS, keep the behaviour, credit the id in a CSS comment and in `THIRD_PARTY.md`.
- A compare slider over two lists is a curtain, not a comparison: every position shows the same numbers with one side cropped. When the only facts are counts, put share, rank and ratio on screen (treemap plus a stat strip) instead of an interaction that hides half the data.
- A treemap sized to contacts gives the long tail unreadable slivers and no room for a comparison figure. A bento with three size tiers keeps every provider legible and leaves space for the ratio chip, while the strip still carries exact share and rank.
- Standing rule from Deep: the stat band under the hero is always the inverse scheme, white ground with green figures and muted labels, so it reads as a break between the dark hero and the body. Every skin and iteration keeps it inverted; do not restyle it to the brand fill.
- Hero background is the 21st.dev Dither Grid gradient drawn on a canvas (`#dither`, palette and cell counts at the top of its script). Copy over it is white with a navy-green wash; any new hero text needs a `.hero` scoped colour rule, since later unscoped rules win and the audit catches it as 1.1:1.
- A `padding: X 0` shorthand on a `.shell` child zeroes the phone gutter. Set only the vertical sides.
- Position bento tiles with `transform: translate()` and transition only transform. Transitions on left, top, width or height fail the layout-animation audit and jank on phones.
- Any flex column card with `overflow: hidden` will silently shrink a clamped name to zero height when the row is short. Set `flex-shrink: 0` on the name and probe name heights at 390.
- Mixing a brand colour toward navy by rank makes the two families converge at the long tail. Keep the mix floor high enough that the floors differ, and cap the ceiling where white text still measures 4.5:1 (teal #00A383 fails above about 65%).
- A `.faq article{background:#fff}` rule beats `.faq__ask{background:navy}` on specificity and ships white text on white. Scope the override (`.faq .faq__ask`) and let the contrast audit catch the rest.
- The halftone word must be fitted to the footer height as well as the width, or on wide screens the glyph box is taller than the footer and the word reads as noise. Keep dots at reduced alpha behind real DOM text.
- `scrollIntoView` with smooth scrolling drifts under Playwright; set `scroll-behavior:auto` before measuring or the probe blames the page for a frame that was still moving.
