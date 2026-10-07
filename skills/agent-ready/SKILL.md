---
name: agent-ready
description: Makes a page or site readable and usable by AI crawlers, scrapers, AI search engines and browser agents, then proves it with an audit. Covers robots.txt for AI bots, llms.txt, markdown twins, JSON-LD, raw-HTML content, the accessibility tree, WebMCP form tools, click depth and Cloudflare AI settings. Use for "agent ready", "LLM readable", "AI crawler", "GEO", "AEO", "llms.txt", "can ChatGPT read our site", "are we blocking AI bots", "WebMCP", "markdown for agents", and as a mandatory gate in refresh-site.
---

# Agent readiness

Assume the next visitor is not a person. It may be ChatGPT, Claude or Perplexity fetching a page for a user, a search index building an answer, a scraper with no JavaScript, or a browser agent trying to fill the form. Each needs the offer, the lists and the action without running our scripts or guessing.

Details, bot tokens and copy-ready snippets are in `references/agent-readiness.md`. Read it before the first build of a site.

## The checklist (build each one; the audit verifies it)

1. **Content is in the raw HTML.** Headline, offer, every list link, FAQ and contact details are present before any script runs. JavaScript may add tabs, search and animation, but it never creates content. The audit compares the no-JS and JS word counts.
2. **Structure agents can parse.** One H1, ordered headings, `<main>`, `<nav>` and `<footer>`, real link text, labelled fields and alt text. Agents read the accessibility tree, so accessibility work is agent work.
3. **JSON-LD that matches the visible page.** Organization, WebSite, Service with Offer (the free 1,000), FAQPage (the questions as written on the page) and ItemList (list categories). Never mark up content that is not visible.
4. **Head metadata.** Title, meta description (120 to 165 chars), canonical, Open Graph, and `<link rel="alternate" type="text/markdown">` pointing to the markdown twin.
5. **Crawl files.** `robots.txt` names every AI token explicitly and follows the policy (group default: allow all, because these are lead-gen sites and being in AI answers is the goal). Add `llms.txt` (H1, a `>` summary, linked sections for every hub and list) and `sitemap.xml`.
6. **Markdown twin.** `index.md` sits next to each page, or Cloudflare "Markdown for Agents" is turned on for the zone so `Accept: text/markdown` returns markdown.
7. **Agent-callable action.** The primary form carries WebMCP attributes: `toolname`, `tooldescription`, and `toolparamdescription` on each field. This is a Chrome origin trial in 2026, so build it as progressive enhancement; it costs nothing when unsupported.
8. **Purpose-first depth.** Every list is linked from the homepage HTML (one click) or from a hub (two clicks). Three clicks is the limit.
9. **Nothing blocks the bots.** On Cloudflare, check AI Crawl Control, managed robots.txt, content signals and the legacy "Block AI bots" switch. Then fetch the live page as each bot (see `ship-page`).

## Commands

```bash
# a built handoff folder (pages + robots + llms.txt + sitemap)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/agent-ready/scripts/agent_audit.py <dist/handoff>
# a live site: also fetches as GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-User, PerplexityBot, Googlebot and tests Accept: text/markdown
python3 ${CLAUDE_PLUGIN_ROOT}/skills/agent-ready/scripts/agent_audit.py https://www.example.com/
# click depth: page vs catalog, or breadth-first crawl of a live site against its sitemap
python3 ${CLAUDE_PLUGIN_ROOT}/skills/agent-ready/scripts/click_depth.py <dist/handoff/index.html> --catalog <catalog.json>
python3 ${CLAUDE_PLUGIN_ROOT}/skills/agent-ready/scripts/click_depth.py https://www.example.com/ --max 3
```

Zero FAIL is the bar, and every WARN is either fixed or explained in the handoff note. The scripts use only the standard library, plus Playwright for the JS comparison (`pip install playwright` and then `playwright install chromium` on a dev machine; Cowork already has it).

## When auditing an existing site (no rebuild)
Run the live audit, then report in this order: bots blocked, content missing without JS, missing crawl files, schema gaps, depth failures. Each item gets a fix an engineer can act on.
