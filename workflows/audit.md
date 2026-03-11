---
description: /audit - Run a full SEO audit for a client (Technical, On-Page, AEO/GEO scoring)
---

# Workflow: Full SEO Audit

## Trigger
```
/audit <website_url_or_client_name> [--type first_time|post_onboarding]
```
**Examples:**
- `/audit thedarenetwork.com` — quick audit, no client record created
- `/audit acme_corp --type first_time` — audit for an existing client in `clients/`

---

## ⚠️ CRITICAL RULE: Client List vs. Standalone Audit

> **DO NOT add a site to the client list just because someone asks for an audit.**

- If the user says **"run an audit on [site]"** or **"audit [site]"** → run the audit and output the report. Do NOT create a client folder or ask for brand kit details.
- If the user says **"add [name] as a client"** or **"onboard [name]"** → follow the `/add_client` workflow and collect all brand kit details first.
- If the user says **"run an audit for my client [name]"** and that client already exists in `clients/` → load the brand kit and run the audit using their stored details.
- If someone asks to do an audit AND add as a client in the same message → first collect all brand kit information (see `/add_client` workflow) before running the audit.

---

## Step-by-Step Instructions

### Step 1: Determine Mode

Check whether a client folder exists:
- `clients/<name>/brand_kit.json` exists → **Client Mode**: load brand kit, use stored `website_url`
- No client folder → **Standalone Mode**: use the URL directly, save output to `.tmp/reports/`

### Step 2: Site Crawl (Technical SEO)
- Run: `python tools/seo_crawler.py --url <website_url> --output .tmp/<slug>_crawl.json`
- Collects: all URLs, HTTP status codes (200, 301, 404, 500), canonical tags, hreflang, noindex tags, H1s, meta descriptions, schema types, internal link graph
- Output: `.tmp/<slug>_crawl.json`

### Step 3: On-Page & CRO/UX Analysis (Top 10 Pages)
- Read top 10 URLs from crawl output (by internal link count = most important pages)
- Run: `python tools/on_page_analyzer.py --urls-file .tmp/<slug>_crawl.json --output .tmp/<slug>_onpage.json`
- Checks: H1 uniqueness, title/meta length, image alt text.
- **Advanced Extractions**: The script now automatically extracts Intent-to-CTA alignment metrics, Trust Signals (SSL, contact info, return policies), E-E-A-T Author Profiles, Expert Citations, and Entity Optimization (Schema `sameAs` validation).
- Output: `.tmp/<slug>_onpage.json`

### Step 4: AEO / GEO Schema Check
- Review crawl data for schema types found on each page
- Check for the following **eligible** schema types based on site type:
  - ✅ **Always valid**: Organization, WebSite, Article/BlogPosting, BreadcrumbList, Person, SiteNavigationElement
  - ✅ **E-commerce only**: Product, Review, Offer
  - ✅ **Local businesses only**: LocalBusiness
  - ❌ **FAQPage** — RESTRICTED since Aug 2023. Only eligible for government and healthcare sites. **Never recommend this to commercial, agency, SaaS, or e-commerce sites.**
  - ❌ **HowTo** — DEPRECATED since Sept 2023. Never recommend.
- Score AEO readiness 0–100 based on coverage of eligible schema types for the detected site type

### Step 5: Competitor Intelligence & Benchmarking
- If in **Client Mode**, retrieve the `top_3_competitors` from the `brand_kit.json`.
- The report generation script will use this to automatically structure the **Keyword Gap Analysis**, **Topic Cluster Mapping**, and **SERP Overlap/Rivalry Scoring** sections in the audit.

### Step 5b: GSC & GA4 Data (Client Mode Only)
- Only attempt if the client brand kit has credentials configured. Integrates AOV & Engagement Metrics to find "High Impression/Low CTR" and "Low Scroll Depth" anomalies.
- If not connected: skip and note clearly in the report.

### Step 6: Perform Strategic Execution (Browser Research)
- **Do not use placeholders.** You (the AI Agent) must use your browser tool to find the top 3 ranking competitors for the client's primary keyword.
- Identify at least 3 high-volume keywords the competitors rank for.
- Find one specific 'Content Asset' (e.g. calculator, lookbook) each competitor has that the client does not.
- Detect the CMS (Shopify/WordPress/Custom). If it's a D2C/E-commerce brand, set `is_ecommerce` to true to trigger CRO logic (WhatsApp, Trust Badges).
- Generate **Idea 1 (Education):** An 'Encyclopedia' or Knowledge Hub resource.
- Generate **Idea 2 (Seasonal):** A 'Craft/Occasion Calendar' mapped to specific festivals.
- Create a file at `.tmp/strategy_input.json` containing:
  ```json
  {
    "cms": "Shopify",
    "is_ecommerce": true,
    "competitors": [{"name": "Comp 1", "asset": "Ring Sizer"}, ...],
    "keywords": ["kw 1", "kw 2", "kw 3"],
    "innovation_idea_1": "Description...",
    "innovation_idea_2": "Description..."
  }
  ```

### Step 7: Generate Word Report
- **ALWAYS run this command** — do not skip or simulate it:
  ```
  python tools/report_builder.py --url <website_url> --type audit --strategy .tmp/strategy_input.json
  ```
  - **Client Mode**: `python tools/report_builder.py --client <name> --type audit --strategy .tmp/strategy_input.json`
- The script saves to `.tmp/reports/<YYYY-MM-DD>_audit_report.docx` and **automatically opens the file in Microsoft Word**.
- Do NOT save to `audit_history/` or any client folder.
- Do NOT generate a `file:///` link — it won't work in Claude Code chat.

### Step 8: Present Summary

Display the summary table in chat:

| Category | Score | Critical Issues |
|---|---|---|
| Technical SEO | /100 | e.g. 12 broken links |
| Core Web Vitals | /100 | e.g. LCP 4.2s (Poor) — use **INP** not FID |
| CRO & UX | /100 | e.g. Missing CTA on 5 pages, no Trust Signals |
| Advanced E-E-A-T | /100 | e.g. No 'sameAs' in schema, missing citations |
| Competitor Gap | /100 | e.g. High SERP overlap rivalry detected |

> ⚠️ **Core Web Vitals Targets (current):** LCP < 2.5s | **INP < 200ms** | CLS < 0.1
> FID was removed on March 12, 2024. Never reference FID in any report.

Then show the file location from the terminal output:
```
✅ Report saved!
📁 Folder : C:\Users\HP\OneDrive\Desktop\SEO ai agency skills\.tmp\reports
📄 File   : 2026-03-10_audit_report.docx

👉 To open: Right-click the file in Windows Explorer and choose 'Open'
```

> ⚠️ **Important:** Do NOT use `file:///` links in chat — they are not clickable in Claude Code.
> Instead, copy the **Full path** from the terminal output and paste it into Windows Explorer's address bar.

Then ask: **"Audit complete. Do you want me to start fixing the Critical Issues, or is there anything else?"**

---

## 🧠 Reasoning Depth — Quality Standard

This audit must read like it was written by a **senior SEO consultant with 10+ years of experience**, not a checklist robot. Before writing the report:

1. **Diagnose, don't just describe.** Don't say "8 pages are missing H1 tags." Say *why it matters*, what Google's crawler sees, and what the likely cause is (CMS template issue, developer oversight, etc.).
2. **Prioritise by business impact.** Every issue must be ranked by the revenue/visibility impact, not just technical severity. A missing canonical on a 10-visit page matters less than one on the homepage.
3. **Connect issues together.** If the site has no canonical tags AND no sitemap AND missing H1s, that's a systemic crawlability problem — say so explicitly.
4. **Be specific with fixes.** Don't say "add schema." Provide the exact JSON-LD template the client can copy-paste into their CMS.
5. **Write the executive summary for a non-technical client.** The first section should be readable by a business owner with no SEO knowledge — plain language, clear business stakes.
6. **Apply industry context.** Use the site type detected in Step 1 to tailor every recommendation. A SaaS company and a local plumber have different SEO priorities.
7. **E-E-A-T is mandatory.** Every audit must include a named E-E-A-T section assessing Experience, Expertise, Authoritativeness, and Trustworthiness signals with specific, actionable evidence from the site.

> 💡 Aim for a report quality that a client would pay £500+ for as a standalone deliverable.

---

## Edge Cases
- GSC not connected → skip GSC step, note in report with instructions on how to connect
- Site has >500 pages → crawl up to 500 URLs, note the limit
- Lighthouse unavailable → skip CWV section, add manual Lighthouse instructions in report and link to https://pagespeed.web.dev
- User asks to audit AND add client → collect brand kit details first via `/add_client`, then run audit
- FAQPage schema requested → only approve for government or healthcare sites; redirect all others to Article or Organization schema
- FID mentioned anywhere → correct it to INP (Interaction to Next Paint). FID was removed March 12, 2024.
