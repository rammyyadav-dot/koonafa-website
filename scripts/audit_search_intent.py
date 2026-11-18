#!/usr/bin/env python3
"""Read-only SEO/AEO inventory across existing pages. Never writes HTML or media.

Usage: python3 scripts/audit_search_intent.py --output audit/search-intent.json
"""
from __future__ import annotations

import argparse
import collections
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://koonafa.com"
PAGES = (sorted(ROOT.glob("*.html")) + sorted((ROOT / "gsa").glob("*.html")) + sorted((ROOT / "global" / "UAE").rglob("index.html")))


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.canonical = []
        self.links = []
        self.headings = []
        self.titles = []
        self.structured_data = []
        self.current = None
        self.buffer = []
        self.jsonld = False

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "link" and "canonical" in attr.get("rel", "").lower().split():
            self.canonical.append(attr.get("href", ""))
        if tag == "meta":
            key = attr.get("name", attr.get("property", "")).lower()
            if key:
                self.meta[key] = attr.get("content", "")
        if tag == "a":
            self.links.append(attr.get("href", ""))
        if tag in ("h1", "h2", "title"):
            self.current = tag
            self.buffer = []
        if tag == "script" and attr.get("type", "").lower() == "application/ld+json":
            self.jsonld = True
            self.buffer = []

    def handle_data(self, data):
        if self.current or self.jsonld:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if self.current == tag:
            value = re.sub(r"\s+", " ", "".join(self.buffer)).strip()
            if tag == "title":
                self.titles.append(value)
            else:
                self.headings.append({"level": tag, "text": value})
            self.current = None
            self.buffer = []
        if tag == "script" and self.jsonld:
            self.structured_data.append("".join(self.buffer))
            self.jsonld = False
            self.buffer = []


def normalize(text):
    return re.sub(r"\s+", " ", html.unescape(text or "").lower()).strip()


def canonical_key(url):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    path = (parsed.path or "/").rstrip("/") or "/"
    return host, path.lower()


def analyze():
    config = json.loads((ROOT / "config/ecosystem.json").read_text(encoding="utf-8"))
    cluster_for = {p: c["id"] for c in config["clusters"] for p in c["existing_pages"]}
    known = {p.relative_to(ROOT).as_posix(): p for p in PAGES}
    records, errors, warnings = [], [], []
    all_canonical, titles, descriptions = collections.defaultdict(list), collections.defaultdict(list), collections.defaultdict(list)
    for file in PAGES:
        relative = file.relative_to(ROOT).as_posix()
        parser = PageParser()
        parser.feed(file.read_text(encoding="utf-8"))
        canonical = parser.canonical[0] if parser.canonical else ""
        if canonical:
            all_canonical[canonical_key(canonical)].append(relative)
        title = parser.titles[0] if parser.titles else ""
        desc = parser.meta.get("description", "")
        if title:
            titles[normalize(title)].append(relative)
        if desc:
            descriptions[normalize(desc)].append(relative)
        schema_types = []
        for i, item in enumerate(parser.structured_data):
            try:
                parsed = json.loads(item)
                obj = parsed if isinstance(parsed, list) else [parsed]
                for node in obj:
                    if isinstance(node, dict):
                        t = node.get("@type")
                        schema_types.extend(t if isinstance(t, list) else [t] if t else [])
            except json.JSONDecodeError as exc:
                errors.append({"path": relative, "code": "invalid_jsonld", "detail": f"script #{i+1}: {exc.msg}"})
        if len(parser.canonical) != 1:
            warnings.append({"path": relative, "code": "canonical_count", "count": len(parser.canonical)})
        h1 = [h["text"] for h in parser.headings if h["level"] == "h1"]
        if len(h1) != 1:
            warnings.append({"path": relative, "code": "h1_count", "count": len(h1)})
        if not desc:
            warnings.append({"path": relative, "code": "description_missing"})
        if not schema_types and "noindex" not in parser.meta.get("robots", "").lower():
            warnings.append({"path": relative, "code": "schema_missing"})
        internal = []
        for href in parser.links:
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            absolute = urljoin(canonical or BASE + "/" + relative, href)
            parsed = urlparse(absolute)
            if (parsed.hostname or "").removeprefix("www.").lower() != "koonafa.com":
                continue
            if absolute not in internal:
                internal.append(absolute)
        records.append({"path": relative, "canonical": canonical, "title": title,
            "description": desc, "h1": h1, "schema_types": schema_types,
            "cluster": cluster_for.get(relative), "internal_links": internal,
            "robots": parser.meta.get("robots", "")})
    duplication = {"titles": [], "descriptions": [], "canonicals": []}
    for field, index in (("titles", titles), ("descriptions", descriptions), ("canonicals", all_canonical)):
        for key, pages in index.items():
            if len(pages) > 1 and not (field == "canonicals" and all("noindex" in next(r["robots"] for r in records if r["path"] == p).lower() for p in pages[1:])):
                duplication[field].append({"value": str(key)[:160], "paths": pages})
    canonical_lookup = {canonical_key(r["canonical"]): r["path"] for r in records if r["canonical"]}
    edges = collections.defaultdict(set)
    for item in records:
        for url in item["internal_links"]:
            target = canonical_lookup.get(canonical_key(url))
            if target and target != item["path"]:
                edges[target].add(item["path"])
    for item in records:
        item["incoming_internal_page_count"] = len(edges[item["path"]])
        del item["internal_links"]
    weak = sorted(({"path": r["path"], "incoming_links": r["incoming_internal_page_count"],
        "cluster": r["cluster"]} for r in records if r["path"].startswith("gsa/") and
        r["incoming_internal_page_count"] < 2), key=lambda r: (r["incoming_links"], r["path"]))
    return {"scope": "repository-source, no live Google Search Console data",
        "summary": {"html_pages": len(records), "gsa_pages": sum(r["path"].startswith("gsa/") for r in records),
        "invalid_jsonld": len(errors), "duplicate_title_groups": len(duplication["titles"]),
        "duplicate_description_groups": len(duplication["descriptions"]),
        "duplicate_canonical_groups": len(duplication["canonicals"]),
        "low_internal_link_gsa_pages": len(weak)},
        "clusters": [{"id": c["id"], "existing_pages": c["existing_pages"]} for c in config["clusters"]],
        "duplicate_metadata": duplication, "weak_internal_link_pages": weak,
        "errors": errors, "warnings": warnings, "pages": records}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="", help="Optional JSON output path (not checked into the site)")
    args = parser.parse_args()
    report = analyze()
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    if report["errors"]:
        for error in report["errors"][:15]:
            print("ERROR", error)
        raise SystemExit(1)
    print("PASS: valid JSON-LD in existing pages; duplicate and linking opportunities reported (not auto-edited)")


if __name__ == "__main__":
    main()
