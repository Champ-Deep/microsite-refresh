---
name: site-intake
description: Collects everything a microsite refresh needs before design starts (logo, brand colours, contact details, confirmed claims, full list catalog, audience, traffic) and writes site.json, catalog.json and brief.md. Use at the start of any microsite refresh, or when someone says "set up a new site for refresh", "intake for <domain>", "add <domain> to the refresh pipeline".
---

# Site intake

Produce one build folder per site: `<working-dir>/<domain>/`, or `<vault>/Efforts/Active/<Site> Refresh/build/` when the Celsus vault is connected. Use `${CLAUDE_PLUGIN_ROOT}/skills/refresh-site/examples/emaildatagroup/` as the worked example for every file.

## 1. Pull what exists (no questions yet)
- Fetch the homepage. Read the raw HTML too (`curl -sL`), because summarised fetches drop menu links. Extract the full navigation tree with every list name and URL, the contact details, the footer address, compliance badges, client names, testimonial names and every numeric claim.
- When Ahrefs is connected, get organic metrics and the top 12 pages for the domain. Note which pages carry the traffic.
- When the Notion connector is available, check the Microsites database under the SEO Team page for the owner, status and vendor of this site.

## 2. Ask once (single AskUserQuestion round)
Ask only what the fetch could not settle:
- the logo file. It must be the real file. When it is missing, ask for it and wait. Never redraw a logo.
- which phone number and email are correct, when the site shows more than one
- which claims are still true and approved (counts like "14 million contacts", client names, guarantees)
- the robots policy for AI bots (group default: allow all)
- where the result ships: dev handoff package, Cloudflare, or both

## 3. Write the files
`site.json`:
- name, domain, tagline
- meta description (120 to 165 chars) and og_image
- phone, email, and address (leave address empty when the site shows none, and it stays out of the schema)
- offer: name, description, quantity, service_type, og_title, llms_line
- nav_cta (the CTA's accessible label)
- faq: three or more [q, a] pairs. These are shown on the page AND written to the FAQPage schema, so write them once, here.
- robots_policy and the logo filename

`catalog.json`:
- `base` (the domain)
- `groups[]`, each with id, name, who (one plain line), hub [label, path] and lists [[name, path]]. Group by who the buyer sells to, not by the site's internal categories. Five to seven groups.
- `services` (the "Fix a list" panel)
- `popular`: four to six names, taken from the Ahrefs top pages when available
- `synonyms`: the words buyers type mapped to list names (lawyer to Attorneys, realtor to Realtors, doctor to Physicians, and so on)
- `custom_note`: optional, only for a confirmed scale claim
- `search_hint` (finder placeholder), `list_noun` ("email lists", "lists") and `catalog_note` (a confirmed promise about every list, or empty)
- a group with no live hub page sets `"hub": null`, and `brief.md` asks for one

`brief.md`: decisions, the five argument answers, the page spine, "Sources to confirm", "Open items before launch" and the gaps found. For example, a niche buyers search for that the catalog lacks (EDG had no insurance lists) becomes a custom-list lead path and a catalog suggestion.

## Rules
- Every claim on the page is traceable to the owner's confirmation or the live site, and is listed in `brief.md`.
- No dashes in any file.
- Keep each group's list names short ("Dentists", not "Dentist Email List"). The page adds the context.
