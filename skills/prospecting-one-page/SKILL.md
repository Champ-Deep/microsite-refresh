---
name: prospecting-one-page
description: Builds an opt-in one-page prospecting microsite with company overview, services and solutions, contact, about and privacy policy. Use when explicitly asked for the five-section prospecting template, not a verification, campaign or venture-story page.
---

# One-page prospecting template

Select this sibling explicitly. The default `refresh-site` workflow and verify-skin remain unchanged. There is no global feature flag or implicit domain detection: choosing this skill enables the template; not choosing it disables it. Do not pass its contract to another builder.

## Intake and build

Use the existing refresh intake to confirm company identity, real transparent PNG logo, contact email, company description, approved services, about text and approved privacy policy. Read `DESIGN.md` and `THIRD_PARTY.md`. No badge above the heading. All five sections are in the initial HTML with same-page navigation, with no scripts or remote resources required.

The worked example is a Champions Group review fixture. Its privacy paragraph is explicitly sample copy, not an approved legal policy. Replace it with the owner's approved policy before any publication. No legal, performance or customer claims may be invented. This route currently produces preview-only HTML with noindex and a disallow-all robots.txt.

```bash
python3 skills/prospecting-one-page/build.py skills/prospecting-one-page/examples/champions --out ./build/prospecting
python3 -m unittest discover -s skills/prospecting-one-page/tests -v
```

`site.json` requires strings `name`, `domain` (HTTPS origin), `email`, `logo` (local PNG), `description`; objects `overview`, `services`, `contact`, `about`, `privacy`, each with `title` and `body`. `services.items` contains 1 to 12 objects with `title` and `body`. All copy is escaped and dashes are refused. The builder validates before writing. Missing content is a build refusal, not an invented empty section. There is no async loading state because all content is built into HTML. Contact opens the email client; it does not submit a form or claim to capture leads.

## Boundaries and proof

Only these five content areas are implemented under the 16 November ruling. Delvin's unspecified recommendations, varied CTA effects, preferred-source and audio are deferred to their sibling work. No auth, billing, backend, production deployment or new UI stack.

Before review: build this example, render 375, 768 and 1440, check anchors and email, keyboard skip link and focus, reduced motion, contrast, zero overflow and console errors. Attach the enabled preview and screenshots. Build the original verify-skin fixture from the base and current checkout, byte-compare outputs and attach its disabled preview. Run the existing campaign and venture-story tests plus plugin validation. Never change those siblings to fit this contract.
