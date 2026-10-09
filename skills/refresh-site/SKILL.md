---
name: refresh-site
description: Refreshes a Champions Group data-list microsite (homepage or list page) into a 2027-ready landing page that converts, serves visitors in two clicks and is readable by AI crawlers and agents. Use when someone says "refresh this site", "redesign emaildatagroup.net", "refresh this microsite", "make this page 2027 ready", "rebuild this list site", "do what we did for EDG on <site>", or pastes a microsite URL and asks for a new look. Runs intake, the argument, the build, every quality gate and the handoff.
---

# Refresh a microsite

The reference run is Email Data Group (emaildatagroup.net), October 2026: brief, site files and catalog in `examples/emaildatagroup/`. Match that standard on every site.

Three rules decide every choice on the page:

1. **Serve the purpose in as few clicks as possible.** Visitors arrive for one thing (a niche list, a fix for their own list). Any list on the site is reachable in two clicks from the home page, three at most. Nobody browses for fun.
2. **One primary action, proof before the ask.** The visitor gets value (a graded report on their own file) before giving anything (a work email).
3. **Readable by machines, not just people.** AI search bots, scrapers and browser agents must get the full offer and every list link from the raw HTML.

## Workflow

Track these as tasks. Do not skip a gate; say which optional pass was skipped and why.

### 1. Intake
Run the `site-intake` skill. It produces a build folder holding `site.json`, `catalog.json`, the real logo and `brief.md`. Stop if the logo or catalog is missing. Never draw a substitute logo or invent lists.

### 2. Read the current site and the traffic
- Fetch the live homepage and the full navigation tree. Every nav list goes into `catalog.json`.
- When Ahrefs is connected, pull `site-explorer-metrics` and `site-explorer-top-pages` (mode `subdomains`). Render them with the Ahrefs render tools. Traffic usually lands on list pages, not the homepage: say so, and use the top pages for the "Most searched" pills.

### 3. The argument (before any layout)
Read `${CLAUDE_PLUGIN_ROOT}/skills/frontend-design-pro/modes/landing-page/MODE.md`. Write the five answers (who arrives, the one belief, the objection, the single action, the strongest true proof) into `brief.md`. Then ask the owner in one AskUserQuestion round, recommended option first:
- first page (homepage or list page)
- brand (keep the logo, refresh around it, unless told otherwise)
- the 2027 audience and how consultative the tone is
- the primary action (default: free verification of the first 1,000 contacts)
- three headline directions that pass the swap test
- three visual identities, each with an ASCII preview

### 4. Copy
Copy `templates/verify-skin/*` into the build folder. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/refresh-site/scripts/logo_palette.py <logo>` and set the `:root` colour tokens in `template.html` from the logo (EDG: logo red is the "problem" pencil, logo green is "verified"). Darken a colour for text until it reaches 4.5:1 contrast, and keep the pure logo hex for fills. Rewrite every line of visible copy for this site:
- `landing-page` mode owns the headline, section order and CTA discipline
- `vinh-copywriting` writes subheads, body, CTA support lines and the strategist voice
- keep the brand's own claims only when the owner confirms them, and list each one under "Sources to confirm" in `brief.md`
- drop any unbacked number (for example "95% deliverability guaranteed")
- examples are labeled as examples, and never describe invented events as real ("a list we checked last week")

Copy that lives in data, not in the template: FAQ (`site.json` faq, rendered on the page and in the FAQPage schema from one source), the offer lines (`offer.og_title`, `offer.service_type`, `offer.llms_line`), the nav CTA label (`nav_cta`), and the finder hint, list noun and catalog note (`catalog.json` `search_hint`, `list_noun`, `catalog_note`).

Copy that lives in `template.html` and must be rewritten for every site:
- eyebrow, H1, subhead and drop-box lines
- proof strip (client names, compliance badges)
- the anatomy rows
- the sample file generator in the script (`sample()`: file name, names, domains, titles)
- the three steps
- the strategist note
- the closing line
- the footer address and contact details

The build stops when reference-site strings remain, and lists them.

For a site whose action is not verification (buy a segment, append), keep the hero shape (drop a file, see a graded report) and change the report's recommendation block and the CTA, using the logic in `templates/append-segment-reference.html`. Set the `offer` fields in `site.json` to match.

The template sections are hero (drop-a-file report), proof strip, list finder, anatomy of a tired list, three steps, strategy call, objections, close, footer. Change the order or shape when the argument needs it. For an append or buy-a-segment site, take the hero logic from `templates/append-segment-reference.html`.

### 5. Navigation (purpose-first)
- Top nav has four items or fewer, named by intent ("Find a list", "Fix a list"), and one CTA button.
- The "Find a list" panel groups lists by buyer type, about five per group plus an "All X lists" hub link. There is no third level: hub pages carry the long tail. This is the SPAN navigation rule.
- The list finder sits directly under the proof strip and has search with synonyms, a category rail and popular pills. A hand-drawn marker in the hero points to it.
- A search with no match never dead-ends. It offers "Request a custom list" and routes to the strategist.
- Everything above comes from `catalog.json`, so `build_site.py` renders every link as real HTML. A group with no hub page on the live site sets `"hub": null`. The panel then links its overflow to the finder, and the brief asks for a hub page.

### 6. Build
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/refresh-site/scripts/build_site.py <build-folder> --out <build-folder>/dist
```
This writes `dist/artifact.html` (the preview) and `dist/handoff/` (the full document, `index.md` twin, `robots.txt`, `llms.txt` and `sitemap.xml`). Design passes follow `frontend-design-pro`: 21st.dev components when connected, full-width layout and brand colours taken from the logo. Motion follows the `scroll-journey-kit` skill: the verify-skin keeps its drop-a-file hero as the interactive scene, add the LakeKit micro-interactions across nav, buttons, finder pills and cards (at least six distinct effects), split headlines, a count-up on the report numbers, the progress bar and a section rail. The opening glow-horizon scene is optional on list pages where the visitor arrives with a purpose; keep the drop box above the fold on phones.

### 7. Gates (all must pass)
1. `no-ai-slop` in Gate mode on every line of copy, plus `python3 ${CLAUDE_PLUGIN_ROOT}/skills/no-ai-slop/slop_lint.py <file>`.
2. No em or en dashes: `grep -cP '\xe2\x80[\x93\x94]'` prints 0 on every output file.
3. `visual-verify` at 390 and 1440, light and dark, plus reduced motion and touch emulation, and one hover state per micro-interaction. Open and critique every screenshot. Also screenshot the open nav panel, a finder search that matches and one that does not, and the mobile menu.
4. `agent-ready`: `agent_audit.py dist/handoff` shows 0 FAIL.
5. Click depth: `click_depth.py dist/handoff/index.html --catalog catalog.json` shows every list linked.
6. The Paddle bar: would a top product site ship this? If not, fix it first.

### 8. Preview and ship
Publish `dist/artifact.html` as an Artifact for review. Then run `ship-page` for the dev handoff package and the Cloudflare checks.

### 9. Close the loop
Ask the owner for critique. Turn each durable note into a rule in this skill or in `site-intake`, and propose the edit; do not just fix the one page.

## Lessons from the EDG run
- Logo colours locked the palette: logo red became the "problem" pencil and logo green the "verified" mark.
- A catalog rendered by JavaScript is invisible to most AI fetchers. Render every list in HTML.
- Verification credits limit the free offer. Confirm the plan size, or use a 24 hour queue, before launch.
- Sites show conflicting phone numbers. Confirm one at intake.
