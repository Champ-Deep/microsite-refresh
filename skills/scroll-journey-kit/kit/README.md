# LakeKit v1

Scroll choreography and micro-interactions for LakeB2B landing pages. Vanilla CSS and JS, no build step, no React, no Tailwind. Born on the Living Data Globe page (v0.4) and proven there. The micro-interactions are ported from MicroKit (github.com/henriquegpb/microkit, microkit.co, 49 shadcn registry items).

Files
- lakekit.css, lakekit.js: inline both into the single-file page, CSS after the page styles, JS before </body>.
- lakekit-demo.html: standalone showcase. Draggable data orb that turns on scroll, a scrubbed chart scene, a filterable playground of every effect (click an attribute to copy it), a live accent picker, cursor follower. Open it to see every effect.
- demo.tpl.html, build-demo.js: rebuild the demo.
- Reference implementation of the pinned journey: LakeB2B_Living_Data_Globe.html (horizon opening that scrubs into a WebGL globe).

## Install in a page
1. Head probe, first thing in <head>, sets `jr` (pinned journey allowed) and `rv-on` (reveal allowed). Copy it from lakekit-demo.html. Without `rv-on` nothing is ever hidden, so a failed script cannot blank the page.
2. Add lakekit.css after page CSS. Override tokens on :root if needed: --mk-accent (gold), --mk-accent2 (lavender), --mk-mag, --mk-line, --mk-muted, --mk-mono.
3. Add lakekit.js before </body>. For `data-mk-journey` load GSAP 3.12.5 and ScrollTrigger from cdnjs with SRI first.

## Attributes
| Attribute | Effect | Use on | MicroKit origin |
|---|---|---|---|
| data-mk="magnetic" | leans toward the pointer | primary CTA | magnetic-fill-button |
| data-mk="glow" | two blurred lights follow the pointer | ghost or secondary button | whats-new-glow-button, cursor-edge-glow-button |
| data-mk="shine" | bright arc traces the border | ghost button, subscribe or request actions | subscribe-shine-button |
| data-mk="swap" | letters roll up one by one | nav links, text links (text only) | staggered-letter-text-swap |
| data-mk="underline" | gradient underline grows | inline links | gradient-underline-button |
| data-mk="spot" | pointer wash plus gold top rail | cards, steps, lanes | social-highlight-cards |
| data-mk="tilt" | card leans toward the pointer | feature cards (not on .rv elements) | n/a |
| data-mk="aura" | soft light follows the pointer | a whole section, finale | n/a |
| data-mk-slide | one pill glides to the active child | chip rows, tabs | sliding-underline-tabs, spotlight-indicator |
| data-rail="Label" | side nav with sliding glow bar, built from sections | each major section (needs an id) | spotlight-indicator |
| body[data-mk-progress] | page scroll progress bar | body | n/a |
| data-mk="split" | headline words rise from a mask | h2 | n/a |
| class="rv" or data-mk="reveal" | fade and rise, stagger with --d | any block | n/a |
| data-mk-count | number counts up, exact text restored | stats | n/a |
| data-mk-journey | pinned scene, sets --p 0 to 1, fires lk:progress | .lk-journey wrapper | n/a |

## Journey markup
```html
<div class="lk-journey" data-mk-journey>
  <div class="lk-stage">
    <div class="lk-horizon"><div class="hz"><i class="arc a-p"></i><i class="arc a-l"></i><i class="arc a-w"></i></div></div>
    <div class="lk-title"><h1>...</h1></div>
    <div class="lk-next">scene two, appears as --p passes 0.4</div>
  </div>
</div>
```
Anything can read `--p` in CSS (calc) or listen for `lk:progress` in JS. The globe page drives a WebGL camera from p. Set `--run` on .lk-journey to change scroll length (default 150vh).

## Rules (do not skip)
- Pointer effects only run on `(hover:hover) and (pointer:fine)` and never under prefers-reduced-motion. Touch gets the plain element.
- Reduced motion: no pinning, no hidden content, no count-up, no split. Content is final and visible.
- Pin only on desktop (min-width 1024) with WebGL2 or enough device memory when the scene needs it. Phones and tablets get a stack: same scenes, normal flow, no pin.
- Never hide content in CSS without the `rv-on` class. Never rely on JS to unhide a heading you need for LCP.
- Use transform, opacity and CSS `translate` only. No large blur filters on full-bleed layers (memory). Glow horizons are radial-gradient discs with mix-blend-mode:screen.
- Keep text for screen readers: swap and split set aria-label on the element.
- Brand: navy #011A6B ground, lavender #7A76DA, gold #FFB703, magenta #DD1286, purple #6D08BE, muted #B9C0E4. Montserrat plus IBM Plex Mono. No em or en dashes anywhere. Logo never animated.
- Budget: kit is about 20KB uncompressed. Whole page under 300KB JS, LCP under 2.5s, 60fps.

## MicroKit catalog: what to reach for
Install the real thing with `npx shadcn@latest add @microkit/<name>` when the project is React. For single-file HTML, port the idea with the attribute above or write the CSS directly (each source is a small CSS recipe).
- Cursor and pointer: cursor-edge-glow-button, cursor-follow-share-button, whats-new-glow-button, staggered-letter-glow-button, magnetic-fill-button
- Fill and wipe: yellow-fill-preview-button, orange-circle-fill-button, circle-surface-button, inset-circle-button, outline-wipe-button, expanding-newsletter-button, expanding-contact-button, talk-arrow-reveal-button
- Arrow and icon swaps: icon-swap-button, sliding-send-button, get-started-circle-swap, see-more-swap-button, next-reveal-button, next-dot-fill-button, projects-arrow-button, preview-browser-button, sliding-arrow-label, pricing-slide-link, read-more-swap, contact-reveal-button, white-contact-orbit-button, glow-arrow-button
- Text swaps: staggered-letter-text-swap, project-text-swap-button, view-more-text-swap, gradient-underline-button, contact-underline-button
- Shine and rim: subscribe-shine-button, aurora-download-button, layered-gradient-button, neon-invert-button, floating-newsletter-button
- Navigation and tabs: spotlight-indicator, sliding-underline-tabs, sliding-content-tabs, expanding-icon-tabs, blur-glide-menu, preview-hover-toolbar
- Cards and inputs: social-highlight-cards, social-icon-buttons, contact-details-reveal, focus-input, scrub-number-field
- Commerce: secure-purchase-button
Recolor orange to gold #FFB703 and blue to lavender #7A76DA when porting.

## Landing page recipe (default composition)
1. Opening scene: glow horizon plus one line of blurred word-by-word headline (lk-journey).
2. Scrub into the hero object (globe, product, map, dashboard) as scene two. Keep it interactive.
3. Content sections: split h2, rv blocks, spot cards, count stats, slide chips for any filter.
4. Navigation: swap on links, rail on desktop, progress bar on top.
5. Buttons: primary magnetic, secondary glow, tertiary shine or underline. Never the same effect on every button.
6. Finale: aura or glow horizon echo, one primary CTA.
7. Test at 1440, 768 and 400 with touch, plus reduced motion. Dash count 0.
