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
from build_india import COLLECTIONS, CONTENT_UPDATED, HOST, HUB, LOCAL_MARKETS, TRADE_HUB, expected_files, load_pages


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

    sitemap = ET.parse(ROOT / 'sitemap-india.xml')
    sitemap_urls = [node.text for node in sitemap.findall('.//{*}loc')]
    assert [node.text for node in sitemap.findall('.//{*}lastmod')] == [CONTENT_UPDATED] * len(pages)
    assert sitemap_urls == [HOST + page.url for page in pages.values()]
    assert f'Sitemap: {HOST}/sitemap-india.xml' in (ROOT / 'robots.txt').read_text()
    for filename in ('index.html', 'global.html'):
        doc = Document((ROOT / filename).read_text(), india_footer_only=True)
        assert HOST + HUB in doc.footer_links, filename

    graph = {}
    for page in pages.values():
        html = page.path.read_text()
        doc = Document(html)
        canonical = HOST + page.url
        assert doc.canonicals == [canonical]
        assert doc.headings == 1 and len(page.seo_title) <= 60
        assert doc.metadata['og:url'] == canonical
        assert doc.metadata['description'] == page.description
        assert doc.metadata['robots'].startswith('index,follow')
        assert doc.metadata['og:locale'] == 'en_IN'
        assert doc.metadata['og:image:width'] == '1200' and doc.metadata['og:image:height'] == '630'
        assert doc.metadata['og:image:alt'] == doc.metadata['twitter:image:alt']
        assert doc.metadata['og:title'] == doc.metadata['twitter:title']
        assert 'max-snippet:-1' in doc.metadata['robots']
        structured = json.loads(doc.schema)['@graph']
        is_collection = page.number in COLLECTIONS
        webpage = next(item for item in structured if item['@type'] in ('WebPage', 'CollectionPage'))
        assert webpage['abstract'] == page.answer and 'summary' in doc.ids
        expected_place, _, region = LOCAL_MARKETS.get(page.number, ('India', 'Country', 'IN'))
        assert webpage['spatialCoverage'][0]['name'] == expected_place
        assert doc.metadata['geo.region'] == region
        assert doc.metadata['og:type'] == ('website' if is_collection else 'article')
        entity = next(item for item in structured if item['@id'] == webpage['mainEntity']['@id'])
        assert entity['@type'] == ('ItemList' if is_collection else 'Article')
        if is_collection:
            assert all(urlsplit(item['url']).path in doc.links for item in entity['itemListElement'])
        else:
            assert entity['headline'] == page.title and entity['abstract'] == page.answer
            assert entity['mainEntityOfPage']['@id'] == webpage['@id']
        breadcrumbs = next(item for item in structured if item['@type'] == 'BreadcrumbList')
        assert breadcrumbs['itemListElement'][-1]['item'] == canonical
        graph[page.url] = set()
        for href in doc.links:
            parsed = urlsplit(href)
            if parsed.path == TRADE_HUB:
                assert page.url == HUB and (ROOT / (TRADE_HUB.lstrip('/') + '.html')).is_file()
                continue
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
