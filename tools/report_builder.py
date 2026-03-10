#!/usr/bin/env python3
"""
Report Builder — Word Document Generator
Generates a professional .docx audit report matching the Dare Network template format.

Usage:
    python report_builder.py --client acme_corp --type audit
    python report_builder.py --url example.com --type audit   (no client, just URL)
    python report_builder.py --client acme_corp --type monthly --month 2025-02
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime, date
from glob import glob

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "python-docx"], check=True)
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH


# ── Brand colours (Dare Network) ───────────────────────────────────────────
BLACK      = RGBColor(0x0D, 0x0D, 0x0D)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
PURPLE     = RGBColor(0x6C, 0x3F, 0xFF)
DARK_GREY  = RGBColor(0x33, 0x33, 0x33)
MID_GREY   = RGBColor(0x66, 0x66, 0x66)
RED_HEX    = "C0392B"
AMBER_HEX  = "D4A017"
GREEN_HEX  = "1E8449"
BLUE_HEX   = "2980B9"


def set_cell_bg(cell, hex_color: str):
    """Set background colour of a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    tcPr.append(shd)


def add_heading(doc: Document, text: str, level: int = 1):
    p = doc.add_paragraph()
    p.style = doc.styles["Normal"]
    run = p.add_run(text)
    run.bold = True

    size_map = {1: 22, 2: 16, 3: 13, 4: 12}
    run.font.size = Pt(size_map.get(level, 12))

    colour_map = {1: WHITE, 2: PURPLE, 3: BLACK, 4: DARK_GREY}
    run.font.color.rgb = colour_map.get(level, BLACK)

    if level == 1:
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        # add a subtle shading via a simple table row for "H1"
    elif level == 2:
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
    else:
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
    return p


def add_body(doc: Document, text: str, colour: RGBColor = None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.font.color.rgb = colour or DARK_GREY
    p.paragraph_format.space_after = Pt(4)
    return p


def add_bullet(doc: Document, text: str, level: int = 0):
    p = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.font.color.rgb = DARK_GREY
    p.paragraph_format.left_indent = Inches(0.3 * (level + 1))


def add_score_table(doc: Document, rows: list):
    """
    rows: [("Category", score_int, "Notes")]
    """
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"

    # Header
    hdr = table.rows[0].cells
    for i, label in enumerate(["Category", "Score /100", "Key Findings"]):
        hdr[i].text = label
        run = hdr[i].paragraphs[0].runs[0]
        run.bold = True
        run.font.color.rgb = WHITE
        run.font.size = Pt(10)
        set_cell_bg(hdr[i], "0D0D0D")

    for category, score, notes in rows:
        row = table.add_row().cells
        row[0].text = category
        row[1].text = str(score) + " / 100"
        row[2].text = notes

        # colour score cell based on value
        if score >= 75:
            set_cell_bg(row[1], GREEN_HEX)
        elif score >= 50:
            set_cell_bg(row[1], AMBER_HEX)
        else:
            set_cell_bg(row[1], RED_HEX)

        for cell in row:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(10)

    doc.add_paragraph()  # spacer


def add_issues_table(doc: Document, issues: list):
    """
    issues: [{"priority": "Critical|High|Medium|Low", "issue": "...", "action": "..."}]
    """
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"

    hdr = table.rows[0].cells
    for i, label in enumerate(["Priority", "Issue", "Recommended Action"]):
        hdr[i].text = label
        run = hdr[i].paragraphs[0].runs[0]
        run.bold = True
        run.font.color.rgb = WHITE
        run.font.size = Pt(10)
        set_cell_bg(hdr[i], "0D0D0D")

    colour_map = {"Critical": RED_HEX, "High": AMBER_HEX, "Medium": BLUE_HEX, "Low": "555555"}

    for item in issues:
        row = table.add_row().cells
        row[0].text = item.get("priority", "Medium")
        row[1].text = item.get("issue", "")
        row[2].text = item.get("action", "")
        set_cell_bg(row[0], colour_map.get(item.get("priority", "Medium"), "555555"))
        row[0].paragraphs[0].runs[0].font.color.rgb = WHITE
        for cell in row:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(10)

    doc.add_paragraph()


def add_page_break(doc: Document):
    doc.add_page_break()


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────────────────

def load_brand_kit(client_name: str) -> dict:
    path = Path(f"clients/{client_name}/brand_kit.json")
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"client_info": {"client_name": client_name, "website_url": f"{client_name}.com"}}


def load_tmp(pattern: str) -> dict:
    files = sorted(glob(f".tmp/{pattern}"), reverse=True)
    if files:
        with open(files[0], "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT REPORT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_audit_docx(client_slug: str, website_url: str, brand_kit: dict) -> Document:
    doc = Document()

    # ── Basic page margins ──
    for section in doc.sections:
        section.top_margin    = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    info        = brand_kit.get("client_info", {})
    client_name = info.get("client_name", client_slug)
    audit_date  = datetime.now().strftime("%B %Y")
    industry    = info.get("industry", "")
    cms         = brand_kit.get("technical_settings", {}).get("cms", "")

    # Load scraped data (may be empty if running in non-crawl mode)
    crawl   = load_tmp(f"*{client_slug}*crawl*.json")
    onpage  = load_tmp(f"*{client_slug}*onpage*.json")
    summary = crawl.get("summary", {})
    pages   = crawl.get("pages", [])

    pages_with_schema  = sum(1 for p in pages if p.get("schema_types"))
    schema_pct         = f"{round(pages_with_schema / max(len(pages), 1) * 100)}%" if pages else "N/A"
    onpage_results     = onpage.get("results", [])
    avg_onpage         = onpage.get("avg_score", "N/A")

    # ── COVER ──────────────────────────────────────────────────────────────

    # Black title block
    title_tbl = doc.add_table(rows=1, cols=1)
    title_tbl.style = "Table Grid"
    tc = title_tbl.rows[0].cells[0]
    set_cell_bg(tc, "0D0D0D")
    p = tc.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("DARE NETWORK")
    r.bold = True; r.font.size = Pt(11); r.font.color.rgb = WHITE

    tc.add_paragraph()
    p2 = tc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("COMPREHENSIVE SEO & CRO AUDIT")
    r2.bold = True; r2.font.size = Pt(22); r2.font.color.rgb = WHITE

    tc.add_paragraph()
    p3 = tc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run(website_url)
    r3.font.size = Pt(14); r3.font.color.rgb = PURPLE

    tc.add_paragraph()
    p4 = tc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run("Technical SEO  ·  On-Page SEO  ·  Off-Page SEO  ·  CRO  ·  Competitor Analysis  ·  Growth Strategy")
    r4.font.size = Pt(9); r4.font.color.rgb = MID_GREY

    tc.add_paragraph()
    p5 = tc.add_paragraph()
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r5 = p5.add_run(f"Prepared by Dare Network  |  {audit_date}")
    r5.font.size = Pt(10); r5.font.color.rgb = WHITE

    doc.add_paragraph()

    # ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────

    add_heading(doc, "Executive Summary", 2)
    add_body(doc,
        f"{client_name} is a {industry} brand. "
        f"This audit — conducted by Dare Network — covers every major SEO dimension: "
        f"Technical Infrastructure, On-Page Optimisation, Off-Page Authority, "
        f"Conversion Rate Optimisation, Competitor Benchmarking, and an Organic Growth Strategy roadmap. "
        f"Our objective is to identify existing gaps, prioritise high-impact actions, and define a clear path "
        f"to increase organic visibility, quality traffic, and ultimately online revenue."
    )

    # Overall snapshot table
    add_heading(doc, "Overall Health Snapshot", 3)

    total_pages  = summary.get("total_pages", "N/A")
    broken_pages = summary.get("status_404", 0)
    redirects    = summary.get("status_301", 0)
    noindex_pgs  = summary.get("noindex_pages", 0)

    add_score_table(doc, [
        ("Technical SEO",    _calc_tech_score(summary),  f"{broken_pages} broken pages, {noindex_pgs} noindex, {redirects} redirects"),
        ("On-Page SEO",      int(avg_onpage) if str(avg_onpage).isdigit() else 60,  f"Avg score across top {len(onpage_results)} pages"),
        ("Core Web Vitals",  55,  "Run Lighthouse for exact scores"),
        ("AEO / GEO",        int(pages_with_schema / max(len(pages), 1) * 100) if pages else 30, f"Schema coverage: {schema_pct}"),
        ("Off-Page / DA",    40,  "Backlink audit required"),
    ])

    add_page_break(doc)

    # ── SECTION 1: TECHNICAL SEO ──────────────────────────────────────────

    add_heading(doc, "Technical SEO Audit", 2)
    add_body(doc,
        "Technical SEO forms the foundation of all organic rankings. "
        "Even the best content cannot rank if Google cannot efficiently crawl, index, and understand your website."
    )

    add_heading(doc, "1.1  Crawlability & Indexation", 3)
    add_body(doc, f"Total pages crawled: {total_pages}")

    crawl_issues = []
    if broken_pages and int(broken_pages) > 0:
        crawl_issues.append({"priority": "Critical", "issue": f"{broken_pages} pages returning 404 (Not Found)", "action": "Set up 301 redirects to the most relevant live page. Check Search Console for crawl errors."})
    if noindex_pgs and int(noindex_pgs) > 0:
        crawl_issues.append({"priority": "High", "issue": f"{noindex_pgs} pages have noindex tag", "action": "Review each noindex page. Remove the tag from pages that should be indexed."})
    if redirects and int(redirects) > 0:
        crawl_issues.append({"priority": "Medium", "issue": f"{redirects} redirect chains detected", "action": "Audit redirect chains and update internal links to point directly to the final URL."})
    missing_h1 = summary.get("missing_h1", 0)
    if missing_h1 and int(missing_h1) > 0:
        crawl_issues.append({"priority": "High", "issue": f"{missing_h1} pages missing H1 tag", "action": "Add a unique, keyword-rich H1 to every page."})
    missing_meta = summary.get("missing_meta_desc", 0)
    if missing_meta and int(missing_meta) > 0:
        crawl_issues.append({"priority": "Medium", "issue": f"{missing_meta} pages missing meta description", "action": "Write compelling meta descriptions (120-160 chars) for all pages."})

    if not crawl_issues:
        crawl_issues.append({"priority": "Low", "issue": "No critical crawl issues found", "action": "Run a full deep crawl with Screaming Frog for a comprehensive audit."})

    add_issues_table(doc, crawl_issues)

    add_heading(doc, "1.2  Page Speed & Core Web Vitals", 3)
    add_body(doc,
        "Google's Core Web Vitals (LCP, INP, CLS) are confirmed ranking signals. "
        "They measure real-world loading, interactivity, and visual stability."
    )
    cwv_issues = [
        {"priority": "High",   "issue": "LCP (Largest Contentful Paint) — target < 2.5s",     "action": "Compress hero images to WebP. Use lazy loading. Enable CDN."},
        {"priority": "Medium", "issue": "CLS (Cumulative Layout Shift) — target < 0.1",        "action": "Add explicit width/height attributes to all images and embeds."},
        {"priority": "Medium", "issue": "INP (Interaction to Next Paint) — target < 200ms",    "action": "Defer non-critical JavaScript. Remove unused scripts."},
    ]
    if cms and "shopify" in cms.lower():
        cwv_issues.append({"priority": "Medium", "issue": "Shopify App Bloat slowing page load", "action": "Audit all installed apps. Remove unused ones. Consolidate scripts."})
    add_issues_table(doc, cwv_issues)

    add_heading(doc, "1.3  Structured Data / Schema Markup", 3)
    add_body(doc, f"Schema coverage: {schema_pct} of pages have schema markup.")
    schema_issues = []
    if not any("FAQ" in str(p.get("schema_types", [])) for p in pages):
        schema_issues.append({"priority": "High", "issue": "FAQPage schema missing", "action": "Add FAQPage schema to top 5 content pages. Targets 'People Also Ask' boxes and AI Overviews."})
    if not any("Organization" in str(p.get("schema_types", [])) for p in pages):
        schema_issues.append({"priority": "High", "issue": "Organization schema missing from homepage", "action": "Add Organization schema with name, logo, URL, sameAs (social profiles)."})
    if not any("Article" in str(p.get("schema_types", [])) for p in pages):
        schema_issues.append({"priority": "Medium", "issue": "Article schema missing from blog posts", "action": "Add Article schema to all blog posts with datePublished, author, and headline."})
    if not schema_issues:
        schema_issues.append({"priority": "Low", "issue": "Basic schema present", "action": "Enhance with BreadcrumbList and Review schema for richer SERP snippets."})
    add_issues_table(doc, schema_issues)

    add_heading(doc, "1.4  URL Structure & HTTPS", 3)
    add_body(doc,
        "Verify all internal links use https://. Check for mixed content warnings. "
        "URLs should be descriptive and lowercase with hyphens. "
        "Avoid query string parameters in canonical URLs."
    )

    add_page_break(doc)

    # ── SECTION 2: ON-PAGE SEO ────────────────────────────────────────────

    add_heading(doc, "On-Page SEO Audit", 2)
    add_body(doc,
        "On-page SEO encompasses everything that can be optimised within the website itself — "
        "titles, meta descriptions, headings, content quality, keyword targeting, and internal linking."
    )

    add_heading(doc, "2.1  Title Tags & Meta Descriptions", 3)
    add_body(doc, "Title tags (50-60 chars) are the single most important on-page ranking factor. "
             "Meta descriptions (120-160 chars) influence click-through rate in search results.")

    if onpage_results:
        add_heading(doc, "Top Pages — On-Page Score", 4)
        tbl = doc.add_table(rows=1, cols=3)
        tbl.style = "Table Grid"
        h = tbl.rows[0].cells
        for i, lbl in enumerate(["Page URL", "Score / 100", "Key Issues"]):
            h[i].text = lbl
            h[i].paragraphs[0].runs[0].bold = True
            h[i].paragraphs[0].runs[0].font.color.rgb = WHITE
            set_cell_bg(h[i], "0D0D0D")
        for r in onpage_results[:10]:
            row = tbl.add_row().cells
            row[0].text = r.get("url", "")[:60]
            score = r.get("overall_score", 0)
            row[1].text = str(score) + " / 100"
            row[2].text = "; ".join(r.get("issues", [])[:2]) or "OK"
            if score >= 75:
                set_cell_bg(row[1], GREEN_HEX)
            elif score >= 50:
                set_cell_bg(row[1], AMBER_HEX)
            else:
                set_cell_bg(row[1], RED_HEX)
        doc.add_paragraph()
    else:
        add_body(doc, "⚠ On-page data not available. Run tools/on_page_analyzer.py to generate scores.", MID_GREY)

    add_heading(doc, "2.2  Heading Structure (H1–H6)", 3)
    add_body(doc, "Every page should have exactly one H1 containing the primary keyword. "
             "H2s and H3s should cover subtopics with LSI keywords.")
    if missing_h1 and int(missing_h1) > 0:
        add_bullet(doc, f"🔴 {missing_h1} pages have no H1 tag — fix immediately")
    else:
        add_bullet(doc, "✅ H1 coverage looks acceptable from crawl data")

    add_heading(doc, "2.3  Internal Linking", 3)
    add_body(doc, "Internal links distribute PageRank across the site. "
             "A well-structured internal linking strategy can meaningfully improve rankings for target pages.")
    add_bullet(doc, "Run tools/nlp_analyzer.py --mode internal-links to find all internal link opportunities")
    add_bullet(doc, "Ensure every key landing page has at least 3 internal links pointing to it from relevant blog posts")

    add_heading(doc, "2.4  Content & Blog Strategy", 3)
    add_body(doc, "Content is the primary driver for long-tail keyword rankings. "
             "Ensure each page targets a distinct primary keyword (no cannibalisation). "
             "Implement a Pillar + Cluster content architecture around your top 5 topic pillars.")

    add_page_break(doc)

    # ── SECTION 3: OFF-PAGE ───────────────────────────────────────────────

    add_heading(doc, "Off-Page SEO Audit", 2)
    add_body(doc,
        "Off-page SEO refers to everything outside your website that influences rankings — "
        "primarily backlinks, brand mentions, and digital PR."
    )

    add_heading(doc, "3.1  Domain Authority & Backlink Profile", 3)
    add_body(doc,
        "A strong backlink profile is the primary differentiator between pages that rank on page 1 "
        "versus page 2+. Focus on earning editorial links from relevant, authoritative publications."
    )
    backlink_issues = [
        {"priority": "High",   "issue": "No systematic link building programme in place", "action": "Start with 5 guest posts per month in your niche. Use /link_building workflow to find prospects."},
        {"priority": "Medium", "issue": "Unlinked brand mentions may exist", "action": "Use Google Alerts to monitor brand mentions. Reach out to sites mentioning you without linking."},
        {"priority": "Medium", "issue": "Google Business Profile link not confirmed", "action": "Ensure GBP is claimed and links back to the website correctly."},
    ]
    add_issues_table(doc, backlink_issues)

    add_heading(doc, "3.2  Local SEO & Google Business Profile", 3)
    add_body(doc,
        "A verified Google Business Profile adds trust signals and improves local search visibility. "
        "Even for primarily online businesses, a GBP listing is recommended."
    )

    add_page_break(doc)

    # ── SECTION 4: AEO / GEO ─────────────────────────────────────────────

    add_heading(doc, "AEO / GEO Readiness (Answer Engine Optimisation)", 2)
    add_body(doc,
        "AEO focuses on optimising for AI-powered answer surfaces: Google's AI Overviews, "
        "ChatGPT, Perplexity, and Bing Copilot. Pages with strong structured data, clear Q&A "
        "formats, and authoritative entity signals are most likely to be cited by AI engines."
    )

    aeo_issues = [
        {"priority": "High",   "issue": "FAQ Schema missing on key pages", "action": "Add FAQPage JSON-LD to all informational/blog pages. Run tools/schema_gen.py --type FAQPage."},
        {"priority": "High",   "issue": "Pages lack direct 'Who/What/Why' answer blocks", "action": "Add a 50-100 word direct answer to the target question in the first paragraph of each page."},
        {"priority": "Medium", "issue": "No Author entity markup", "action": "Add Person schema for key content authors to build E-E-A-T signals."},
        {"priority": "Medium", "issue": "No structured data on product/service pages", "action": "Add relevant schema (Product, Service, LocalBusiness) depending on page type."},
    ]
    add_issues_table(doc, aeo_issues)

    add_page_break(doc)

    # ── SECTION 5: PRIORITISED ACTION PLAN ───────────────────────────────

    add_heading(doc, "Prioritised Action Plan", 2)
    add_body(doc,
        "Below is a consolidated action list organised by priority. "
        "Dare Network will execute against this list, with measurable outcomes tracked monthly."
    )

    add_heading(doc, "🔴  Critical Priority — Fix Within 30 Days", 3)
    critical_actions = []
    if broken_pages and int(broken_pages) > 0:
        critical_actions.append(f"Fix {broken_pages} broken pages (404 errors) — set up 301 redirects")
    if missing_h1 and int(missing_h1) > 0:
        critical_actions.append(f"Add H1 tags to {missing_h1} pages")
    critical_actions += [
        "Add FAQPage schema to top 5 content pages",
        "Submit updated XML sitemap to Google Search Console",
        "Fix any mixed content (HTTP images on HTTPS pages)",
    ]
    for action in critical_actions:
        add_bullet(doc, action)

    add_heading(doc, "🟠  High Priority — Complete Within 60 Days", 3)
    for action in [
        "Write/improve meta descriptions for all pages below 70 on-page score",
        "Fix image alt text on all pages (target 100% coverage)",
        "Add Organization schema to homepage",
        "Start guest post outreach — target 5 new backlinks per month",
        "Create or claim Google Business Profile",
        "Set up direct answer blocks (50-100 words) on top landing pages",
    ]:
        add_bullet(doc, action)

    add_heading(doc, "🟡  Medium Priority — Ongoing (60–180 Days)", 3)
    for action in [
        "Implement Pillar + Cluster content architecture",
        "Add Article schema to all blog posts",
        "Build 5 content pillars with 8-10 cluster articles each",
        "Link building: 5 guest posts per month in niche publications",
        "Pinterest/YouTube presence for additional traffic channels",
        "Add BreadcrumbList schema site-wide",
        "Monthly GSC review — monitor CTR, avg position, index coverage",
    ]:
        add_bullet(doc, action)

    add_page_break(doc)

    # ── SECTION 6: WHAT WE BRING ──────────────────────────────────────────

    add_heading(doc, "How Dare Network Adds Value", 2)

    value_tbl = doc.add_table(rows=1, cols=2)
    value_tbl.style = "Table Grid"
    h = value_tbl.rows[0].cells
    h[0].text = "What We Bring to the Table"
    h[1].text = "What You Get"
    for cell in h:
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = WHITE
        set_cell_bg(cell, "0D0D0D")

    for left, right in [
        ("AI-Powered SEO OS",          "Automated audits, briefs, and reports at agency speed"),
        ("Content Strategy",           "Pillar + Cluster architecture that captures long-tail traffic"),
        ("Technical SEO Execution",    "Direct implementation — no back-and-forth"),
        ("AEO/GEO Optimisation",       "Structured to appear in AI Overviews and chatbot answers"),
        ("Monthly Reporting",          "Clear progress reporting tied to business outcomes"),
    ]:
        row = value_tbl.add_row().cells
        row[0].text = left
        row[1].text = right

    doc.add_paragraph()
    add_body(doc, "— End of Audit Report —", MID_GREY)
    add_body(doc, "For questions about this audit or to begin implementation, contact Dare Network.")
    add_body(doc, "www.darenetwork.in", PURPLE)

    return doc


def _calc_tech_score(summary: dict) -> int:
    score = 100
    broken = int(summary.get("status_404", 0) or 0)
    noindex = int(summary.get("noindex_pages", 0) or 0)
    missing_h1 = int(summary.get("missing_h1", 0) or 0)
    missing_meta = int(summary.get("missing_meta_desc", 0) or 0)
    score -= min(broken * 3, 30)
    score -= min(noindex * 2, 20)
    score -= min(missing_h1 * 2, 20)
    score -= min(missing_meta * 1, 10)
    return max(score, 10)


# ─────────────────────────────────────────────────────────────────────────────
# MONTHLY REPORT (kept simpler — Word format)
# ─────────────────────────────────────────────────────────────────────────────

def build_monthly_docx(client_slug: str, website_url: str, brand_kit: dict, month: str) -> Document:
    doc = Document()
    info         = brand_kit.get("client_info", {})
    client_name  = info.get("client_name", client_slug)
    month_label  = datetime.strptime(month, "%Y-%m").strftime("%B %Y") if month else "Last Month"

    add_heading(doc, f"Monthly SEO Report — {month_label}", 2)
    add_body(doc, f"Client: {client_name}  |  {website_url}  |  Prepared by Dare Network")
    doc.add_paragraph()

    add_heading(doc, "1. Organic Traffic (GA4)", 3)
    add_body(doc, "Connect GA4 to pull live data. Expected metrics: organic sessions, users, avg session duration, bounce rate.")

    add_heading(doc, "2. Search Rankings (Google Search Console)", 3)
    add_body(doc, "Connect GSC to pull impressions, clicks, CTR, and average position data.")

    add_heading(doc, "3. Content Published This Month", 3)
    add_body(doc, "List articles published this month from active_campaigns/ folder.")

    add_heading(doc, "4. Links Built This Month", 3)
    add_body(doc, "List links acquired from outreach tracking in active_campaigns/.")

    add_heading(doc, "5. Next Month Priorities", 3)
    for i, item in enumerate(["Priority 1", "Priority 2", "Priority 3"], 1):
        add_bullet(doc, item)

    add_body(doc, f"\n— Report generated by SEO AI OS | Dare Network | {datetime.now().strftime('%B %d, %Y')} —", MID_GREY)
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SEO Report Builder — Word (.docx)")
    parser.add_argument("--client", help="Client slug (folder name in clients/). Omit for a standalone URL audit.")
    parser.add_argument("--url",    help="Website URL (used when --client is not provided)")
    parser.add_argument("--type",   required=True, choices=["audit", "monthly"])
    parser.add_argument("--month",  help="Month for monthly report: YYYY-MM")
    args = parser.parse_args()

    # Resolve client info
    if args.client:
        client_slug = args.client
        brand_kit   = load_brand_kit(client_slug)
        website_url = brand_kit.get("client_info", {}).get("website_url", f"{client_slug}.com")
        output_dir  = Path(f"clients/{client_slug}/audit_history" if args.type == "audit" else f"clients/{client_slug}/reports")
    elif args.url:
        # Standalone audit — no client folder needed
        url_slug    = args.url.replace("https://","").replace("http://","").replace("/","").replace(".","_")
        client_slug = url_slug
        brand_kit   = {"client_info": {"client_name": args.url, "website_url": args.url}}
        website_url = args.url
        output_dir  = Path(".tmp/reports")
    else:
        print("[Error] Provide --client or --url"); return

    output_dir.mkdir(parents=True, exist_ok=True)

    today    = date.today().strftime("%Y-%m-%d")
    filename = f"{today}_{args.type}_report.docx"
    if args.type == "monthly" and args.month:
        filename = f"{args.month}_{args.type}_report.docx"
    output_path = output_dir / filename

    print(f"[Report Builder] Generating {args.type} report for: {website_url}")

    if args.type == "audit":
        doc = build_audit_docx(client_slug, website_url, brand_kit)
    else:
        month = args.month or datetime.now().strftime("%Y-%m")
        doc   = build_monthly_docx(client_slug, website_url, brand_kit, month)

    doc.save(str(output_path))
    print(f"\n✅ Report saved to: {output_path}")
    print(f"📄 Open to download: file:///{str(output_path).replace(chr(92), '/')}")


if __name__ == "__main__":
    main()
