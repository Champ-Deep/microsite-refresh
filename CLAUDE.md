# microsite-refresh plugin: how to change it

This repo is the microsite-refresh plugin for Champions Group. It improves after every refresh: owner critique becomes a rule in a skill, not a one-off fix.

## Release steps (every change)
1. Edit the skill. Put durable lessons where they will be read: `refresh-site` for process, `signature-hero` (and its `references/`) for hero concepts and the build contract, `no-ai-slop` for writing rules, `frontend-design-pro` for page design.
2. Log the hero concept in `skills/signature-hero/references/innovation-log.md` after each refresh.
3. Run `python3 scripts/validate_plugin.py`. It must print 0 failures. It checks the installer rules (description at most 1024 characters, no angle-bracket tags in descriptions, name matches folder, semver) and zero em and en dashes in our own files.
4. Bump `version` in `.claude-plugin/plugin.json` (minor for new skills or rules, patch for fixes) and add a line to `CHANGELOG.md`.
5. Commit with a plain message saying what changed and why, push to `main`, and build the `.plugin` zip for installation: `zip -r microsite-refresh.plugin . -x ".git/*" "*.DS_Store"`.

## House rules for files in this repo
- Zero em and en dashes in any file we write. Vendored third-party skills (`skills/scroll-craft`, `skills/no-ai-slop/references/human-speak`) stay as published and carry a NOTICE.
- Skill descriptions: third person, specific trigger phrases, no angle brackets (write "this site", not a placeholder in brackets), at most 1024 characters.
- Credit every third-party source (21st.dev component ids, MicroKit, cobe, scroll-craft, human-speak) with its licence.

## Upstreams to check for updates
- github.com/nateherkai/scroll-craft (skills/scroll-craft)
- github.com/nateherkai/human-speak (skills/no-ai-slop/references/human-speak)
- github.com/shuding/cobe (skills/signature-hero/reference/cobe.iife.js, bundle with esbuild as an IIFE that sets window.createGlobe)
- github.com/henriquegpb/microkit (micro-interaction catalog in scroll-journey-kit)
