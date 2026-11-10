"""Synchronize the Global footer into content pages; keep the homepage/redirects intact.
Run from any directory: python scripts/sync_global_footer.py
The footer is static HTML, so standalone pages need no JavaScript to render it.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / 'components/global-footer.template').read_text().strip()
LINK = '<link rel="stylesheet" href="/global-footer.css">'
START = '<!-- SHARED GLOBAL FOOTER START -->'
END = '<!-- SHARED GLOBAL FOOTER END -->'

def synchronize():
    changed = []
    for path in sorted([*ROOT.glob('*.html'), *(ROOT / 'gsa').glob('*.html')]):
        if path == ROOT / 'index.html':
            continue
        old = path.read_text()
        if re.search(r'<meta[^>]+http-equiv=["\']refresh', old, re.I):
            continue
        html = re.sub(r'<section class="associations-strip">.*?</section>', '', old, flags=re.S)
        if START in html:
            html = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _: TEMPLATE, html, flags=re.S)
        elif re.search(r'<footer\b', html):
            html = re.sub(r'<footer\b[^>]*>.*?</footer>', lambda _: TEMPLATE, html, count=1, flags=re.S)
        else:
            html = html.replace('</body>', TEMPLATE + '\n</body>', 1)
        if LINK not in html:
            html = html.replace('</head>', LINK + '\n</head>', 1)
        if html != old:
            path.write_text(html)
            changed.append(str(path.relative_to(ROOT)))
    return changed

if __name__ == '__main__':
    files = synchronize()
    print(f'Synchronized {len(files)} content pages.')
