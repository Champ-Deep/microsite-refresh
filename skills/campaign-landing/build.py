#!/usr/bin/env python3
"""Build a SPAN campaign landing page from site.json. Standard library only, one inline HTML file.

Usage: python3 build.py examples/span-peo-eor --out /abs/path/artifact.html
"""
import argparse
import base64
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
E = html.escape
DASH = re.compile('[\u2013\u2014]')
GLOBE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
         '<path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>')


def safe_url(value, allow_tel=False):
    if not isinstance(value, str) or re.search(r'[\s<>"\x00-\x1f]', value):
        raise ValueError('URL contains whitespace, control characters or markup: %r' % value)
    if allow_tel and value.startswith('tel:'):
        return value
    p = urlsplit(value)
    if p.scheme != 'https' or not p.hostname or p.username or p.password:
        raise ValueError('Only absolute HTTPS URLs without credentials: %r' % value)
    return value


def walk_strings(obj, path='site'):
    """Every string in the contract: no dashes, nothing empty."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk_strings(v, path + '.' + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk_strings(v, '%s[%d]' % (path, i))
    elif isinstance(obj, str):
        if DASH.search(obj):
            raise ValueError('Forbidden dash in ' + path)
        if not obj.strip() and not path.endswith('.href'):
            raise ValueError('Empty text in ' + path)


def validate(site, source):
    walk_strings(site)
    for key in ['brand', 'meta', 'headlines', 'hero', 'form', 'band', 'clients', 'compare',
                'account', 'dossier', 'faq', 'closer', 'footer', 'tracking']:
        if key not in site:
            raise ValueError('Missing section ' + key)
    safe_url(site['brand']['domain'])
    safe_url(site['brand']['privacyUrl'])
    safe_url(site['meta']['canonical'])
    logo = (source / site['brand']['logo']).resolve()
    if not logo.is_relative_to(source.resolve()) or not logo.is_file() or \
            not logo.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Logo must be a PNG inside the source directory')
    for side in ('left', 'right'):
        s = site['compare'][side]
        if not s['items'] or any(int(i['count']) <= 0 for i in s['items']):
            raise ValueError('compare.%s needs positive counts' % side)
        if sum(int(i['count']) for i in s['items']) > int(s['total']):
            raise ValueError('compare.%s items exceed the stated total' % side)
    if len(site['band']) != 4:
        raise ValueError('band needs exactly four counters')
    for src in site['hero']['sources'] + site['account']['sources']:
        safe_url(src['url'])
    for col in site['footer']['columns']:
        for item in col['items']:
            if item.get('href'):
                safe_url(item['href'], allow_tel=True)
    if len(site['faq']['items']) != 5:
        raise ValueError('faq.items needs exactly five entries (the sixth tile is the ask)')


def fav(domain):
    return ('<span class="fav">%s<img src="https://www.google.com/s2/favicons?domain=%s&amp;sz=64" '
            'width="22" height="22" alt="" loading="lazy" onerror="this.remove()"></span>') % (GLOBE, E(domain))


def sources(id_, items, label):
    stack = ''.join(fav(i['domain']) for i in items)
    rows = ''.join(
        '<li><a href="%s" target="_blank" rel="noopener">%s<span><b>%s</b><small>%s</small></span></a></li>'
        % (E(i['url']), fav(i['domain']), E(i['title']), E(i['snippet'])) for i in items)
    return ('<div class="srcs" id="%s"><button type="button" class="srcs__btn" aria-expanded="false" aria-controls="%s-list">'
            '<span class="srcs__stack">%s</span><span>%s</span>'
            '<svg class="srcs__chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg></button>'
            '<div class="srcs__list" id="%s-list"><ul>%s</ul></div></div>') % (id_, id_, stack, E(label), id_, rows)


def compare_rows(side):
    items = [(i['name'], int(i['count']), False) for i in side['items']]
    other = int(side['total']) - sum(c for _, c, _ in items)
    if other > 0:
        items.append((side['otherLabel'], other, True))
    mx = max(c for _, c, _ in items)
    out = ''
    for name, count, is_all in items:
        out += ('        <button type="button" class="row%s" data-seg="%s" data-label="%s" style="--w:%s%%">'
                '<span>%s</span><b>%s</b><i></i></button>\n') % (
            ' row--all' if is_all else '', E(side['segment']), E(name),
            round(count / mx * 50, 2), E(name), format(count, ','))
    return out


def render(site, source):
    tick = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>'
    logo = 'data:image/png;base64,' + base64.b64encode((source / site['brand']['logo']).read_bytes()).decode()
    headlines = dict(site['headlines'].get('variants', {}))
    d = site['dossier']
    cols = ''
    for col in d['columns']:
        rows = ''.join('            <div class="srow"><span>%s</span><b>%s</b>%s</div>\n' % (
            E(r['label']), E(r['value']),
            '<span class="ok">%s</span>' % E(d['verifiedLabel']) if r.get('verified') else '') for r in col['rows'])
        cols += '          <div class="dcol">\n            <h3>%s</h3>\n%s          </div>\n' % (E(col['title']), rows)
    faq = ''
    for n, item in enumerate(site['faq']['items'], 1):
        faq += ('        <article>\n          <span class="faq__n">%02d</span>\n          <h3>%s</h3>\n'
                '          <p class="faq__lead">%s</p>\n          <p>%s</p>\n        </article>\n') % (
            n, E(item['q']), E(item['lead']), E(item['detail']))
    fcols = ''
    for col in site['footer']['columns']:
        lis = ''.join('<li>%s</li>' % (
            '<a href="%s">%s</a>' % (E(i['href']), E(i['label'])) if i.get('href') else E(i['label'])) for i in col['items'])
        fcols += '    <nav class="hwf__col" aria-label="%s">\n      <h3>%s</h3>\n      <ul>%s</ul>\n    </nav>\n' % (
            E(col['title']), E(col['title']), lis)
    v = {
        'logo': logo,
        'brand.name': E(site['brand']['name']), 'brand.domain': E(site['brand']['domain']),
        'brand.phone': E(site['brand']['phone']), 'brand.phoneHref': E(site['brand']['phoneHref']),
        'brand.privacyUrl': E(site['brand']['privacyUrl']),
        'meta.title': E(site['meta']['title']), 'meta.description': E(site['meta']['description']),
        'meta.canonical': E(site['meta']['canonical']),
        'headlines.default': E(site['headlines']['default']), 'headlines.json': json.dumps(headlines),
        'hero.eyebrow': E(site['hero']['eyebrow']), 'hero.lede': E(site['hero']['lede']),
        'hero.ledeEmphasis': E(site['hero']['ledeEmphasis']),
        'hero.ticks': ''.join('        <li>%s%s</li>\n' % (tick, E(t)) for t in site['hero']['ticks']),
        'hero.callout.lead': E(site['hero']['callout']['lead']), 'hero.callout.text': E(site['hero']['callout']['text']),
        'hero.callout.link': E(site['hero']['callout']['link']),
        'hero.sources': sources('sources', site['hero']['sources'], site['hero']['sourcesLabel']),
        'form.title': E(site['form']['title']), 'form.sub': E(site['form']['sub']),
        'form.subChosenJson': json.dumps(site['form']['subChosen']),
        'form.segments': ''.join('                <option>%s</option>\n' % E(x) for x in site['form']['segments'])
                         + '                <option>%s</option>\n' % E(site['form']['specific']),
        'form.specificJson': json.dumps(site['form']['specific']),
        'form.providerPlaceholder': E(site['form']['providerPlaceholder']),
        'form.consent': E(site['form']['consent']), 'form.submit': E(site['form']['submit']),
        'form.sticky': E(site['form']['sticky']), 'form.foot': E(site['form']['foot']),
        'form.thanksTitle': E(site['form']['thanksTitle']), 'form.thanksText': E(site['form']['thanksText']),
        'band': ''.join('    <div class="band__n"><b>%s</b><span>%s</span></div>\n' % (E(b['value']), E(b['label'])) for b in site['band']),
        'clients.label': E(site['clients']['label']),
        'clients.names': '    ' + ''.join('<span>%s</span>' % E(n) for n in site['clients']['names']) + '\n',
        'compare.title': E(site['compare']['title']), 'compare.sub': E(site['compare']['sub']),
        'compare.rangeLabel': E(site['compare']['rangeLabel']), 'compare.rangeAria': E(site['compare']['rangeAria']),
        'compare.note': E(site['compare']['note']),
        'account.title': E(site['account']['title']), 'account.lede': E(site['account']['lede']),
        'account.groups': ''.join('          <li>%s</li>\n' % E(g) for g in site['account']['groups']),
        'account.fit': E(site['account']['fit']),
        'account.sources': sources('sources2', site['account']['sources'], site['account']['sourcesLabel']),
        'dossier.title': E(d['title']), 'dossier.tag': E(d['tag']), 'dossier.providerLabel': E(d['providerLabel']),
        'dossier.provider': E(d['provider']), 'dossier.columns': cols, 'dossier.footer': E(d['footer']),
        'faq.title': E(site['faq']['title']), 'faq.sub': E(site['faq']['sub']), 'faq.items': faq,
        'faq.ask.title': E(site['faq']['ask']['title']), 'faq.ask.text': E(site['faq']['ask']['text']),
        'faq.ask.button': E(site['faq']['ask']['button']),
        'closer.title': E(site['closer']['title']), 'closer.text': E(site['closer']['text']),
        'closer.button': E(site['closer']['button']), 'closer.small': E(site['closer']['small']),
        'footer.wordmark': E(site['footer']['wordmark']), 'footer.wordmarkJson': json.dumps(site['footer']['wordmark']),
        'footer.meta': E(site['footer']['meta']), 'footer.columns': fcols,
        'tracking.offerJson': json.dumps(site['tracking']['offer']), 'tracking.campaignJson': json.dumps(site['tracking']['campaign']),
        'tracking.formJson': json.dumps(site['tracking']['form']), 'tracking.conversionJson': json.dumps(site['tracking']['conversionLabel']),
    }
    for side in ('left', 'right'):
        s = site['compare'][side]
        v['compare.%s.name' % side] = E(s['name'])
        v['compare.%s.total' % side] = format(int(s['total']), ',')
        v['compare.%s.rows' % side] = compare_rows(s)
    template = (ROOT / 'template.html').read_text(encoding='utf-8')
    out = re.sub(r'\{\{([a-zA-Z.]+)\}\}', lambda m: v[m.group(1)], template)
    if DASH.search(out):
        raise ValueError('Dash in built output')
    return out


def build(source, out):
    source = Path(source)
    site = json.loads((source / 'site.json').read_text(encoding='utf-8'))
    validate(site, source)
    text = render(site, source)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding='utf-8')
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path, help='Directory holding site.json and the PNG logo')
    p.add_argument('--out', type=Path, required=True, help='Path of the HTML file to write')
    a = p.parse_args()
    build(a.source, a.out)
    print('built', a.out)
