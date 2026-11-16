#!/usr/bin/env python3
"""Exercise the existing CTA kit. Writes portable enabled/disabled previews and screenshots.
Run: python3 skills/scroll-journey-kit/tests/browser_check.py --out /absolute/evidence
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
KIT = ROOT / 'skills/scroll-journey-kit/kit'
EFFECTS = ('magnetic', 'glow', 'shine', 'swap', 'underline')


def preview(enabled):
    rows = []
    for effect in EFFECTS:
        attr = f' data-mk="{effect}"' if enabled else ''
        rows.append(f'''<section><h2>{effect.title()}</h2><div class="controls">
<button id="{effect}"{attr}>Request sample</button>
<a id="{effect}-link" href="#result"{attr}>View details</a>
<button id="{effect}-disabled" disabled{attr}>Unavailable</button>
</div></section>''')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>LakeKit CTA verification</title><style>
/* Preserve LakeKit's navy, gold and purple tokens. This is a test fixture, not a new skin. */
*{box-sizing:border-box}body{margin:0;background:#011A6B;color:#fff;font:16px/1.5 Montserrat,Arial,sans-serif}
main{padding:32px clamp(20px,5vw,80px);max-width:1440px;margin:auto}h1{font-size:clamp(28px,4vw,48px);line-height:1.1;margin:0 0 16px}p{max-width:65ch;color:#fff}
section{border-top:1px solid #7A76DA;padding:16px 0;display:flex;align-items:center;justify-content:space-between;gap:16px}h2{font-size:18px;margin:0;color:#fff}
.controls{display:flex;gap:20px;align-items:center;flex-wrap:wrap}button,a{font:600 15px/1.3 Montserrat,Arial,sans-serif;min-height:44px;display:inline-flex;align-items:center;justify-content:center;border-radius:6px;padding:12px 16px;text-decoration:none}
button{background:#FFB703;color:#1A1400;border:1px solid #FFB703;cursor:pointer}a{color:#fff;border:1px solid #7A76DA}button:disabled{background:#011A6B;color:#B9C0E4;border-color:#7A76DA;cursor:not-allowed}
button:focus-visible,a:focus-visible{outline:2px solid currentColor;outline-offset:4px}output{display:block;color:#fff;padding:16px 0}
@media(max-width:767px){section{display:block}h2{margin-bottom:12px}.controls{gap:12px}main{padding-top:24px}}
''' + (KIT.joinpath('lakekit.css').read_text() if enabled else '') + '''</style></head><body><main>
<h1>Varied CTA interactions</h1><p>''' + ('Effects enabled through data-mk.' if enabled else 'Effects disabled. Plain host controls, unchanged actions.') + ''' Click, Tab and Enter work on every action. Space activates buttons.</p>
''' + ''.join(rows) + '''<section><h2>Default control</h2><button id="default">Request sample</button></section>
<output id="result" aria-live="polite">No action yet.</output></main><script>
window.actions={};document.querySelectorAll('button,a').forEach(function(el){
  el.addEventListener('click',function(){actions[el.id]=(actions[el.id]||0)+1;document.querySelector('output').textContent=el.id+': '+actions[el.id]+' activation(s).';});
});
</script>''' + ('<script>' + KIT.joinpath('lakekit.js').read_text() + '</script>' if enabled else '') + '</body></html>'


def check(page, base, enabled, reduced, touch, out):
    name = 'enabled' if enabled else 'disabled'
    page.goto(f'{base}/{name}.html')
    for effect in (*EFFECTS, 'default'):
        button = page.locator('#' + effect)
        button.tap() if touch else button.click()
        button.focus()
        page.keyboard.press('Enter')
        page.keyboard.press('Space')
        assert page.evaluate('(id)=>actions[id]', effect) == 3, effect
        assert button.evaluate('(e)=>e.matches(":focus-visible")'), effect
        assert button.evaluate('(e)=>getComputedStyle(e).outlineStyle') != 'none', effect
        if effect == 'default':
            assert button.inner_text() == 'Request sample'
            assert button.locator('*').count() == 0
            continue
        link = page.locator(f'#{effect}-link')
        link.tap() if touch else link.click()
        link.focus()
        page.keyboard.press('Enter')
        assert page.evaluate('(id)=>actions[id]', effect + '-link') == 2
        assert page.url.endswith('#result')
        assert link.get_attribute('href') == '#result'
        disabled = page.locator(f'#{effect}-disabled')
        disabled.dispatch_event('pointermove', {'clientX': 30, 'clientY': 30})
        disabled.hover(force=True)
        page.mouse.down()
        page.mouse.up()
        assert page.evaluate('(id)=>actions[id]||0', effect + '-disabled') == 0
        assert disabled.is_disabled()
        if enabled:
            assert disabled.evaluate('(e)=>getComputedStyle(e).translate') in ('none', '0px')
            if effect == 'shine':
                assert disabled.evaluate('(e)=>getComputedStyle(e,"::after").animationName') == 'none'
    # Use Tab, not just programmatic focus, and preserve author-provided names.
    page.goto(f'{base}/{name}.html')
    page.keyboard.press('Tab')
    assert page.locator('#magnetic').evaluate('(e)=>e===document.activeElement')
    if enabled:
        page.locator('#magnetic').hover(position={'x': 8, 'y': 8})
        mx = page.locator('#magnetic').evaluate('(e)=>e.style.getPropertyValue("--mx")')
        assert bool(mx) == (not reduced and not touch), (reduced, touch, mx)
        page.keyboard.press('Tab')
        page.locator('#magnetic').focus()
        page.wait_for_function('getComputedStyle(document.querySelector("#magnetic")).translate === "none"')
        page.locator('#shine').focus()
        assert page.locator('#shine').evaluate('(e)=>getComputedStyle(e,"::after").animationName') == ('none' if reduced else 'mkSpin')
        page.locator('#underline').focus()
        page.wait_for_function('getComputedStyle(document.querySelector("#underline")).backgroundSize === "100% 2px"')
        assert page.locator('#glow .mk-g').count() == 2
        page.locator('#glow').focus()
        page.wait_for_timeout(300)
        assert page.locator('#glow .mk-g').first.evaluate('(e)=>getComputedStyle(e).display') == ('none' if reduced or touch else 'block')
        assert float(page.locator('#glow .mk-g').first.evaluate('(e)=>getComputedStyle(e).opacity')) <= .5
        assert page.locator('#swap .mk-sw').count() == (0 if reduced else 1)
        assert page.locator('#underline').evaluate('(e)=>getComputedStyle(e).backgroundColor') == 'rgb(255, 183, 3)'
        assert page.get_by_role('button', name='Request sample', exact=True).count() == 6
        for attrs, expected in [('aria-label="Custom sample"', 'Custom sample'), ('aria-labelledby="label"', 'Named sample')]:
            page.set_content(f'<span id="label">Named sample</span><button data-mk="swap" {attrs}>Sample</button>')
            page.add_script_tag(content=KIT.joinpath('lakekit.js').read_text())
            assert page.get_by_role('button', name=expected, exact=True).count() == 1
        page.set_content('<form><button type="submit" data-mk="shine">Submit</button></form><script>window.submits=0;document.querySelector("form").onsubmit=function(e){e.preventDefault();submits++;}</script>')
        page.add_script_tag(content=KIT.joinpath('lakekit.js').read_text())
        page.get_by_role('button').click()
        page.get_by_role('button').press('Enter')
        assert page.evaluate('submits') == 2
    page.goto(f'{base}/{name}.html')
    for width in (375, 768, 1440):
        page.set_viewport_size({'width': width, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('button,a').evaluate_all('(els)=>els.every(e=>e.getBoundingClientRect().height>=44)')
        if not reduced and not touch:
            page.screenshot(path=str(out / f'{name}-{width}.png'), full_page=True)
    if touch:
        page.set_viewport_size({'width': 375, 'height': 900})
        page.screenshot(path=str(out / f'{name}-touch-375.png'), full_page=True)
    if enabled and not touch:
        page.set_viewport_size({'width': 1440, 'height': 900})
        for effect in EFFECTS:
            page.locator('#' + effect).focus()
            page.wait_for_timeout(900)
            page.locator('main').screenshot(path=str(out / f'{effect}-{"reduced" if reduced else "focus"}.png'))
        if not reduced:
            page.locator('#default').click()
            for effect in EFFECTS:
                page.locator('#' + effect).hover(position={'x': 8, 'y': 8})
                page.wait_for_timeout(900)
                page.locator('main').screenshot(path=str(out / f'{effect}-hover.png'))
            page.emulate_media(reduced_motion='reduce')
            page.locator('#swap').focus()
            assert page.locator('#swap .mk-l>span').first.evaluate('(e)=>getComputedStyle(e).transform') == 'none'
            page.locator('#shine').focus()
            assert page.locator('#shine').evaluate('(e)=>getComputedStyle(e,"::after").animationName') == 'none'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for ext in ('css', 'js'):
        canonical = KIT.joinpath('lakekit.' + ext).read_text().strip()
        assert canonical == ROOT.joinpath('skills/venture-story/vendor/lakekit.' + ext).read_text().strip()
        assert canonical in KIT.joinpath('lakekit-demo.html').read_text()
    for enabled in (True, False):
        (out / ('enabled.html' if enabled else 'disabled.html')).write_text(preview(enabled))
    server = None
    for port in range(3100, 3200):
        try:
            server = ThreadingHTTPServer(('127.0.0.1', port), partial(SimpleHTTPRequestHandler, directory=str(out)))
            break
        except OSError:
            continue
    assert server is not None, 'No free preview port in 3100..3199'
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    errors = []
    cases = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for enabled in (True, False):
                for reduced, touch in ((False, False), (True, False), (False, True)):
                    context = browser.new_context(reduced_motion='reduce' if reduced else 'no-preference', has_touch=touch, is_mobile=touch)
                    page = context.new_page()
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('console', lambda message: errors.append(message.text) if message.type == 'error' else None)
                    check(page, base, enabled, reduced, touch, out)
                    cases.append({'enabled': enabled, 'reduced': reduced, 'touch': touch, 'passed': True})
                    context.close()
            browser.close()
        assert not errors, errors
        result = {'cases': cases, 'console_errors': errors, 'preview_url': base, 'server_stopped_on_exit': True}
        (out / 'results.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    main()
