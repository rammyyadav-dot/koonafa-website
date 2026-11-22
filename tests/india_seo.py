"""Check India indexability, discoverability and keyword-to-page coverage."""
from collections import deque
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_india import HOST, HUB, expected_files, load_pages


class Document(HTMLParser):
    def __init__(self, html, india_footer_only=False):
        super().__init__()
        self.links = set()
        self.footer_links = set()
        self.in_footer = False
        self.india_footer_only = india_footer_only
        self.metadata = {}
        self.canonicals = []
        self.ids = set()
        self.headings = 0
        self.schema = ''
        self.in_schema = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'footer':
            self.in_footer = True
        if tag == 'a' and 'href' in attrs:
            self.links.add(attrs['href'])
            if self.in_footer:
                self.footer_links.add(attrs['href'])
            else:
                assert not self.india_footer_only or attrs['href'] != HOST + HUB
        if tag == 'h1':
            self.headings += 1
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonicals.append(attrs['href'])
        if tag == 'meta':
            self.metadata[attrs.get('name') or attrs.get('property')] = attrs.get('content')
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        self.in_schema = tag == 'script' and attrs.get('type') == 'application/ld+json'

    def handle_data(self, data):
        if self.in_schema:
            self.schema += data

    def handle_endtag(self, tag):
        if tag == 'footer':
            self.in_footer = False
        if tag == 'script':
            self.in_schema = False


def main():
    pages = load_pages()
    for path, expected in expected_files().items():
        assert path.read_text() == expected, path

    sitemap_urls = [node.text for node in ET.parse(ROOT / 'sitemap-india.xml').findall('.//{*}loc')]
    assert sitemap_urls == [HOST + page.url for page in pages.values()]
    assert f'Sitemap: {HOST}/sitemap-india.xml' in (ROOT / 'robots.txt').read_text()
    for filename in ('index.html', 'global.html'):
        doc = Document((ROOT / filename).read_text(), india_footer_only=True)
        assert HOST + HUB in doc.footer_links, filename

    graph = {}
    for page in pages.values():
        doc = Document(page.path.read_text())
        canonical = HOST + page.url
        assert doc.canonicals == [canonical]
        assert doc.headings == 1 and len(page.title) <= 60
        assert doc.metadata['og:url'] == canonical
        assert doc.metadata['description'] == page.description
        assert doc.metadata['robots'].startswith('index,follow')
        structured = json.loads(doc.schema)['@graph']
        breadcrumbs = next(item for item in structured if item['@type'] == 'BreadcrumbList')
        assert breadcrumbs['itemListElement'][-1]['item'] == canonical
        graph[page.url] = set()
        for href in doc.links:
            parsed = urlsplit(href)
            if parsed.path == HUB or parsed.path.startswith(HUB + '/'):
                assert HOST + parsed.path in sitemap_urls
                graph[page.url].add(parsed.path)
            if href.startswith('#'):
                assert parsed.fragment in doc.ids
            if parsed.path.startswith('/gsa/'):
                candidate = ROOT / parsed.path.lstrip('/')
                assert candidate.is_file() or candidate.with_suffix('.html').is_file()

    depths = {HUB: 0}
    queue = deque([HUB])
    while queue:
        current = queue.popleft()
        for target in graph[current] - depths.keys():
            depths[target] = depths[current] + 1
            queue.append(target)
    assert depths.keys() == graph.keys() and max(depths.values()) <= 2
    print('PASS 100 India pages with unique metadata, structured breadcrumbs and crawl depth ≤ 2')


if __name__ == '__main__':
    main()
