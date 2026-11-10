"""Validate the shared Global footer without changing the homepage.
Serve the repository, then run BASE_URL=http://127.0.0.1:8000 python tests/global_footer_smoke.py.
Requires Python Playwright and Chromium. AXE_SCRIPT_PATH optionally enables WCAG checks.
"""
from pathlib import Path
import os,re
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('BASE_URL','http://127.0.0.1:8000').rstrip('/')
template=(ROOT/'components/global-footer.template').read_text().strip()
pages=[]
for path in sorted([*ROOT.glob('*.html'),*(ROOT/'gsa').glob('*.html')]):
    if path.name=='index.html' and path.parent==ROOT:continue
    html=path.read_text()
    if re.search(r'<meta[^>]+http-equiv=["\']refresh',html,re.I):continue
    block=re.search(r'<!-- SHARED GLOBAL FOOTER START -->.*?<!-- SHARED GLOBAL FOOTER END -->',html,re.S)
    assert block and block[0]==template,path
    assert html.count('id="koonafa-global-footer"')==1,path
    assert '<link rel="stylesheet" href="/global-footer.css">' in html,path
    assert 'class="associations-strip"' not in html,path
    pages.append(path.relative_to(ROOT).as_posix())
assert 'global-footer.css' not in (ROOT/'index.html').read_text()
assert len(pages)==109,len(pages)
print('PASS identical static footer on 109 content pages; homepage excluded',flush=True)
axe_path=os.environ.get('AXE_SCRIPT_PATH')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':390,'height':844},reduced_motion='reduce')
    page.route('https://**/*',lambda route:route.abort())
    for path in pages:
        page.goto(f'{BASE}/{path}',wait_until='load')
        footer=page.locator('#koonafa-global-footer')
        assert footer.count()==1,path
        assert footer.evaluate('(el)=>el.scrollWidth<=el.clientWidth'),path
        assert footer.evaluate('(el)=>getComputedStyle(el).backgroundColor')=='rgb(26, 26, 26)',path
        assert footer.locator('.kg-quick-links').evaluate('(el)=>getComputedStyle(el).position')=='static',path
        assert footer.locator('.kg-quick-links a').evaluate_all('(els)=>els.every(el=>el.getBoundingClientRect().height>=48)'),path
        assert page.locator('.kg-association-list li').count()==15,path
    print('PASS 109 mobile pages: dark palette, layout, association strip, 48px links',flush=True)
    for path in ['About.html','global.html','GSA.html','DMC.html','gsa/airline-gsa-india.html','gsa/index.html','packages.html','case-studies.html','patna-brochure.html','GlobalHospitalitymarketing.html']:
        for width in [320,1440]:
            page.set_viewport_size({'width':width,'height':1000})
            page.goto(f'{BASE}/{path}',wait_until='load')
            footer=page.locator('#koonafa-global-footer')
            assert footer.evaluate('(el)=>el.scrollWidth<=el.clientWidth'),(path,width)
            columns=footer.locator('.kg-footer-grid').evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
            assert columns==(1 if width==320 else 4),(path,width,columns)
            assert page.locator('.kg-footer-system').evaluate('(el)=>el.scrollWidth<=el.clientWidth'),(path,width)
            if axe_path:
                page.add_script_tag(content=Path(axe_path).read_text())
                report=page.evaluate("async()=>await axe.run(document.querySelector('.kg-footer-system'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
                assert not report['violations'],(path,width,[(v['id'],[n['target'] for n in v['nodes']]) for v in report['violations']])
    print('PASS mobile/desktop footer variants and optional automated WCAG checks',flush=True)
    browser.close()
