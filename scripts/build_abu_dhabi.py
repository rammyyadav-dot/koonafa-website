"""Build the Abu Dhabi service directory and its static landing pages."""
import csv
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
HOST = "https://www.koonafa.com"
REGION = "/global/UAE/"
HUB = REGION + "abu-dhabi/"
HUB_FILE = ROOT / HUB.strip("/") / "index.html"
IMAGE = "/hero-infinity-pool.png"
GROUPS = {
    "agency": "Marketing & Advertising",
    "representation": "Hospitality & Tourism Representation",
    "aviation": "Airlines & General Sales Agency",
    "hospitality": "Hotels, Resorts, DMCs, Tourism Boards & Bedbanks",
    "digital": "Digital & Performance Marketing",
    "studio": "Web Design, Video & Creative Production",
}
RELATED = (
    (17, 19, 24, 29, 30, 46, 47, 51, 54, 85, 92),
    (20, 25, 35, 48, 55),
    (16, 21, 31, 49, 53),
    (28, 50, 56, 60),
    (36, 37, 38, 39, 41, 44, 45),
    (61, 66, 71, 72, 80, 99),
    (62, 64, 65, 67, 73, 79, 93),
    (81, 83, 86, 90, 95, 96),
    (82, 84, 85, 88, 89, 91, 97, 98),
)


def url(topic):
    return HUB + topic["slug"] + "/"


def list_links(topics):
    links = (f'<li><a href="{url(topic)}">{escape(topic["heading"])}</a></li>'
             for topic in topics)
    return '<ul class="service-links">' + "\n".join(links) + "</ul>"


def replace_block(document, label, body, before):
    start = f"<!-- {label} START -->"
    end = f"<!-- {label} END -->"
    block = f"{start}\n{body}\n{end}\n"
    if start in document:
        return re.sub(re.escape(start) + r".*?" + re.escape(end) + r"\n?",
                      lambda _: block, document, flags=re.S)
    if before not in document:
        raise ValueError(f"Missing insertion point for {label}")
    return document.replace(before, block + before, 1)


def directory(topics):
    navigation = "".join(f'<a href="#{key}">{escape(label)}</a>'
                         for key, label in GROUPS.items())
    sections = "".join(
        f'<div class="directory-group" id="{key}"><h3>{escape(label)}</h3>'
        f'{list_links(t for t in topics if t["cluster"] == key)}</div>'
        for key, label in GROUPS.items()
    )
    return f"""<section class="section cream" id="services" aria-labelledby="services-title">
<div class="wrap directory">
<h2 class="heading" id="services-title">Explore Abu Dhabi <em>services.</em></h2>
<p>Find trade representation, distribution and marketing services for airlines, hotels, resorts, DMCs, tourism boards and bedbanks.</p>
<nav class="directory-nav" aria-label="Service categories">{navigation}</nav>
{sections}
</div></section>"""


def page(topic, related):
    heading, tagline, approach, deliverable = (
        topic[key] for key in ("heading", "tagline", "approach", "deliverable")
    )
    title = heading + " | Koonafa Global"
    desc = tagline + ". " + deliverable + " from Koonafa Global."
    canonical = HOST + url(topic)
    group = topic["cluster"]
    area = {
        3: "United Arab Emirates", 14: "Gulf Cooperation Council",
        18: "Middle East", 22: "Middle East", 23: "Gulf Cooperation Council",
        24: "Middle East", 27: "Dubai, United Arab Emirates",
        31: "Middle East", 38: "Middle East", 44: "Middle East",
    }.get(topic["number"], "Abu Dhabi, United Arab Emirates")
    crumbs = [("Global", "/global"), ("UAE Markets", REGION), ("Abu Dhabi", HUB), (heading, url(topic))]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Service", "name": heading, "url": canonical,
             "description": approach, "areaServed": {"@type": "Place", "name": area},
             "provider": {"@type": "Organization", "name": "Koonafa Global", "url": HOST + "/global"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": number, "name": label, "item": HOST + link}
                for number, (label, link) in enumerate(crumbs, 1)
            ]},
        ],
    }
    breadcrumb = '<span aria-hidden="true">/</span>'.join(
        f'<a href="{link}">{label}</a>' for label, link in crumbs[:-1]
    ) + '<span aria-hidden="true">/</span><span aria-current="page">' + escape(heading) + '</span>'
    contact = "mailto:Hello@koonafa.com?subject=" + quote(heading + " enquiry")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{HOST}/og-image.jpg">
<meta property="og:site_name" content="Koonafa Global">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(desc)}">
<meta name="twitter:image" content="{HOST}/og-image.jpg">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="{REGION}emirates.css">
<link rel="stylesheet" href="{HUB}services.css">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace("<", chr(92) + "u003c")}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast"><div class="wrap mast-inner">
<a class="brand" href="/global">KOONAFA<small>Hospitality Marketing &amp; Representation</small></a>
<nav class="primary-nav" aria-label="Main navigation"><a href="/global">Global</a><a href="{HUB}#services">Abu Dhabi Services</a><a class="nav-contact" href="#contact">Partner With Us</a></nav>
</div></header>
<main id="main">
<section class="hero service-hero" aria-labelledby="page-title">
<img class="hero-photo" src="{IMAGE}" alt="" fetchpriority="high" decoding="async">
<div class="wrap hero-body"><nav class="crumb" aria-label="Breadcrumb">{breadcrumb}</nav>
<p class="eyebrow">{escape(GROUPS[group])}</p>
<h1 id="page-title">{escape(heading)}</h1>
<p class="hero-tag">{escape(tagline)}.</p>
<div class="btns"><a class="btn btn-gold" href="{contact}">Discuss Your Brief</a><a class="btn btn-light" href="#scope">Explore the Service</a></div>
</div></section>
<section class="section" id="scope"><div class="wrap two-col">
<h2 class="heading">How we can <em>help.</em></h2>
<div class="service-copy"><p>{escape(approach)}</p><dl><dt>Typical deliverables</dt><dd>{escape(deliverable)}.</dd></dl>
<dl><dt>What to measure</dt><dd>{escape(topic["measurement"])}.</dd></dl></div>
</div></section>
<section class="section cream"><div class="wrap">
<h2 class="heading">Related <em>services.</em></h2>
{list_links(related)}
<div class="crosslinks"><a href="{HUB}#{group}">Explore {escape(GROUPS[group])}</a></div>
</div></section>
<section class="callout" id="contact"><div class="wrap callout-inner">
<div><h2>Tell us about <em>your brief.</em></h2><p>Share your target audience, market and timeline so we can scope the work.</p></div>
<a class="btn" href="{contact}">Hello@koonafa.com</a></div></section>
</main>
<footer class="service-footer"><div class="wrap">
<a class="brand" href="/global">KOONAFA</a><p>Bespoke Craftsmanship. Global Reach.</p>
<nav class="crosslinks" aria-label="Footer navigation"><a href="/global">Global Services</a><a href="{REGION}">UAE Markets</a><a href="{HUB}#services">Abu Dhabi Services</a><a href="/About">About Us</a></nav>
</div></footer>
</body></html>
"""


def build():
    with (ROOT / "config/abu-dhabi-topics.tsv").open(newline="", encoding="utf-8") as source:
        topics = list(csv.DictReader(source, delimiter="\t"))
    if len(topics) != 100 or len({url(topic) for topic in topics}) != 100:
        raise ValueError("Expected 100 unique Abu Dhabi service URLs")
    for idx, topic in enumerate(topics, 1):
        topic["number"] = idx

    for topic in topics:
        match = next((group for group in RELATED if topic["number"] in group), ())
        preferred = [topics[number - 1] for number in match]
        neighbours = sorted((t for t in topics if t["cluster"] == topic["cluster"]),
                            key=lambda t: abs(t["number"] - topic["number"]))
        related = []
        for other in preferred + neighbours:
            if other != topic and other not in related:
                related.append(other)
        path = ROOT / url(topic).strip("/") / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(page(topic, related[:3]), encoding="utf-8")

    hub = HUB_FILE.read_text(encoding="utf-8")
    stylesheet = f'<link rel="stylesheet" href="{HUB}services.css">'
    hub = replace_block(hub, "ABU DHABI SERVICE CSS", stylesheet, "</head>")
    hub = replace_block(hub, "ABU DHABI SERVICE DIRECTORY", directory(topics),
                        '<section class="callout" id="contact">')
    hub = hub.replace('<a href="#expertise">Expertise</a>', '<a href="#services">Services</a>')
    hub = hub.replace('href="#expertise">Explore Abu Dhabi', 'href="#services">Explore Abu Dhabi Services')
    HUB_FILE.write_text(hub, encoding="utf-8")

    sitemap = ROOT / "sitemap.xml"
    entries = "\n".join(f"  <url><loc>{HOST}{url(topic)}</loc></url>" for topic in topics)
    xml = replace_block(sitemap.read_text(encoding="utf-8"), "ABU DHABI SERVICES", entries, "</urlset>")
    sitemap.write_text(xml, encoding="utf-8")


if __name__ == "__main__":
    build()
