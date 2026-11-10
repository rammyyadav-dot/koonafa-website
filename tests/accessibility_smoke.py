"""Landing-page accessibility regressions (requires Python Playwright + Chromium).
Serve the repository first: python -m http.server 8000
Run: python tests/accessibility_smoke.py
Optional: BASE_URL, CHROMIUM_PATH, AXE_SCRIPT_PATH (path to axe-core's axe.min.js).
External assets are blocked deliberately to verify accessible fallback behavior.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = os.environ.get('BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
axe_path = os.environ.get('AXE_SCRIPT_PATH')
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'),
        args=['--no-sandbox'],
    )
    for name in ['index', 'global', 'GSA', 'DMC']:
        for width, motion in [(390, 'no-preference'), (320, 'reduce'), (1280, 'no-preference')]:
            page = browser.new_page(viewport={'width': width, 'height': 844}, reduced_motion=motion)
            page.route('https://**/*', lambda route: route.abort())
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'{BASE}/{name}.html', wait_until='load')
            assert page.locator('h1').count() == 1, (name, 'one H1')
            assert page.locator('main').count() == 1, (name, 'main landmark')
            assert page.locator('a[href="#"]').count() == 0
            page.locator('.skip-link').focus()
            page.keyboard.press('Enter')
            assert page.locator('main').evaluate('(el) => el === document.activeElement')
            trigger = page.locator('#hamburger,#menuToggle')
            if width < 1000:
                box = trigger.bounding_box()
                assert box['width'] >= 48 and box['height'] >= 48
                trigger.focus()
                page.keyboard.press('Enter')
                assert trigger.get_attribute('aria-expanded') == 'true'
                if name in ['index', 'global']:
                    close = page.locator('.mo-close,.mobile-menu-close')
                    assert page.locator('main').evaluate('(el) => el.inert')
                    assert close.evaluate('(el) => el === document.activeElement')
                    page.keyboard.press('Shift+Tab')
                    page.keyboard.press('Tab')
                    assert close.evaluate('(el) => el === document.activeElement')
                else:
                    page.keyboard.press('Tab')
                    assert page.locator('#nav a').first.evaluate('(el) => el === document.activeElement')
                page.keyboard.press('Escape')
                assert trigger.get_attribute('aria-expanded') == 'false'
                assert trigger.evaluate('(el) => el === document.activeElement')
                assert not page.locator('main').evaluate('(el) => el.inert')
            elif name in ['GSA', 'DMC']:
                assert not page.locator('#nav').evaluate('(el) => el.inert')
                assert page.locator('#nav a').first.is_visible()
            if motion == 'reduce':
                assert page.locator('.motion-control').is_disabled()
                assert page.evaluate('window.__siteMotionPaused')
                assert page.evaluate('Array.from(document.querySelectorAll("video")).every(v => v.paused)')
            else:
                page.locator('.motion-control').click()
                assert page.locator('.motion-control').get_attribute('aria-pressed') == 'true'
            if axe_path and width == 390:
                page.add_script_tag(content=Path(axe_path).read_text())
                report = page.evaluate("""async () => await axe.run(document, {
                    runOnly: {type:'tag', values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}
                })""")
                assert not report['violations'], [(v['id'], [n['target'] for n in v['nodes']]) for v in report['violations']]
            assert not errors, errors
            print(f'PASS {name} {width}px {motion}')
            page.close()
    browser.close()
