# Agent readiness reference (checked October 2026)

Standards in this area move monthly. Re-check the sources at the bottom before changing policy.

## AI crawler tokens

| Token | Operator | Purpose | Group default |
|---|---|---|---|
| GPTBot | OpenAI | Model training | Allow |
| OAI-SearchBot | OpenAI | ChatGPT search index | Allow |
| ChatGPT-User | OpenAI | Fetch triggered by a user in ChatGPT | Allow |
| ClaudeBot | Anthropic | Model training | Allow |
| Claude-SearchBot | Anthropic | Claude search index | Allow |
| Claude-User | Anthropic | Fetch triggered by a user in Claude | Allow |
| PerplexityBot | Perplexity | Search index | Allow |
| Perplexity-User | Perplexity | Fetch triggered by a user | Allow |
| Google-Extended | Google | Gemini training and grounding control token (not a crawler) | Allow |
| Googlebot | Google | Search, also feeds AI Overviews | Allow, never block |
| Applebot-Extended | Apple | Apple model training control token | Allow |
| meta-externalagent | Meta | Training and product features | Allow |
| CCBot | Common Crawl | Open dataset used by many models | Allow |

Training bots, search indexers and user-triggered fetchers are different jobs. Blocking them all as one group removes a site from AI answers, even when the owner only meant to refuse training. When a site owner picks "search and fetch only", block only GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, meta-externalagent and CCBot. `build_site.py` writes both policies from `robots_policy` in `site.json`.

## llms.txt shape

```
# Site Name

> One paragraph: what the site offers and the free action.

Free offer line.

## Key pages
- [Home](https://domain/): what happens there
- [Home as markdown](https://domain/index.md)

## <Group> email lists
- [All <group> lists](hub-url): who it is for
- [List name](url)

## Contact
- Phone: ...
```

## JSON-LD pattern (one @graph)
Organization (name, url, slogan, email, telephone, PostalAddress), WebSite (publisher to Organization), Service (offers: Offer price 0, eligibleQuantity maxValue 1000 contacts), FAQPage (questions verbatim from the page), ItemList (each group hub). Do not add Product prices or AggregateRating unless they are real and visible.

## WebMCP (Chrome origin trial)
```html
<form toolname="requestFreeEmailVerification"
      tooldescription="Verify up to 1,000 email contacts from a CSV or Excel file for free. Results are emailed to the work address given.">
  <input type="file" name="list" toolparamdescription="The contact list as CSV, TSV or Excel with a header row and an email column">
  <input type="email" name="email" toolparamdescription="Work email for results. Personal addresses are not accepted.">
</form>
```
The browser shows the form while an agent fills it, so the person can review before submitting. Keep validation messages written for people. Agents read them too.

## Cloudflare zone checks (do these on every site behind Cloudflare)
1. **AI Crawl Control:** agent and training bots set to Allow, matching the allow-all policy. Reports say Cloudflare changed its defaults for new domains in 2026, including blocking some bot classes on pages that show ads, so check each zone rather than assume.
2. **Managed robots.txt and content signals:** when enabled, Cloudflare prepends its own rules to ours. Read the served `/robots.txt` and confirm it matches the policy.
3. **Legacy "Block AI bots" switch:** off. Reported trap: blocking training can also block multi-purpose crawlers such as Googlebot, Bingbot and Applebot.
4. **Bot Fight Mode or Super Bot Fight Mode:** confirm verified AI bots are not challenged. The live audit flags challenge pages.
5. **Markdown for Agents:** on, so `Accept: text/markdown` returns markdown. Responses carry `x-markdown-tokens` and a `content-signal` header.

## Sources
- Cloudflare changelog, Markdown for Agents (2026-02-12): https://developers.cloudflare.com/changelog/2026-02-12-markdown-for-agents
- Chrome for Developers, WebMCP declarative API: https://developer.chrome.com/docs/ai/webmcp/declarative-api
- AI crawler token list 2026: https://www.anagram.ai/blog/ai-crawler-user-agent-list-2026-14-bots-and-robotstxt-tokens-to-know
- Cloudflare 2026 crawler defaults and the multi-purpose crawler trap: https://suganthan.com/notes/cloudflare-ai-crawler-defaults/
