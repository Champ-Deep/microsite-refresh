---
name: frontend-design-pro
description: 'Advanced marketing-site and page design, distinct from standard frontend-design. Four modes plus a showcase route: build landing pages that convert (message hierarchy, hero patterns, proof, CTA discipline, mobile fold budget); refresh bland pages in the outcome-first editorial design language while keeping every word of the copy; polish AI-default or vibe-coded UIs into production-grade products; the trend and identity pass with developer handoff (tokens, redlines, component inventory); and premium proof pages (case studies, recaps) via showcase-page. Every mode sources components from 21st.dev, adds MicroKit micro-interactions, locks the brand and passes a screenshot gate. MANDATORY TRIGGER for: landing page, marketing page, product page, homepage, hero section, pricing page, waitlist or coming-soon page, campaign or event page, sales page, ''page that converts'', ''refresh this page'', ''reskin this'', ''glow up'', ''showpiece design'', ''looks AI-made'', ''looks generic'', ''looks basic'', ''mediocre'', ''vibe-coded'', ''make it look professional'', ''make it premium'', ''add micro-interactions'', ''scroll effects'', ''scroll animation'', ''interactive section'', ''glow horizon'', ''make it feel alive'', ''looks dated'', ''modernise this'', ''feels soulless'', ''visual identity'', ''design handoff'', ''design tokens'', ''Figma handoff''. Replaces landing-page, page-refresh, ui-polish and design-trends.'
---

# Frontend Design Pro

Standard `frontend-design` builds the first version of an interface. This skill is the pro layer on top of it: pages that must convert, pages that must look premium, and the passes that remove the AI-default look. Brand locks from the relevant brand skill are absolute in every mode.

| Mode | Use when | Read |
|---|---|---|
| **landing-page** | Build or rewrite a page whose job is conversion: homepage, product, pricing, campaign, waitlist, hero rewrite | `modes/landing-page/MODE.md` |
| **page-refresh** | Reskin an existing page without changing its copy. Uses `modes/page-refresh/template.html` and `design-system.md` | `modes/page-refresh/MODE.md` |
| **ui-polish** | Second pass on a built UI, dashboard, SaaS app, admin or billing screen that looks generic or vibe-coded | `modes/ui-polish/MODE.md` |
| **design-trends** | Final pass: dated or soulless diagnosis, identity rebuild, motion signature, then the developer handoff | `modes/design-trends/MODE.md` |
| **scroll-journey** | Any page that should feel alive: opening scene scrolling into an interactive hero, interactive sections, broad micro-interactions. Runs inside every mode above | the `scroll-journey-kit` skill |
| **showcase** | A scroll page that proves a result: case study, campaign win, event recap, data snapshot | the `showcase-page` skill |

Mode files live in `modes/` next to this file (`${CLAUDE_PLUGIN_ROOT}/skills/frontend-design-pro/modes/`). The vanilla component kit (`core.css`, `core.js`) lives in `kit/`. Showcase pages are out of scope for this plugin; use the account `showcase-page` skill if it is installed.

## Pipeline

For a new page: `landing-page` builds it (with `frontend-design` for the design system), then `ui-polish`, then `design-trends`, then the `visual-verify` skill as the closing gate. For an existing page: `page-refresh` or `ui-polish`, then `design-trends`, then `visual-verify`. Run only the modes the ask needs; say which ones you skipped and why.

Where a mode file says "after frontend-design" or names one of the other modes as a separate skill, read the matching mode file here instead.

## Shared steps for every mode

These run in every mode, in this order, before the mode's own build steps.

### 1. Brand

Infer the brand from the request or ask "which brand?" once. Load the brand skill (`lakeb2b-brand-guidelines`, `span-brand-guidelines`, `ampliz-brand-guidelines`, `metricfox-brand-guidelines`, `champions-group-brand`) and lock its colours, fonts and logo rules. No brand named means the neutral theme in `references/templates.md`. Brand rules override every palette, font and treatment in the mode files.

### 2. Template

For a new page, propose one template from `references/templates.md` (Case Study, Executive One-Pager, Campaign Report, Partner Pitch, Event Recap, Market or Data Snapshot) in a single AskUserQuestion, recommended first. Skip it when the request names the format.

### 3. Components from 21st.dev

List the 3 to 5 components the page depends on most. When the 21st.dev MCP is connected (tools `search`, `get_inspiration`, `get_component`, `search_logo`):

1. `search` each one with the query from `references/components.md` (`type:"component"`, limit 6); use `get_inspiration` when the project has a `.21st/design.json`.
2. Read names, descriptions and previews; choose.
3. `get_component` for at most two (free tier allows 2 code pulls a day; `get_usage` shows what is left). Adapt the React and Tailwind code to the project's stack, or port it to vanilla for single-file pages, and credit the id in a comment.
4. `search_logo` for brand and partner logos (svgl.app SVGs).

When the MCP is not connected, say so in one line and build from the tested fallbacks in `references/components.md`. Never write an API key into a file, page or the vault; it lives in the connector settings or the `API_KEY_21ST` environment variable.

### 4. Micro-interactions from MicroKit (breadth rule)

Every interactive element gets a hover, focus and touch response, and the page as a whole uses a broad set, not one. Use the `scroll-journey-kit` skill: its LakeKit attributes cover magnetic and glow buttons, edge shine, letter-swap links, spotlight cards, tilt, aura, a sliding pill on chip and tab rows, a side rail with scroll spy, a progress bar, split headlines and count-ups. The full MicroKit catalog (49 items, MIT, `references/micro-interactions.md`) lists what to reach for beyond the kit. Rules: at least six distinct effects per page, different effects on different elements (primary CTA is not styled like the ghost button or the nav links), one effect per element, 200 to 500ms, brand colours, reduced motion and touch respected. In a React project, install originals with `npx shadcn@latest add @microkit/<name>`.

### 4b. Scroll journey and interactive sections

Plan the page as scenes with the `scroll-journey-kit` skill: an opening scene (glow horizon and a one-line headline) that scrubs into the interactive hero, content sections that reveal and respond, and a finale. Each landing page gets at least one interactive section (filter chips that re-cut something, a hover readout tied to real data, cards that prefill the form, a calculator). Pin on desktop, stack on phones and tablets, never hide content without the `rv-on` probe class. Skip the pinned opening only when the brief says the page must be static (one-pagers, PDF exports) and say so.

### 5. Charts, tables and motion

Charts and tables follow `references/charts-tables.md` (pick by data shape, values on marks, separate scales when units differ, hairline tables with computed columns). Motion follows `references/motion.md` (one load sequence, reveals on scroll, count-ups ending on stated values, `prefers-reduced-motion`, `?static=1` for PDF and PNG export).

### 6. Quality gate (before delivery, every mode)

1. Render at 390 and 1440 (and dark if the page supports it). Open the screenshots with the Read tool and critique them.
2. Zero em dashes and en dashes in the HTML and any export (`grep -cP '\xe2\x80[\x93\x94]'` prints 0).
3. Run `no-ai-slop` in Gate mode on every line of copy.
4. Mobile: no horizontal overflow, 44px tap targets, cards and grids stack cleanly.
5. Zero console errors.
6. Full width on wide screens: no narrow centered column with dead space either side.
7. Motion proof. Screenshots of the journey at several scroll positions, one hover state per micro-interaction, reduced motion and touch emulation render, a heading still visible with scripts blocked. Real-GPU frame time is reported as measured or unverified.
8. The Paddle bar. Would Paddle ship this? Editorial numbers on hairlines, real visuals in every section, responsive details under the pointer. If not, fix before delivery.

## References

`references/components.md`, `references/charts-tables.md`, `references/motion.md`, `references/micro-interactions.md`, `references/templates.md`, plus the `scroll-journey-kit` skill for the scroll and interaction layer. All of them ship in `references/` inside this plugin.
