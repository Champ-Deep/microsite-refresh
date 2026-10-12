#!/usr/bin/env python3
"""Validate the microsite-refresh plugin before every release.

Checks the rules the plugin installer enforces (plugin.json, skill frontmatter,
description length and no XML tags) plus house rules (zero em and en dashes in
our own files). Exit code 1 on any failure.

Usage: python3 scripts/validate_plugin.py [plugin_root]
"""
import json, os, re, sys

root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails, warns = [], []
DASH = re.compile('[–—]')
VENDORED = {"scroll-craft"}  # third-party skills kept as published; dashes there are warnings only

try:
    pj = json.load(open(os.path.join(root, ".claude-plugin", "plugin.json")))
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", pj.get("name", "")):
        fails.append("plugin.json: name must be kebab-case")
    if not re.fullmatch(r"\d+\.\d+\.\d+", pj.get("version", "")):
        fails.append("plugin.json: version must be semver")
except Exception as e:
    fails.append(f"plugin.json: {e}")

skills = os.path.join(root, "skills")
for name in sorted(os.listdir(skills)):
    d = os.path.join(skills, name)
    if not os.path.isdir(d):
        continue
    p = os.path.join(d, "SKILL.md")
    if not os.path.exists(p):
        fails.append(f"{name}: SKILL.md missing"); continue
    text = open(p, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fails.append(f"{name}: frontmatter missing"); continue
    fm = m.group(1)
    try:
        import yaml
        meta = yaml.safe_load(fm) or {}
    except ImportError:
        meta = dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", fm, re.M))
    desc = str(meta.get("description", "")).strip()
    if meta.get("name") != name:
        fails.append(f"{name}: frontmatter name '{meta.get('name')}' must match the folder")
    if not desc:
        fails.append(f"{name}: description missing")
    if len(desc) > 1024:
        fails.append(f"{name}: description is {len(desc)} characters (max 1024)")
    if re.search(r"<[^>]*>", desc):
        fails.append(f"{name}: description contains an XML or angle-bracket tag")
    for dp, _, files in os.walk(d):
        for fn in files:
            if not fn.endswith((".md", ".html", ".css", ".js", ".json", ".py")):
                continue
            fp = os.path.join(dp, fn)
            try:
                n = len(DASH.findall(open(fp, encoding="utf-8").read()))
            except Exception:
                continue
            if n:
                (warns if name in VENDORED else fails).append(f"{os.path.relpath(fp, root)}: {n} em or en dashes")

for f in fails: print("FAIL", f)
for w in warns: print("WARN", w)
print(f"{len(fails)} failures, {len(warns)} warnings")
sys.exit(1 if fails else 0)
