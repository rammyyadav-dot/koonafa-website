"""Render the India directory topics that need a new canonical landing page."""
import csv
from html import escape
import json
from urllib.parse import quote

from build_india import FOOTER, HOST, ROOT, SOCIAL_ALT, SOCIAL_IMAGE


def render(topic):
    title = topic['title']
    path = f"/india/{topic['slug']}/"
    canonical = HOST + path
    description = topic['tagline'] + ' ' + topic['deliverable']
    if len(description) > 160:
        description = topic['tagline']
    seo_title = title + ' | Koonafa Global' if len(title) <= 43 else title
    enquiry = 'mailto:Hello@koonafa.com?subject=' + quote(title + ' enquiry')
    org = HOST + '/global#organization'
    graph = [
        {'@type': 'Organization', '@id': org, 'name': 'Koonafa Global', 'url': HOST + '/global'},
        {'@type': 'Article' if topic['slug'].startswith('appoint-') else 'Service',
         'name': title, 'url': canonical, 'description': description,
         **({'author': {'@id': org}, 'headline': title} if topic['slug'].startswith('appoint-')
            else {'provider': {'@id': org}, 'areaServed': {'@type': 'Country', 'name': 'India'}})},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': n, 'name': label, 'item': HOST + url}
            for n, (label, url) in enumerate([('Global', '/global'), ('India', '/india'), (title, path)], 1)
        ]},
    ]
    schema = json.dumps({'@context': 'https://schema.org', '@graph': graph},
                        ensure_ascii=False).replace('<', '\\u003c')
    title, description = escape(title), escape(description)
    return f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(seo_title)}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Koonafa Global">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{HOST}{SOCIAL_IMAGE}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{SOCIAL_ALT}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{HOST}{SOCIAL_IMAGE}">
<meta name="twitter:image:alt" content="{SOCIAL_ALT}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="/global/UAE/emirates.css">
<link rel="stylesheet" href="/india/india.css">
<link rel="stylesheet" href="/global-footer.css">
<script type="application/ld+json">{schema}</script>
</head>
<body class="india-page">
<a class="skip" href="#main-content">Skip to main content</a>
<header class="mast"><div class="wrap mast-inner">
<a class="brand" href="/global">KOONAFA<small>Hospitality Marketing &amp; Representation</small></a>
<nav class="primary-nav" aria-label="Primary"><a href="/global">Global</a><a href="/india">India</a><a href="/india#services">India Services</a><a class="nav-contact" href="#contact">Contact</a></nav>
</div></header>
<main id="main-content">
<nav class="india-breadcrumbs" aria-label="Breadcrumb"><ol class="wrap">
<li><a href="/global">Global</a></li><li><a href="/india">India</a></li><li aria-current="page">{title}</li>
</ol></nav>
<section class="hero india-topic-hero" aria-labelledby="page-title">
<div class="wrap hero-body">
<p class="eyebrow">Koonafa Global · India</p>
<h1 id="page-title">{title}</h1>
<p class="hero-lead">{escape(topic['tagline'])}</p>
<div class="btns"><a class="btn btn-gold" href="{enquiry}">Discuss Your Brief</a></div>
</div></section>
<section class="section"><div class="wrap two-col">
<h2 class="heading">How the <em>engagement works.</em></h2>
<div><p>{escape(topic['body'])}</p><p><strong>Typical output</strong> · {escape(topic['deliverable'])}</p></div>
</div></section>
<section class="section cream"><div class="wrap">
<h2 class="heading">{escape(topic['question'])}</h2>
<p>{escape(topic['answer'])}</p>
<div class="crosslinks"><a href="/india#services">Explore all India services</a></div>
</div></section>
<section class="callout" id="contact"><div class="wrap callout-inner">
<div><h2>Discuss your <em>India brief.</em></h2><p>Share your market, target buyers and timeline with Koonafa Global.</p></div>
<a class="btn" href="{enquiry}">Email Your Enquiry</a></div></section>
</main>
{FOOTER}
</body>
</html>
'''


def build():
    with (ROOT / 'config/india-service-topics.tsv').open(newline='', encoding='utf-8') as source:
        topics = list(csv.DictReader(source, delimiter='\t'))
    routes = [f"/india/{topic['slug']}/" for topic in topics]
    if len(routes) != len(set(routes)):
        raise ValueError('Duplicate India service route')
    for topic, route in zip(topics, routes):
        page = ROOT / route.strip('/') / 'index.html'
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(render(topic), encoding='utf-8')
    entries = '\n'.join(f'  <url><loc>{HOST}{route}</loc></url>' for route in routes)
    (ROOT / 'sitemap-india-services.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries + '\n</urlset>\n', encoding='utf-8'
    )


if __name__ == '__main__':
    build()
