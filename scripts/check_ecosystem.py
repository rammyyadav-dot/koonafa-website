#!/usr/bin/env python3
"""Non-visual SEO, AEO and ecosystem contract checks. No site files are rewritten."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "ecosystem.json"
SITEMAP = ROOT / "sitemap.xml"

class Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = []
        self.robots = ""
        self.description = ""
        self.h1 = 0
        self.title = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "link" and data.get("rel", "").lower() == "canonical":
            self.canonical.append(data.get("href", ""))
        if tag == "meta" and data.get("name", "").lower() == "robots":
            self.robots = data.get("content", "")
        if tag == "meta" and data.get("name", "").lower() == "description":
            self.description = data.get("content", "")
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title += 1

def check():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    errors, warnings = [], []
    try:
        sitemap_paths = {SITEMAP, *(ROOT / site["sitemap"] for site in config["sites"] if "sitemap" in site)}
        sitemap = [node.text.strip() for path in sorted(sitemap_paths)
                   for node in ET.parse(path).findall(".//{*}loc") if node.text]
    except (ET.ParseError, OSError) as exc:
        return [f"Invalid sitemap: {exc}"], []
    if len(sitemap) != len(set(sitemap)):
        errors.append("Duplicate URLs in sitemap")
    sitemap_set = set(sitemap)
    if len(config["sites"]) != len({site["path"] for site in config["sites"]}):
        errors.append("Duplicate site routes in ecosystem manifest")
    seen_cluster_pages = {}
    for cluster in config["clusters"]:
        if not cluster["existing_pages"]:
            errors.append(f"Empty content cluster: {cluster['id']}")
        for page in cluster["existing_pages"]:
            if page in seen_cluster_pages:
                errors.append(f"Cluster page duplicated: {page}")
            seen_cluster_pages[page] = cluster["id"]
            if not page.startswith("gsa/") or not (ROOT / page).is_file():
                errors.append(f"Missing or unexpected cluster page: {page}")
    required = [site["entry"] for site in config["sites"]]
    for path in required + list(seen_cluster_pages):
        file = ROOT / path
        if not file.is_file():
            errors.append(f"Missing HTML source: {path}")
            continue
        parser = Meta()
        parser.feed(file.read_text(encoding="utf-8"))
        if len(parser.canonical) != 1:
            errors.append(f"{path}: expected exactly one canonical, found {len(parser.canonical)}")
            continue
        canonical = parser.canonical[0]
        parsed = urlparse(canonical)
        if parsed.scheme != "https" or parsed.netloc not in ("koonafa.com", "www.koonafa.com"):
            errors.append(f"{path}: unexpected canonical domain {canonical}")
        if parser.title != 1 or parser.h1 != 1:
            errors.append(f"{path}: expected one title and one H1; got {parser.title}, {parser.h1}")
        if not parser.description.strip():
            warnings.append(f"{path}: missing meta description")
        if "noindex" in parser.robots.lower():
            warnings.append(f"{path}: page is noindex")
        elif canonical not in sitemap_set:
            errors.append(f"{path}: canonical missing from sitemap: {canonical}")
    for url in sitemap:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ("koonafa.com", "www.koonafa.com"):
            errors.append(f"Sitemap URL is outside Koonafa: {url}")
    if len(sitemap) < 100:
        warnings.append(f"Unexpectedly small sitemap ({len(sitemap)} URLs)")
    return errors, warnings

if __name__ == "__main__":
    errors, warnings = check()
    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("FAIL:", e)
    print(f"Ecosystem manifest: {len(json.loads(CONFIG.read_text())['sites'])} journeys; 5 curated SEO clusters")
    if errors:
        sys.exit(1)
    print("PASS: canonical, sitemap, metadata and content-cluster contract")
