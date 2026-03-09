#!/usr/bin/env python3
"""
SEO Crawler Tool
Crawls a website to find all URLs, their HTTP status codes,
canonical tags, internal link structure, and SEO metadata.

Usage:
    python seo_crawler.py --url https://example.com --sitemap https://example.com/sitemap.xml
    python seo_crawler.py --url https://example.com --max-pages 500
"""

import argparse
import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run(["pip", "install", "requests", "beautifulsoup4", "lxml"], check=True)
    import requests
    from bs4 import BeautifulSoup


def normalize_url(url: str, base: str) -> str | None:
    """Normalize and validate a URL."""
    try:
        full = urljoin(base, url)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            return None
        # Remove fragments
        return parsed._replace(fragment="").geturl()
    except Exception:
        return None


def crawl_url(session: requests.Session, url: str, timeout: int = 10) -> dict:
    """Crawl a single URL and return its SEO metadata."""
    result = {
        "url": url,
        "status_code": None,
        "title": None,
        "meta_description": None,
        "h1": [],
        "canonical": None,
        "noindex": False,
        "internal_links": [],
        "images_missing_alt": 0,
        "word_count": 0,
        "schema_types": [],
        "error": None,
    }
    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        result["status_code"] = resp.status_code
        result["final_url"] = resp.url

        if resp.status_code != 200:
            return result

        soup = BeautifulSoup(resp.text, "lxml")

        # Title
        title_tag = soup.find("title")
        result["title"] = title_tag.get_text(strip=True) if title_tag else None

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        result["meta_description"] = meta_desc.get("content", "").strip() if meta_desc else None

        # H1s
        result["h1"] = [h.get_text(strip=True) for h in soup.find_all("h1")]

        # Canonical
        canonical = soup.find("link", attrs={"rel": "canonical"})
        result["canonical"] = canonical.get("href") if canonical else None

        # Noindex
        robots_meta = soup.find("meta", attrs={"name": re.compile("robots", re.I)})
        if robots_meta:
            content = robots_meta.get("content", "").lower()
            result["noindex"] = "noindex" in content

        # Internal links
        base_domain = urlparse(url).netloc
        for a in soup.find_all("a", href=True):
            normalized = normalize_url(a["href"], url)
            if normalized and urlparse(normalized).netloc == base_domain:
                result["internal_links"].append(normalized)

        # Images missing alt
        result["images_missing_alt"] = sum(
            1 for img in soup.find_all("img") if not img.get("alt")
        )

        # Word count (visible text)
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        result["word_count"] = len(text.split())

        # Schema types
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, dict) and "@type" in data:
                    result["schema_types"].append(data["@type"])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "@type" in item:
                            result["schema_types"].append(item["@type"])
            except json.JSONDecodeError:
                pass

    except requests.exceptions.RequestException as e:
        result["error"] = str(e)

    return result


def crawl_site(start_url: str, sitemap_url: str = None, max_pages: int = 500) -> dict:
    """Crawl an entire website starting from start_url."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "SEO-AI-OS-Crawler/1.0 (SEO Audit Bot; contact@youragency.com)"
    })

    base_domain = urlparse(start_url).netloc
    to_visit = {start_url}
    visited = set()
    results = []

    # Add sitemap URLs if provided
    if sitemap_url:
        try:
            resp = session.get(sitemap_url, timeout=10)
            soup = BeautifulSoup(resp.text, "lxml-xml")
            sitemap_urls = {loc.get_text() for loc in soup.find_all("loc")}
            # Filter to same domain
            to_visit.update(u for u in sitemap_urls if urlparse(u).netloc == base_domain)
            print(f"[Sitemap] Found {len(sitemap_urls)} URLs in sitemap")
        except Exception as e:
            print(f"[Sitemap] Could not fetch sitemap: {e}")

    print(f"[Crawl] Starting crawl of {start_url} (max {max_pages} pages)")

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue

        visited.add(url)
        print(f"[{len(visited)}/{max_pages}] Crawling: {url}")

        result = crawl_url(session, url)
        results.append(result)

        # Discover new URLs
        for link in result.get("internal_links", []):
            if link not in visited and urlparse(link).netloc == base_domain:
                to_visit.add(link)

        time.sleep(0.5)  # Be polite

    return {
        "crawl_date": datetime.now().isoformat(),
        "start_url": start_url,
        "pages_crawled": len(results),
        "pages": results,
        "summary": {
            "total_pages": len(results),
            "status_200": sum(1 for p in results if p.get("status_code") == 200),
            "status_301": sum(1 for p in results if p.get("status_code") == 301),
            "status_404": sum(1 for p in results if p.get("status_code") == 404),
            "status_500": sum(1 for p in results if p.get("status_code") == 500),
            "missing_h1": sum(1 for p in results if not p.get("h1")),
            "missing_title": sum(1 for p in results if not p.get("title")),
            "missing_meta_desc": sum(1 for p in results if not p.get("meta_description")),
            "noindex_pages": sum(1 for p in results if p.get("noindex")),
        }
    }


def main():
    parser = argparse.ArgumentParser(description="SEO Site Crawler")
    parser.add_argument("--url", required=True, help="Website URL to crawl")
    parser.add_argument("--sitemap", help="Sitemap XML URL")
    parser.add_argument("--max-pages", type=int, default=500, help="Maximum pages to crawl")
    parser.add_argument("--output", help="Output JSON file path")
    args = parser.parse_args()

    data = crawl_site(args.url, args.sitemap, args.max_pages)

    # Print summary
    print("\n=== CRAWL SUMMARY ===")
    for k, v in data["summary"].items():
        print(f"  {k}: {v}")

    # Save output
    output_path = args.output or f".tmp/crawl_{urlparse(args.url).netloc}_{datetime.now().strftime('%Y%m%d')}.json"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n[Output] Saved to: {output_path}")


if __name__ == "__main__":
    main()
