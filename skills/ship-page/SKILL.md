---
name: ship-page
description: Packages a refreshed microsite page for engineers and checks the Cloudflare side before and after launch. Use after refresh-site passes its gates, or when someone says "hand this off to dev", "package the page", "ship the refresh", "deploy to Cloudflare", "is the live site agent ready".
---

# Ship a refreshed page

## 1. Dev handoff package
Start from `<build>/dist/handoff/` (written by `build_site.py`) and add `HANDOFF.md` next to it. Deliver the folder as a zip, and when the Celsus vault is connected, also save it to `Efforts/Active/<Site> Refresh/handoff/`.

`HANDOFF.md` sections, in this order, with no dashes:
1. **What ships:** index.html, index.md, robots.txt, llms.txt and sitemap.xml, and where each one goes on the server (root paths).
2. **Wire up:**
   - the verification endpoint (the form posts the file and the work email; first 1,000 rows only; reject free mail server side too)
   - the booking link for the strategy call
   - analytics events: file_dropped, report_shown, verify_requested, call_booked, list_search, list_search_nomatch
3. **Keep these intact:**
   - content stays in the raw HTML
   - JSON-LD stays in sync with the visible copy
   - the WebMCP attributes stay on the form
   - every catalog link keeps an `<a href>`
4. **Open items:** copy the "Sources to confirm" and "Open items before launch" lists from `brief.md`.
5. **Acceptance tests:** the commands below. They must show 0 FAIL on staging and again on production.

## 2. Cloudflare
- **Claude Code (engineers):** deploy static files with Wrangler, for example `npx wrangler pages deploy dist/handoff --project-name <site>`, or the team's Workers static assets setup. The token comes from `CLOUDFLARE_API_TOKEN` in the environment, never from a file.
- **Cowork (marketing):** the Cloudflare connector can read Workers, KV, R2 and the docs, but it cannot deploy. Hand the package to an engineer, then run the checks below once it is live.
- On every zone, work through "Cloudflare zone checks" in `${CLAUDE_PLUGIN_ROOT}/skills/agent-ready/references/agent-readiness.md`. These settings live in the Cloudflare dashboard. List each one for the owner with its expected value.

## 3. Post-launch proof
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/agent-ready/scripts/agent_audit.py https://<domain>/
python3 ${CLAUDE_PLUGIN_ROOT}/skills/agent-ready/scripts/click_depth.py https://<domain>/ --max 3
```
Report in two lines: bots that get the page, and lists deeper than three clicks. When anything fails, name the setting or file that causes it.
