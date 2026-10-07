---
title: EDG Homepage Refresh Brief
date: 2026-10-07
status: v1.1 built (list finder, nav, agent ready), awaiting Champ review
prototype: https://claude.ai/artifact/2Giw5e787RAahK2EmvSijN
related: [[Lake B2B]], Prepackagelists Refresh (Drop-Audit Hero Spec)
---

# Email Data Group homepage refresh

**Bottom line:** emaildatagroup.net becomes the third skin of the drop-audit engine ("verify"), next to QuickAppend (append) and prepackagelists (buy a segment). One action: drop a file, get 1,000 contacts verified free. The strategist call is the reward after results, not a second button.

## Decisions (Champ, 2026-10-07)

| Decision | Choice |
|---|---|
| First page | Homepage |
| Brand | Own brand, refreshed. EDG logo kept as is (red mark, green and red wordmark, "Your Green Marketing Partner") |
| Audience | SMB marketers, positioned consultatively: help them pick the right list and channels, push toward a booked strategy call |
| Primary action | Free email verification of the first 1,000 contacts in a dropped file |
| Headline | Direct offer: "1,000 contacts verified free. Drop your list." |
| Identity | Strategist's markup: ruled paper, red pencil for problems (logo red), green for verified (logo green), handwritten margin notes, grade stamp |

## The argument

| Question | Answer |
|---|---|
| Who arrives | SMB marketer, searched a niche list (dentists, Salesforce users), has a list or is about to buy one |
| One belief | These people will tell me what is wrong with my list and what to run next before asking for money |
| Objections | "Every vendor claims 95% accuracy" and "I will get spammed by a rep" |
| Proof | Their own file, graded in seconds, then a strategist's read |

## Page spine

Hero (drop zone + live sample report) / proof strip (client names + GDPR, CCPA, CAN-SPAM) / anatomy of a tired list (five marked rows) / how it works (3 real steps) / the strategy call (example strategist note) / list catalog by buyer / objections / closing CTA / footer.

## Open items before launch

1. **Verification credits.** Clearout plan is 3,000 credits a month. Free 1,000 per visitor needs a bigger plan, an in-house SMTP checker, or a sales-qualified 24h queue.
2. **Sources to confirm:** "14 million business contacts and 210 million consumer records" (carried from the current site); client names (CQ Roll Call, CA Technologies, ReachForce, M Systems, AllDigital, Telintel) still current and approved?
3. **Policy lines to confirm with sales:** "Your results arrive by email. The strategy call happens only if you book it." and "within one business day".
4. **Dropped:** "95% deliverability guaranteed" (unsourced).
5. **Backend:** verification endpoint, booking link, phone number (site shows two: 800 710 4895 and 800 971 2028).
6. List catalog links marked # need real URLs.

## Skill pipeline used

frontend-design-pro (conductor) > landing-page (argument, headline, spine) > build with MicroKit interactions and kit fallbacks (21st.dev MCP not connected in Cowork) > ui-polish > design-trends > no-ai-slop gate > visual-verify at 390 and 1440, light and dark.

## v1.1 changes (2026-10-07)

- Purpose-first navigation: any list reachable in two clicks from home. Nav cut to Find a list, Fix a list, Strategy call, Questions. The Find a list panel groups lists by buyer type with hub links, with no third level (SPAN rule).
- List finder moved directly under the proof strip: search with synonyms, category rail, "Most searched" pills from Ahrefs top pages, and a hand-drawn marker in the hero pointing to it.
- A search with no match (for example "insurance") offers a custom list through the strategist instead of a dead end. EDG has no insurance list today: a catalog gap worth filling.
- Agent ready: every list in the raw HTML, JSON-LD (Organization, WebSite, Service with free Offer, FAQPage, ItemList), canonical, OG, a markdown twin, llms.txt, robots.txt allowing every AI bot, and WebMCP attributes on the verification form. Audit: 0 FAIL. Click depth: 48 of 48 lists and hubs one click from home.
