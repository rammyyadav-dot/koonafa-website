"""Generate the India airline representation hub, spokes and XML sitemap."""
import csv
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
HOST = "https://www.koonafa.com"
HUB = "/global/india/airline-representation-in-india/"
SOCIAL_IMAGE = HOST + "/og-image.jpg"
SOCIAL_ALT = "Koonafa Global brand preview"
GROUPS = {
    "representation": "Airline Representation & GSA",
    "entry": "Market Entry & Launch Readiness",
    "cities": "India Cities & Airport Catchments",
    "distribution": "Distribution, Ticketing & Finance",
    "specialist": "Cargo, Charter & Specialist Travel",
    "marketing": "Airline Marketing, PR & Trade Events",
    "corridors": "International Airline Corridors",
    "guides": "Airline Commercial Decision Guides",
    "trade": "Trade, Corporate & Proposal Enquiries",
}


def path(topic):
    return HUB + (topic["slug"] + "/" if topic["slug"] else "")


def links(topics):
    return '<ul class="air-list">' + "\n".join(
        f'<li><a href="{path(t)}">{escape(t["heading"])}</a></li>' for t in topics
    ) + '</ul>'


def directory(topics):
    sections = "\n".join(
        f'<section class="air-group" id="{key}"><h3>{escape(name)}</h3>'
        f'{links(t for t in topics if t["group"] == key)}</section>'
        for key, name in GROUPS.items()
    )
    nav = "".join(f'<a href="#{key}">{escape(name)}</a>' for key, name in GROUPS.items())
    return f'''<section class="section cream" id="directory"><div class="wrap">
<h2 class="heading">Explore <em>airline representation in India.</em></h2>
<nav class="crosslinks" aria-label="Airline service topics">{nav}</nav>
{sections}</div></section>'''


def related(topic, topics):
    neighbours = [t for t in topics[1:-1] if t != topic and t["group"] == topic["group"]]
    offset = next(i for i, t in enumerate(topics) if t == topic)
    order = {t["slug"]: i for i, t in enumerate(topics)}
    neighbours.sort(key=lambda t: abs(order[t["slug"]] - offset))
    part = links(neighbours[:3])
    return f'''<section class="section cream"><div class="wrap">
<h2 class="heading">Related <em>airline topics.</em></h2>{part}
<div class="crosslinks"><a href="{HUB}#{topic["group"]}">{escape(GROUPS[topic["group"]])}</a></div>
</div></section>'''


def render(topic, topics):
    heading = topic["heading"]
    canonical = HOST + path(topic)
    body = topic["body"]
    tagline = topic["tagline"] + "."
    description = tagline + " " + topic["deliverable"] + "."
    if len(description) > 160:
        description = tagline
    social_description = body if len(body) <= 180 else body.split(". ", 1)[0].rstrip(".") + "."
    title = topic["seo_title"]
    is_hub = not topic["slug"]
    proposal = path(topics[-1])
    enquiry = "mailto:Hello@koonafa.com?subject=" + quote(heading + " enquiry")
    crumbs = [("Global", "/global"), ("India", "/india"), (topics[0]["heading"], HUB)]
    if not is_hub:
        crumbs.append((heading, path(topic)))
    crumb_html = ' <span aria-hidden="true">/</span> '.join(
        f'<a href="{link}">{escape(label)}</a>' for label, link in crumbs[:-1]
    ) + f' <span aria-hidden="true">/</span> <span aria-current="page">{escape(heading)}</span>'
    provider = {"@type": "Organization", "@id": HOST + "/global#organization",
                "name": "Koonafa Global", "url": HOST + "/global"}
    subjects = {
        "guides": {"@type": "Article", "headline": heading, "author": {"@id": provider["@id"]},
                   "mainEntityOfPage": canonical},
        "trade": {"@type": "WebPage", "name": heading, "publisher": {"@id": provider["@id"]}},
    }
    main_entity = subjects.get(topic["group"], {
        "@type": "Service", "name": heading, "provider": {"@id": provider["@id"]},
        "areaServed": {"@type": "Country", "name": "India"},
    })
    main_entity.update(url=canonical, description=description)
    schema = {"@context": "https://schema.org", "@graph": [
        provider, main_entity, {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": label, "item": HOST + link}
            for i, (label, link) in enumerate(crumbs, 1)]}]}
    schema_text = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")
    title, description, social_description = map(escape, (title, description, social_description))
    if path(topic) == proposal:
        cta, cta_label = enquiry, "Email Your Proposal Brief"
    elif topic["group"] == "trade":
        cta, cta_label = enquiry, "Email Your Enquiry"
    else:
        cta, cta_label = proposal, "Request a GSA Proposal"
    return f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content='{"article" if topic["group"] == "guides" else "website"}'>
<meta property="og:locale" content="en_IN">
<meta property="og:site_name" content="Koonafa Global">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{social_description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SOCIAL_IMAGE}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{SOCIAL_ALT}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{social_description}">
<meta name="twitter:image" content="{SOCIAL_IMAGE}">
<meta name="twitter:image:alt" content="{SOCIAL_ALT}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/india/fonts.css">
<link rel="stylesheet" href="/global/UAE/emirates.css">
<link rel="stylesheet" href="{HUB}airline.css">
<script type="application/ld+json">{schema_text}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="wrap mast-inner">
<a class="brand" href="/global">KOONAFA<small>Hospitality Marketing &amp; Representation</small></a>
<nav class="primary-nav" aria-label="Main navigation"><a href="/global">Global</a><a href="/india">India</a>
<a href="{HUB}#directory">Airline Services</a><a class="nav-contact" href="{proposal}">Request a Proposal</a></nav>
</div></header>
<main id="main">
<section class="hero air-hero" aria-labelledby="page-title">
<img class="hero-photo" src="/india/media/aviation-hero-1080.webp" srcset="/india/media/aviation-hero-640.webp 640w, /india/media/aviation-hero-1080.webp 1080w, /india/media/aviation-hero-1600.webp 1600w" sizes="100vw" alt="" width="1080" height="720" fetchpriority="high" decoding="async">
<div class="wrap hero-body"><nav class="crumb" aria-label="Breadcrumb">{crumb_html}</nav>
<p class="eyebrow">{escape(GROUPS[topic["group"]])} / India</p>
<h1 id="page-title">{escape(heading)}</h1>
<p class="hero-tag">{escape(tagline)}</p>
<div class="btns"><a class="btn btn-gold" href="{cta}">{cta_label}</a>
<a class="btn btn-light" href="#{"directory" if is_hub else "scope"}">{"Explore Airline Topics" if is_hub else "Explore This Topic"}</a></div>
</div></section>
<section class="section" id="scope"><div class="wrap two-col">
<h2 class="heading">{"Passenger, cargo and <em>travel trade.</em>" if is_hub else "What to <em>plan for.</em>"}</h2>
<div class="air-copy"><p>{escape(body)}</p>
<dl><dt>{"Planning resources" if topic["group"] == "guides" else "What we can scope"}</dt>
<dd>{escape(topic["deliverable"])}.</dd></dl></div>
</div></section>
{directory(topics[1:]) if is_hub else related(topic, topics)}
<section class="callout" id="contact"><div class="wrap callout-inner">
<div><h2>Speak with <em>Koonafa Global.</em></h2><p>Share the carrier, routes or commercial priorities you’d like to discuss.</p></div>
<a class="btn" href="{enquiry}">Email Your Enquiry</a></div></section>
</main>
<footer class="air-footer"><div class="wrap">
<a class="brand" href="/global">KOONAFA</a>
<nav class="crosslinks" aria-label="Footer navigation"><a href="/global">Global Services</a><a href="/india">India Market</a>
<a href="/gsa/">India GSA Services</a><a href="{HUB}">Airline Representation in India</a></nav>
</div></footer>
</body></html>
'''


def build():
    with (ROOT / "config/india-airline-topics.tsv").open(newline="", encoding="utf-8") as source:
        topics = list(csv.DictReader(source, delimiter="\t"))
    if len(topics) != 100 or len({path(t) for t in topics}) != 100 or path(topics[0]) != HUB:
        raise ValueError("Expected one airline hub and 99 unique Indian airline topic pages")
    for topic in topics:
        page = ROOT / path(topic).strip("/") / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(render(topic, topics), encoding="utf-8")
    entries = "\n".join(f"  <url><loc>{HOST}{path(t)}</loc></url>" for t in topics)
    (ROOT / "sitemap-india-airline.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + entries + "\n</urlset>\n", encoding="utf-8"
    )


if __name__ == "__main__":
    build()
