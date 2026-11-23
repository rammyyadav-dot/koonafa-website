# Phase 2 — UAE SEO activation and verification
Updated: 23 November 2026
Site: https://koonafa.com/global/UAE/
Repo: rammyyadav-dot/koonafa-website

## 1. Search Console indexing
Preferred canonical hostname for this UAE section: https://koonafa.com
Property access: domain property for koonafa.com is preferred (includes www and print hostnames).
1. Open https://search.google.com/search-console and select the right domain property.
2. Submit https://koonafa.com/sitemap.xml in Sitemaps. No indexing guarantee.
3. Use URL Inspection on each of the eight urls listed in SEO-UAE-EXECUTION-2026-11-23.md.
4. For each, record: live fetch status, crawl allowed, user-declared canonical, Google-selected canonical, and indexed state.
5. If live URL is valid and not indexed, request indexing once. Recheck after Google processes it.
6. In Performance > Search results, filter by Country=United Arab Emirates, Page contains /global/UAE/, Search type=Web. Compare equal periods. Exclude print subdomain by page filter.
7. Do not equate 8 sitemap URLs with 8 indexed URLs. Status must come from URL Inspection or Page indexing report.

## 2. Canonical host & redirects
- The source now uses https://koonafa.com/global/UAE/... across eight service canonicals and the sitemap.
- CNAME in the repository says koonafa.com but does not establish the hosting vendor or prove that www redirects.
- At DNS/CDN/hosting, configure a permanent 301 or 308 redirect for https://www.koonafa.com/* -> https://koonafa.com/* preserving path and query only after identifying the actual provider and confirming the full site architecture.
- Do NOT add a cross-host wildcard in _redirects without verifying its platform support, as it could break pages or create redirect loops.
- Test both hosts with: curl -I -L -o /dev/null -w '%{http_code} %{url_effective} %{num_redirects}\n' https://www.koonafa.com/global/UAE/hospitality-marketing-dubai/
- The live SEO monitor will report this test; it does not modify DNS or redirects.

## 3. GA4 / GTM event activation
Current eight pages emit these events only if GA4 gtag or a GTM dataLayer already exists:
- email_enquiry: click on email CTA
- contact_cta: click on #contact CTA
Event parameters: service_page, link_url
There is no confirmed GA4 ID in the examined UAE page code, so collecting real analytics is NOT active.
To activate:
1. Create or select owned GA4 web data stream for koonafa.com.
2. Install approved Google Tag or GTM container via site-wide layout, with appropriate consent disclosures/configuration, and verify that measurement is allowed for visitors.
3. Check browser console and GA4 DebugView while clicking a service enquiry CTA.
4. Choose a meaningful key event: ideally a verified form-success or CRM-qualified lead, not every anchor click.
5. Verify no double firing and avoid putting PII (email address, guest/customer name, phone numbers) in event parameters.
6. Segment users/sessions by /global/UAE/ and country=United Arab Emirates. Do not infer leads from raw clicks.

## 4. Dubai local SEO / Google Business Profile
A business profile can only be set up or claimed by an eligible real business meeting Google's in-person interaction rules.
Before action, obtain from company records:
- legally accurate public business name (no search keywords appended)
- eligible staffed Dubai office or real service-area business arrangement
- verified official business telephone, hours, physical customer interaction mode
- supporting exterior/interior/on-site documentation as Google asks
- owner account access and whether a profile already exists
Never invent an office address, post client reviews on their behalf, or claim unapproved affiliations.
If ineligible, pursue organic local content and citations without creating a Google Maps listing.

## 5. Trust and content evidence
Collect permission for: real hotel client testimonials, branded case studies, property imagery, named team bios and verified partnerships.
Suggested case study structure: challenge, scope, dates, strategy, supported measurable results, attribution and client approval. No fabricated growth percentages.

## 6. Weekly automated audit
GitHub Actions: .github/workflows/uae-seo-validation.yml (Monday 05:18 UTC, plus manual trigger and relevant pushes).
Command locally: python3 scripts/uae_seo_audit.py --live
Reports: seo-reports/uae-seo-report.json and seo-reports/uae-seo-report.md
These artifacts are source/live validation outputs and are not Google Search Console indexed status.

## Baseline to compare
Search Console export daily rows: 8–21 Nov 2026; 6 clicks, 156 impressions, 3.85% CTR, avg position 12.58. UAE: 12 impressions, 0 clicks, 0% CTR, avg position 19.75.
Caution: export predates the new pages. Compare to a future equivalent 14-day period after indexing, using same filters.
