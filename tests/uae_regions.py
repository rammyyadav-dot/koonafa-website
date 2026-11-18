"""Static SEO and internal-navigation contract for all seven UAE emirate pages."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
UAE = ROOT / "global" / "UAE"
NAMES = {
    "dubai": "Dubai",
    "abu-dhabi": "Abu Dhabi",
    "sharjah": "Sharjah",
    "ras-al-khaimah": "Ras Al Khaimah",
    "fujairah": "Fujairah",
    "ajman": "Ajman",
    "umm-al-quwain": "Umm Al Quwain",
}

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.titles = []
        self.canonicals = []
        self.h1_count = 0
        self.descriptions = []
        self.images = []
        self.jsonld = []
        self._tag = None
        self._buffer = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "img":
            self.images.append(a)
        if tag == "meta" and a.get("name") == "description":
            self.descriptions.append(a.get("content", ""))
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href", ""))
        if tag == "h1":
            self.h1_count += 1
        if tag == "title":
            self._tag = tag
            self._buffer = []
        if tag == "script" and a.get("type") == "application/ld+json":
            self._tag = "script"
            self._buffer = []

    def handle_data(self, data):
        if self._tag is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == self._tag:
            if tag == "title":
                self.titles.append("".join(self._buffer).strip())
            if tag == "script":
                self.jsonld.append(json.loads("".join(self._buffer)))
            self._tag = None
            self._buffer = []

def parse(path):
    doc = Document()
    doc.feed(path.read_text(encoding="utf-8"))
    return doc

parent = parse(UAE / "index.html")
sitemap = {x.text for x in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc")}
config = json.loads((ROOT / "config" / "ecosystem.json").read_text())
paths = {x["path"]: x["entry"] for x in config["sites"]}
titles = set()
descs = set()
assert len(NAMES) == 7
for slug, name in NAMES.items():
    uri = f"/global/UAE/{slug}/"
    canonical = "https://koonafa.com" + uri
    page = UAE / slug / "index.html"
    assert page.is_file(), page
    d = parse(page)
    assert d.h1_count == 1, (slug, d.h1_count)
    assert len(d.titles) == len(d.canonicals) == len(d.descriptions) == 1, slug
    assert d.canonicals == [canonical], slug
    assert canonical in sitemap, slug
    assert paths.get(uri) == f"global/UAE/{slug}/index.html", slug
    assert d.titles[0] not in titles, ("duplicate title", slug)
    assert d.descriptions[0] not in descs, ("duplicate description", slug)
    titles.add(d.titles[0])
    descs.add(d.descriptions[0])
    assert any(name in title for title in d.titles), slug
    assert len(d.jsonld) == 1, slug
    nodes = d.jsonld[0].get("@graph", [])
    assert {"WebPage", "Service", "BreadcrumbList"} <= {n.get("@type") for n in nodes}, slug
    assert uri in parent.links, ("missing overview navigation", slug)
    assert "/global/UAE/" in d.links, ("missing back-link", slug)
    assert d.images and all(im.get("alt") for im in d.images), slug
    assert len([im for im in d.images if im.get("fetchpriority") == "high"]) == 1, slug
    assert (UAE / "emirates.css").is_file()

assert len([link for link in parent.links if re.fullmatch(r"/global/UAE/[^/]+/", link)]) == 7
print("PASS seven unique UAE pages, structured data, canonical URLs, sitemap, imagery and overview links")
