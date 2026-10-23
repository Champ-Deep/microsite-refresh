# Changelog

## 0.6.0 (23 Oct 2026)
- campaign-landing: platform section is now a bento board, a vanilla port of the 21st.dev Draggable Widget Grid used on deependhq. Tiles sized by share tier, drag to reorder (touch press and hold, Alt plus arrows), click to pin with a ratio chip on every other tile, `?hl=` pins on load. Transform-only motion, contrast-capped colour ramps, 0 audit fails at 1440 and 390.

## 0.5.1 (22 Oct 2026)
- campaign-landing: platform section rebuilt as a provider market map (two regions sized by book, squarified tiles, pin and hover-to-compare strip that writes into the form). FAQ rebuilt as an objection rail with a visual answer per question (call openers, source trail, renewal window, scoped sample, roles). Tests cover tile shares and the visual contract.

## 0.5.0 (22 Oct 2026)
- New: campaign-landing skill, a SPAN paid-campaign landing page built from site.json (example: PEO and EOR install base). Ports three 21st.dev components to vanilla CSS/JS: Compare, AI Sources, Halftone Wordmark Footer. Four-field form with a work-email gate, headline variants per ad group, answer-first FAQ grid, build tests.

## 0.4.0 (12 Oct 2026)
- New: scroll-craft (Nate Herk, MIT) vendored as the method behind signature-hero.
- signature-hero: interview from scroll-craft, page grammars, fingerprint gate across our microsites, options to pick from and combine, prototypes of the top two concepts, scroll-craft harness and feel check in verification, button and taste rules.
- no-ai-slop: merged with human-speak (Nate Herk, MIT). New patterns (tee-ups, manufactured candor, fake question and answer splits, two-beat negative fragments, filler after statistics, fake-profound metaphors, sales language, reworded variants), Draft job, top 20 ordering for audits; slop_lint.py catches the new surface patterns.
- Fixed installer validation: no angle-bracket placeholders in refresh-site and site-intake descriptions; frontend-design-pro description under 1024 characters.
- New: scripts/validate_plugin.py, CLAUDE.md release steps, this changelog.

## 0.3.0 (12 Oct 2026)
- New: signature-hero skill (direction workshop, concepts, build contract, LakeB2B globe reference). refresh-site runs it as step 3b.

## 0.2.0 (9 Oct 2026)
- New: scroll-journey-kit (LakeKit). frontend-design-pro breadth rule for micro-interactions and scroll journey step.

## 0.1.0 (7 Oct 2026)
- First release from the emaildatagroup.net refresh.
