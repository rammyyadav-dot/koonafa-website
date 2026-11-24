#!/usr/bin/env python3
"""Koonafa UAE SEO source and live checks. stdlib only, no credentials."""
import argparse
import datetime as dt
import html.parser
import json
import pathlib
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://www.koonafa.com"
SLUGS = [
    "hospitality-marketing-dubai",
    "hotel-sales-representation-dubai",
    "tourism-marketing-dubai",
    "hotel-marketing-uae",
    "dmc-representation-middle-east",
    "hospitality-pr-dubai",
    "tourism-board-representation-gcc",
    "hotel-gsa-uae",
]

class HeadParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.in_title, self.h1, self.in_h1 = "", False, [], False
        self.description, self.canonical = "", ""
        self.robots = ""
        self.jsonld = []
        self.in_jsonld = False
        self.schema_buffer = ""
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "title": self.in_title = True
        if tag == "h1": self.in_h1 = True; self.h1.append("")
        if tag == "meta" and d.get("name", "").lower() == "description": self.description = d.get("content", "")
        if tag == "meta" and d.get("name", "").lower() == "robots": self.robots = d.get("content", "")
        if tag == "link" and d.get("rel", "").lower() == "canonical": self.canonical = d.get("href", "")
        if tag == "script" and d.get("type") == "application/ld+json": self.in_jsonld = True; self.schema_buffer = ""
    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_h1 and self.h1: self.h1[-1] += data
        if self.in_jsonld: self.schema_buffer += data
    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "h1": self.in_h1 = False
        if tag == "script" and self.in_jsonld:
            try: self.jsonld.append(json.loads(self.schema_buffer))
            except json.JSONDecodeError: self.jsonld.append(None)
            self.in_jsonld = False

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "KoonafaSEOMonitor/1.0 (+https://koonafa.com/)"})
    try:
        with urllib.request.urlopen(req, timeout=18) as r:
            body = r.read(1000000).decode("utf-8", errors="replace")
            return {"status": r.status, "final_url": r.url, "body": body}
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        return {"status": getattr(exc, "code", None), "error": str(exc)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="Also inspect live canonical, status and apex redirect")
    args = ap.parse_args()
    sitemap = ROOT / "sitemap.xml"
    all_urls = set()
    if sitemap.exists():
        root = ET.parse(sitemap).getroot()
        all_urls = {node.text.strip() for node in root.iter() if node.tag.endswith("}loc") and node.text}
    results = []
    for slug in SLUGS:
        path = ROOT / "global" / "UAE" / slug / "index.html"
        url = BASE + "/global/UAE/" + slug + "/"
        item = {"slug": slug, "url": url, "checks": {}, "warnings": []}
        if not path.exists():
            item["checks"]["file_exists"] = False
            results.append(item)
            continue
        p = HeadParser()
        p.feed(path.read_text(encoding="utf-8"))
        item["title"] = p.title.strip()
        item["description_length"] = len(p.description)
        item["checks"] = {
            "file_exists": True,
            "one_h1": len(p.h1) == 1,
            "title": bool(p.title.strip()),
            "meta_description": 90 <= len(p.description) <= 170,
            "canonical": p.canonical == url,
            "sitemap": url in all_urls,
            "schema_valid_json": bool(p.jsonld) and all(x is not None for x in p.jsonld),
            "indexable_meta": "noindex" not in p.robots.lower(),
        }
        if args.live:
            live = fetch(url)
            item["live"] = {k: v for k, v in live.items() if k != "body"}
            item["checks"]["live_200"] = live.get("status") == 200
            if live.get("status") == 200:
                lp = HeadParser()
                lp.feed(live["body"])
                item["checks"]["rendered_canonical"] = lp.canonical == url
            apex = fetch(url.replace("https://www.koonafa.com", "https://koonafa.com"))
            item["apex_probe"] = {k: v for k, v in apex.items() if k != "body"}
            item["checks"]["apex_resolves_to_www"] = apex.get("final_url") == url
        results.append(item)
    checks = [v for item in results for v in item["checks"].values()]
    report = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "live_probe_enabled": args.live,
        "checks_passed": sum(checks),
        "checks_total": len(checks),
        "source_pass_percentage": round(100 * sum(checks)/len(checks), 2) if checks else None,
        "note": "This is a checklist completion percentage, not a Google ranking or Core Web Vitals score.",
        "pages": results,
    }
    output = ROOT / "seo-reports"
    output.mkdir(exist_ok=True)
    (output / "uae-seo-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# UAE SEO validation", "", f"Generated UTC: {report['generated_utc']}", "",
             f"Checks passed: {report['checks_passed']} / {report['checks_total']}", "",
             "| Page | Source checks | Live |", "|---|---|---|"]
    for item in results:
        checks = item["checks"]
        source = f"{sum(checks.values())}/{len(checks)}"
        live = str(item.get("live", {}).get("status", "Not checked"))
        lines.append(f"| {item['slug']} | {source} | {live} |")
    lines += ["", "## Follow-up", "Confirm indexed status individually in Google Search Console URL Inspection.",
              "Confirm analytics consent and event receipt in GA4 DebugView.",
              "Only an eligible verified business can create or claim a Google Business Profile."]
    (output / "uae-seo-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["checks_passed"], "total": report["checks_total"], "live": args.live}))
    if not all(item["checks"].get("file_exists") for item in results):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
