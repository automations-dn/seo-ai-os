---
description: /audit - Run a full SEO audit for a client (Technical, On-Page, AEO/GEO scoring)
---

# Workflow: Full SEO Audit

## Trigger
```
/audit <client_name> [--type first_time|post_onboarding|monthly]
```
**Example:** `/audit acme_corp --type first_time`

## Objective
Produce a comprehensive SEO audit report with scores across Technical SEO, On-Page, Content Quality, AEO/GEO Readiness, and Core Web Vitals. Save to `clients/<client_name>/audit_history/`.

## Required Inputs
1. `<client_name>` — must match folder name in `clients/`
2. `--type` — defaults to `first_time` if not specified

## Step-by-Step Instructions

### Step 1: Load Client Context
- Read `clients/<client_name>/brand_kit.json`
- Extract: `website_url`, `sitemap_url`, `robots_txt_url`, `cms`
- Confirm GSC and GA4 connection status

### Step 2: Site Crawl (Technical SEO)
- Run: `tools/seo_crawler.py --url <website_url> --sitemap <sitemap_url>`
- Collects: all URLs, HTTP status codes (301, 404, 500), canonical tags, hreflang, noindex tags, internal link graph
- Output: `.tmp/<client_name>_crawl.json`

### Step 3: Core Web Vitals & Lighthouse
- Run: `tools/lighthouse_audit.py --url <website_url>`
- Scores: LCP, CLS, FID/INP, TBT, Speed Index for both Mobile and Desktop
- Output: `.tmp/<client_name>_lighthouse.json`

### Step 4: On-Page Analysis (Sample Top 10 URLs)
- Read top 10 URLs from crawl output (by internal link count = most important pages)
- Run: `tools/on_page_analyzer.py --urls <top_10_urls>`
- Checks: H1 uniqueness, title tag length (50-60 chars), meta description length (120-160 chars), keyword in title, image alt text coverage
- Output: `.tmp/<client_name>_onpage.json`

### Step 5: AEO / GEO Readiness Scoring
- Run: `tools/schema_checker.py --url <website_url>`
- Checks for presence and validity of: FAQ schema, Article schema, LocalBusiness schema, BreadcrumbList, Organization schema
- Bonus checks: Does the site have a structured "Who/What/Why" answer block? Does it have a clear author entity?
- Score: 0-100 based on checklist
- Output: `.tmp/<client_name>_aeo_score.json`

### Step 6: GSC Data Pull (if connected)
- Run: `tools/fetch_gsc_data.py --client <client_name>`
- Pulls: Impressions, Clicks, CTR, Avg Position for top 50 queries
- Checks: Index coverage errors, mobile usability errors
- Output: `.tmp/<client_name>_gsc.json`

### Step 7: Generate Audit Report
- Run: `tools/report_builder.py --client <client_name> --type audit --data-dir .tmp/`
- Compiles all `.tmp/<client_name>_*.json` files into a structured report
- Uses template: `templates/audit_report_template.md`
- Saves final report: `clients/<client_name>/audit_history/<YYYY-MM-DD>_audit.md`

### Step 8: Present Summary to User
Display a concise summary table in chat:

| Category | Score | Critical Issues |
|---|---|---|
| Technical SEO | /100 | e.g. 12 broken links |
| Core Web Vitals | /100 | e.g. LCP 4.2s (Poor) |
| On-Page | /100 | e.g. 5 missing H1s |
| AEO/GEO Readiness | /100 | e.g. No FAQ Schema |
| GSC Index Health | /100 | e.g. 23 noindex errors |

Then ask: **"Audit complete. Do you want me to start fixing Critical Issues now, or generate the PDF client report first?"**

## Edge Cases
- If GSC is not connected: skip Step 6, note it clearly in the report and add a recommendation to connect it.
- If Lighthouse fails on a URL: retry once. If it fails again, skip and flag in report.
- If the site has > 500 pages: only crawl up to 500 URLs and note the limit.
