---
description: /monthly_report - Generate a complete monthly SEO performance report for a client
---

# Workflow: Monthly Report Generation

## Trigger
```
/monthly_report <client_name> [--month YYYY-MM] [--format markdown|pdf|slides]
```
**Example:** `/monthly_report acme_corp --month 2025-02 --format pdf`

## Objective
Pull all available data sources and generate a comprehensive, beautifully formatted monthly SEO report. Deliver to the client or save locally.

## Required Inputs
1. `<client_name>` — loads brand_kit and previous month's data
2. `--month` — defaults to last full calendar month
3. `--format` — defaults to `markdown`

## Step-by-Step Instructions

### Step 1: Load Context
- Read `clients/<client_name>/brand_kit.json`
- Confirm `gsc_connected` and `ga4_connected` status
- Check `reporting.custom_report_template` — use it if set, else use `templates/monthly_report_template.md`

### Step 2: Pull GA4 Data (if connected)
- Run: `tools/fetch_ga4_data.py --client <client_name> --month <YYYY-MM>`
- Pulls: Organic sessions, users, bounce rate, avg. session duration, top landing pages by organic traffic
- Calculates: Month-over-month % change
- Output: `.tmp/<client_name>_ga4_<month>.json`

### Step 3: Pull GSC Data (if connected)
- Run: `tools/fetch_gsc_data.py --client <client_name> --month <YYYY-MM>`
- Pulls: Total impressions, clicks, avg CTR, avg position
- Top 10 queries by clicks (with position change from last month)
- Top 10 pages by impressions
- New keywords ranking in top 10 this month
- Keywords that dropped out of top 10
- Output: `.tmp/<client_name>_gsc_<month>.json`

### Step 4: GSC Algorithmic Strategy Feedback Loop (CRITICAL)
- Compare the current month's GSC impression data (Step 3) against the previous month's.
- Identify "Topic Clusters" or specific pages that lost >15% impressions month-over-month.
- Flag this explicitly: *"Strategy degradation detected on [Cluster Name]. Competitors may be outperforming."*
- Recommend running `/competitor_gap` on the dropping clusters.

### Step 5: Technical Health Snapshot
- Compare latest crawl data with previous month's crawl (from `audit_history/`)
- Notes: New 404s found, New redirect issues, Index count change

### Step 6: Content & Link Building Summary
- Scan `clients/<client_name>/active_campaigns/` for:
  - Articles published this month
  - Links built / outreach sent this month

### Step 7: Compile Report
- Run: `tools/report_builder.py --client <client_name> --type monthly --month <YYYY-MM>`
- Fills in the template with all collected data
- Report Sections:
  1. **Executive Summary** — 3-5 bullet highlights (biggest wins, concerns)
  2. **Traffic Overview** — GA4 organic traffic chart data
  3. **Rankings & Visibility** — GSC position tracking, new wins, drops
  4. **The GSC Algorithm Feedback Loop** — List of dropping clusters and recommended pivot strategy
  5. **Technical Health** — crawl health summary
  6. **Content Published** — list of new articles with performance
  7. **Links Built** — new backlinks acquired this month
  8. **AEO/GEO Status** — any new featured snippets or AI overview appearances
  9. **Next Month Priorities** — 3-5 recommended actions

### Step 8: Format Output
- If `--format markdown`: Save to `clients/<client_name>/reports/<month>_report.md`
- If `--format pdf`: Run `tools/report_builder.py --render pdf` to generate PDF
- If `--format slides`: Generate a Google Slides-compatible presentation outline

### Step 9: Present Summary & Deliver
- Display executive summary in chat.
- Show the **Human QA Publishing Checklist** (did you review data anomalies? formatting? tone?).
- Ask: **"Monthly report is ready! Shall I push this to Google Drive, or do you want to review it locally first?"**

## Edge Cases
- If neither GSC nor GA4 is connected: generate a "manual input" report template with empty fields and instructions on how to connect APIs. Flag this loudly.
- If it's the first month (no comparison data): skip MoM change calculations and note it's the baseline month.
