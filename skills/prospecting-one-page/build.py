#!/usr/bin/env python3
"""Build the explicitly selected prospecting sibling. Preview only, no dependencies."""
import argparse
import base64
import html
import json
from pathlib import Path
import re
from string import Template
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SECTIONS = ('overview', 'services', 'contact', 'about', 'privacy')
E = html.escape


def text(obj, key):
    value = obj.get(key) if isinstance(obj, dict) else None
    if not isinstance(value, str) or not value.strip() or len(value) > 6000:
        raise ValueError(f'Missing or invalid text: {key}')
    if any(c in value for c in ('\u2013', '\u2014')):
        raise ValueError(f'Forbidden dash: {key}')
    return value


def validate(site, source):
    for key in ('name', 'domain', 'email', 'logo', 'description'):
        text(site, key)
    url = urlsplit(site['domain'])
    if (url.scheme != 'https' or not url.hostname or url.username or url.password
            or url.query or url.fragment or url.path not in ('', '/')
            or re.search(r'[\s<>"\x00-\x1f\\]', site['domain'])):
        raise ValueError('Domain must be an absolute HTTPS origin without credentials')
    if not re.fullmatch(r'[A-Za-z0-9._+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', site['email']):
        raise ValueError('Invalid email')
    for section in SECTIONS:
        for key in ('title', 'body'):
            text(site.get(section), key)
    services = site['services'].get('items')
    if not isinstance(services, list) or not 1 <= len(services) <= 12:
        raise ValueError('Supply 1 to 12 services')
    for item in services:
        for key in ('title', 'body'):
            text(item, key)
    asset = (source / site['logo']).resolve()
    if (not asset.is_relative_to(source.resolve()) or asset.suffix.lower() != '.png'
            or not asset.is_file() or not asset.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')):
        raise ValueError('Logo must be a real PNG inside the input directory')
    return asset


def build(source, out):
    source, out = Path(source), Path(out)
    site = json.loads((source / 'site.json').read_text())
    asset = validate(site, source)
    values = {k: E(site[k]) for k in ('name', 'description', 'email')}
    for section in SECTIONS:
        for key in ('title', 'body'):
            values[f'{section}_{key}'] = E(site[section][key])
    values['logo'] = 'data:image/png;base64,' + base64.b64encode(asset.read_bytes()).decode()
    values['services_items'] = ''.join(
        f'<article class="service"><h3>{E(i["title"])}</h3><p>{E(i["body"])}</p></article>'
        for i in site['services']['items'])
    values['style'] = (ROOT / 'styles.css').read_text()
    page = Template((ROOT / 'template.html').read_text()).substitute(values)
    if any(c in html.unescape(page) for c in ('\u2013', '\u2014')):
        raise ValueError('Forbidden dash in rendered output')
    if out.resolve() == source.resolve() or out.resolve() in source.resolve().parents:
        raise ValueError('Output must not overwrite the input directory or an ancestor')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'index.html').write_text(page)
    (out / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    print(f'Built opt-in prospecting preview: {out / "index.html"}')
    return page


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.source, args.out)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Build refused: {error}\n')
