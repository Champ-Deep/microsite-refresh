#!/usr/bin/env python3
"""Print the brand colours in a logo so the page palette starts from the real brand.

  python3 logo_palette.py logo.png

Ignores transparent, near-white and near-black pixels. Use the first colour as the
primary accent and the second as the support colour; then darken either one until
text on the page background reaches 4.5:1 contrast (keep the pure logo hex for fills).
"""
import sys
from collections import Counter
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGBA")
im.thumbnail((300, 300))
c = Counter()
for r, g, b, a in (im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()):
    if a < 200 or max(r, g, b) < 50 or min(r, g, b) > 225:
        continue
    c[(r // 12 * 12, g // 12 * 12, b // 12 * 12)] += 1
total = sum(c.values()) or 1
picked = []
for (r, g, b), n in c.most_common(40):
    if all(abs(r - p[0]) + abs(g - p[1]) + abs(b - p[2]) > 90 for p, _ in picked):
        picked.append(((r, g, b), n))
    if len(picked) == 4:
        break
for (r, g, b), n in picked:
    print(f"#{r:02X}{g:02X}{b:02X}  {n / total:.0%} of coloured pixels")
