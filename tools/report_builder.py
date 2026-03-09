#!/usr/bin/env python3
"""
Report Builder Tool
Compiles all analysis data from .tmp/ into clean markdown or PDF reports.
Uses client brand_kit.json for report personalization.

Usage:
    python report_builder.py --client acme_corp --type audit
    python report_builder.py --client acme_corp --type monthly --month 2025-02
    python report_builder.py --client acme_corp --type audit --format pdf
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime, date
from glob import glob


def load_brand_kit(client_name: str) -> dict:
    path = Path(f"clients/{client_name}/brand_kit.json")
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"client_info": {"client_name": client_name, "website_url": ""}}


def load_tmp_json(pattern: str) -> dict:
    """Load the most recent .tmp file matching a glob pattern."""
    files = sorted(glob(f".tmp/{pattern}"), reverse=True)
    if files:
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_audit_report(client_name: str, brand_kit: dict) -> str:
    info = brand_kit.get("client_info", {})
    audit_date = datetime.now().strftime("%B %d, %Y")
    website = info.get("website_url", "N/A")

    crawl = load_tmp_json(f"*{client_name}*crawl*.json")
    onpage = load_tmp_json(f"*{client_name}*onpage*.json")
    aeo = load_tmp_json(f"*{client_name}*aeo*.json")

    crawl_summary = crawl.get("summary", {})
    onpage_results = onpage.get("results", [])
    avg_onpage = onpage.get("avg_score", "N/A")

    # Count schema stats from crawl
    pages = crawl.get("pages", [])
    pages_with_schema = sum(1 for p in pages if p.get("schema_types"))
    schema_coverage = f"{round(pages_with_schema / max(len(pages), 1) * 100)}%" if pages else "N/A"

    report = f"""# SEO Audit Report
**Client:** {info.get('client_name', client_name)}
**Website:** {website}
**Audit Date:** {audit_date}
**Report Type:** {'First-Time Onboarding Audit' if True else 'Post-Onboarding Audit'}

---

## Executive Summary

This audit covers Technical SEO, On-Page Optimization, AEO/GEO Readiness, and overall site health.
Use this report as the baseline to track progress against each month.

---

## 1. Technical SEO Overview

| Metric | Result |
|--------|--------|
| Total Pages Crawled | {crawl_summary.get('total_pages', 'N/A')} |
| Pages Returning 200 OK | {crawl_summary.get('status_200', 'N/A')} |
| Broken Pages (404) | {crawl_summary.get('status_404', 'N/A')} |
| Server Errors (500) | {crawl_summary.get('status_500', 'N/A')} |
| Redirects (301) | {crawl_summary.get('status_301', 'N/A')} |
| Pages Missing H1 | {crawl_summary.get('missing_h1', 'N/A')} |
| Pages Missing Title | {crawl_summary.get('missing_title', 'N/A')} |
| Pages Missing Meta Desc | {crawl_summary.get('missing_meta_desc', 'N/A')} |
| Noindex Pages | {crawl_summary.get('noindex_pages', 'N/A')} |

### Critical Technical Issues
"""
    status_404 = crawl_summary.get('status_404', 0)
    if status_404 and int(status_404) > 0:
        report += f"- 🔴 **{status_404} broken pages (404)** found — these lose link equity and damage user experience.\n"

    noindex = crawl_summary.get('noindex_pages', 0)
    if noindex and int(noindex) > 0:
        report += f"- 🔴 **{noindex} noindex pages** detected — verify these are intentionally excluded.\n"

    missing_h1 = crawl_summary.get('missing_h1', 0)
    if missing_h1 and int(missing_h1) > 0:
        report += f"- 🟡 **{missing_h1} pages missing H1** — these cannot be properly understood by search engines.\n"

    if not status_404 and not noindex:
        report += "- ✅ No critical technical issues found in this crawl.\n"

    report += f"""
---

## 2. On-Page SEO Analysis

**Average On-Page Score: {avg_onpage}/100**

| Page | Score | Key Issues |
|------|-------|------------|
"""
    for r in onpage_results[:10]:
        issues_preview = "; ".join(r.get("issues", [])[:2]) or "None"
        report += f"| {r.get('url', '')} | {r.get('overall_score', 'N/A')}/100 | {issues_preview} |\n"

    if not onpage_results:
        report += "| No on-page data available | Run on_page_analyzer.py | — |\n"

    report += f"""
---

## 3. AEO / GEO Readiness

### Schema Markup Coverage
| Metric | Status |
|--------|--------|
| Pages with Schema Markup | {pages_with_schema} / {len(pages)} ({schema_coverage}) |
| FAQ Schema | {'✅ Found' if any('FAQ' in str(p.get('schema_types', [])) for p in pages) else '❌ Not Found'} |
| Article Schema | {'✅ Found' if any('Article' in str(p.get('schema_types', [])) for p in pages) else '❌ Not Found'} |
| Organization Schema | {'✅ Found' if any('Organization' in str(p.get('schema_types', [])) for p in pages) else '❌ Not Found'} |

### AEO Recommendations
- Add **FAQPage schema** to top content pages to target "People Also Ask" boxes
- Add **Article schema** to all blog posts to improve AI Overview inclusion
- Ensure every key page answers a clear "Who/What/Why/How" question in the first 100 words

---

## 4. Recommended Priorities

### This Week (Critical)
"""
    priority_items = []
    if status_404 and int(status_404) > 0:
        priority_items.append(f"Fix {status_404} broken pages (404 errors)")
    if noindex and int(noindex) > 0:
        priority_items.append(f"Review {noindex} noindex pages — confirm all are intentional")
    if missing_h1 and int(missing_h1) > 0:
        priority_items.append(f"Add H1 tags to {missing_h1} pages")

    if priority_items:
        for item in priority_items:
            report += f"1. {item}\n"
    else:
        report += "1. ✅ No critical fixes needed — focus on High priority items\n"

    report += f"""
### This Month (High)
1. Add FAQ Schema to top 5 content pages
2. Improve meta descriptions on all pages scoring below 70
3. Fix any missing alt text on images

---

*Report generated by SEO AI OS on {audit_date}*
*Next audit: 30 days after implementing fixes*
"""
    return report


def build_monthly_report(client_name: str, brand_kit: dict, month: str) -> str:
    info = brand_kit.get("client_info", {})
    report_date = datetime.now().strftime("%B %d, %Y")
    month_label = datetime.strptime(month, "%Y-%m").strftime("%B %Y") if month else "Last Month"

    gsc = load_tmp_json(f"*{client_name}*gsc*{month.replace('-', '') if month else ''}*.json")
    ga4 = load_tmp_json(f"*{client_name}*ga4*{month.replace('-', '') if month else ''}*.json")

    report = f"""# Monthly SEO Performance Report
**Client:** {info.get('client_name', client_name)}
**Website:** {info.get('website_url', 'N/A')}
**Reporting Period:** {month_label}
**Generated:** {report_date}

---

## Executive Summary

*3-5 key highlights go here after reviewing the full data.*

---

## 1. Organic Traffic (GA4)

| Metric | This Month | Last Month | Change |
|--------|-----------|------------|--------|
| Organic Sessions | {ga4.get('sessions', 'Connect GA4')} | — | — |
| Organic Users | {ga4.get('users', 'Connect GA4')} | — | — |
| Avg Session Duration | {ga4.get('avg_duration', 'Connect GA4')} | — | — |

---

## 2. Search Rankings (Google Search Console)

| Metric | This Month | Last Month | Change |
|--------|-----------|------------|--------|
| Total Impressions | {gsc.get('impressions', 'Connect GSC')} | — | — |
| Total Clicks | {gsc.get('clicks', 'Connect GSC')} | — | — |
| Average CTR | {gsc.get('ctr', 'Connect GSC')} | — | — |
| Average Position | {gsc.get('avg_position', 'Connect GSC')} | — | — |

### Top Performing Keywords This Month
*(Data available once GSC is connected)*

---

## 3. Content Published This Month

*(List articles published — check active_campaigns/ folder)*

---

## 4. Links Built This Month

*(List links acquired — check outreach tracking in active_campaigns/)*

---

## 5. Next Month Priorities

1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

---

*Report generated by SEO AI OS | {report_date}*
"""
    return report


def save_report(content: str, client_name: str, report_type: str,
                month: str = None, fmt: str = "markdown") -> str:
    today = date.today().strftime("%Y-%m-%d")
    filename = f"{today}_{report_type}_report"
    if month:
        filename = f"{month}_{report_type}_report"

    output_dir = Path(f"clients/{client_name}/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    if fmt == "markdown":
        path = output_dir / f"{filename}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    elif fmt == "pdf":
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            path = output_dir / f"{filename}.pdf"
            c = canvas.Canvas(str(path), pagesize=A4)
            width, height = A4
            y = height - 50
            for line in content.split("\n"):
                if y < 50:
                    c.showPage()
                    y = height - 50
                clean_line = line.lstrip("#").strip()
                fontsize = 14 if line.startswith("# ") else 12 if line.startswith("## ") else 10
                c.setFont("Helvetica-Bold" if line.startswith("#") else "Helvetica", fontsize)
                c.drawString(50, y, clean_line[:110])
                y -= fontsize + 4
            c.save()
        except ImportError:
            import subprocess
            subprocess.run(["pip", "install", "reportlab"], check=True)
            path = output_dir / f"{filename}.md"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content + "\n\n*Note: Install reportlab for PDF export: pip install reportlab*")

    return str(path)


def main():
    parser = argparse.ArgumentParser(description="SEO Report Builder")
    parser.add_argument("--client", required=True)
    parser.add_argument("--type", required=True, choices=["audit", "monthly"])
    parser.add_argument("--month", help="Month for monthly report: YYYY-MM")
    parser.add_argument("--format", default="markdown", choices=["markdown", "pdf"])
    args = parser.parse_args()

    brand_kit = load_brand_kit(args.client)
    client_display = brand_kit.get("client_info", {}).get("client_name", args.client)
    print(f"[Report Builder] Generating {args.type} report for: {client_display}")

    if args.type == "audit":
        content = build_audit_report(args.client, brand_kit)
    elif args.type == "monthly":
        month = args.month or datetime.now().strftime("%Y-%m")
        content = build_monthly_report(args.client, brand_kit, month)

    output_path = save_report(content, args.client, args.type, args.month, args.format)
    print(f"[Output] Report saved to: {output_path}")
    print("\n--- REPORT PREVIEW (first 1000 chars) ---")
    print(content[:1000])


if __name__ == "__main__":
    main()
