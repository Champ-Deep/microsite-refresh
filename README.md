# Microsite Refresh

Turns an old data-list microsite into a 2027 landing page that does four things:

- serves the visitor's purpose in two clicks
- converts with a drop-a-file free verification
- reads like a person wrote it
- is fully readable by AI crawlers, scrapers and browser agents

It was built on the emaildatagroup.net refresh (October 2026). That run ships inside the plugin as the worked example.

## What you get

| Skill | What it does |
|---|---|
| `refresh-site` | The one to start with. Runs the whole refresh from intake to handoff |
| `site-intake` | Collects the logo, contacts, approved claims and the full list catalog, and writes the site files |
| `frontend-design-pro` | The design pipeline: landing page, polish, trend pass, 21st.dev components, MicroKit interactions |
| `vinh-copywriting` | Body copy, subheads and CTA lines in a plain, persuasive voice |
| `no-ai-slop` | Final gate on every line of copy. Zero dashes |
| `visual-verify` | Screenshots at phone and desktop, light and dark, plus an interface audit |
| `agent-ready` | robots.txt for AI bots, llms.txt, markdown twin, JSON-LD, WebMCP form, plus an audit that proves it |
| `ship-page` | Dev handoff package, Cloudflare checks and post-launch proof |

## Setup for marketing (Cowork, Claude desktop app)

1. Install the plugin: open the `.plugin` file and press **Install**.
2. Turn on these connectors for your chat (Settings, Connectors):
   - **Ahrefs:** traffic and top pages
   - **Cloudflare Developer Platform:** zone checks
   - **Figma** (optional): send the design to designers
   - **Notion** (optional): the Microsites database
3. Optional: **21st.dev** components. Add it as a custom connector with URL `https://21st.dev/api/mcp` and header `x-api-key` set to your key. Without it, the plugin uses its built-in components and tells you so.
4. Have the site's **real logo file** ready (PNG with a transparent background is best).

### Run it
Type one line:

> Refresh emaildatagroup.net

or `/refresh-site https://www.prepackagelists.com`

Claude reads the site and its traffic, asks you about six questions in one go (audience, offer, headline, look, claims to keep, phone number), then builds. You get:

- a private preview link
- a brief with every decision and every claim to confirm
- a handoff folder for engineers

Review the preview, write your critique in plain words, and Claude updates both the page and the plugin's rules.

## Setup for engineers (Claude Code)

```bash
claude --plugin-dir ./microsite-refresh.plugin       # try it for one session (a folder or the .plugin zip)
# for everyone: add it to the team marketplace, then  claude plugin install microsite-refresh@<marketplace>
pip install playwright pillow && playwright install chromium
export API_KEY_21ST=...            # optional, enables 21st.dev components
export CLOUDFLARE_API_TOKEN=...    # only for wrangler deploys
```

Build and test any site folder directly:

```bash
R=./microsite-refresh   # wherever the plugin folder lives; inside Claude the skills use ${CLAUDE_PLUGIN_ROOT}
python3 $R/skills/refresh-site/scripts/build_site.py ./my-site --out ./my-site/dist
python3 $R/skills/agent-ready/scripts/agent_audit.py ./my-site/dist/handoff
python3 $R/skills/agent-ready/scripts/click_depth.py ./my-site/dist/handoff/index.html --catalog ./my-site/catalog.json
python3 $R/skills/visual-verify/scripts/shoot.py ./my-site/dist/handoff/index.html --out ./my-site/.verify --widths 390,1440 --themes light,dark
```

A site folder holds `template.html`, `finder.js`, `extra.css` (copied from `skills/refresh-site/templates/verify-skin/`), plus `site.json`, `catalog.json` and `logo.png`. See `skills/refresh-site/examples/emaildatagroup/`. The build stops if copy from the EDG example is still on another site's page; `refresh-site/SKILL.md` lists every string to rewrite.

## The rules every refreshed page meets

1. Any list on the site is reachable within two clicks of the home page, three at most. Search with no match offers a custom list.
2. One primary action. The visitor sees value (a graded report on their own file) before giving an email.
3. No invented claims, people, numbers or logos. Every claim is listed in the brief for sign-off.
4. No em or en dashes, anywhere. Copy passes the no-ai-slop gate.
5. Full-width layout, scroll motion, micro-interactions, tested at 390 and 1440 in light and dark.
6. Agent ready, with 0 FAIL on the audit:
   - content in the raw HTML
   - JSON-LD that matches the page
   - robots.txt that allows every AI bot (group default)
   - llms.txt
   - markdown twin
   - WebMCP attributes on the form

## Known limits (v0.1)

- Cowork cannot deploy to Cloudflare. Engineers deploy with Wrangler, and marketing runs the live checks afterwards.
- The free verification needs a backend endpoint and enough verification credits. The page is a front end until engineering wires it up.
- One template ships today (the verify skin). Append and buy-a-segment sites (prepackagelists, QuickAppend) reuse it and adapt the hero by hand from `templates/append-segment-reference.html`. Dedicated skins come in v0.2.
- Hub pages for every list group are assumed. Where a site has none, the brief asks for one.
- WebMCP is a Chrome origin trial. The attributes are harmless where unsupported.
