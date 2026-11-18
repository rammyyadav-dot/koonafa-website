# Koonafa Digital Ecosystem — Phase 1 implementation

This phase introduces non-visual infrastructure only. It does **not** change a page's wording, photographs, typography, colours, spacing, or layout.

## Existing journeys (no URL migrations)

- `/`: Marketing and advertising company homepage
- `/global`: Global hospitality, tourism marketing and representation
- `/GSA`: India GSA representation
- `/DMC`: Overseas DMC representation in India
- `/gsa/`: Existing specialist GSA directory
- `/About`, `/packages`, `/case-studies`, `/patna-brochure`: existing support journeys

All are listed in `config/ecosystem.json`. They do not imply a physical branch office, legal entity or new domain.

## Existing SEO & AEO content clusters (curation, not generated copy)

The manifest maps existing URLs to five themes:
1. Hotels & Resorts
2. DMCs & Tourism Boards
3. MICE & Corporate
4. Aviation & Mobility
5. Market Intelligence & Trade

This internal mapping is deliberately **not** a public navigation or new page. Do not manufacture location variants or publish programmatic landing pages until each has differentiated content, verifiable market-specific expertise and a useful commercial conversion path.

## SEO release contract

Run `python3 scripts/check_ecosystem.py` from the repository root. The standard-library-only checker enforces:
- valid XML sitemap and unique URL entries;
- published ecosystem site source files exist;
- exactly one canonical URL, H1 and title on checked entrypoints and curated cluster pages;
- canonical HTTPS host within Koonafa and canonical presence in sitemap;
- cluster pages exist without overlap.

Warnings identify missing descriptions and noindex content. The workflow runs on PR and main changes. This is a smoke test, not a comprehensive structured-data correctness or live-crawl check.

## Preservation boundaries

Agency (black/white/red) and Global hospitality (Royal Brown/Sandstone/warm neutrals) remain distinct existing page themes. This phase does not touch them. Preserve the current user-facing page structures, headings, imagery and styling.

## Phase 2 (separate approval/review)

Audit all GSA pages for search intent overlap, factual claims and duplication; verify hosting/DNS and canonical www behavior; add structured data linting and live site route checks; assess analytics and consent requirements; only then consider content architecture/framework migrations.
