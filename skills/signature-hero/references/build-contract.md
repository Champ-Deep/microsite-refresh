# Build contract

Every signature hero follows these rules. Each one fixed a real problem on the globe build.

## Structure
- Head probe first in `<head>`: sets `jr` (journey allowed) and `rv-on` (reveal allowed) only when motion is allowed. Nothing is hidden without those classes.
- Poster first: a static image or canvas of the object paints before any scene script. The scene loads after the page is interactive (`requestIdleCallback` after `load`).
- Plain HTML twin: the counts the object shows also live in a table or list.

## Journey
- One progress number `p` (0 to 1) from GSAP ScrollTrigger drives everything: horizon, headline, object pose, copy reveal.
- Pin mode on desktop (1024px and up, 560px tall and up). Stack mode on phones and tablets: same scenes in normal flow, no pin. No journey when reduced motion is set: the end state shows at once.
- The CSS glow horizon and the object share one pose (`cx`, `cy`, `r`) so they never drift apart. The horizon is radial-gradient discs with `mix-blend-mode:screen`, never big blur filters.
- Enter when `p` passes 0.62 (pin) or 0.45 (stack). **Leave when `p` drops below 0.5 (pin) or 0.3 (stack): release the pin, close the card, fold the markers and arcs away.** Enter replays them. Without this, arcs and the card hang over the opening scene when the visitor scrolls back up.
- Picking and clicking only work while entered.

## Object (cobe globe)
- One full-size canvas over the hero. Place the globe with `scale = r / (0.4 * canvasHeight)` and `offset = [2 * (cx - W/2), 2 * (cy - H/2)]` (measured: cobe draws radius 0.4 x height x scale, and offset moves it by half). Using width instead of height made the phone globe three times too big.
- Give every marker an `id`. cobe writes an anchor element per marker and a `--cobe-visible-<id>` flag in a style tag. Read those each frame for hover hit tests and card placement; this works in every browser, without CSS anchor positioning.
- Re-send markers only when something changed (hover easing, filter, pin), not every frame.
- Arcs rise out of the globe by tweening `arcHeight` from 0; the hovered or pinned arc turns gold.

## Interaction
- Hover shows a glass card with counts, a sparkline and top titles; click pins; click again or Escape releases. The CTA reads "Get a sample for <market>" and the form prefills market and industry.
- Filter chips (with the LakeKit sliding pill) re-cut markers, arcs, counters, table and CTA together, and turn the object to the top result.
- Drag rotates. Idle rotation stops on hover or pin and resumes after three seconds.

## Buttons and taste
- CTAs are rectangular with a small radius, and the label is not bold. One magnetic primary at most; other buttons use glow, shine, underline or letter swap so no two roles move the same way.
- No animated scroll nudge, no section counters, no gradient text, at most one eyebrow per three sections, no rule line before an eyebrow.

## Budget and checks
- JS under 300KB, LCP under 2.5s, 60fps target on a laptop GPU, file under 16MB.
- Dash count 0. No console errors. Screenshots at 1440, 768 and 400 opened and critiqued. The pin and scroll-back test passes.
