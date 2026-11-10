"""Check the site's single About destination, redirects, and legacy hash navigation.
Run against a local static server: BASE_URL=http://127.0.0.1:8000 python tests/about_routes.py.
Requires Python Playwright and Chromium. About navigation is intercepted with local HTML,
so tests do not depend on production deployment or third-party assets.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import os,re
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
ABOUT='https://www.koonafa.com/About'
BASE=os.environ.get('BASE_URL','http://127.0.0.1:8000').rstrip('/')
class Links(HTMLParser):
    def __init__(self):super().__init__();self.current=None;self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        if tag=='a':self.current=[attrs.get('href',''),'']
    def handle_data(self,text):
        if self.current is not None:self.current[1]+=text
    def handle_endtag(self,tag):
        if tag=='a' and self.current is not None:self.links.append(tuple(self.current));self.current=None
count=0
for path in [*ROOT.glob('*.html'),*(ROOT/'gsa').glob('*.html')]:
    parsed=Links();parsed.feed(path.read_text())
    for href,label in parsed.links:
        if re.fullmatch(r'about(?: us| koonafa)?',' '.join(label.split()),re.I):
            assert href==ABOUT,(path,href);count+=1
        assert not href.lower().endswith('#about'),(path,href)
        if href.startswith('#'):assert href[1:] in parsed.ids,(path,href)
assert count==218,count
assert (ROOT/'About.html').is_file() and not (ROOT/'about.html').exists()
assert f'href="{ABOUT}"' in (ROOT/'components/global-footer.template').read_text()
assert f"href: '{ABOUT}'" in (ROOT/'nav.js').read_text()
rules={}
for line in (ROOT/'_redirects').read_text().splitlines():
    if not line.strip() or line.lstrip().startswith('#'):continue
    source,destination,status=line.split();assert destination==ABOUT and status=='301';rules[source]=destination
assert '/about' in rules and '/about.html' in rules and '/About.html' in rules
assert '/About' not in rules and '/about.css' not in rules
print(f'PASS {count} About links, canonical source file, redirect rules, and local anchors',flush=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
    def production(route):
        path=unquote(urlsplit(route.request.url).path)
        file=ROOT/('About.html' if path=='/About' else path.lstrip('/'))
        if file.is_file():
            typ='text/html' if file.suffix=='.html' else 'text/css' if file.suffix=='.css' else 'application/javascript' if file.suffix=='.js' else 'application/octet-stream'
            route.fulfill(body=file.read_bytes(),content_type=typ)
        else:route.abort()
    for width in [1440,390]:
        page=browser.new_page(viewport={'width':width,'height':900})
        page.route('https://**/*',lambda route:route.abort())
        page.route('https://www.koonafa.com/**',production)
        for path in ['index.html','global.html','GSA.html','DMC.html','gsa/airline-gsa-india.html','About.html']:
            page.goto(f'{BASE}/{path}',wait_until='load')
            toggle=page.locator('#hamburger,#menuToggle')
            if width==390 and toggle.count():toggle.click()
            matches=page.get_by_role('link',name='About',exact=True)
            matches.filter(visible=True).first.click()
            page.wait_for_url(ABOUT)
            assert page.locator('#about-title').count()==1,(path,width)
        for legacy in ['global.html#about','index.html#about','gsa/airline-gsa-india.html#about']:
            page.goto(f'{BASE}/{legacy}',wait_until='load');page.wait_for_url(ABOUT)
        page.goto(f'{BASE}/gsa/airline-gsa-india.html',wait_until='load')
        page.get_by_role('link',name='Explore Our Expertise').click()
        page.wait_for_url('**/gsa/airline-gsa-india.html#service-overview')
        assert page.locator('#service-overview').count()==1
        page.goto(f'{BASE}/packages.html',wait_until='load')
        page.get_by_role('link',name='About Us',exact=True).click();page.wait_for_url(ABOUT)
        print('PASS',width,'header/footer navigation, old bookmarks, and local service-overview link',flush=True)
        page.close()
    browser.close()
