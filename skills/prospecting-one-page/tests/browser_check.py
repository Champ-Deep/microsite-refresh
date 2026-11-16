"""Exercise a served preview. Usage: python browser_check.py URL OUTPUT_DIR."""
import json
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

url, output = sys.argv[1], Path(sys.argv[2])
output.mkdir(parents=True, exist_ok=True)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    for width, height in [(375, 812), (768, 1024), (1440, 900)]:
        page = browser.new_page(viewport={'width': width, 'height': height})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        response = page.goto(url)
        assert response and response.ok
        page.evaluate('document.fonts.ready')
        assert page.locator('main section').count() == 5
        assert page.locator('h1').count() == 1
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert page.locator('img').evaluate_all('(images) => images.every(i => i.complete && i.naturalWidth > 0)')
        assert page.locator('a[href^="mailto:"]').get_attribute('href') == 'mailto:info@championsgroup.com'
        assert page.locator('script').count() == 0
        page.screenshot(path=str(output / f'enabled-{width}.png'), full_page=True)
        page.screenshot(path=str(output / f'fold-{width}.png'))
        page.keyboard.press('Tab')
        assert page.locator('.skip').evaluate('(el) => el === document.activeElement')
        page.keyboard.press('Enter')
        assert page.evaluate('document.activeElement.id') == 'overview'
        for section in ['services', 'contact', 'about', 'privacy']:
            page.locator(f'nav a[href="#{section}"]').click()
            assert page.evaluate('location.hash') == '#' + section
        page.emulate_media(reduced_motion='reduce')
        assert page.evaluate('getComputedStyle(document.documentElement).scrollBehavior') == 'auto'
        targets = page.locator('a').evaluate_all('(links) => links.map(el => ({text:el.textContent.trim(),height:el.getBoundingClientRect().height}))')
        assert all(t['height'] >= 44 for t in targets), targets
        assert not errors, errors
        results.append({'width': width, 'overflow': False, 'consoleErrors': errors, 'anchors': 4, 'skipLink': True, 'reducedMotion': True, 'targets': targets})
        page.close()
    browser.close()
(output / 'browser-results.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
