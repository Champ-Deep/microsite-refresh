---
name: venture-story
description: "Use when refreshing a corporate or portfolio homepage. Build a motion-led, four-ecosystem site with GSAP chapters, architectural visuals and a filterable venture directory. Opt-in alternative to the verification-led refresh-site skin, not its replacement."
---

# Venture Story

An additive homepage template for the Website / Microsite Refresh plugin. The example is Champions Group, with original artwork and motion informed by YuVerse's scroll experience.

## Route and scope

Choose this when the visitor needs to understand a group, portfolio, or suite of complementary capabilities. Keep `refresh-site` and `verify-skin` for contact-list acquisition and file verification. Do not force the free-verification offer, catalog shape, or data-list audits onto this corporate template.

The artifact is a **preview**, not a production deploy. It deliberately carries noindex, a blocking robots policy and an empty sitemap. It does not claim to replace the live website. Publishing requires confirmed portfolio facts and destinations, production metadata, crawler-policy changes, and the plugin's ship-page gates.

## Files

| File | Purpose |
|---|---|
| `examples/champions/site.json` | All brand-specific copy, four ecosystems, venture descriptions, URLs, attributed proof and review notes |
| `examples/champions/logo.png` | Real transparent logo, never invented |
| `template.html` | Semantic static page and motion slots |
| `styles.css` | Responsive tokens and scene presentation |
| `motion.js` | GSAP/ScrollTrigger enhancement, responsive cleanup, directory and mobile navigation |
| `build.py` | Standard-library validation and build; generates the SVG scene presets |
| `vendor/` | Pinned GSAP, ScrollTrigger, LakeKit and local font; notices retained |
| `DESIGN.md` | Art direction and motion budget |
| `tests/` | Build boundary tests and actual browser interaction/scroll tests |

## Build

From this skill folder:

```bash
python3 build.py examples/champions --out /absolute/path/to/output
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tests/browser_check.py /absolute/path/to/output/artifact.html --out /absolute/path/to/output/verification
```

The browser test needs Playwright and Chromium. Probe for an existing interpreter first. Building needs only Python 3.10+ and does not need Node, network access or API credentials.

Outputs: a self-contained `artifact.html`, and `handoff/index.html`, `index.md`, `robots.txt`, `llms.txt`, `sitemap.xml`. Fonts, real logo, scripts and styles are inlined. The HTML can open from disk without network access. Markdown is the plain-text twin. Contact buttons open a real mail client; no fake form submissions.

## Rebrand contract

Copy the example directory. Replace the local PNG, name, email, domain, accent, accentText, all headline/body fields, group labels, ventures, proof and sources. Exactly four groups are supported by this narrative. Each group selects one visual preset: `network`, `steps`, `rings`, `architecture`. The preset names are fixed, but their order and the group copy are not.

Each venture requires `name`, `description` and either a verified HTTPS `url` or `null`. Null links use the group's email and a venture-specific inquiry subject. Group and directory counts derive from the supplied arrays. Editorial numerals in headlines and prose remain the author's responsibility.

`accent` recolors key materials. `accentText` must pass text contrast on white and warm surfaces. The neutral palette remains deliberately warm. SVG gradients use derived material tokens. This is a warm editorial template, not a universal theme engine.

Validation rejects duplicate IDs/names, non-HTTPS destinations, credential-bearing URLs, CSS-injected colors, invalid email, missing assets and asset traversal. Copy is HTML-escaped. Do not edit compiled HTML; edit source and rebuild.

## Motion contract

The hero is a four-layer architectural illustration with staggered assembly and scroll separation. The connection section draws a linking path. On desktop at least 1024px wide and 720px high, the ecosystem stage pins and scroll-scrubs across four distinct scenes. Chapter buttons move to the real ScrollTrigger ranges. The current chapter is the only interactive layer. Reverse scrolling restores previous states.

Phones and short landscape viewports use normal document flow. Reduced-motion changes are handled live through `gsap.matchMedia()`, reverting pins, transforms and inert state. No JavaScript or missing GSAP leaves every chapter readable. No perpetual animation loop, autoplay video, forced scroll snapping or scroll hijacking.

Do not claim motion works because a screenshot looks finished. Read `window.VentureStory.getState()` at multiple real scroll positions. Assert chapter index, opacity, transforms, inert state and progress. Capture distinct frames and test reverse scroll, chapter buttons, filters, mobile taps and preference changes.

## Gates

1. Unit tests and `node --check motion.js`.
2. Browser tests at 320, 390, 768, 1024, 1440, and short landscape. The test exercises all five filters, all twelve example disclosures, all chapter controls, reduced motion, JavaScript-off, missing GSAP and hover state reset.
3. Visual Verify audit at mobile and desktop. Brand-required Inter and white are intentional warnings, not unexamined defaults.
4. Open the screenshots, including the four scroll states, mobile menu, directory and finale. Record actual defects before fixing them.
5. Run the existing visual-verify offline check with a `file://` URL, not a bare path. Assert no external requests, console errors or storage writes.
6. Copy lint exceptions must be explicit. The official Champions tagline contains “Empowering”; do not rewrite a protected tagline to satisfy a banned-word scan. Concise factual descriptions of related platforms may legitimately share structure.
7. Production `agent-ready` allow-all crawler assertions are not preview acceptance criteria. Keep preview noindex. Static data/link availability is covered by build tests. Before a public launch, add canonical/OG/Organization metadata and a real sitemap, then run the production audit.

## Integration without disturbing other work

Place this complete folder at `skills/venture-story/` in a plugin checkout. Plugin skills are discovered as sibling skill directories. Do not modify the existing builder or route every site to this skin. Keep the existing list-page workflow intact. Do not commit, push or publish without authorization.

## Lessons

A visual reference is a behavior reference when the user praises scroll craft. Inspect the live page across scroll positions before selecting mechanisms; color and typography extraction are not a substitute. Do not call timed playback scroll-driven. Preserve real brand content, then borrow the interaction language. A failed library must leave a page, not a hidden starting frame. For stroke-dash scroll drawing, keep an arrowhead on the same continuous SVG subpath as its curve. A separate path or move command can expose a floating arrow fragment before the line reaches it; verify both mid-draw and complete states.
