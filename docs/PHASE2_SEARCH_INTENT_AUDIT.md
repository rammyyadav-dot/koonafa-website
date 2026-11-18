# Phase 2: content-intent and AEO technical audit

This phase **does not edit or generate customer-facing copy, images, CSS, page markup, or navigation**.

`python3 scripts/audit_search_intent.py --output audit/search-intent.json`

The audit inventories current root and `gsa/` HTML files and produces machine-readable, deterministic observations:
- canonical URL and metadata (title, description, H1)
- parse validity of JSON-LD (error gate)
- structured-data types (no unsupported claims are injected)
- duplicate title/description/canonical groups for editorial review
- internal link counts to existing pages and underlinked GSA pages
- association to curated clusters from `config/ecosystem.json`

**Warnings are not fixes.** Duplicate titles or descriptions may be intentional; internal-link counts are a heuristic, not Google's crawl graph, and no live indexability, keyword ranking or backlink conclusion can be inferred. Do not automatically rewrite titles, descriptions, headings, schemas, or content on the basis of this report.

Any future on-page changes need explicit page-by-page approval and preservation of the existing typography, photography, layout, content, and page-specific brand kit. The repo's canonical host rules should be resolved with production hosting before changing URLs.
