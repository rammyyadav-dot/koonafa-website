#!/usr/bin/env python3
"""Render the India hub and articles as static HTML from the editorial brief mapping."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
HOST = 'https://www.koonafa.com'
HUB = '/india'
TRADE_HUB = HUB + '/tourism-and-trade-support-in-india'
IMAGE = '/hero-beach-resort.png'
SOCIAL_IMAGE = '/og-image.jpg'
SOCIAL_ALT = 'Koonafa Global hospitality and tourism'
CONTENT_UPDATED = '2026-11-22'
COUNTRY = {'@type': 'Country', 'name': 'India', 'identifier': 'IN'}
FOOTER = (ROOT / 'components/global-footer.template').read_text().strip()

# Each pillar is one of the 100 editorial pages and doubles as its topic directory.
CLUSTERS = {
    'representation': (range(2, 26), 2, 'Hotel Sales & Representation',
                       'Trade representation, market entry and property-level sales planning for India.'),
    'digital-marketing': (range(26, 51), 26, 'Digital Marketing & Direct Bookings',
                          'Hotel SEO, campaigns, brand content and the direct reservation journey.'),
    'revenue-distribution': (range(51, 76), 51, 'Revenue & Distribution',
                             'Pricing, OTA operations, contracting, corporate accounts and group demand.'),
    'guides': (range(76, 101), 79, 'Hotel Marketing & Representation Guides',
               'Compare providers, plan a launch and evaluate your next commercial decision.'),
}
HUB_FAQ = (
    ('What does hotel sales representation in India cover?',
     'A representation brief can include identifying trade and corporate buyers, introducing the property, '
     'training partner sellers and following up on proposals. The hotel and Koonafa agree the territory, '
     'decision rights and reporting before work starts.'),
    ('Can an overseas hotel use the India market hub?',
     'Yes. International hotels can start with the India launch guide to assess feeder cities, '
     'air access and travel trade requirements before planning an outbound partner programme.'),
    ('What should I include in a hotel marketing enquiry?',
     'Share your property website, target guests and source markets, priority stay dates, current booking '
     'channels and the commercial objective. Include any constraints on room stock or offer approvals.'),
)
LOCAL_MARKETS = {
    19: ('Delhi NCR', 'Place', 'IN'), 20: ('Mumbai', 'City', 'IN-MH'),
    21: ('Bengaluru', 'City', 'IN-KA'), 22: ('Goa', 'State', 'IN-GA'),
    23: ('Jaipur', 'City', 'IN-RJ'), 24: ('Kolkata', 'City', 'IN-WB'),
    88: ('Delhi', 'City', 'IN-DL'), 89: ('Mumbai', 'City', 'IN-MH'),
    90: ('Gurugram', 'City', 'IN-HR'),
}
CITIES = (19, 20, 21, 22, 23, 24, 90)
COLLECTIONS = {1, *(group[1] for group in CLUSTERS.values())}
FEATURED = (4, 28, 32, 52, 83, 95)
RELATED_GROUPS = (
    (4, 13, 66, 87, 98), (5, 14, 36, 86), (6, 9, 10, 50, 77, 85, 99, 100),
    (7, 35, 70, 94), (8, 18, 67, 73, 98), (11, 15, 16, 17, 61, 72),
    (12, 44, 91, 95), (19, 88, 90), (20, 89, 24), (21, 22, 23),
    (25, 39, 45, 46, 47, 96), (27, 30, 38, 40, 41, 42),
    (28, 33, 48, 92), (31, 34, 43, 49, 97), (32, 33, 42, 84),
    (51, 56, 57, 60, 70, 75), (52, 53, 58, 59, 69), (54, 55, 69, 71, 73),
    (61, 62, 74, 93), (62, 63, 64, 65, 68), (76, 78, 79, 80, 81, 82, 83),
)
EXISTING = {
    4: ('India outbound hotel marketing services', '/gsa/outbound-hotel-marketing-india'),
    5: ('Luxury hotel GSA services', '/gsa/luxury-hotel-gsa-india'),
    7: ('Boutique hotel representation services', '/gsa/boutique-hotel-representation-india'),
    14: ('Resort sales office services', '/gsa/resort-sales-office-india'),
    16: ('Koonafa hotel representation services', '/gsa/hotel-representation-india'),
    17: ('India hotel GSA network', '/gsa/hotel-gsa-network-india'),
    19: ('Delhi hotel representation services', '/gsa/hotel-representation-delhi'),
    20: ('Mumbai hotel representation services', '/gsa/hotel-representation-mumbai'),
    71: ('Bedbank account management services', '/gsa/bedbank-account-management-india'),
    98: ('Tourism board representation services', '/gsa/tourism-board-representation-india'),
}


@dataclass(frozen=True)
class Page:
    number: int
    slug: str
    title: str
    description: str
    heading: str
    body: str
    second_heading: str
    second_body: str
    keyword: str
    answer: str

    @property
    def seo_title(self):
        branded = f'{self.title} | Koonafa'
        return branded if len(branded) <= 60 else self.title

    @property
    def cluster(self):
        return next(key for key, (numbers, _, _, _) in CLUSTERS.items() if self.number in numbers)

    @property
    def url(self):
        if self.number == 1:
            return HUB
        if self.number == CLUSTERS[self.cluster][1]:
            return f'{HUB}/{self.cluster}/'
        return f'{HUB}/{self.cluster}/{self.slug}/'

    @property
    def path(self):
        return ROOT / ('india.html' if self.number == 1 else f'{self.url.strip("/")}/index.html')


def load_pages():
    pages = {}
    for line in (ROOT / 'config/india-editorial.tsv').read_text().splitlines():
        number, *fields = line.split('|')
        page = Page(int(number), *fields)
        if page.number in pages or not all(fields):
            raise ValueError(f'Missing copy or duplicate ID on row {number}')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', page.slug):
            raise ValueError(f'Invalid slug on row {number}')
        pages[page.number] = page
    if set(pages) != set(range(1, 101)):
        raise ValueError('The brief must map all 100 keywords to editorial pages')
    for field in ('url', 'seo_title', 'description', 'keyword', 'body', 'second_body', 'answer'):
        if len({getattr(page, field) for page in pages.values()}) != len(pages):
            raise ValueError(f'Duplicate page {field}')
    return pages


def link(label, url, current=False):
    attribute = ' aria-current="page"' if current else ''
    return f'<a href="{escape(url)}"{attribute}>{escape(label)}</a>'


def breadcrumbs(page):
    trail = [('Home', '/'), ('Global Hospitality', '/global'), ('India', HUB)]
    if page.number != 1:
        _, pillar, label, _ = CLUSTERS[page.cluster]
        trail.append((label, f'{HUB}/{page.cluster}/'))
        if page.number != pillar:
            trail.append((page.title, page.url))
    return trail


def markup(page, trail, pages):
    canonical = HOST + page.url
    organization = {
        '@type': 'Organization', '@id': 'https://koonafa.com/global#organization',
        'name': 'Koonafa Global', 'url': 'https://koonafa.com/global',
        'email': 'Hello@koonafa.com', 'logo': 'https://koonafa.com/favicon.svg',
        'image': HOST + SOCIAL_IMAGE,
    }
    crumbs = {'@type': 'BreadcrumbList', '@id': canonical + '#breadcrumbs', 'itemListElement': [
        {'@type': 'ListItem', 'position': position, 'name': name,
         'item': HOST + url if url.startswith(HUB) else 'https://koonafa.com' + url}
        for position, (name, url) in enumerate(trail, 1)]}
    market, place_type, _ = LOCAL_MARKETS.get(page.number, ('India', 'Country', 'IN'))
    places = [COUNTRY]
    if market != 'India':
        places.insert(0, {'@type': place_type, 'name': market, 'containedInPlace': COUNTRY})
    collection = page.number in COLLECTIONS
    image = {'@type': 'ImageObject', '@id': canonical + '#image', 'url': HOST + SOCIAL_IMAGE,
             'width': 1200, 'height': 630, 'caption': SOCIAL_ALT}
    webpage = {
        '@type': 'CollectionPage' if collection else 'WebPage',
        '@id': canonical + '#webpage', 'url': canonical, 'name': page.title,
        'description': page.description, 'inLanguage': 'en-IN',
        'publisher': {'@id': organization['@id']},
        'breadcrumb': {'@id': crumbs['@id']},
        'about': {'@type': 'Thing', 'name': page.title},
        'abstract': page.answer, 'spatialCoverage': places, 'dateModified': CONTENT_UPDATED,
        'primaryImageOfPage': {'@id': image['@id']},
    }
    graph = [organization, webpage, crumbs, image]
    if collection:
        items = ([(label, pages[pillar].url) for _, pillar, label, _ in CLUSTERS.values()]
                 if page.number == 1 else
                 article_links(pages, [n for n in CLUSTERS[page.cluster][0] if n != page.number]))
        listing = {
            '@type': 'ItemList', '@id': canonical + '#directory', 'numberOfItems': len(items),
            'itemListElement': [
                {'@type': 'ListItem', 'position': position, 'name': label, 'url': HOST + url}
                for position, (label, url) in enumerate(items, 1)
            ],
        }
        webpage['mainEntity'] = {'@id': listing['@id']}
        graph.append(listing)
    else:
        article = {
            '@type': 'Article', '@id': canonical + '#article', 'headline': page.title,
            'description': page.description, 'abstract': page.answer, 'inLanguage': 'en-IN',
            'dateModified': CONTENT_UPDATED, 'spatialCoverage': places,
            'mainEntityOfPage': {'@id': webpage['@id']},
            'articleSection': CLUSTERS[page.cluster][2],
            'author': {'@id': organization['@id']}, 'publisher': {'@id': organization['@id']},
            'image': {'@id': image['@id']},
        }
        webpage['mainEntity'] = {'@id': article['@id']}
        graph.append(article)
    if page.number == 1:
        graph.append({
            '@type': 'Service', '@id': canonical + '#representation',
            'name': 'Hotel Representation and Hospitality Marketing',
            'url': canonical, 'provider': {'@id': organization['@id']},
            'areaServed': COUNTRY,
        })
        graph.append({
            '@type': 'FAQPage', '@id': canonical + '#questions', 'isPartOf': {'@id': webpage['@id']},
            'mainEntity': [
                {'@type': 'Question', 'name': question,
                 'acceptedAnswer': {'@type': 'Answer', 'text': answer}}
                for question, answer in HUB_FAQ
            ],
        })
    return json.dumps({'@context': 'https://schema.org', '@graph': graph},
                      ensure_ascii=False).replace('<', '\\u003c')


def list_links(items, directory=False):
    cls = 'india-link-list india-directory' if directory else 'india-link-list'
    items_html = '\n'.join(f'  <li>{link(label, url)}</li>' for label, url in items)
    return f'<ul class="{cls}">\n{items_html}\n</ul>'


def article_links(pages, numbers):
    return [(pages[number].title, pages[number].url) for number in numbers]


def cards(entries):
    return '\n'.join(
        f'<article class="focus india-card"><h3>{escape(title)}</h3>'
        f'<p>{escape(description)}</p>{link(label + " →", url)}</article>'
        for title, description, label, url in entries
    )


def directory(title, links, section_id):
    return f'''<section class="section cream" id="{section_id}">
  <div class="wrap">
    <h2 class="heading">{escape(title)}</h2>
    {list_links(links, directory=True)}
  </div>
</section>'''


def topic_sections(page, pages):
    numbers, pillar, label, _ = CLUSTERS[page.cluster]
    related = list(dict.fromkeys(
        number for group in RELATED_GROUPS if page.number in group for number in group
        if number not in (page.number, pillar)
    ))
    related.extend(number for number in numbers if number not in (page.number, pillar, *related))
    links = article_links(pages, related[:3])
    if page.number != pillar:
        links.insert(0, (f'All {label.lower()} topics', pages[pillar].url))
    if page.number in EXISTING:
        links.append(EXISTING[page.number])
    detail = f'''<section class="section" id="overview">
  <div class="wrap india-copy-layout">
    <div class="india-copy">
      <h2>{escape(page.heading)}</h2>
      <p>{escape(page.body)}</p>
      <h2>{escape(page.second_heading)}</h2>
      <p>{escape(page.second_body)}</p>
    </div>
    <aside class="india-related" aria-labelledby="related-title">
      <h2 id="related-title">Related reading</h2>
      {list_links(links)}
    </aside>
  </div>
</section>'''
    if page.number == pillar:
        detail += '\n' + directory('Explore ' + label.lower(),
                                   article_links(pages, [number for number in numbers if number != pillar]),
                                   'topics')
    return detail


def hub_sections(page, pages):
    pillars = [(label, description, 'Explore ' + label.lower(), pages[pillar].url)
               for _, pillar, label, description in CLUSTERS.values()]
    featured = [(pages[n].title, pages[n].description, 'Read ' + pages[n].title.lower(), pages[n].url)
                for n in FEATURED]
    faq = '\n'.join(f'<details><summary>{escape(question)}</summary><p>{escape(answer)}</p></details>'
                    for question, answer in HUB_FAQ)
    return f'''<section class="section" id="explore">
  <div class="wrap">
    <div class="section-intro">
      <h2 class="heading">{escape(page.heading)}</h2>
      <p>{escape(page.body)}</p>
    </div>
    <div class="market-focus india-pillars">{cards(pillars)}</div>
    <p><a class="btn btn-gold" href="{TRADE_HUB}">Explore tourism &amp; trade support</a></p>
  </div>
</section>
{directory('India market guides by city', article_links(pages, CITIES), 'markets')}
<section class="section" id="featured">
  <div class="wrap">
    <h2 class="heading">Featured guides and services</h2>
    <div class="market-focus">{cards(featured)}</div>
  </div>
</section>
<section class="section cream" id="questions">
  <div class="wrap">
    <h2 class="heading">Questions about India representation</h2>
    <div class="india-faq">{faq}</div>
  </div>
</section>'''


def render(page, pages):
    canonical = HOST + page.url
    is_hub = page.number == 1
    trail = breadcrumbs(page)
    crumb_links = '\n'.join(f'      <li>{link(name, url)}</li>' for name, url in trail[:-1])
    crumb_links += f'\n      <li aria-current="page">{escape(trail[-1][0])}</li>'
    email = 'mailto:Hello@koonafa.com?subject=' + quote('India enquiry — ' + page.title)
    photo = (f'\n      <img class="hero-photo" src="{IMAGE}" alt="" width="804" height="826" '
             'fetchpriority="high">') if is_hub else ''
    cluster_label = 'India market' if is_hub else CLUSTERS[page.cluster][2]
    sections = hub_sections(page, pages) if is_hub else topic_sections(page, pages)
    hero_class = 'hero' if is_hub else 'hero india-topic-hero'
    action = '<a class="btn btn-light" href="#explore">Explore India topics</a>' if is_hub else ''
    nav = ' '.join((link('Global', '/global'), link('India', HUB, is_hub),
                    link('GSA', '/GSA'), link('About', 'https://www.koonafa.com/About')))
    contact_title = page.second_heading if is_hub else 'Discuss your India brief'
    contact_copy = (page.second_body if is_hub else
                    'Share your property, target audience and the dates or segments you want to grow.')
    title, description = escape(page.title), escape(page.description)
    seo_title = escape(page.seo_title)
    social_title = escape(f'{page.title} | Koonafa Global')
    is_article = page.number not in COLLECTIONS
    social_type = 'article' if is_article else 'website'
    article_section = (f'\n  <meta property="article:section" content="{escape(cluster_label)}">'
                       f'\n  <meta property="article:modified_time" content="{CONTENT_UPDATED}">'
                       if is_article else '')
    region = LOCAL_MARKETS.get(page.number, ('India', 'Country', 'IN'))[2]
    return f'''<!doctype html>
<!-- Generated by scripts/build_india.py. Edit config/india-editorial.tsv to update copy. -->
<html lang="en-IN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{seo_title}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="geo.region" content="{region}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="{social_type}">{article_section}
  <meta property="og:site_name" content="Koonafa Global">
  <meta property="og:locale" content="en_IN">
  <meta property="og:title" content="{social_title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{HOST + SOCIAL_IMAGE}">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{SOCIAL_ALT}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{social_title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{HOST + SOCIAL_IMAGE}">
  <meta name="twitter:image:alt" content="{SOCIAL_ALT}">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;display=swap">
  <link rel="stylesheet" href="/global/UAE/emirates.css">
  <link rel="stylesheet" href="/india/india.css">
  <link rel="stylesheet" href="/global-footer.css">
  <script type="application/ld+json">{markup(page, trail, pages)}</script>
</head>
<body class="india-page">
  <a class="skip" href="#main-content">Skip to content</a>
  <header class="mast">
    <div class="wrap mast-inner">
      <a class="brand" href="/global" aria-label="Koonafa Global home">KOONAFA<small>Hospitality &amp; Tourism</small></a>
      <nav class="primary-nav" aria-label="Primary">{nav}
        <a class="nav-contact" href="#contact">Contact</a>
      </nav>
    </div>
  </header>
  <nav class="india-breadcrumbs" aria-label="Breadcrumb">
    <ol class="wrap">
{crumb_links}
    </ol>
  </nav>
  <main id="main-content" tabindex="-1">
    <section class="{hero_class}" aria-labelledby="page-title">{photo}
      <div class="wrap hero-body">
        <p class="eyebrow">{escape(cluster_label)}</p>
        <h1 id="page-title">{title}</h1>
        <p class="hero-lead" id="summary">{escape(page.answer)}</p>
        <div class="btns"><a class="btn btn-gold" href="#contact">Discuss your project</a>{action}</div>
      </div>
    </section>
{sections}
    <section class="callout" id="contact">
      <div class="wrap callout-inner">
        <div><h2>{escape(contact_title)}</h2><p>{escape(contact_copy)}</p></div>
        <a class="btn" href="{email}">Email Koonafa Global</a>
      </div>
    </section>
  </main>
{FOOTER}
</body>
</html>
'''


def expected_files():
    pages = load_pages()
    files = {page.path: render(page, pages) for page in pages.values()}
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for page in pages.values():
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text = HOST + page.url
        ET.SubElement(entry, 'lastmod').text = CONTENT_UPDATED
    ET.indent(sitemap, space='  ')
    files[ROOT / 'sitemap-india.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
        sitemap, encoding='unicode') + '\n'
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify committed HTML and sitemap')
    args = parser.parse_args()
    files = expected_files()
    if args.check:
        actual = {path for cluster in CLUSTERS for path in (ROOT / 'india' / cluster).rglob('index.html')}
        actual.add(ROOT / 'india.html')
        extra = actual - files.keys()
        stale = {path for path, contents in files.items()
                 if not path.is_file() or path.read_text() != contents}
        if extra or stale:
            parser.exit(1, 'Unexpected or stale India output:\n' + '\n'.join(
                str(path.relative_to(ROOT)) for path in sorted(extra | stale)) + '\n')
        print('Verified 100 static India pages and the India sitemap.')
    else:
        for path, contents in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents)
        print('Rendered 100 static India pages and the India sitemap.')


if __name__ == '__main__':
    main()
