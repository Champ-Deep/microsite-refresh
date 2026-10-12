---
name: signature-hero
description: Designs and builds the signature moment of a microsite refresh, an opening scene that scrolls into an interactive object tied to what the site sells (the LakeB2B Living Data Globe is the reference). Runs a direction workshop with the owner using the scroll-craft interview, shows options to pick from and combine, sources the object from 21st.dev, and builds it to a tested scroll contract. Use inside refresh-site, or when someone says "signature hero", "hero concept", "make the hero innovative", "something like the globe", "interactive hero", "wow moment", "first scroll", "what should the hero be".
---

# Signature hero

Every refreshed microsite gets one moment a visitor remembers. It is an opening scene, then a first scroll that lands on a live object they can touch, and that object feeds the call to action.

The LakeB2B Living Data Globe (October 2026) is the bar. A glow horizon and one line of headline open the page. Scrolling raises a globe out of the horizon into the hero. Visitors hover a market for a glass card, pin it, re-cut it by industry, and the sample request prefills with their market. The finished build ships in `reference/LakeB2B_Living_Data_Globe_cobe.html`. Open it before you design anything.

Deep's direction is to keep bringing ideas of this quality and to work them out with the owner instead of guessing.

This skill stands on two tools:
- **`scroll-craft`** (Nate Herk, MIT, vendored in this plugin) supplies the method: the interview, the eight page grammars, the feeling curve and peak, the signature move, dimensional hero layering, the fingerprint gate, and the scroll verification harness.
- **`scroll-journey-kit`** (LakeKit) supplies our pinned journey and micro-interactions, tuned to Champions Group brands.

Where scroll-craft and this file disagree, this file wins for microsites. Brand rules from the brand skill win over both.

## Workflow

Track each step as a task.

### 1. Read what intake produced
Read `brief.md`, `site.json` and `catalog.json` from `site-intake`, plus the traffic notes.

Pull out three things:
- what the site sells (lists by geography, industry, title, technology, consumer);
- the one action (verify a file, get a sample, buy a segment);
- the numbers you are allowed to show.

Read `references/innovation-log.md`, which is the fingerprint registry across our microsites.

### 2. Direction workshop: round one, the brief
Read `scroll-craft/SKILL.md` Step 0 and `scroll-craft/references/feel.md`. Then ask the owner in one AskUserQuestion pass (four questions per call, so two calls back to back). Build every option from this site's catalog and brief rather than generic choices.

1. **First ten seconds.** What a visitor should do before reading anything. Offer: explore our coverage, test their own file, find their list, or see proof from a named result.
2. **The living object.** Offer three or four objects from `references/concepts.md` that fit this catalog, each with one line on what the visitor can do with it.
3. **Vibe in three to five words, plus references from any medium.** A film, an album cover, a shop, a magazine, a game. Avoid asking for websites, because naming sites is how a page ends up looking like an existing one.
4. **The one moment a visitor should remember.** It becomes the peak in the feeling curve.
5. **One thing this site should do that no site they have seen does.** It becomes the seed of the signature move. Push for a real answer.
6. **Motion appetite.** Cinematic (pinned opening that scrubs into the object), calm (the object rises as the page loads, no pin), or still.
7. **One unbroken world, or distinct scenes.** This is scroll-craft's biggest structural fork.
8. **Assets they already have.** Product shots, photography, footage, data exports. Real assets beat generated ones.

Write the answers into `brief.md` in their words, with the feeling curve, the peak, and the sentence "It's the site where ___".

If the owner says "use your judgment", write the brief yourself under a `Self-authored under explicit creative delegation` heading and carry on.

### 3. Grammar and the fingerprint gate
Pick a page grammar from `scroll-craft/references/uniqueness.md`:
- filmic one-shot;
- chaptered editorial;
- live surface;
- continuous world;
- typographic poster;
- gallery or catalog;
- split stage;
- rhythmic cutlist.

Say in one line why the others lost.

Then run the fingerprint gate against every row in `references/innovation-log.md`. The plan must differ from each row on at least 4 of 6 dimensions:
- grammar;
- nav treatment;
- hero device;
- act-sequence shape;
- close pattern;
- signature move.

If it fails, change the plan, not the log.

### 4. Options to pick from and combine
Deep likes to see a couple of options, take the best parts of each, and combine them. Build the concept round for that.

Write two or three concepts into `brief.md`, each with:
- a name and one sentence on the idea;
- a three-frame ASCII storyboard: opening, mid-scroll, landed (examples in `references/concepts.md`);
- the grammar, the feeling curve and the peak;
- the signature move, which must be a bespoke interaction and not a retuned kit effect;
- the data it reads, and which `catalog.json` or `site.json` fields drive it;
- the three interactions (hover, pin or select, filter) and how each one changes the CTA;
- the risk (performance, missing data, mobile) and the fallback.

When time allows, build a one-screen prototype of the top two concepts and screenshot the opening and landed frames. Seeing motion beats reading about it.

Then ask a second AskUserQuestion with multi-select, one option per part, so the owner can take parts from different concepts: "the opening from A, the object from B, the close from A". Combine the picks into one plan and write it into `brief.md`.

At least one concept is not in `references/concepts.md` yet. Invent it from the site's own data. If the owner is not present, take the most on-brief concept, say so at the top of `brief.md`, and carry on.

### 5. Source the object
1. **21st.dev.** When the MCP is connected, search 21st.dev with `search` (`type:"component"`, limit 6), using the queries in `references/concepts.md`. Pull at most two components with `get_component`, port them to vanilla for the single-file page, and credit the id in a comment.
2. **Globes.** The globe is solved. Use cobe (MIT, 13KB, inlined from `reference/cobe.iife.js`) exactly as the reference does.
3. **Photographic heroes.** When the concept is a photographic or product hero, follow `scroll-craft/references/hero-depth.md`: independent background, subject, foreground and atmosphere planes, real alpha cutouts, and text between planes.
4. **Asset generation.** Only generate assets with scroll-craft's `kie.mjs` when the owner approves the spend and the key is set. Real assets come first.
5. **Journey and interactions.** The scroll journey and micro-interactions come from `scroll-journey-kit`.
6. **No MCP.** When the MCP is not connected, say so in one line and build from the reference, the kit and scroll-craft's engine.

### 6. Build to the contract
Follow `references/build-contract.md`. It covers:
- the pose geometry shared by the CSS horizon and the object;
- the pin and stack modes;
- the hover card, the pin and the filter;
- the CTA prefill;
- the leave and re-enter behaviour;
- mobile, reduced motion and the budget.

Each rule in it fixed a real bug.

Apply scroll-craft's taste floor (`scroll-craft/references/taste.md`) to type, spacing and contrast.

### 7. Verify
In a real browser, at 1440, 768 and 400 with touch:
1. Run scroll-craft's harness (`scroll-craft/scripts/shoot.mjs`) for the contact sheet, dead-scroll and contrast checks, then read the sheet.
2. Screenshot the journey at 0, 30, 60 and 100 percent.
3. Hover and pin a market, then scroll back to the top. The opening scene must be clean, with no card, no pin and no arcs. Scroll down again and the object replays.
4. Check that the filter chips change the object, the counters and the CTA.
5. Check reduced motion (everything visible, no pin) and the page with the scene script blocked (the poster and the plain HTML twin still tell the story).
6. Run the feel check from `scroll-craft/references/feel.md`: one word per act, scrolled cold, then diff the words against the intended curve.
7. Confirm the dash count is 0 and there are no console errors.
8. Report real-GPU frame rate and real-phone behaviour as measured or unverified.

### 8. Close the loop
Ask the owner for critique of the hero and the first scroll first. Add a row to `references/innovation-log.md` with:
- the site;
- the six fingerprint dimensions;
- what the owner liked;
- what to try next time.

When a critique is durable, propose an edit to this skill, `references/concepts.md` or `references/build-contract.md`, then release it with the steps in the plugin's `CLAUDE.md`.

## Rules
- **Data.** The object shows what the site sells, with sample figures labelled once in the footer. Never invent a number that reads as live, and never put an invented statistic in a counter.
- **Conversion.** Every interaction updates the CTA or the form.
- **Plain HTML twin.** Every piece of information in the hero also exists in plain HTML (a table or a list) for crawlers, screen readers and people without WebGL.
- **Brand.** The site's logo colours lead (from `logo_palette.py`). Zero em and en dashes. No logo in a white box.
- **Taste.** These follow Deep's preferences and scroll-craft's hard rules:
  - no short rule line before an eyebrow, and at most one eyebrow per three sections;
  - no section counters;
  - no animated "scroll" nudge;
  - no gradient text.
- **Buttons.** CTAs are rectangular (not pills) and the label is not bold. Vary the button animation by role: one magnetic primary at most, then glow, shine or underline for the rest.
