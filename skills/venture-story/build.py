#!/usr/bin/env python3
"""Build the opt-in four-ecosystem homepage. Standard library only, fully inline output."""
import argparse
import base64
import html
import json
import math
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent
E = html.escape


def multiline(text):
    return E(text).replace('\n', '<br>')


def safe_url(value):
    if not isinstance(value, str) or re.search(r'[\s<>"\x00-\x1f]', value):
        raise ValueError('URLs must not contain whitespace, control characters or markup')
    p = urlsplit(value)
    if p.scheme != 'https' or not p.hostname or p.username or p.password:
        raise ValueError('Only absolute HTTPS URLs without embedded credentials are allowed')
    return value


def validate(site, source):
    """Fail closed on shape, identifiers, destinations, local asset escape and CSS injection."""
    def text(obj, key):
        value = obj.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > 3000:
            raise ValueError(f'Missing or invalid text: {key}')
        if '\u2014' in value or '\u2013' in value:
            raise ValueError(f'Forbidden dash in {key}')
    for key in ['name', 'domain', 'email', 'logo', 'accent', 'accentText', 'tagline', 'chaptersTitle', 'chaptersIntro']:
        text(site, key)
    safe_url(site['domain'])
    if not re.fullmatch(r'[A-Za-z0-9._+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', site['email']):
        raise ValueError('Invalid email')
    for color in ['accent', 'accentText']:
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', site[color]):
            raise ValueError('Colors must be six-digit hex')
    asset = (source / site['logo']).resolve()
    if not asset.is_relative_to(source.resolve()) or asset.suffix.lower() != '.png' or not asset.is_file():
        raise ValueError('Logo must be an existing PNG inside the input directory')
    if not asset.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Logo is not a PNG')
    fields = {
        'hero': ['eyebrow', 'title', 'emphasis', 'description', 'primary', 'secondary', 'sceneLabel', 'sceneNote'],
        'intro': ['eyebrow', 'title', 'description'],
        'proof': ['eyebrow', 'title', 'description', 'source', 'url', 'link'],
        'directory': ['eyebrow', 'title', 'description', 'filterLabel', 'allLabel', 'action', 'inquiry'],
        'contact': ['eyebrow', 'title', 'description', 'primary'],
    }
    for section, keys in fields.items():
        if not isinstance(site.get(section), dict):
            raise ValueError(f'Missing section {section}')
        for key in keys:
            text(site[section], key)
    safe_url(site['proof']['url'])
    groups = site.get('groups')
    if not isinstance(groups, list) or len(groups) != 4:
        raise ValueError('This narrative requires exactly four ecosystems')
    ids, names = set(), set()
    for g in groups:
        for key in ['id', 'label', 'short', 'visual', 'title', 'description', 'footnote']:
            text(g, key)
        if not re.fullmatch(r'[a-z][a-z0-9-]*', g['id']) or g['id'] in ids:
            raise ValueError('Ecosystem IDs must be unique lowercase slugs')
        ids.add(g['id'])
        if g['visual'] not in ['network', 'steps', 'rings', 'architecture']:
            raise ValueError('Unknown visual preset')
        for k in ['value', 'label']:
            text(g.get('metric', {}), k)
        if not isinstance(g.get('ventures'), list) or not g['ventures']:
            raise ValueError('Each ecosystem needs at least one venture')
        for v in g['ventures']:
            for k in ['name', 'description']:
                text(v, k)
            if v['name'] in names:
                raise ValueError('Duplicate venture name')
            names.add(v['name'])
            if v.get('url') is not None:
                safe_url(v['url'])
    if not isinstance(site['proof'].get('metrics'), list) or len(site['proof']['metrics']) != 3:
        raise ValueError('Proof requires three attributed metrics')
    for m in site['proof']['metrics']:
        for k in ['value', 'label', 'note']:
            text(m, k)
    cities = site['contact'].get('cities')
    if not isinstance(cities, list) or not cities or not all(isinstance(c, str) and c for c in cities):
        raise ValueError('Contact requires city names')
    return asset


def svg_wrap(body, suffix, view='0 0 600 460'):
    return f'''<svg class="diagram" viewBox="{view}" fill="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="white-{suffix}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#f2e5db"/></linearGradient>
    <linearGradient id="orange-{suffix}" x1="0" y1="0" x2="1" y2="1"><stop stop-color="var(--material-light)"/><stop offset=".55" stop-color="var(--accent)"/><stop offset="1" stop-color="var(--material-dark)"/></linearGradient>
    <linearGradient id="side-{suffix}" x1="0" y1="0" x2="1" y2="0"><stop stop-color="var(--material-dark)"/><stop offset="1" stop-color="var(--accent)"/></linearGradient>
    </defs>{body}</svg>'''


def hero_diagram(groups):
    # Four stacked architectural planes, rather than mock UI panels or a fake brand mark.
    body = '<g class="hero-grid" stroke="#ece5de" stroke-width="1">'
    for n in range(-4, 5):
        body += f'<path d="M{300+n*42-200} 430l300 150M{300+n*42+200} 430l-300 150"/>'
    body += '</g><ellipse cx="300" cy="490" rx="180" ry="49" fill="#eee0d5" opacity=".45"/>'
    for i in reversed(range(4)):
        y = 70 + i * 72
        orange = i == 1
        fill = 'orange' if orange else 'white'
        side = f'url(#side-hero)' if orange else '#e4d3c5'
        body += f'''<g class="hero-layer hero-layer-{i}">
        <path d="M110 {y+105}L300 {y+210}L490 {y+105}v17L300 {y+227}L110 {y+122}Z" fill="{side}" stroke="#cdae97" stroke-width=".6"/>
        <path d="M300 {y}L490 {y+105}L300 {y+210}L110 {y+105}Z M300 {y+49}L400 {y+105}L300 {y+161}L200 {y+105}Z" fill="url(#{fill}-hero)" fill-rule="evenodd" stroke="{'#ad4d1d' if orange else '#dcc7b6'}" stroke-width="1"/>
        <path d="M300 {y+11}L471 {y+105}L300 {y+199}L129 {y+105}Z" stroke="{'#ffd4b3' if orange else '#fff'}" stroke-width="1"/>
        <path d="M300 {y+49}v12L389 {y+110}L400 {y+105}" fill="{'#b45121' if orange else '#e8d7c8'}"/>
        </g>'''
    body += '<g class="hero-axis"><path d="M300 40v432" stroke="#c9865d" stroke-dasharray="3 5"/><circle cx="300" cy="42" r="5" fill="var(--accent)"/><circle cx="300" cy="473" r="5" fill="var(--accent)"/></g>'
    # Labels remain horizontal for legibility.
    positions = [(485, 150, 590, 124), (110, 250, 10, 228), (490, 350, 590, 323), (110, 425, 10, 459)]
    for i, (x, y, tx, ty) in enumerate(positions):
        right = tx > 300
        anchor = 'end' if right else 'start'
        end = tx - 4 if right else tx + 4
        body += f'''<g class="hero-label"><path d="M{x} {y}H{end}V{ty+12}" stroke="#baa99b"/><circle cx="{x}" cy="{y}" r="3" fill="var(--accent)"/><text x="{tx}" y="{ty}" text-anchor="{anchor}" class="node-label">{E(groups[i]['short'])}</text><text x="{tx}" y="{ty-17}" text-anchor="{anchor}" class="small-text">0{i+1}</text></g>'''
    return svg_wrap(body, 'hero', '0 0 600 590')


def scene(group, i):
    suffix = str(i)
    kind = group['visual']
    body = '<ellipse cx="300" cy="375" rx="196" ry="44" fill="#eee6dc" opacity=".65"/>'
    if kind == 'network':
        body += '<g class="visual-unit"><ellipse cx="300" cy="235" rx="207" ry="146" stroke="#e0d4c8"/><ellipse cx="300" cy="235" rx="154" ry="105" stroke="#e0d4c8" stroke-dasharray="2 7"/>'
        pts = [(110, 165), (487, 158), (113, 312), (490, 310)]
        for j, (x, y) in enumerate(pts):
            body += f'<path class="draw-path" d="M300 235Q{x} 235 {x} {y}" stroke="var(--accent)" stroke-width="1.5"/>'
            body += f'<g class="scene-node"><circle cx="{x}" cy="{y}" r="27" fill="#fff" stroke="#d7c3b1"/><circle cx="{x}" cy="{y}" r="6" fill="var(--accent)"/><text x="{x}" y="{y+49}" text-anchor="middle" class="small-text">0{j+1}</text></g>'
        for k in range(24):
            a = k*math.pi/12
            x, y = 300 + 207*math.cos(a), 235 + 146*math.sin(a)
            body += f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.3" fill="#9a8472"/>'
        body += f'<path d="M300 141l88 50v95l-88 50-88-50v-95Z" fill="url(#orange-{suffix})" stroke="#c66c37"/><path d="M212 191l88 50 88-50M300 241v95" stroke="#fff0db"/><path d="M300 141v100" stroke="#fff0db" opacity=".45"/></g>'
    elif kind == 'steps':
        for j in range(4):
            x, y = 80+j*95, 275-j*47
            body += f'''<g class="step-block visual-unit"><path d="M{x} {y}l80 42 80-42v{65+j*15}l-80 42-80-42Z" fill="{'#eddfd0' if j<3 else '#cf581e'}" stroke="#c5ab95"/><path d="M{x} {y}l80-42 80 42-80 42Z" fill="url(#{'white' if j<3 else 'orange'}-{suffix})" stroke="#c5ab95"/><path d="M{x+80} {y+42}v{65+j*15}" stroke="#c5ab95"/><text x="{x+80}" y="{y+5}" text-anchor="middle" class="small-text">0{j+1}</text></g>'''
        # Keep the arrowhead in the scrubbed path so it cannot float ahead of the line.
        body += '<path class="draw-path" d="M110 230C150 60 380 90 470 43l-14-2 14 2-5 13" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    elif kind == 'rings':
        for j, (x, y) in enumerate([(225, 205), (375, 205), (300, 318)]):
            body += f'<g class="well-ring visual-unit"><ellipse cx="{x}" cy="{y+14}" rx="102" ry="83" stroke="#c89574" stroke-width="22"/><ellipse cx="{x}" cy="{y}" rx="102" ry="83" stroke="url(#orange-{suffix})" stroke-width="22"/><ellipse cx="{x}" cy="{y-1}" rx="102" ry="83" stroke="#ffd9ba" stroke-width="1"/><circle cx="{x}" cy="{y}" r="4" fill="#c26634"/></g>'
    else:
        for j in reversed(range(4)):
            x, y = 105+j*70, 156-j*26
            body += f'''<g class="arch-unit visual-unit"><path d="M{x} {y+210}v-210l100-55 100 55v210l-28 16V{y+20}l-72-40-72 40v206Z" fill="url(#{'orange' if j==0 else 'white'}-{suffix})" fill-rule="evenodd" stroke="#bfa28b"/><path d="M{x+100} {y-55}v35M{x+200} {y}l-28 20M{x} {y}l28 20" stroke="#d9b99e"/></g>'''
        body += '<path class="draw-path" d="M70 394L315 257L535 384" stroke="var(--accent)" stroke-width="1.5"/>'
    return svg_wrap(body, suffix)


def render(site, source):
    logo = validate(site, source)
    groups = site['groups']
    total = sum(len(g['ventures']) for g in groups)
    tokens = {'NAME': E(site['name']), 'TAGLINE': E(site['tagline']), 'EMAIL': E(site['email']), 'ACCENT': site['accent'], 'ACCENT_TEXT': site['accentText'], 'VENTURE_COUNT': str(total), 'GROUP_COUNT': str(len(groups)), 'META_DESCRIPTION': E(site['hero']['description'])}
    for section, mapping in {
        'hero': {'eyebrow':'HERO_EYEBROW','title':'HERO_TITLE','emphasis':'HERO_EMPHASIS','description':'HERO_DESCRIPTION','primary':'PRIMARY','secondary':'SECONDARY','sceneLabel':'SCENE_LABEL','sceneNote':'SCENE_NOTE'},
        'intro': {'eyebrow':'INTRO_EYEBROW','title':'INTRO_TITLE','description':'INTRO_DESCRIPTION'},
        'proof': {'eyebrow':'PROOF_EYEBROW','title':'PROOF_TITLE','description':'PROOF_DESCRIPTION','source':'PROOF_SOURCE','url':'PROOF_URL','link':'PROOF_LINK'},
        'directory': {'eyebrow':'DIRECTORY_EYEBROW','title':'DIRECTORY_TITLE','description':'DIRECTORY_DESCRIPTION','filterLabel':'FILTER_LABEL','allLabel':'ALL_LABEL'},
        'contact': {'eyebrow':'CONTACT_EYEBROW','title':'CONTACT_TITLE','description':'CONTACT_DESCRIPTION','primary':'CONTACT_PRIMARY'},
    }.items():
        tokens.update({target: multiline(site[section][key]) for key,target in mapping.items()})
    tokens['CHAPTERS_TITLE'] = multiline(site['chaptersTitle'])
    tokens['CHAPTERS_INTRO'] = E(site['chaptersIntro'])
    tokens['LOGO'] = 'data:image/png;base64,' + base64.b64encode(logo.read_bytes()).decode()
    tokens['FONT_URI'] = 'data:font/woff2;base64,' + base64.b64encode((ROOT/'vendor/inter-latin.woff2').read_bytes()).decode()
    tokens['HERO_SVG'] = hero_diagram(groups)
    chapters, nav, filters, ventures = [], [], [], []
    n = 0
    for i,g in enumerate(groups):
        gid = E(g['id'])
        chapters.append(f'''<article class="chapter" id="chapter-{gid}" data-chapter="{i}" aria-labelledby="title-{gid}">
        <div class="chapter-copy"><p class="chapter-number"><span>0{i+1}</span> {E(g['label'])}</p><h3 id="title-{gid}">{multiline(g['title'])}</h3><p>{E(g['description'])}</p>
        <div class="chapter-metric"><b>{E(g['metric']['value'])}</b><span>{E(g['metric']['label'])}</span></div>
        <a class="text-link" href="#portfolio" data-show-group="{gid}">Meet the {len(g['ventures'])} {'ventures' if len(g['ventures'])!=1 else 'venture'} <span aria-hidden="true">↗</span></a></div>
        <div class="chapter-visual">{scene(g,i)}<p class="diagram-caption">{E(g['footnote'])}</p></div></article>''')
        nav.append(f'<button type="button" data-chapter-jump="{i}" aria-controls="chapter-{gid}"><span class="tab-number">0{i+1}</span>{E(g["short"])}</button>')
        filters.append(f'<button type="button" data-filter="{gid}" aria-pressed="false">{E(g["short"])} <span>{len(g["ventures"])}</span></button>')
        for v in g['ventures']:
            n += 1
            target = v.get('url') or f'mailto:{site["email"]}?subject={quote("Inquiry: " + v["name"])}'
            action = site['directory']['action' if v.get('url') else 'inquiry']
            ventures.append(f'''<details class="venture" data-group="{gid}" data-mk="spot"><summary><span class="num">{n:02}</span><span class="venture-name">{E(v['name'])}</span><span class="category">{E(g['label'])}</span><span class="expand" aria-hidden="true">+</span></summary><div class="venture-body"><p>{E(v['description'])}</p><a href="{E(target)}" aria-label="{E(action)}: {E(v['name'])}">{E(action)} <span aria-hidden="true">↗</span></a></div></details>''')
    tokens.update(CHAPTERS='\n'.join(chapters), CHAPTER_NAV=''.join(nav), FILTERS=''.join(filters), VENTURES='\n'.join(ventures))
    tokens['METRICS'] = ''.join(f'<div class="metric"><b>{E(m["value"])}</b><h3>{E(m["label"])}</h3><p>{E(m["note"])}</p></div>' for m in site['proof']['metrics'])
    tokens['CITIES'] = ''.join(f'<span>{E(c)}</span>' for c in site['contact']['cities'])
    def expand(s):
        return re.sub(r'\{\{([A-Z_]+)\}\}', lambda m: tokens[m[1]], s)
    tokens['PAGE_CSS'] = expand((ROOT/'styles.css').read_text())
    for token,filename in [('KIT_CSS','vendor/lakekit.css'),('KIT_JS','vendor/lakekit.js'),('GSAP','vendor/gsap.min.js'),('SCROLLTRIGGER','vendor/ScrollTrigger.min.js'),('PAGE_JS','motion.js')]:
        tokens[token] = (ROOT/filename).read_text()
    tokens['FONT_CSS'] = ''
    result = expand((ROOT/'template.html').read_text())
    if '{{' in result and re.search(r'\{\{[A-Z_]+\}\}',result):
        raise ValueError('Unresolved template token')
    return result


def build(source, out):
    source, out = Path(source).resolve(), Path(out).resolve()
    site = json.loads((source/'site.json').read_text())
    result = render(site, source)
    handoff = out/'handoff'
    handoff.mkdir(parents=True, exist_ok=True)
    (handoff/'index.html').write_text(result)
    (out/'artifact.html').write_text(result)
    lines = [f'# {site["name"]}', site['tagline'], '', site['hero']['title']+' '+site['hero']['emphasis'], site['hero']['description']]
    for g in site['groups']:
        lines += ['', '## '+g['label'], g['description']]
        for v in g['ventures']:
            lines += [f'- {v["name"]}: {v["description"]}' + (f' {v["url"]}' if v.get('url') else '')]
    lines += ['', '## Scale', site['proof']['description']]
    lines += [f'- {m["value"]} {m["label"]}: {m["note"]}' for m in site['proof']['metrics']]
    lines += ['', site['proof']['source'], '', '## Contact', site['email'], '', '## Review notes'] + site.get('reviewNotes', [])
    (handoff/'index.md').write_text('\n'.join(lines)+'\n')
    (handoff/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (handoff/'llms.txt').write_text(f'# {site["name"]} design concept\n\nNot the live website. Preview only.\n\n- [Content](index.md)\n')
    (handoff/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>\n')
    (out/'build-report.json').write_text(json.dumps({'template':'venture-story','groups':len(site['groups']),'ventures':sum(len(g['ventures']) for g in site['groups']),'html_bytes':len(result.encode()),'sources':site.get('sources',[]),'reviewNotes':site.get('reviewNotes',[]),'preview_only':True},indent=2)+'\n')
    print(json.dumps({'artifact':str(out/'artifact.html'),'bytes':len(result.encode()),'handoff':str(handoff)}))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path,help='Directory holding site.json and the local PNG logo')
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    try:
        build(args.source,args.out)
    except (ValueError,KeyError,TypeError,OSError) as e:
        p.exit(1,f'Build refused: {e}\n')
