#!/usr/bin/env python3
"""Generate the tourism and travel trade section from its 100-keyword editorial file."""
import argparse
from dataclasses import dataclass
from html import escape
import json
import re
from urllib.parse import quote
import xml.etree.ElementTree as ET

from build_india import ROOT, HOST, COUNTRY, CONTENT_UPDATED, FOOTER, TRADE_HUB, link

HUB = TRADE_HUB
TOPIC_ROOT = '/india/tourism-and-trade-support'
IMAGE = '/palm-jumeirah.webp'
PHOTO_ALT = 'Aerial view of Palm Jumeirah in Dubai'
SOCIAL_IMAGE = '/og-image.jpg'
SOCIAL_ALT = 'Koonafa Global hospitality and tourism'
META_DESCRIPTIONS = {
    1: 'Explore tourism and travel trade support in India for destination boards, DMCs and travel suppliers, from market entry and trade sales to operations.',
    94: 'Learn how to read India’s tourism foreign exchange earnings, verify the Ministry of Tourism series and compare figures by period, currency and methodology.',
}
REGION_CODES = {77: 'IN-MH', 78: 'IN-KA', 79: 'IN-WB', 80: 'IN-GJ'}
QUESTIONS = {
    1: ('Who uses tourism and travel trade support in India?',
        'Destination organisations, DMCs, tour operators and travel suppliers use trade support to establish partner relationships, prepare sellable products and coordinate operations in the Indian market.'),
    2: ('What should a travel trade representative report?',
        'Ask for qualified buyer meetings, quotes, first bookings and repeat production, together with a named owner for each open opportunity.'),
    4: ('How is tourism board representation different from a roadshow?',
        'Representation is an ongoing mandate for a market. A roadshow is a time-bound activity that can sit within that mandate.'),
    5: ('Can a tourism GSA sign contracts for the principal?',
        'Only if the principal has granted that authority. Confirm signing limits, territory and eligible accounts in the written mandate.'),
    11: ('What should an India market entry pilot measure?',
         'Measure qualified quotes, reasons buyers decline, actual bookings and the cost of supporting the accounts that convert.'),
    26: ('What should a DMC give an India sales representative?',
         'Provide sample itineraries, net or commissionable rates, exclusions, operating windows, cancellation terms and a named ground operations contact.'),
    29: ('What terms should be checked before loading a B2B travel contract?',
         'Verify rate validity, taxes, inclusions, release schedules, cancellation, settlement and onward distribution rights against the signed terms.'),
    41: ('What makes a travel trade roadshow worthwhile?',
         'Use pre-booked meetings with buyers who can sell the product and assign an owner to each next step. Track qualified quotes and bookings after the event.'),
    51: ('Which travel process should a team outsource first?',
         'Start with a repeatable workflow with predictable inputs, a measurable output and a clear escalation path, such as invoice reconciliation or quote preparation.'),
    57: ('Who approves IATA accreditation?',
         'IATA makes accreditation decisions under the applicable programme. Consultants may help prepare evidence and organise the application.'),
    59: ('Does tourism ministry recognition replace business registration?',
         'Ministry recognition follows its own scheme. Check business registration and any activity-specific obligations with the relevant authorities.'),
    62: ('Which API scenarios should be tested before launch?',
         'Test revalidation, duplicate retry handling, confirmation, cancellation and reconciliation against the supplier’s records in an authorised test environment.'),
    76: ('How should travel trade coverage be planned across Delhi NCR?',
         'Group buyers by commercial role and practical meeting catchment. Compare Central Delhi, airport-linked accounts, Gurugram and Noida using relevant buyer activity.'),
    85: ('What should go in a tourism representation agreement?',
         'Define the mandate, territory, reserved accounts, approval rights, fees, reporting, access to data and handover obligations.'),
    86: ('What costs are typically outside a representation retainer?',
         'Event space, travel, collateral and joint marketing are often quoted separately. Ask for an itemised scope and written approval thresholds.'),
    88: ('How should I choose an Indian travel trade show?',
         'Compare the official exhibitor materials, buyer roles and appointment formats. Confirm current dates and venue directly with the organiser.'),
    94: ('How do I compare tourism foreign exchange earnings over time?',
         'Use the same official series and currency. Compare like-for-like periods, and label figures that the Ministry identifies as provisional or revised.'),
    100: ('What is the difference between a travel wholesaler and a DMC?',
          'A wholesaler distributes travel products to other sellers. A DMC arranges ground services in a destination and may contract with wholesalers or agencies.'),
}
BRAND = 'https://koonafa.com/global#organization'
GROUPS = (
    ('representation', 2, 25, 'Tourism Representation', 'Market entry, trade relationships and destination promotion.'),
    ('contracting-and-sales', 26, 50, 'Contracting & Trade Sales', 'DMC and GSA mandates, agent networks and buyer events.'),
    ('travel-operations', 51, 75, 'Travel Operations', 'Back-office workflows, integrations and accreditation guidance.'),
    ('market-guides', 76, 100, 'India Market Guides', 'Regional coverage, industry events and institutional resources.'),
)
REGIONS = {
    76: (('Delhi NCR', 'Place'),), 77: (('Mumbai', 'City'),),
    78: (('Bengaluru', 'City'),), 79: (('Kolkata', 'City'), ('Eastern India', 'Place')),
    80: (('Ahmedabad', 'City'), ('Gujarat', 'State')),
    81: (('Hyderabad', 'City'), ('Chennai', 'City')), 99: (('Eastern India', 'Place'),),
}
SOURCES = {
    57: [('IATA accreditation', 'https://www.iata.org/en/services/accreditation/')],
    58: [('Ministry of Corporate Affairs', 'https://www.mca.gov.in/')],
    59: [('Ministry of Tourism', 'https://tourism.gov.in/')],
    60: [('ATOAI', 'https://www.atoai.org/'), ('IATO', 'https://iato.in/'), ('TAAI', 'https://www.travelagentsofindia.com/')],
    61: [('Ministry of External Affairs', 'https://www.mea.gov.in/')],
    73: [('Reserve Bank of India', 'https://www.rbi.org.in/')],
    88: [('SATTE', 'https://satte.in/'), ('OTM', 'https://otm.co.in/'), ('TTF', 'https://www.ttfotm.com/')],
    89: [('SATTE', 'https://satte.in/'), ('OTM', 'https://otm.co.in/'), ('TTF', 'https://www.ttfotm.com/')],
    93: [('Ministry of Tourism', 'https://tourism.gov.in/')],
    94: [('Ministry of Tourism market research', 'https://tourism.gov.in/market-research-and-statistics')],
    98: [('Invest India', 'https://www.investindia.gov.in/')],
}
PILLARS = (2, 26, 51, 76)
# Retain the existing canonical when the international account guide is retitled.
STABLE_SLUGS = {9: 'international-tourism-representation-in-india'}
RELATED = (
    (3, 4, 5, 16, 20, 85), (8, 11, 23, 82, 87, 95), (12, 26, 27, 30, 40),
    (14, 51, 52, 53, 56, 70), (18, 29, 31, 39, 62, 69, 100),
    (37, 38, 79, 95, 99), (41, 42, 43, 44, 88, 89),
    (57, 58, 59, 60, 61, 74, 75), (76, 77, 78, 80, 81), (92, 93, 94, 98),
    (2, 9, 10, 15, 19, 24, 83, 84, 86), (6, 7, 13, 17, 21, 25, 35, 36, 45, 90, 91),
    (22, 63, 65, 67, 68, 73), (28, 32, 33, 34, 46, 96),
    (47, 48, 49, 50, 55, 71), (54, 64, 66, 72), (44, 88, 89, 97),
)


@dataclass(frozen=True)
class Topic:
    number: int
    title: str
    tagline: str
    answer: str
    action: str
    keyword: str

    @property
    def group(self):
        return next(group for group in GROUPS if group[1] <= self.number <= group[2])

    @property
    def url(self):
        if self.number == 1:
            return HUB
        group, pillar, *_ = self.group
        if self.number == pillar:
            return f'{TOPIC_ROOT}/{group}/'
        slug = STABLE_SLUGS.get(self.number) or re.sub('[^a-z0-9]+', '-', self.title.lower()).strip('-')
        return f'{TOPIC_ROOT}/{group}/{slug}/'

    @property
    def path(self):
        return ROOT / (f'{HUB[1:]}.html' if self.number == 1 else f'{self.url[1:]}index.html')

    @property
    def seo_title(self):
        branded = self.title + ' | Koonafa'
        return branded if len(branded) <= 60 else self.title

    @property
    def description(self):
        return META_DESCRIPTIONS.get(self.number, self.answer)


def load_topics():
    lines = (ROOT / 'config/india-tourism-trade.txt').read_text().splitlines()
    topics = {number: Topic(number, *line.split('|')) for number, line in enumerate(lines, 1)}
    if set(topics) != set(range(1, 101)):
        raise ValueError('Expected 100 keyword mappings')
    if any(not (0 < len(topic.seo_title) <= 60 and 0 < len(topic.description) <= 160)
           for topic in topics.values()):
        raise ValueError('A title or description exceeds editorial limits')
    for field in ('url', 'seo_title', 'description', 'tagline', 'answer', 'action', 'keyword'):
        if len({getattr(topic, field) for topic in topics.values()}) != len(topics):
            raise ValueError(f'Duplicate {field}')
    return topics


def directory_items(topic, topics):
    if topic.number == 1:
        return [(name, topics[pillar].url) for _, pillar, _, name, _ in GROUPS]
    _, first, last, _, _ = topic.group
    return [(topics[n].title, topics[n].url) for n in range(first + 1, last + 1)]


def crumbs(topic):
    trail = [('Home', '/'), ('India', '/india'), ('Tourism & Trade Support', HUB)]
    if topic.number != 1:
        group, pillar, _, label, _ = topic.group
        trail.append((label, f'{TOPIC_ROOT}/{group}/'))
        if topic.number != pillar:
            trail.append((topic.title, topic.url))
    return trail


def structured(topic, topics):
    canonical = HOST + topic.url
    collection = topic.number in (1, *PILLARS)
    coverage = [{'@type': kind, 'name': name, 'containedInPlace': COUNTRY}
                for name, kind in REGIONS.get(topic.number, ())] or [COUNTRY]
    breadcrumb_id = canonical + '#breadcrumbs'
    organization = {'@type': 'Organization', '@id': BRAND, 'name': 'Koonafa Global',
                    'url': 'https://koonafa.com/global', 'logo': 'https://koonafa.com/favicon.svg',
                    'email': 'Hello@koonafa.com'}
    image = {'@type': 'ImageObject', '@id': canonical + '#image', 'url': HOST + SOCIAL_IMAGE,
             'width': 1200, 'height': 630, 'caption': SOCIAL_ALT}
    page = {'@type': 'CollectionPage' if collection else 'WebPage',
            '@id': canonical + '#webpage', 'name': topic.title, 'url': canonical,
            'description': topic.description, 'abstract': topic.answer, 'inLanguage': 'en-IN',
            'about': {'@type': 'Thing', 'name': topic.title},
            'spatialCoverage': coverage, 'dateModified': CONTENT_UPDATED,
            'publisher': {'@id': BRAND}, 'primaryImageOfPage': {'@id': image['@id']},
            'breadcrumb': {'@id': breadcrumb_id}}
    breadcrumb = {'@type': 'BreadcrumbList', '@id': breadcrumb_id, 'itemListElement': [
        {'@type': 'ListItem', 'position': position, 'name': label, 'item': HOST + url}
        for position, (label, url) in enumerate(crumbs(topic), 1)
    ]}
    if collection:
        main = {'@type': 'ItemList', '@id': canonical + '#directory', 'itemListElement': [
            {'@type': 'ListItem', 'position': position, 'name': label, 'url': HOST + url}
            for position, (label, url) in enumerate(directory_items(topic, topics), 1)
        ]}
    else:
        main = {'@type': 'Article', '@id': canonical + '#article', 'headline': topic.title,
                'dateModified': CONTENT_UPDATED, 'inLanguage': 'en-IN', 'abstract': topic.answer,
                'description': topic.description, 'spatialCoverage': coverage,
                'articleSection': topic.group[3], 'author': {'@id': BRAND},
                'publisher': {'@id': BRAND}, 'image': {'@id': image['@id']},
                'mainEntityOfPage': {'@id': page['@id']}}
    if sources := SOURCES.get(topic.number):
        (page if collection else main)['citation'] = [
            {'@type': 'WebPage', 'name': title, 'url': url} for title, url in sources
        ]
    page['mainEntity'] = {'@id': main['@id']}
    graph = [organization, page, image, breadcrumb, main]
    if topic.number == 1:
        page['mentions'] = {'@id': canonical + '#service'}
        graph.append({'@type': 'Service', '@id': canonical + '#service',
                      'name': 'Tourism and Travel Trade Representation',
                      'url': canonical, 'provider': {'@id': BRAND}, 'areaServed': COUNTRY})
    return json.dumps({'@context': 'https://schema.org', '@graph': graph},
                      ensure_ascii=False).replace('<', '\\u003c')


def link_list(items, css='trade-links'):
    return f'<ul class="{css}">\n' + '\n'.join(f'  <li>{link(label, url)}</li>' for label, url in items) + '\n</ul>'


def answer_block(topic):
    if topic.number not in QUESTIONS:
        return ''
    question, answer = QUESTIONS[topic.number]
    return f'\n    <div class="trade-answer"><h2>{escape(question)}</h2><p>{escape(answer)}</p></div>'


def body(topic, topics):
    if topic.number == 1:
        cards = '\n'.join(
            f'<article class="trade-card"><h3>{link(label, topics[pillar].url)}</h3><p>{escape(copy)}</p></article>'
            for _, pillar, _, label, copy in GROUPS
        )
        return f'''<section class="trade-section" id="topics">
  <div class="wrap">
    <h2>Explore travel trade support</h2>
    <div class="trade-grid">{cards}</div>{answer_block(topic)}
  </div>
</section>
<section class="trade-section trade-band" id="markets">
  <div class="wrap"><h2>India market guides</h2>
    {link_list([(topics[n].title, topics[n].url) for n in (*range(76, 82), 99)], 'trade-links trade-index')}
  </div>
</section>'''
    _, pillar, _, label, _ = topic.group
    related = list(dict.fromkeys(n for group in RELATED if topic.number in group for n in group
                                 if n not in (topic.number, pillar)))

    links = ([(label, topics[pillar].url)] if topic.number != pillar else [])
    links += [(topics[n].title, topics[n].url) for n in related[:2]]
    sources = SOURCES.get(topic.number)
    references = f'\n    <h3>Official resources</h3>{link_list(sources)}' if sources else ''
    detail = f'''<section class="trade-section" id="approach"><div class="wrap trade-detail">
  <div class="trade-prose">
    <h2>{escape(topic.tagline.rstrip('.'))}</h2>
    <p>{escape(topic.action)}</p>{answer_block(topic)}{references}
  </div>
  <aside class="trade-aside" aria-labelledby="related-title">
    <h2 id="related-title">Related reading</h2>{link_list(links)}
  </aside>
</div></section>'''
    if topic.number == pillar:
        detail += f'''\n<section class="trade-section trade-band" id="topics"><div class="wrap">
  <h2>Explore {escape(label.lower())}</h2>{link_list(directory_items(topic, topics), 'trade-links trade-index')}
</div></section>'''
    return detail


def render(topic, topics):
    canonical = HOST + topic.url
    title = escape(topic.title)
    social_title = escape(topic.title + ' | Koonafa Global')
    description = escape(topic.description)
    hub = topic.number == 1
    collection = topic.number in (1, *PILLARS)
    trail = crumbs(topic)
    crumbs_html = ''.join(f'<li>{link(label, url)}</li>' for label, url in trail[:-1])
    crumbs_html += f'<li aria-current="page">{escape(trail[-1][0])}</li>'
    photo = (f'<img src="{IMAGE}" width="3840" height="2010" fetchpriority="high" alt="{PHOTO_ALT}">'
             if hub else '')
    tagline = f'\n        <p class="trade-tagline">{escape(topic.tagline)}</p>' if hub else ''
    hero_class = 'trade-hero trade-hero-photo' if hub else 'trade-hero'
    browse = '#topics' if collection else '#approach'
    action = 'Explore topics' if collection else 'Read the guide'
    subject = quote('India tourism and trade — ' + topic.title)
    article_meta = (f'\n  <meta property="article:section" content="{escape(topic.group[3])}">'
                    f'\n  <meta property="article:modified_time" content="{CONTENT_UPDATED}">'
                    if not collection else '')
    return f'''<!doctype html>
<!-- Generated by scripts/build_india_trade.py. -->
<html lang="en-IN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(topic.seo_title)}</title>
  <meta name="description" content="{description}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="geo.region" content="{REGION_CODES.get(topic.number, 'IN')}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="{'website' if collection else 'article'}">{article_meta}
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
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap">
  <link rel="stylesheet" href="/global/UAE/emirates.css">
  <link rel="stylesheet" href="/india/india.css">
  <link rel="stylesheet" href="/india/tourism-trade.css">
  <link rel="stylesheet" href="/global-footer.css">
  <script type="application/ld+json">{structured(topic, topics)}</script>
</head>
<body class="india-page trade-page">
  <a class="skip" href="#main-content">Skip to content</a>
  <header class="mast"><div class="wrap mast-inner">
    <a class="brand" href="/global" aria-label="Koonafa Global home">KOONAFA<small>Hospitality &amp; Tourism</small></a>
    <nav class="primary-nav" aria-label="Primary"><a href="/global">Global</a><a href="/GSA">GSA</a>
      <a href="/DMC">DMC</a><a class="nav-contact" href="#contact">Contact</a></nav>
  </div></header>
  <nav class="india-breadcrumbs" aria-label="Breadcrumb"><ol class="wrap">{crumbs_html}</ol></nav>
  <main id="main-content" tabindex="-1">
    <section class="{hero_class}" aria-labelledby="page-title">
      <div class="wrap trade-hero-inner"><div class="trade-hero-copy">
        <h1 id="page-title">{title}</h1>{tagline}
        <p id="summary">{escape(topic.answer)}</p>
        <a class="btn btn-gold" href="{browse}">{action}</a>
      </div>{photo}</div>
    </section>
{body(topic, topics)}
    <section class="trade-contact" id="contact" aria-labelledby="trade-contact-title">
      <div class="wrap trade-contact-inner">
        <div><h2 id="trade-contact-title">Talk trade with Koonafa</h2>
          <p>{escape(topic.action if hub else 'Tell us about your programme, target buyers and market priorities.')}</p></div>
        <a class="btn btn-gold" href="mailto:Hello@koonafa.com?subject={subject}">Email Koonafa Global</a>
      </div>
    </section>
  </main>
{FOOTER}
</body>
</html>
'''


def expected_files():
    topics = load_topics()
    files = {topic.path: render(topic, topics) for topic in topics.values()}
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for topic in topics.values():
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text = HOST + topic.url
        ET.SubElement(entry, 'lastmod').text = CONTENT_UPDATED
    ET.indent(sitemap, space='  ')
    files[ROOT / 'sitemap-india-tourism-trade.xml'] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(sitemap, encoding='unicode') + '\n'
    )
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    files = expected_files()
    if args.check:
        stale = [path for path, content in files.items() if not path.is_file() or path.read_text() != content]
        extra = set((ROOT / TOPIC_ROOT.lstrip('/')).rglob('index.html')) - files.keys()
        if stale or extra:
            parser.exit(1, '\n'.join(str(path) for path in [*stale, *sorted(extra)]) + '\n')
    else:
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(f'{"Verified" if args.check else "Rendered"} 100 tourism and trade pages and their sitemap.')
