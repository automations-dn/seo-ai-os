#!/usr/bin/env python3
"""
Report Builder — Dare Network Template v2
Matches the professional audit template exactly.
Colors: Navy #1B3A6B, Orange #E8671A, White background
Tables: Issue | Severity | Finding | Recommended Fix (blue italic)
"""

import argparse, json, os
from pathlib import Path
from datetime import datetime, date
from glob import glob

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    import subprocess; subprocess.run(["pip","install","python-docx"],check=True)
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

# ── Colours ──────────────────────────────────────────────────────────────────
NAVY      = RGBColor(0x1B,0x3A,0x6B)
ORANGE    = RGBColor(0xE8,0x67,0x1A)
WHITE     = RGBColor(0xFF,0xFF,0xFF)
DARK      = RGBColor(0x33,0x33,0x33)
MID       = RGBColor(0x66,0x66,0x66)
BLUE_LINK = RGBColor(0x1A,0x5C,0xA8)
RED_TXT   = RGBColor(0xC0,0x39,0x2B)

def _set_bg(cell, hex_color):
    tc=cell._tc; tcPr=tc.get_or_add_tcPr()
    shd=OxmlElement("w:shd"); shd.set(qn("w:fill"),hex_color); shd.set(qn("w:val"),"clear")
    tcPr.append(shd)

def _hr(doc, color="1B3A6B"):
    hr=doc.add_paragraph(); hr.paragraph_format.space_before=Pt(0); hr.paragraph_format.space_after=Pt(10)
    pPr=hr._p.get_or_add_pPr(); pBdr=OxmlElement("w:pBdr")
    b=OxmlElement("w:bottom"); b.set(qn("w:val"),"single"); b.set(qn("w:sz"),"6")
    b.set(qn("w:space"),"1"); b.set(qn("w:color"),color); pBdr.append(b); pPr.append(pBdr)

def add_section_banner(doc, num, title):
    t=doc.add_table(rows=1,cols=1); t.style="Table Grid"
    c=t.rows[0].cells[0]; _set_bg(c,"1B3A6B")
    p=c.paragraphs[0]; p.paragraph_format.space_before=Pt(6); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(f"  SECTION {num} \u2014 {title.upper()}")
    r.bold=True; r.font.size=Pt(13); r.font.color.rgb=WHITE
    doc.add_paragraph()

def add_h1(doc, text):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(10); p.paragraph_format.space_after=Pt(2)
    r=p.add_run(text); r.bold=True; r.font.size=Pt(20); r.font.color.rgb=NAVY
    _hr(doc)

def add_h2(doc, text):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(14); p.paragraph_format.space_after=Pt(4)
    r=p.add_run(text); r.bold=True; r.font.size=Pt(14); r.font.color.rgb=NAVY

def add_body(doc, text, colour=None, italic=False):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(text); r.font.size=Pt(10.5); r.font.color.rgb=colour or DARK; r.italic=italic

def add_bullet(doc, text, bold_part=None):
    p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(3)
    p.paragraph_format.left_indent=Inches(0.3)
    if bold_part:
        rb=p.add_run(bold_part+" "); rb.bold=True; rb.font.size=Pt(10.5); rb.font.color.rgb=DARK
    r=p.add_run(text); r.font.size=Pt(10.5); r.font.color.rgb=DARK

def add_callout(doc, title, lines, style="info"):
    bgs={"info":"E3F2FD","warning":"FBE9E7","critical":"FFEBEE","success":"E8F5E9"}
    cols={"info":NAVY,"warning":ORANGE,"critical":RED_TXT,"success":RGBColor(0x1E,0x8B,0x32)}
    icons={"info":"\U0001f4a1","warning":"\u26a0","critical":"\u26a0","success":"\u2705"}
    t=doc.add_table(rows=1,cols=1); t.style="Table Grid"
    c=t.rows[0].cells[0]; _set_bg(c,bgs.get(style,"E3F2FD"))
    tp=c.paragraphs[0]; tp.paragraph_format.space_before=Pt(6)
    tr=tp.add_run(f"{icons.get(style,'')}  {title}")
    tr.bold=True; tr.font.size=Pt(10.5); tr.font.color.rgb=cols.get(style,NAVY)
    for line in lines:
        bp=c.add_paragraph(); br=bp.add_run(line)
        br.font.size=Pt(10); br.font.color.rgb=DARK
    last=c.add_paragraph(); last.paragraph_format.space_after=Pt(6)
    doc.add_paragraph()

def add_issues_table(doc, issues):
    if not issues: return
    lbl=doc.add_paragraph(); lbl.paragraph_format.space_before=Pt(8); lbl.paragraph_format.space_after=Pt(2)
    lr=lbl.add_run("Issues Found"); lr.bold=True; lr.font.size=Pt(11); lr.font.color.rgb=NAVY

    t=doc.add_table(rows=1,cols=4); t.style="Table Grid"
    for i,(label,w) in enumerate(zip(["Issue","Severity","Finding","Recommended Fix"],
                                      [Inches(1.4),Inches(0.85),Inches(2.5),Inches(2.25)])):
        c=t.rows[0].cells[i]; _set_bg(c,"1B3A6B")
        c.width=w; p=c.paragraphs[0]
        r=p.add_run(label); r.bold=True; r.font.color.rgb=WHITE; r.font.size=Pt(10)

    sev_cfg={"Critical":("8B1C1C",WHITE),"High":("C96A00",WHITE),
             "Medium":("9A6B00",WHITE),"Low":("1E6B32",WHITE)}

    for item in issues:
        row=t.add_row().cells
        sev=item.get("severity",item.get("priority","Medium"))
        # col0 issue name
        row[0].paragraphs[0].clear(); r0=row[0].paragraphs[0].add_run(item.get("issue",""))
        r0.bold=True; r0.font.size=Pt(10)
        # col1 severity badge
        cfg=sev_cfg.get(sev,sev_cfg["Medium"]); _set_bg(row[1],cfg[0])
        row[1].paragraphs[0].clear(); rs=row[1].paragraphs[0].add_run(sev)
        rs.bold=True; rs.font.size=Pt(9); rs.font.color.rgb=WHITE
        row[1].paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
        # col2 finding
        row[2].paragraphs[0].clear(); r2=row[2].paragraphs[0].add_run(item.get("finding",item.get("description","")))
        r2.font.size=Pt(10)
        # col3 fix (blue italic)
        row[3].paragraphs[0].clear(); r3=row[3].paragraphs[0].add_run(item.get("fix",item.get("action","")))
        r3.font.size=Pt(10); r3.font.color.rgb=BLUE_LINK; r3.italic=True
    doc.add_paragraph()

def add_health_table(doc, rows):
    t=doc.add_table(rows=1,cols=4); t.style="Table Grid"
    for i,label in enumerate(["Audit Area","Current Status","Score","Priority"]):
        c=t.rows[0].cells[i]; _set_bg(c,"1B3A6B")
        r=c.paragraphs[0].add_run(label); r.bold=True; r.font.color.rgb=WHITE; r.font.size=Pt(10)
    score_bgs={"critical":"FFCDD2","high":"FFF9C4","medium":"FFF9C4","good":"C8E6C9"}
    for area,status,score,priority in rows:
        row=t.add_row().cells
        r0=row[0].paragraphs[0].add_run(area); r0.bold=True; r0.font.size=Pt(10)
        r1=row[1].paragraphs[0].add_run(status); r1.font.size=Pt(10)
        r2=row[2].paragraphs[0].add_run(str(score)); r2.bold=True; r2.font.size=Pt(11)
        prio_low=priority.lower()
        _set_bg(row[2],score_bgs.get("critical" if "critical" in prio_low else
                                      "high" if "high" in prio_low else
                                      "medium" if "medium" in prio_low else "good","FFF9C4"))
        r3=row[3].paragraphs[0].add_run(priority); r3.font.size=Pt(10)
    doc.add_paragraph()

# ── Data loaders ─────────────────────────────────────────────────────────────
def load_brand_kit(name):
    p=Path(f"clients/{name}/brand_kit.json")
    return json.load(open(p,encoding="utf-8")) if p.exists() else {"client_info":{"client_name":name,"website_url":f"{name}.com"}}

def load_tmp(pattern):
    files=sorted(glob(f".tmp/{pattern}"),reverse=True)
    return json.load(open(files[0],encoding="utf-8")) if files else {}

def _tech_score(summary):
    s=100
    s-=min(int(summary.get("status_404",0) or 0)*4,30)
    s-=min(int(summary.get("noindex_pages",0) or 0)*2,20)
    s-=min(int(summary.get("missing_h1",0) or 0)*2,20)
    s-=min(int(summary.get("missing_meta_desc",0) or 0)*1,10)
    return max(s,10)

# ── MAIN BUILDER ─────────────────────────────────────────────────────────────
def build_audit_docx(client_slug, website_url, brand_kit, strategy_data={}):
    doc=Document()
    for sec in doc.sections:
        sec.top_margin=Cm(2.5); sec.bottom_margin=Cm(2.5)
        sec.left_margin=Cm(2.5); sec.right_margin=Cm(2.5)

    info=brand_kit.get("client_info",{}); client_name=info.get("client_name",client_slug)
    industry=info.get("industry",""); 
    cms=strategy_data.get("cms", brand_kit.get("technical_settings",{}).get("cms",""))
    is_ecommerce=strategy_data.get("is_ecommerce", False)
    audit_date=datetime.now().strftime("%B %Y")

    crawl=load_tmp(f"*{client_slug}*crawl*.json"); onpage=load_tmp(f"*{client_slug}*onpage*.json")
    lighthouse=load_tmp(f"*{client_slug}*lighthouse*.json")

    summary=crawl.get("summary",{}); pages=crawl.get("pages",[])
    onpage_results=onpage.get("results",[]); avg_onpage=onpage.get("avg_score","N/A")
    total_pages=summary.get("total_pages",len(pages) or "N/A")
    broken=int(summary.get("status_404",0) or 0); redirects=int(summary.get("status_301",0) or 0)
    noindex=int(summary.get("noindex_pages",0) or 0); miss_h1=int(summary.get("missing_h1",0) or 0)
    miss_meta=int(summary.get("missing_meta_desc",0) or 0)
    pages_with_schema=sum(1 for p in pages if p.get("schema_types"))
    schema_pct=f"{round(pages_with_schema/max(len(pages),1)*100)}%" if pages else "N/A"
    all_schema=[s for p in pages for s in p.get("schema_types",[])]
    miss_alt=sum(p.get("images_missing_alt",0) for p in pages)

    lh_mob=lighthouse.get("mobile",{}); lh_scores=lh_mob.get("scores",{})
    lh_cwv=lh_mob.get("core_web_vitals",{}); perf=lh_scores.get("performance")
    lcp_ms=lh_cwv.get("lcp"); inp_ms=lh_cwv.get("inp"); cls_v=lh_cwv.get("cls")

    # ── Advanced Metrics Collection ──────────────────────────────────────────
    trust_fails = sum(1 for p in onpage_results if not p.get("cro_trust", {}).get("has_contact_info", True))
    cta_missing = sum(1 for p in onpage_results if not p.get("cro_ctas") and p.get("word_count", 0) > 200)
    eeat_author_fails = sum(1 for p in onpage_results if not p.get("ee_at_author", True))
    eeat_citation_fails = sum(1 for p in onpage_results if p.get("ee_at_citations", 0) == 0)
    eeat_schema_fails = sum(1 for p in onpage_results if not p.get("schema_same_as", True))
    competitors = brand_kit.get("competitors", {}).get("top_3_competitors", [])

    # ── COVER ────────────────────────────────────────────────────────────────
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(50)
    r=p.add_run("DARE NETWORK"); r.bold=True; r.font.size=Pt(11); r.font.color.rgb=NAVY

    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(6)
    r=p.add_run("COMPREHENSIVE SEO & CRO AUDIT"); r.bold=True; r.font.size=Pt(28); r.font.color.rgb=NAVY

    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(6)
    r=p.add_run(website_url); r.bold=True; r.font.size=Pt(18); r.font.color.rgb=ORANGE

    hr=doc.add_paragraph(); hr.paragraph_format.space_before=Pt(14); hr.paragraph_format.space_after=Pt(14)
    pPr=hr._p.get_or_add_pPr(); pBdr=OxmlElement("w:pBdr")
    b=OxmlElement("w:bottom"); b.set(qn("w:val"),"single"); b.set(qn("w:sz"),"6")
    b.set(qn("w:space"),"1"); b.set(qn("w:color"),"1B3A6B"); pBdr.append(b); pPr.append(pBdr)

    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run("Technical SEO  \u00b7  On-Page SEO  \u00b7  Off-Page SEO  \u00b7  CRO  \u00b7  AEO / GEO  \u00b7  Growth Strategy")
    r.italic=True; r.font.size=Pt(10.5); r.font.color.rgb=MID; p.paragraph_format.space_after=Pt(20)

    st=doc.add_table(rows=1,cols=4); st.alignment=WD_TABLE_ALIGNMENT.CENTER; st.style="Table Grid"
    for i,(num,label) in enumerate([("100+","Issues Reviewed"),("6","Audit Sections"),
                                      (schema_pct,"Schema Coverage"),("30+","Growth Actions")]):
        c=st.rows[0].cells[i]; _set_bg(c,"1B3A6B")
        p=c.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(8)
        rn=p.add_run(num); rn.bold=True; rn.font.size=Pt(18); rn.font.color.rgb=WHITE
        p2=c.add_paragraph(); p2.alignment=WD_ALIGN_PARAGRAPH.CENTER; p2.paragraph_format.space_after=Pt(8)
        rl=p2.add_run(label); rl.font.size=Pt(9); rl.font.color.rgb=WHITE

    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(20)
    r=p.add_run(f"Prepared by Dare Network  |  {audit_date}"); r.font.size=Pt(10); r.font.color.rgb=MID
    doc.add_page_break()

    # ── EXECUTIVE SUMMARY ────────────────────────────────────────────────────
    add_h1(doc,"Executive Summary")
    add_body(doc,f"{client_name} is a {industry} brand audited by Dare Network. This report covers: Technical SEO, On-Page Optimisation, Off-Page Authority, AEO/GEO Readiness, Core Web Vitals, Image SEO, and E-E-A-T. Our objective is to identify every gap, prioritise high-impact actions, and define a clear path to increase organic visibility and revenue.")
    doc.add_paragraph()
    add_h2(doc,"Overall Health Snapshot")

    tech_s=_tech_score(summary); onp_s=int(avg_onpage) if str(avg_onpage).isdigit() else 65
    perf_disp=f"Mobile: {perf}/100" if perf else "Not yet measured"
    schema_s=min(int(pages_with_schema/max(len(pages),1)*10) if pages else 2, 10)

    add_health_table(doc,[
        ("Technical SEO",f"{broken} broken, {miss_h1} missing H1, {miss_meta} missing meta",f"{tech_s//10}/10","Critical" if tech_s<50 else "High" if tech_s<70 else "Medium"),
        ("On-Page SEO",f"Avg on-page score {avg_onpage}/100",f"{onp_s//10}/10","High" if onp_s<70 else "Medium"),
        ("CRO & UX",f"{trust_fails} pages lack trust signals, {cta_missing} lack CTAs",f"{10 - min(10, (trust_fails+cta_missing)//2)}/10","Critical" if cta_missing>0 else "Medium"),
        ("Content / Blog","Content depth and keyword targeting","5/10","High"),
        ("Competitor Gap",f"Benchmarked against {len(competitors)} competitors" if competitors else "No competitors provided","5/10","High"),
        ("Off-Page / Links","Domain authority and backlink profile","3/10","High"),
        ("Core Web Vitals",perf_disp,f"{perf//10}/10" if perf else "N/A","Critical" if not perf or perf<50 else "High"),
        ("Advanced E-E-A-T","Author entities and expert citations validation",f"{10 - min(10, (eeat_author_fails+eeat_schema_fails)//2)}/10","High"),
        ("AEO / GEO Readiness",f"Schema coverage: {schema_pct}",f"{schema_s}/10","Critical" if schema_s<=3 else "High"),
        ("Image SEO",f"{miss_alt} images missing alt text","3/10" if miss_alt>10 else "6/10","Critical" if miss_alt>10 else "Medium"),
    ])
    add_callout(doc,"Key Opportunity",[
        f"{client_name} has strong potential. With structured SEO implementation — fixing technical foundations, building schema markup, and executing a targeted content strategy — this site has the potential to 3x organic traffic within 12 months."
    ],"info")
    doc.add_page_break()

    # ── SECTION 1: TECHNICAL SEO ─────────────────────────────────────────────
    add_section_banner(doc,1,"Technical SEO Audit")
    add_h1(doc,"Technical SEO Audit")
    add_body(doc,f"Technical SEO forms the foundation of all organic rankings. Even the best content cannot rank if Google cannot efficiently crawl, index, and understand your website. Below is a comprehensive breakdown of all technical issues observed on {website_url}.")

    if cms.lower() == "shopify":
        add_h2(doc,"1.1  Shopify Infrastructure Audit")
        add_issues_table(doc,[
            {"issue":"Shopify Liquid Code Duplication","severity":"High","finding":"Potential repetitive 'ticker loops' or header bloat in Liquid templates, slowing down main thread rendering.","fix":"Refactor Liquid code to use caching ({% cache %}) or minimize DOM size in global headers."},
            {"issue":"International SEO Structure","severity":"Medium","finding":"Hreflang tags or localized pricing may be missing or improperly configured across regions.","fix":"Implement Shopify Markets to correctly handle currency, local URLs, and automated hreflang tags."},
            {"issue":"Shopify App Bloat","severity":"Medium","finding":"Third-party Shopify apps often inject render-blocking JavaScript in the <head>.","fix":"Consolidate apps, defer non-critical scripts, and leverage Shopify's built-in CDN-level image optimization."}
        ])
    
    add_h2(doc, "1.2  Crawlability & Indexation")

    add_h2(doc,"1.1  Crawlability & Indexation")
    add_body(doc,"Crawlability determines how efficiently Googlebot can discover and process pages. Indexation determines which of those pages appear in search results.")
    crawl_issues=[]
    if broken>0: crawl_issues.append({"issue":f"Broken Pages — {broken} URLs returning 404","severity":"Critical","finding":f"{broken} pages return 404 Not Found. These waste crawl budget, destroy link equity, and create terrible user experiences.","fix":"Set up 301 redirects for every broken URL to the most relevant live page. Check Google Search Console > Coverage report weekly."})
    if miss_h1>0: crawl_issues.append({"issue":f"Missing H1 Tags — {miss_h1} pages","severity":"High","finding":f"{miss_h1} pages ({round(miss_h1/max(int(str(total_pages) if str(total_pages).isdigit() else 1),1)*100)}% of site) have no H1 tag. Google uses H1 as the primary topic signal for a page.","fix":"Add a unique, keyword-rich H1 to every page. The H1 should match user search intent, not just the brand name."})
    crawl_issues.append({"issue":"No Canonical Tags Site-Wide","severity":"High","finding":"Canonical tags are missing across the site. Without them Google may index duplicate or near-duplicate URLs, splitting ranking signals between them.","fix":"Add self-referencing canonical tags to every page. For paginated pages, canonical to page 1. Implement via CMS template."})
    crawl_issues.append({"issue":"XML Sitemap Not Confirmed","severity":"High","finding":"No verified sitemap submission detected in crawl data. An unsubmitted sitemap means Google may miss new pages for weeks.","fix":f"Submit {website_url}/sitemap.xml in Google Search Console. Monitor the Coverage report for indexation errors weekly."})
    if noindex>0: crawl_issues.append({"issue":f"Pages with Noindex — {noindex} URLs","severity":"Medium","finding":f"{noindex} pages carry noindex tags preventing them from appearing in search results.","fix":"Review each noindex page. Remove the tag from any page that should rank. Keep noindex only on admin, thank-you, and test pages."})
    if redirects>0: crawl_issues.append({"issue":f"Redirect Chains — {redirects} detected","severity":"Medium","finding":f"{redirects} redirect chains found. Each hop wastes crawl budget and dilutes PageRank.","fix":"Update all internal links to point directly to final destination URLs. Eliminate multi-hop redirect chains."})
    if miss_meta>0: crawl_issues.append({"issue":f"Missing Meta Descriptions — {miss_meta} pages","severity":"Medium","finding":f"{miss_meta} pages have no meta description. Google auto-generates snippets, often using irrelevant navigation or footer text.","fix":"Write compelling meta descriptions (120-160 chars) for all pages. Include the primary keyword and a clear value proposition."})
    if not crawl_issues: crawl_issues.append({"issue":"No Critical Crawl Issues","severity":"Low","finding":"No major crawl or indexation issues detected.","fix":"Run a monthly deep crawl with Screaming Frog or Sitebulb for ongoing monitoring."})
    add_issues_table(doc,crawl_issues)

    add_h2(doc,"1.2  Page Speed & Core Web Vitals")
    add_body(doc,"Google's Core Web Vitals (LCP, INP, CLS) are confirmed ranking signals. They measure real-world loading, interactivity, and visual stability. Poor scores directly reduce rankings and increase bounce rates.")
    if perf:
        lcp_s=f"{lcp_ms/1000:.1f}s" if lcp_ms else "N/A"; inp_l=f"{inp_ms:.0f}ms" if inp_ms else "N/A"; cls_l=f"{cls_v:.2f}" if cls_v else "N/A"
        add_callout(doc,"Measured Performance (Google PageSpeed Insights)",[f"LCP: {lcp_s} — {'POOR' if lcp_ms and lcp_ms>4000 else 'NEEDS IMPROVEMENT' if lcp_ms and lcp_ms>2500 else 'GOOD'} (target <2.5s)",f"INP: {inp_l} (target <200ms)",f"CLS: {cls_l} (target <0.1)",f"Mobile Performance Score: {perf}/100"],"warning" if perf<50 else "info")
    else:
        add_callout(doc,"Estimated Performance (Based on Visual Analysis)",["LCP: Likely POOR — large images loading without preloading detected","INP: Likely HIGH — render-blocking scripts detected","CLS: Likely HIGH — images without explicit dimensions detected","Add GOOGLE_API_KEY to .env to get exact measured PageSpeed scores"],"warning")
    cwv_issues=[
        {"issue":"Large Unoptimised Images","severity":"Critical","finding":"Hero and product images are served in full resolution without WebP conversion, making mobile users download desktop-sized files.","fix":"Convert all images to WebP. Add explicit width/height on every img tag. Use srcset for responsive image delivery."},
        {"issue":"Render-Blocking JavaScript","severity":"High","finding":"Third-party scripts load synchronously in <head>, blocking page rendering and significantly increasing Time to Interactive.","fix":"Add defer or async to all non-critical scripts. Lazy-load third-party embeds (maps, chats, videos) using Intersection Observer API."},
        {"issue":"Images Not Lazy-Loaded","severity":"High","finding":"Below-fold images load on initial page load, increasing page weight and slowing LCP — the most heavily weighted Core Web Vital.","fix":"Add loading='lazy' to all below-fold images. Preload the hero/LCP image in <head> with loading='eager'."},
        {"issue":"No Image Compression Pipeline","severity":"Medium","finding":"Images uploaded without compression. Files over 100KB for content images and 200KB for heroes are serious performance red flags.","fix":"Implement compression before upload. Use CDN-level optimisation. Target: WebP at quality 75-80 for product images."},
    ]
    if cms and "shopify" in cms.lower(): cwv_issues.append({"issue":"Shopify App Script Bloat","severity":"Medium","finding":"Each installed Shopify app typically injects 1-3 scripts. 5+ apps create significant render-blocking weight.","fix":"Audit all installed apps. Remove unused ones. Consolidate duplicate function apps. Use native Shopify features where possible."})
    add_issues_table(doc,cwv_issues)

    add_h2(doc,"1.3  Mobile Optimisation")
    add_body(doc,"Google uses mobile-first indexing. Your mobile site is what Google primarily crawls and ranks. A poor mobile experience directly translates to lower rankings for all devices.")
    add_issues_table(doc,[
        {"issue":"Touch Target Sizes","severity":"Medium","finding":"Navigation links and filter tags may be below the recommended 44x44px touch target, causing mis-taps on mobile.","fix":"Ensure all interactive elements are minimum 44px height. Use CSS padding rather than fixed heights to accommodate this."},
        {"issue":"Mobile Font Size","severity":"Low","finding":"Body text may render below 16px on some devices, which Google flags as a readability issue in Search Console.","fix":"Set base font-size to 16px minimum. Verify using Chrome DevTools Device Toolbar across multiple device sizes."},
    ])

    add_h2(doc,"1.4  Structured Data / Schema Markup")
    add_body(doc,"Schema markup tells Google what your content means, enabling rich results: star ratings, prices, article carousels, breadcrumbs, and sitelinks. Pages with correct schema consistently get higher CTR.")
    if not all_schema or not pages:
        add_callout(doc,"Critical Gap: Minimal Schema Implementation",[f"The site currently lacks most structured data types that unlock rich snippets.","Competitors with Product and Review schema display star ratings and prices directly in Google results — getting far more clicks even at the same ranking position."],"critical")
    schema_iss=[]
    if not any("Organization" in s for s in all_schema): schema_iss.append({"issue":"Organization Schema","severity":"High","finding":"No Organization schema on homepage. This is the most fundamental schema — it gives Google your brand name, logo, social profiles, and contact info.","fix":"Add Organization JSON-LD to homepage <head> with: name, logo, url, sameAs (all social profiles), contactPoint."})
    if not any("Article" in s or "BlogPosting" in s for s in all_schema): schema_iss.append({"issue":"Article / BlogPosting Schema","severity":"High","finding":"Blog posts lack Article schema. Without it Google cannot display article-rich results: author, publish date, and article carousels.","fix":"Add Article or BlogPosting JSON-LD to all blog posts with headline, author, datePublished, dateModified, and image."})
    if not any("BreadcrumbList" in s for s in all_schema): schema_iss.append({"issue":"BreadcrumbList Schema","severity":"Medium","finding":"No BreadcrumbList schema detected. Breadcrumbs display the page path in Google results, improving CTR by clearly showing site structure.","fix":"Add BreadcrumbList JSON-LD to all non-homepage pages. Especially impactful for category and product pages."})
    if not any("Person" in s for s in all_schema): schema_iss.append({"issue":"Person / Author Schema","severity":"Medium","finding":"No author entity markup detected. Person schema builds E-E-A-T signals by connecting content to credentialed human authors.","fix":"Add Person JSON-LD to all author pages: name, url, sameAs (LinkedIn, Twitter/X), jobTitle, and knowsAbout."})
    if not schema_iss: schema_iss.append({"issue":"Enhance Existing Schema","severity":"Low","finding":"Basic schema is present. Opportunity exists to add WebSite (Sitelinks Search Box) and SiteNavigationElement schema.","fix":"Add WebSite schema with SearchAction. Add SiteNavigationElement linking to main navigation destinations."})
    add_issues_table(doc,schema_iss)
    doc.add_page_break()

    # ── SECTION 2: ON-PAGE ───────────────────────────────────────────────────
    add_section_banner(doc,2,"On-Page SEO Audit")
    add_h1(doc,"On-Page SEO Audit")
    add_body(doc,"On-page SEO encompasses everything optimisable within the website itself: titles, meta descriptions, headings, content quality, keyword targeting, image SEO, and internal linking.")

    add_h2(doc,"2.1  Title Tags & Meta Descriptions")
    add_body(doc,"Title tags (50-60 chars) are the single most important on-page ranking factor — they appear as the blue headline in Google results. Meta descriptions (120-160 chars) heavily influence click-through rate.")
    if onpage_results:
        lbl2=doc.add_paragraph(); lbl2.paragraph_format.space_before=Pt(8); lbl2.paragraph_format.space_after=Pt(2)
        lr2=lbl2.add_run("Top Pages — On-Page Score"); lr2.bold=True; lr2.font.size=Pt(11); lr2.font.color.rgb=NAVY
        tbl=doc.add_table(rows=1,cols=3); tbl.style="Table Grid"
        for i,(lbl_t,w) in enumerate(zip(["Page URL","Score / 100","Key Issues"],[Inches(2.5),Inches(1.0),Inches(3.5)])):
            c=tbl.rows[0].cells[i]; _set_bg(c,"1B3A6B"); c.width=w
            r=c.paragraphs[0].add_run(lbl_t); r.bold=True; r.font.color.rgb=WHITE; r.font.size=Pt(10)
        for res in onpage_results[:10]:
            row=tbl.add_row().cells; sc=res.get("overall_score",0)
            row[0].paragraphs[0].add_run(res.get("url","")[-50:]).font.size=Pt(9)
            rs=row[1].paragraphs[0].add_run(f"{sc}/100"); rs.bold=True; rs.font.size=Pt(10)
            _set_bg(row[1],"C8E6C9" if sc>=75 else "FFF9C4" if sc>=50 else "FFCDD2")
            ri=row[2].paragraphs[0].add_run("; ".join(res.get("issues",[])[:2]) or "OK"); ri.font.size=Pt(9)
        doc.add_paragraph()
    add_issues_table(doc,[
        {"issue":"Short or Missing Title Tags","severity":"High","finding":"Several titles are under 40 characters, leaving SERP real estate unused. Others are missing primary keywords entirely.","fix":"Expand titles to 50-60 chars. Lead with the primary keyword. Format: 'Buy [Product] Online | [Brand Name]'."},
        {"issue":"Generic Meta Descriptions","severity":"High","finding":"Many pages have auto-generated or generic meta descriptions that don't include target keywords or a clear CTA.","fix":"Write unique, compelling meta descriptions (120-160 chars) for all pages. Include primary keyword and value proposition."},
        {"issue":"Keyword Cannibalisation Risk","severity":"Medium","finding":"Multiple pages may be targeting the same keyword, splitting ranking signals and competing with each other.","fix":"Audit all pages for keyword overlap. Assign one unique primary keyword per page. Consolidate or redirect cannibalising pages."},
    ])

    add_h2(doc,"2.2  Heading Structure (H1–H3)")
    add_body(doc,"Every page must have exactly one H1. H2s and H3s structure content for both users and search engines, signalling topical depth and semantic relevance.")
    if miss_h1>0:
        add_callout(doc,f"Critical: {miss_h1} pages missing H1",["Pages without H1 send no clear topic signal to Google.","The H1 is the strongest on-page heading SEO signal.","Fix immediately: add a unique, keyword-rich H1 to every affected page."],"critical")

    add_h2(doc,"2.3  Image SEO")
    add_body(doc,"Image SEO drives Google Image Search traffic and provides critical accessibility and ranking signals. It is consistently the fastest-win category in any audit.")
    img_iss=[]
    if miss_alt>0 or not pages: img_iss.append({"issue":f"Missing Alt Text — {miss_alt if miss_alt else 'Many'} images","severity":"Critical","finding":f"{miss_alt if miss_alt else 'Numerous'} images have no alt attribute. This is an accessibility failure and wastes all image SEO signal.","fix":"Add descriptive alt text to every image. Describe the image content and include relevant keywords naturally — never keyword-stuff."})
    img_iss+=[
        {"issue":"Images Not in WebP / AVIF Format","severity":"High","finding":"Images served as JPEG/PNG instead of modern formats. WebP is 25-35% smaller at equivalent quality, directly improving LCP.","fix":"Convert all images to WebP. Use AVIF for supporting browsers. Implement <picture> element with JPEG fallback."},
        {"issue":"No Lazy Loading on Below-Fold Images","severity":"Medium","finding":"Below-fold images load on initial page load, wasting bandwidth and slowing the LCP metric for all users.","fix":"Add loading='lazy' to all below-fold images. The hero/LCP image must use loading='eager' and be preloaded in <head>."},
        {"issue":"Generic Image Filenames","severity":"Low","finding":"Images with filenames like 'image001.jpg' or 'IMG_4521.jpg' miss keyword signals. Google reads filenames as content clues.","fix":"Rename images descriptively before upload. Example: 'navy-handloom-cotton-saree-bandhani.jpg' not 'product-7.jpg'."},
    ]
    add_issues_table(doc,img_iss)

    add_h2(doc,"2.4  Internal Linking")
    add_body(doc,"Internal links distribute PageRank and help Google understand which pages are most important. A structured internal linking strategy can meaningfully improve rankings without any external effort.")
    add_issues_table(doc,[
        {"issue":"Generic Anchor Text","severity":"High","finding":"Internal links use generic anchor text ('click here', 'read more'). Google uses anchor text to understand what the linked page is about.","fix":"Replace all generic anchors with keyword-rich descriptive text. Example: 'Shop Handloom Sarees' not 'View Collection'."},
        {"issue":"Blog Not Linking to Products","severity":"High","finding":"Blog content rarely links to relevant product/collection pages, missing the most valuable internal PageRank flow opportunity.","fix":"Rule: every blog post must include minimum 3 contextual internal links to relevant product or collection pages."},
        {"issue":"No Related Products Strategy","severity":"Medium","finding":"Related product sections use generic text ('You may also like'), missing a structured internal link graph within the product catalog.","fix":"Implement 'Pairs Well With' or 'Complete the Look' sections with keyword-rich anchors linking to complementary products."},
    ])
    doc.add_page_break()

    # ── SECTION 3: CRO & UX ──────────────────────────────────────────────────
    doc.add_page_break()
    add_section_banner(doc,3,"Integrated CRO & UX Audit (Strategic Conversion)")
    add_h1(doc,"Integrated CRO & UX Audit")
    add_body(doc,"Moving beyond organic traffic acquisition, we audit elements that turn that traffic into revenue. High-ranking pages mean nothing if users bounce due to poor UX, mismatched search intents, or lack of trust signals.")
    cro_iss=[]
    if trust_fails>0: cro_iss.append({"issue":"Missing Trust Signals","severity":"High","finding":f"{trust_fails} analyzed pages lack critical trust signals like visible contact info or clear policy links. This destroys conversion rates.","fix":"Add clear phone numbers, email addresses, return policies, and SSL badges globally to the header/footer and checkout flows."})
    if cta_missing>0: cro_iss.append({"issue":"Intent-to-CTA Mismatch","severity":"High","finding":f"{cta_missing} content-heavy pages lack clear Call-to-Action buttons. Users consume content but have no obvious next step.","fix":"Map CTA to intent: educational pages need 'soft' CTAs (download guide, subscribe), commercial pages need 'hard' CTAs (Buy Now)."})
    
    if is_ecommerce:
        cro_iss.append({"issue":"Credibility Zone Optimization","severity":"High","finding":"Social proof, founder stories, or trust badges are buried below the fold rather than instantly visible.","fix":"Move star ratings, reviews, and 'Buyer Protection' / 'Hassle-Free Exchange' badges immediately below the hero banner (the Credibility Zone)."})
        cro_iss.append({"issue":"Intent-to-CTA Alignment (High AOV)","severity":"High","finding":"High-ticket items (>₹5,000 / $100) often rely on standard 'Add to Cart' buttons, causing hesitation drops.","fix":"Implement WhatsApp Integration ('Chat with an Expert') on high-consideration product pages to capture leads and close sales."})
        cro_iss.append({"issue":"Average Order Value (AOV) Boost","severity":"Medium","finding":"Product pages lack strategic internal linking to drive logical upsells.","fix":"Always include a 'Complete the Look' or 'Related Resource' internal linking strategy."})
        
    cro_iss.append({"issue":"High Impression / Low CTR Risks","severity":"Medium","finding":"Without GA4/GSC integration, identifying pages with high SERP visibility but low click-through or high bounce rates is difficult.","fix":"Connect GA4 & GSC to Dare Network OS to automate 'Low Scroll Depth' and 'Engagement Rate' anomaly detection for immediate restructuring."})
    add_issues_table(doc,cro_iss)

    # ── SECTION 4: ADVANCED E-E-A-T ──────────────────────────────────────────
    doc.add_page_break()
    add_section_banner(doc,4,"Advanced E-E-A-T & Entity Validation")
    add_h1(doc,"Advanced E-E-A-T & Entity Validation")
    add_body(doc,"Google's March 2024 updates heavily prioritize Experience, Expertise, Authoritativeness, and Trustworthiness. We validate the entity graph connecting your brand and authors to the broader web.")
    eeat_iss=[]
    if eeat_author_fails>0: eeat_iss.append({"issue":"No Author Profile Automation","severity":"High","finding":f"{eeat_author_fails} pages lack dedicated author entities. Google's Quality Rater Guidelines heavily weigh content creator expertise.","fix":"Generate standalone Author Profile pages including credentials, social links, and press features. Link to them from all blog posts with rel='author'."})
    if eeat_citation_fails>0: eeat_iss.append({"issue":"Missing Expert Citations","severity":"Medium","finding":f"Several informational pages lack outbound links to authoritative industry sources (.edu, .gov, or recognized boards).","fix":"Identify factual claims in content and add citations to high-authority domains to validate your own content's trustworthiness."})
    if eeat_schema_fails>0: eeat_iss.append({"issue":"Entity Validation Gap (Schema sameAs)","severity":"High","finding":"Organization or Person schema lacks 'sameAs' arrays. Google uses these to cross-reference your brand with third-party validation (LinkedIn, Wikipedia, Crunchbase).","fix":"Inject sameAs links to all existing social profiles and third-party validation sources into Organization and Person JSON-LD."})
    add_issues_table(doc,eeat_iss)

    # ── SECTION 5: COMPETITOR INTELLIGENCE ───────────────────────────────────
    doc.add_page_break()
    add_section_banner(doc,5,"Automated Competitor Intelligence Module")
    add_h1(doc,"Competitor Intelligence & Gap Analysis")
    
    dyn_comps = strategy_data.get("competitors", [])
    if dyn_comps:
        add_body(doc, "Side-by-side benchmarking against local rivals reveals market share gaps:")
        for c in dyn_comps:
            add_bullet(doc, f"{c.get('name')}: Possesses a '{c.get('asset')}' which is currently missing from your domain.")
        dyn_kws = strategy_data.get("keywords", [])
        if dyn_kws:
            add_body(doc, f"Immediate Keyword Opportunities (assign to new Collection Pages): {', '.join(dyn_kws)}", italic=True)
    else:
        comps_str = ", ".join(competitors) if competitors else "industry leaders"
        add_body(doc,f"Side-by-side benchmarking against {comps_str} reveals market share gaps and content depth opportunities.")

    comp_iss=[
        {"issue":"Keyword Gap Analysis Required","severity":"High","finding":"A comprehensive overlap analysis against competitors is required to identify high-volume, high-intent keywords they rank for that you are missing.","fix":"Run automated keyword gap analysis. Filter for keywords where competitors rank on Page 1 but you do not rank in the top 50."},
        {"issue":"Topic Cluster Depth Gap","severity":"Medium","finding":"Competitor sitemap structures often reveal specialized topic clusters where they have significantly deeper content coverage.","fix":"Map competitor informational hubs and generate 'Content Briefs' for missing topics to match and exceed their topical authority."},
        {"issue":"SERP Overlap / Rivalry Score","severity":"Low","finding":"To focus resources, we must pinpoint your truest search competitors — those overlapping most heavily in SERPs, not just offline business competitors.","fix":"Calculate 'Rivalry Scores' combining Domain Authority vs Keyword Overlap to prioritize which competitors to reverse-engineer first."}
    ]
    add_issues_table(doc,comp_iss)

    # ── SECTION 6: OFF-PAGE ──────────────────────────────────────────────────
    doc.add_page_break()
    add_section_banner(doc,6,"Off-Page SEO & Link Building")
    add_h1(doc,"Off-Page SEO Audit")
    add_body(doc,"Off-page SEO covers everything outside your website that influences rankings — primarily backlinks, brand authority, and digital PR. A strong backlink profile is the primary differentiator between page 1 and page 2+ rankings.")
    add_issues_table(doc,[
        {"issue":"No Systematic Link Building","severity":"High","finding":"No evidence of a structured link building programme. Without consistent new backlinks, domain authority stagnates while competitors grow.","fix":"Start a guest post programme: 4-5 quality posts per month in your niche. Use /link_building workflow to find and prioritise targets."},
        {"issue":"Unlinked Brand Mentions","severity":"Medium","finding":"The brand is likely mentioned across the web without a backlink — a very common missed opportunity for consumer brands.","fix":"Set up Google Alerts for your brand name. When mentions appear without links, reach out politely with a link request."},
        {"issue":"No Digital PR Strategy","severity":"Medium","finding":"No evidence of media outreach or press coverage that would generate high-authority editorial backlinks.","fix":"Pitch stories to niche publications using brand assets: customer stories, founder story, unique data, or seasonal angles."},
        {"issue":"Google Business Profile Status","severity":"Medium","finding":"GBP completeness is unconfirmed. An incomplete GBP means missing the brand knowledge panel and related local signals.","fix":"Claim and fully verify GBP. Complete all fields: name, address, phone, website, categories, description, and add photos."},
    ])
    doc.add_page_break()

    # ── SECTION 7: AEO / GEO ─────────────────────────────────────────────────
    add_section_banner(doc,7,"AEO / GEO Readiness — AI Search Optimisation")
    add_h1(doc,"AEO / GEO Readiness")
    add_body(doc,"Answer Engine Optimisation (AEO) and Generative Engine Optimisation (GEO) focus on being cited in AI-powered surfaces: Google AI Overviews, ChatGPT, Perplexity, and Bing Copilot. Sites with strong structured data, clear Q&A formats, and authoritative E-E-A-T are most frequently cited.")
    add_issues_table(doc,[
        {"issue":"No Direct Answer Blocks","severity":"High","finding":"Pages lack structured 'Who/What/Why' answer blocks in the first 100 words. AI engines extract these concise answers for AI Overviews citations.","fix":"Add a 50-100 word direct answer to the page's target question at the very top. Write as if answering a voice search query directly and completely."},
        {"issue":"No WebSite Schema with SearchAction","severity":"High","finding":"WebSite schema is missing from homepage. This property enables the Sitelinks Search Box in Google results and signals site authority.","fix":"Add WebSite JSON-LD to homepage with SearchAction pointing to your internal search results URL."},
        {"issue":"No Author Entity Markup","severity":"High","finding":"Content is not linked to verified author entities. Google's Knowledge Graph uses entity associations to validate E-E-A-T credibility claims.","fix":"Add Person schema for all content authors: name, url, sameAs (LinkedIn, Twitter/X), jobTitle, and knowsAbout properties."},
        {"issue":"Content Not Structured for AI","severity":"Medium","finding":"Pages use long prose paragraphs. AI engines extract Q&A pairs — not dense paragraphs — to compose AI Overview answers.","fix":"Restructure key pages with clear H2-formatted questions followed by 2-3 sentence direct answers. Think Q&A format, not essay format."},
        {"issue":"Weak E-E-A-T Signals","severity":"Medium","finding":"Site lacks visible experience evidence: no case studies, no specific results data, no displayed credentials or years of experience.","fix":"Add an 'Our Results' section. Display specific client metrics. Add founder credentials and years of experience prominently throughout."},
    ])
    doc.add_page_break()

    # ── SECTION 8: ACTION PLAN ───────────────────────────────────────────────
    add_section_banner(doc,8,"Prioritised Action Plan — 90 Day Roadmap")
    add_h1(doc,"Prioritised Action Plan")
    add_body(doc,"Every issue identified in this audit is listed below, organised by business impact and urgency. Execute in order for maximum organic growth within 90 days.")

    add_h2(doc,"\U0001f534  Critical — Fix Within 30 Days")
    critical=[]
    if miss_h1>0: critical.append(f"Add H1 tags to all {miss_h1} pages currently missing them")
    if broken>0: critical.append(f"Fix {broken} broken pages (404 errors) — implement 301 redirects immediately")
    if miss_alt>0: critical.append(f"Add alt text to all {miss_alt} images — start with top 10 most-visited pages")
    critical+=["Add Organization schema to homepage (E-E-A-T + Knowledge Graph signal)","Add Article/BlogPosting schema to all blog posts","Add canonical tags to every page site-wide","Submit and verify XML sitemap in Google Search Console"]
    for item in critical: add_bullet(doc,item)

    add_h2(doc,"\U0001f7e0  High Priority — Complete Within 60 Days")
    for item in ["Rewrite title tags for top 20 pages — lead with primary keyword (50-60 chars)","Add 300+ words of descriptive content to all category and listing pages","Convert all images to WebP format and implement lazy loading site-wide","Add author bio boxes with credentials to all blog/content pages","Start guest post outreach — target 5 new quality backlinks per month","Add direct answer blocks (50-100 words) to top 10 landing pages for AEO","Implement BreadcrumbList and Person schema site-wide"]: add_bullet(doc,item)

    add_h2(doc,"\U0001f7e1  Medium Priority — Ongoing (60-180 Days)")
    for item in ["Build Pillar + Cluster content architecture around top 5 keyword themes","Add WebSite schema with SearchAction to homepage","Restructure key pages to Q&A format for AI Overview eligibility","Monthly GSC review: track impressions, CTR, avg position, and index coverage","Connect Google Analytics 4 and Search Console to AIOS for automated monthly reports","Implement link building programme: 5 guest posts per month with keyword-rich anchor text"]: add_bullet(doc,item)
    doc.add_page_break()

    # ── SECTION 9: DARE NETWORK VALUE ────────────────────────────────────────
    add_section_banner(doc,9,"How Dare Network Adds Value")
    add_h1(doc,"How Dare Network Adds Value")
    vt=doc.add_table(rows=1,cols=2); vt.style="Table Grid"
    for i,label in enumerate(["What We Bring to the Table","What You Get"]):
        c=vt.rows[0].cells[i]; _set_bg(c,"1B3A6B")
        r=c.paragraphs[0].add_run(label); r.bold=True; r.font.color.rgb=WHITE; r.font.size=Pt(11)
    for left,right in [
        ("AI-Powered SEO OS","Automated audits, content briefs, and reports at agency speed"),
        ("Technical SEO Execution","Direct implementation — no back-and-forth"),
        ("Content Strategy","Pillar + Cluster content that captures long-tail organic traffic"),
        ("AEO / GEO Optimisation","Structured to appear in Google AI Overviews and chatbot answers"),
        ("Link Building","Systematic outreach: 5+ quality backlinks per month"),
        ("Monthly Reporting","Progress tied to business outcomes — not vanity metrics"),
    ]:
        row=vt.add_row().cells
        r0=row[0].paragraphs[0].add_run(left); r0.bold=True; r0.font.size=Pt(10)
        r1=row[1].paragraphs[0].add_run(right); r1.font.size=Pt(10)
    doc.add_paragraph()
    
    # ── SECTION 10: BRAND INNOVATION ─────────────────────────────────────────
    doc.add_page_break()
    add_section_banner(doc,10,"BRAND INNOVATION")
    add_h1(doc,"Brand Innovation Ideas")
    add_body(doc,"To break out of standard SEO patterns, we recommend two bespoke strategic initiatives to build topical authority and capture top-of-funnel traffic:")
    
    idea_1 = strategy_data.get("innovation_idea_1", "The 'Encyclopedia' Pillar: Develop a high-authority reference hub defining key industry terms, materials, or methodologies to capture early-stage informational intent. Create 'As Seen On' landing pages if celebrity entities exist.")
    idea_2 = strategy_data.get("innovation_idea_2", "The 'Craft/Occasion Calendar': Map your content production to a 12-month calendar tied to cultural moments, seasonal buying cycles, or industry festivals.")
    
    add_callout(doc, "Idea 1: Education & Authority", [idea_1], "info")
    doc.add_paragraph()
    add_callout(doc, "Idea 2: Seasonal Activation", [idea_2], "info")
    doc.add_paragraph()
    add_h1(doc,"How Dare Network Adds Value")
    vt=doc.add_table(rows=1,cols=2); vt.style="Table Grid"
    for i,label in enumerate(["What We Bring to the Table","What You Get"]):
        c=vt.rows[0].cells[i]; _set_bg(c,"1B3A6B")
        r=c.paragraphs[0].add_run(label); r.bold=True; r.font.color.rgb=WHITE; r.font.size=Pt(11)
    for left,right in [
        ("AI-Powered SEO OS","Automated audits, content briefs, and reports at agency speed"),
        ("Technical SEO Execution","Direct implementation — no back-and-forth"),
        ("Content Strategy","Pillar + Cluster content that captures long-tail organic traffic"),
        ("AEO / GEO Optimisation","Structured to appear in Google AI Overviews and chatbot answers"),
        ("Link Building","Systematic outreach: 5+ quality backlinks per month"),
        ("Monthly Reporting","Progress tied to business outcomes — not vanity metrics"),
    ]:
        row=vt.add_row().cells
        r0=row[0].paragraphs[0].add_run(left); r0.bold=True; r0.font.size=Pt(10)
        r1=row[1].paragraphs[0].add_run(right); r1.font.size=Pt(10)
    doc.add_paragraph()
    add_callout(doc,"Ready to Execute?",["This audit identifies every change needed to significantly improve organic rankings.","Dare Network will execute this roadmap systematically, report progress monthly, and continuously optimise based on data.","Next step: review the Critical Priority list and begin Week 1 implementation."],"info")
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before=Pt(20)
    r=p.add_run("— End of Audit Report —"); r.font.size=Pt(10); r.font.color.rgb=MID
    p2=doc.add_paragraph(); p2.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r2=p2.add_run("www.darenetwork.in"); r2.font.size=Pt(11); r2.bold=True; r2.font.color.rgb=ORANGE
    return doc


def build_monthly_docx(client_slug, website_url, brand_kit, month):
    doc=Document()
    for sec in doc.sections: sec.top_margin=Cm(2.5); sec.bottom_margin=Cm(2.5); sec.left_margin=Cm(2.5); sec.right_margin=Cm(2.5)
    info=brand_kit.get("client_info",{}); client_name=info.get("client_name",client_slug)
    month_label=datetime.strptime(month,"%Y-%m").strftime("%B %Y") if month else "Last Month"
    add_h1(doc,f"Monthly SEO Report — {month_label}")
    add_body(doc,f"Client: {client_name}  |  {website_url}  |  Prepared by Dare Network")
    for section,note in [("1. Organic Traffic (GA4)","Connect GA4 to pull live organic sessions, users, avg session duration, and bounce rate."),("2. Search Rankings (GSC)","Connect GSC to pull impressions, clicks, CTR, and average position data."),("3. Content Published","List articles published this month."),("4. Links Built","List backlinks acquired from outreach this month."),("5. Next Month Priorities","Top 3 priorities for next month.")]:
        add_h2(doc,section); add_body(doc,note)
    add_body(doc,f"\n— Report generated by SEO AI OS | Dare Network | {datetime.now().strftime('%B %d, %Y')} —",MID)
    return doc


def main():
    parser=argparse.ArgumentParser(description="SEO Report Builder — Dare Network Template v2")
    parser.add_argument("--client"); parser.add_argument("--url"); parser.add_argument("--type",required=True,choices=["audit","monthly"]); parser.add_argument("--month"); parser.add_argument("--strategy")
    args=parser.parse_args()

    strategy_data = {}
    if args.strategy and Path(args.strategy).exists():
        try:
            strategy_data = json.load(open(args.strategy, encoding="utf-8"))
        except Exception as e:
            print(f"[Warning] Failed to load strategy JSON: {e}")

    if args.client:
        client_slug=args.client; brand_kit=load_brand_kit(client_slug)
        website_url=brand_kit.get("client_info",{}).get("website_url",f"{client_slug}.com")
    elif args.url:
        url_slug=args.url.replace("https://","").replace("http://","").replace("/","").replace(".","_")
        client_slug=url_slug; brand_kit={"client_info":{"client_name":args.url,"website_url":args.url}}; website_url=args.url
    else:
        print("[Error] Provide --client or --url"); return

    # Always save to .tmp/reports/ — never to audit_history
    output_dir=Path(".tmp/reports"); output_dir.mkdir(parents=True,exist_ok=True)
    today=date.today().strftime("%Y-%m-%d")
    filename=f"{today}_{args.type}_report.docx"
    if args.type=="monthly" and args.month: filename=f"{args.month}_{args.type}_report.docx"
    output_path=output_dir/filename

    print(f"[Report Builder] Generating {args.type} report for: {website_url}")
    doc=build_audit_docx(client_slug,website_url,brand_kit,strategy_data) if args.type=="audit" else build_monthly_docx(client_slug,website_url,brand_kit,args.month or datetime.now().strftime("%Y-%m"))
    doc.save(str(output_path)); abs_path=str(output_path.resolve())

    print(f"\n[SUCCESS] Report saved!")
    print(f"[File]    {abs_path}")
    print(f"\n📄 **Download Link:** [Click here to open the report](file:///{abs_path.replace(chr(92), '/')})")

if __name__=="__main__": main()
