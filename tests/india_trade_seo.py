"""Verify discovery, metadata and answer markup for the tourism and trade section."""
from collections import deque
from html import escape
import json
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from india_seo import Document
from build_india_trade import HOST, HUB, PILLARS, REGIONS, ROOT, expected_files, load_topics

topics = load_topics()
sitemap = ROOT / 'sitemap-india-tourism-trade.xml'
urls = [node.text for node in ET.parse(sitemap).findall('.//{*}loc')]
assert urls == [HOST + topic.url for topic in topics.values()]
assert f'Sitemap: {HOST}/sitemap-india-tourism-trade.xml' in (ROOT / 'robots.txt').read_text()
assert HUB in Document((ROOT / 'india.html').read_text()).links
for path, expected in expected_files().items():
    assert path.read_text() == expected, path

graph = {}
for topic in topics.values():
    html = topic.path.read_text()
    doc = Document(html)
    canonical = HOST + topic.url
    assert doc.headings == 1 and doc.canonicals == [canonical]
    assert len(topic.seo_title) <= 60 and doc.metadata['description'] == topic.description
    assert doc.metadata['og:url'] == canonical and doc.metadata['og:locale'] == 'en_IN'
    assert doc.metadata['robots'].startswith('index,follow')
    assert f'id="summary">{escape(topic.answer)}</p>' in html
    schema = json.loads(doc.schema)['@graph']
    page = next(node for node in schema if node['@type'] in ('WebPage', 'CollectionPage'))
    assert page['abstract'] == topic.answer
    assert [place['name'] for place in page['spatialCoverage']] == [
        name for name, _ in REGIONS.get(topic.number, (('India', 'Country'),))]
    primary = next(node for node in schema if node['@id'] == page['mainEntity']['@id'])
    collection = topic.number in (1, *PILLARS)
    assert primary['@type'] == ('ItemList' if collection else 'Article')
    if collection:
        assert all(urlsplit(item['url']).path in doc.links for item in primary['itemListElement'])
    crumbs = next(node for node in schema if node['@type'] == 'BreadcrumbList')
    assert crumbs['itemListElement'][-1]['item'] == canonical
    for href in doc.links:
        if href.startswith('#'):
            assert href[1:] in doc.ids
    graph[topic.url] = {href for href in doc.links if href == HUB or href.startswith(HUB + '/')}
    assert all(HOST + href in urls for href in graph[topic.url])

depth = {HUB: 0}
pending = deque([HUB])
while pending:
    route = pending.popleft()
    for href in graph[route] - depth.keys():
        depth[href] = depth[route] + 1
        pending.append(href)
assert depth.keys() == graph.keys() and max(depth.values()) <= 2
print('PASS all 100 tourism and trade URLs, crawl depth, answer markup and structured entities')
