# Micro-interactions

Small responses to a hover, focus, tap or scroll that tell the reader the page is alive and built with care. Source library: MicroKit UI (github.com/henriquegpb/microkit, MIT, 49 interactions, CSS and Tailwind variants, shadcn registry `@microkit`). Second source: 21st.dev for larger interactive components. The kit already ports the ones below to vanilla CSS and JS in `core.css` and `core.js`.

## The rules

1. Every interactive element gets a hover state, a `:focus-visible` state that matches it, and a touch equivalent where hover carries meaning.
2. One micro-interaction per element. A button can swap its label and slide its arrow, which reads as one gesture; it does not also bounce, glow and shake.
3. Durations 200 to 500ms, `cubic-bezier(.16,1,.3,1)`. Loops only while hovered.
4. Colours come from the brand. MicroKit's orange accents become the brand primary or gold.
5. Respect `prefers-reduced-motion` and the static export mode; every micro-interaction degrades to a plain colour change.
6. Tap targets stay 44px or more after any scale change.
7. Credit the source in a CSS comment.

## Ported set (in the kit)

| Element | Interaction | MicroKit source | Kit class |
|---|---|---|---|
| Primary buttons | label rises out as an identical copy rises in | project-text-swap-button | `.btn .swap > .cur + .inc` (build with `swap()` in build.py) |
| Arrow squares | arrow slides out right as a second arrow slides in from the left | projects-arrow-button | `.btn .arr > i + i` |
| Dark and light CTAs | two brand-coloured blurred glows follow the pointer across the button | whats-new-glow-button | `.mk-glow > .gl.a + .gl.b`, JS sets `--gx` |
| Ghost button on gradient | a conic highlight traces the border while hovered | subscribe-shine-button | `.mk-shine` |
| Step lists | a glowing brand rail slides to the step nearest the reading line; that step's title takes the brand colour | spotlight-indicator | `.steps` (JS appends `.rail`, toggles `.active`) |
| Pills and chips | lift 2px, brand rail grows across the top edge | social-highlight-cards | `.pill`, `.tag:hover` |
| Floating stat cards | perspective tilt toward the pointer with a lavender sheen; touch-hold works on phones | 21st.dev Optimized Tilt Card (27139) | `.fcard`, JS sets `--rx`, `--ry`, `--px`, `--py` |
| Sortable tables | rows glide to their new position, the sort arrow flips | 21st.dev Sortable Data Table (35036) | `table.data[data-sortable]` (FLIP in JS) |
| Table rows | brand accent bar appears on the first cell | spotlight-indicator, simplified | `table.data tbody tr:hover` |
| Heat tiles, unit dots | lift and scale on hover, risk outline intensifies | none | `.tile:hover`, `.udots i:hover` |
| Map bubbles | ring springs outward | none | `.map .bub:hover .ring` |
| Panels | shadow deepens toward the brand colour | none | `.panel:hover` |

## Worth adding when the page has the element

| Element | MicroKit item | Notes |
|---|---|---|
| Tabs | sliding-underline-tabs, sliding-content-tabs | underline glides between labels |
| Contact or email CTA | contact-details-reveal, contact-underline-button | show the address as selectable text, not only a mailto |
| Number input | scrub-number-field | calculators and ROI tools |
| Text link "read more" | read-more-swap, pricing-slide-link | arrow swaps sides |
| Newsletter or download | aurora-download-button, floating-newsletter-button | one per page at most |
| Menu | blur-glide-menu | multi-level nav only |

Install the original with `npx shadcn@latest add @microkit/<name>` in a React project, or copy the CSS variant from microkit.co and port it to the kit's tokens for a single-file page.


## LakeKit set and the full catalog

The `scroll-journey-kit` skill (kit in its `kit/` folder) ports a broader set to vanilla attributes: `data-mk="magnetic"` (magnetic-fill-button), `glow` (whats-new-glow-button, cursor-edge-glow-button), `shine` (subscribe-shine-button), `swap` (staggered-letter-text-swap), `underline` (gradient-underline-button), `spot` (social-highlight-cards), `tilt`, `aura`, `data-mk-slide` (sliding-underline-tabs, spotlight-indicator), `data-rail`, `data-mk="split"`, `data-mk-count`. Use at least six distinct effects per page and different effects on different elements.

The remaining MicroKit items, by job, for when the element calls for them: fill and wipe (yellow-fill-preview-button, orange-circle-fill-button, circle-surface-button, inset-circle-button, outline-wipe-button, expanding-newsletter-button, expanding-contact-button, talk-arrow-reveal-button); arrow and icon swaps (icon-swap-button, sliding-send-button, get-started-circle-swap, see-more-swap-button, next-reveal-button, next-dot-fill-button, preview-browser-button, sliding-arrow-label, pricing-slide-link, read-more-swap, contact-reveal-button, white-contact-orbit-button, glow-arrow-button); shine and rim (aurora-download-button, layered-gradient-button, neon-invert-button, floating-newsletter-button); navigation (expanding-icon-tabs, blur-glide-menu, preview-hover-toolbar); cards and inputs (social-icon-buttons, contact-details-reveal, focus-input, scrub-number-field); commerce (secure-purchase-button). Recolour orange to the brand gold and blue to lavender.
