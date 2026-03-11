#!/usr/bin/env python3
"""
On-Page Analyzer Tool
Analyzes on-page SEO health: titles, meta, headings, images, canonical, schema.

Usage:
    python on_page_analyzer.py --urls "https://example.com/page1"
    python on_page_analyzer.py --client acme_corp --top 10 --keyword "target keyword"
"""

import argparse
import json
import time
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "requests", "beautifulsoup4", "lxml"], check=True)
    import requests
    from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; SEO-AI-OS-OnPage/1.0)"}
TITLE_MIN, TITLE_MAX = 50, 60
META_MIN, META_MAX = 120, 160


def analyze_page(url: str, keyword: str = None) -> dict:
    result = {"url": url, "analyzed_at": datetime.now().isoformat(), "issues": [], "overall_score": 0}
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        result["status_code"] = resp.status_code
        if resp.status_code != 200:
            result["issues"].append(f"CRITICAL: Page returned {resp.status_code}")
            return result

        soup = BeautifulSoup(resp.text, "lxml")
        scores = []

        # --- Title ---
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None
        title_issues = []
        if not title:
            title_issues.append("CRITICAL: Missing title tag")
        else:
            if len(title) < TITLE_MIN: title_issues.append(f"Title too short ({len(title)} chars)")
            if len(title) > TITLE_MAX: title_issues.append(f"Title too long ({len(title)} chars)")
            if keyword and keyword.lower() not in title.lower():
                title_issues.append(f"Keyword '{keyword}' not in title")
        title_score = max(0, 100 - len(title_issues) * 25)
        scores.append(title_score)
        result["title"] = {"text": title, "length": len(title) if title else 0, "score": title_score, "issues": title_issues}

        # --- Meta ---
        meta_tag = soup.find("meta", attrs={"name": re.compile("description", re.I)})
        meta = meta_tag.get("content", "").strip() if meta_tag else None
        meta_issues = []
        if not meta:
            meta_issues.append("HIGH: Missing meta description")
        else:
            if len(meta) < META_MIN: meta_issues.append(f"Meta too short ({len(meta)} chars)")
            if len(meta) > META_MAX: meta_issues.append(f"Meta too long ({len(meta)} chars)")
            if keyword and keyword.lower() not in meta.lower():
                meta_issues.append(f"Keyword '{keyword}' not in meta description")
        meta_score = max(0, 100 - len(meta_issues) * 30)
        scores.append(meta_score)
        result["meta"] = {"text": meta, "length": len(meta) if meta else 0, "score": meta_score, "issues": meta_issues}

        # --- Headings ---
        h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
        heading_issues = []
        if not h1s: heading_issues.append("CRITICAL: No H1 tag")
        elif len(h1s) > 1: heading_issues.append(f"HIGH: Multiple H1 tags ({len(h1s)})")
        if keyword and h1s and keyword.lower() not in h1s[0].lower():
            heading_issues.append(f"MEDIUM: Keyword not in H1")
        if not h2s: heading_issues.append("MEDIUM: No H2 tags")
        heading_score = max(0, 100 - sum(30 if "CRITICAL" in i else 20 if "HIGH" in i else 10 for i in heading_issues))
        scores.append(heading_score)
        result["headings"] = {"h1": h1s, "h2": h2s[:8], "h2_count": len(h2s), "score": heading_score, "issues": heading_issues}

        # --- Images ---
        all_imgs = soup.find_all("img")
        missing_alt = sum(1 for img in all_imgs if not img.get("alt"))
        img_issue = None
        if all_imgs and missing_alt / len(all_imgs) > 0.2:
            img_issue = f"HIGH: {missing_alt}/{len(all_imgs)} images missing alt text"
            result["issues"].append(img_issue)
        result["images"] = {"total": len(all_imgs), "missing_alt": missing_alt, "issue": img_issue}

        # --- Canonical ---
        canonical = soup.find("link", attrs={"rel": "canonical"})
        result["canonical"] = canonical.get("href") if canonical else None
        if not canonical:
            result["issues"].append("MEDIUM: No canonical tag")

        # --- Noindex ---
        robots_meta = soup.find("meta", attrs={"name": re.compile("robots", re.I)})
        result["noindex"] = "noindex" in (robots_meta.get("content", "").lower() if robots_meta else "")
        if result["noindex"]:
            result["issues"].append("CRITICAL: Page has noindex tag!")

        # --- Word Count ---
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        body_text = soup.get_text(separator=" ").strip()
        result["word_count"] = len(body_text.split())
        if result["word_count"] < 300:
            result["issues"].append(f"HIGH: Thin content ({result['word_count']} words)")
            
        # --- Advanced CRO & Trust Signals ---
        # 1. Trust Signals
        has_phone = bool(re.search(r'\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b', body_text)) or bool(soup.find("a", href=re.compile(r'^tel:')))
        has_email = bool(re.search(r'[\w\.-]+@[\w\.-]+', body_text)) or bool(soup.find("a", href=re.compile(r'^mailto:')))
        policy_links = len(soup.find_all("a", href=re.compile(r'(policy|privacy|terms|returns|refund)', re.I)))
        result["cro_trust"] = {
            "has_contact_info": has_phone or has_email,
            "policy_links": policy_links,
            "ssl_secure": url.startswith("https://")
        }
        if not (has_phone or has_email): result["issues"].append("MEDIUM: No visible contact info (Trust Signal)")
        
        # 2. Intent-to-CTA Alignment
        ctas = soup.find_all(["a", "button"], class_=re.compile(r'(btn|button|cta)', re.I))
        cta_texts = [cta.get_text(strip=True) for cta in ctas if cta.get_text(strip=True)][:5]
        result["cro_ctas"] = cta_texts
        if not cta_texts and result["word_count"] > 200:
            result["issues"].append("MEDIUM: No clear Call-to-Action buttons found")

        # --- Advanced E-E-A-T & Entity Validation ---
        # 1. Author Profile Validation
        author_meta = soup.find("meta", attrs={"name": "author"})
        author_link = soup.find("a", attrs={"rel": "author"})
        has_author = bool(author_meta) or bool(author_link) or bool(re.search(r'By\s+[A-Z][a-z]+\s+[A-Z][a-z]+', body_text[:1000]))
        result["ee_at_author"] = has_author
        
        # 2. Expert Citations
        external_links = soup.find_all("a", href=re.compile(r'^https?://(?!' + re.escape(urlparse(url).netloc) + ')'))
        edu_gov_links = [link.get('href') for link in external_links if re.search(r'\.(edu|gov|org)', link.get('href', ''))]
        result["ee_at_citations"] = len(edu_gov_links)

        # --- Schema ---
        schema_types = []
        schema_same_as = False
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, dict): 
                    schema_types.append(data.get("@type", "Unknown"))
                    if "sameAs" in data and data.get("@type") in ["Organization", "Person"]: schema_same_as = True
                elif isinstance(data, list): 
                    for d in data:
                        if isinstance(d, dict):
                            schema_types.append(d.get("@type", "Unknown"))
                            if "sameAs" in d and d.get("@type") in ["Organization", "Person"]: schema_same_as = True
            except Exception:
                pass
        result["schema_types"] = schema_types
        result["schema_same_as"] = schema_same_as
        if not schema_same_as and ("Organization" in schema_types or "Person" in schema_types):
            result["issues"].append("MEDIUM: Schema Organization/Person missing 'sameAs' entity validation (E-E-A-T gap)")
        result["schema_types"] = schema_types
        if not schema_types:
            result["issues"].append("MEDIUM: No JSON-LD schema found — add Article/FAQ schema for AEO")

        result["overall_score"] = int(sum(scores) / max(len(scores), 1))

    except requests.exceptions.RequestException as e:
        result["issues"].append(f"CRITICAL: Cannot fetch page — {e}")

    return result


def main():
    parser = argparse.ArgumentParser(description="On-Page SEO Analyzer")
    parser.add_argument("--urls", help="Comma-separated URLs")
    parser.add_argument("--client", help="Client name (loads from crawl data)")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--keyword", help="Target keyword to check")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    urls = []
    if args.urls:
        urls = [u.strip() for u in args.urls.split(",")]
    elif args.client:
        crawl_files = list(Path(".tmp").glob(f"*{args.client}*crawl*.json"))
        if crawl_files:
            with open(crawl_files[-1], "r") as f:
                crawl = json.load(f)
            pages = sorted(crawl.get("pages", []), key=lambda p: len(p.get("internal_links", [])), reverse=True)
            urls = [p["url"] for p in pages[:args.top] if p.get("status_code") == 200]
        else:
            print(f"[Error] No crawl data found for '{args.client}'"); return

    all_results = []
    for url in urls:
        print(f"  Analyzing: {url}")
        all_results.append(analyze_page(url, args.keyword))
        time.sleep(0.5)

    output_data = {
        "pages_analyzed": len(all_results),
        "avg_score": int(sum(r["overall_score"] for r in all_results) / max(len(all_results), 1)),
        "results": all_results,
        "analyzed_at": datetime.now().isoformat(),
    }

    output_path = args.output or f".tmp/onpage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n=== ON-PAGE SUMMARY === Avg Score: {output_data['avg_score']}/100")
    for r in all_results:
        print(f"  {r['url']} — {r['overall_score']}/100 | Issues: {len(r['issues'])}")
    print(f"\n[Output] Saved to: {output_path}")


if __name__ == "__main__":
    main()
