# Koonafa Global — UAE SEO execution log
Date: 2026-11-23
Scope: /global/UAE/ and eight specialist landing pages

## Baseline (Google Search Console export uploaded 23 Nov 2026)
Data availability: daily export 8–21 Nov 2026 (not a complete three-month period).
- Search clicks: 6
- Impressions: 156
- CTR: 3.85%
- Average position: 12.58
- UAE: 12 impressions, 0 clicks, 0% CTR, average position 19.75.
- Eight new SEO URLs were added after the export dates, so their indexing cannot be judged from this file.
Do not report these as leads or Dubai-city-only data.

## Changes committed on 23 Nov 2026
1. Align canonical and Open Graph URLs for all eight specialist UAE landing pages to the non-www hostname (koonafa.com) already used by the sitemap and UAE hub.
2. Rewrite eight service meta descriptions individually, between 127 and 145 characters.
3. Add service-topic labels, locale and image social metadata to specialist pages.
4. Add lightweight click events to track mailto enquiry and contact CTA interactions if an existing GA4 gtag or GTM dataLayer is loaded. Avoid double firing.
5. Add contextual links from /global/UAE/dubai/ to six specialist service URLs; original UAE hub already links all eight services.
6. Existing sitemap.xml contains all eight URLs.

## Important outstanding checks — NOT yet verified
- Host-level permanent redirects from https://www.koonafa.com/* to https://koonafa.com/*, including no chains and avoiding conflicts with /About: configure at CDN/hosting level only after determining platform and testing both hosts.
- Verify deployment and each URL's HTTP status (200), robots allowance, rendered canonical, mobile rendering, and Rich Results / schema validity.
- Google Search Console: inspect each URL; request indexing of valid live URLs; resubmit https://koonafa.com/sitemap.xml; verify preferred Google-selected canonical and indexed status.
- GA4/GTM: add the actual owner-approved measurement ID or container ID. Event hooks alone do NOT transmit telemetry without a loaded analytics system. Define `email_enquiry` and `contact_cta` as custom events, and mark the qualified enquiry event as key event only after validation.
- Google Business Profile: confirm an eligible genuine Dubai office / staffed service-area model; do not create a listing using an unstaffed virtual office. Verify ownership before any profile changes.
- Trust: add real permitted client logos, case studies, project outcomes, staff biographies and trade relationships only with supporting evidence.
- Core Web Vitals/PageSpeed: run independent mobile and desktop measurements on live deployed URLs.
- Measure SEO in GSC filtered to /global/UAE/ and separately from print-related subdomains or queries. Monitor non-branded UAE impressions, indexed target URLs, CTR and qualified enquiries.

## Service pages for GSC URL Inspection
- https://koonafa.com/global/UAE/hospitality-marketing-dubai/
- https://koonafa.com/global/UAE/hotel-sales-representation-dubai/
- https://koonafa.com/global/UAE/tourism-marketing-dubai/
- https://koonafa.com/global/UAE/hotel-marketing-uae/
- https://koonafa.com/global/UAE/dmc-representation-middle-east/
- https://koonafa.com/global/UAE/hospitality-pr-dubai/
- https://koonafa.com/global/UAE/tourism-board-representation-gcc/
- https://koonafa.com/global/UAE/hotel-gsa-uae/

## Measurement definitions
- UAE CTR = UAE organic clicks / UAE organic impressions.
- Indexed page % = verified indexed target service pages / 8 * 100.
- Qualified lead conversion = qualified UAE service enquiries / UAE organic landing sessions.
- Search visibility: compare the same UAE geography, query set, date duration and search type.
- No rank or revenue guarantees.
