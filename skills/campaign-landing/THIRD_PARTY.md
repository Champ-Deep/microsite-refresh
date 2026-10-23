# Third-party sources

The template ports three 21st.dev community components to vanilla CSS and JavaScript. The ports keep the behaviour and drop the React, Tailwind, framer-motion and icon dependencies.

| Component | Source | Where in template.html |
|---|---|---|
| Compare (Aceternity UI) | 21st.dev, `compare.tsx` | `.cmp` platform ledger: clipped top pane, glow line, handle, hover sweep. The sparkles layer was not ported. |
| AI Sources | 21st.dev, `ai-sources.tsx` | `.srcs` favicon stack and expanding source rows in the hero and the account section |
| Halftone Wordmark Footer | 21st.dev, `halftone-wordmark-footer.tsx` | `.hwf` footer canvas: coverage-sized dots, pointer springs, click ring, print grain |

Favicons in the sources stack are fetched from Google's favicon service at runtime; a neutral globe is drawn when one fails. Fonts are Google Fonts (Montserrat, Inter).

## Draggable Widget Grid (21st.dev), via the deependhq island port
- Upstream: the 21st.dev "Draggable Widget Grid" component, first ported for deependhq.com as `islands/widget-grid.island.jsx` (React plus `motion/react`).
- Here: `template.html`, the `/* ---- Bento ---- */` script and `.wg*` styles. The exact-tiling layout (`tile`, `pack`, `canonical`, `candidatesFor`, `choose`), the 40ms settle, 350ms long press with 8px slop, 1.015 lift scale, 620ms landed ring and Alt plus arrow keyboard reorder are ported one to one. Dragging is pointer events plus an inline transform instead of `motion`, and React state is a plain `order` array of tile ids.
- Omitted: React, `motion`, localStorage persistence of the order (a landing page resets on every visit).
