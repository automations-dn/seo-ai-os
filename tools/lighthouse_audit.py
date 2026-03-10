#!/usr/bin/env python3
"""
Lighthouse Audit Tool
Runs PageSpeed Insights API to get Core Web Vitals and Lighthouse scores.

Usage:
    python lighthouse_audit.py --url https://example.com
    python lighthouse_audit.py --url https://example.com --strategy mobile
"""

import argparse
import json
import os
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run(["pip", "install", "requests", "python-dotenv"], check=True)
    import requests
    from dotenv import load_dotenv

load_dotenv()


def run_lighthouse(url: str, strategy: str = "mobile", api_key: str = None) -> dict:
    """Run PageSpeed Insights API for a URL."""

    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment. Add it to .env file.")

    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    params = {
        "url": url,
        "strategy": strategy,
        "key": api_key,
        "category": ["performance", "accessibility", "best-practices", "seo"]
    }

    print(f"[Lighthouse] Running audit for {url} ({strategy})...")

    try:
        response = requests.get(api_url, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        lighthouse_result = data.get("lighthouseResult", {})
        categories = lighthouse_result.get("categories", {})
        audits = lighthouse_result.get("audits", {})

        # Extract Core Web Vitals
        cwv = {
            "lcp": audits.get("largest-contentful-paint", {}).get("numericValue"),
            "fid": audits.get("max-potential-fid", {}).get("numericValue"),
            "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
            "fcp": audits.get("first-contentful-paint", {}).get("numericValue"),
            "tti": audits.get("interactive", {}).get("numericValue"),
            "tbt": audits.get("total-blocking-time", {}).get("numericValue"),
            "speed_index": audits.get("speed-index", {}).get("numericValue"),
        }

        # Extract scores
        scores = {
            "performance": categories.get("performance", {}).get("score"),
            "accessibility": categories.get("accessibility", {}).get("score"),
            "best_practices": categories.get("best-practices", {}).get("score"),
            "seo": categories.get("seo", {}).get("score"),
        }

        # Convert scores from 0-1 to 0-100
        scores = {k: int(v * 100) if v is not None else None for k, v in scores.items()}

        # Get SEO audit details
        seo_audits = {}
        seo_audit_refs = categories.get("seo", {}).get("auditRefs", [])
        for ref in seo_audit_refs:
            audit_id = ref.get("id")
            if audit_id in audits:
                audit_data = audits[audit_id]
                seo_audits[audit_id] = {
                    "score": audit_data.get("score"),
                    "title": audit_data.get("title"),
                    "description": audit_data.get("description")
                }

        return {
            "url": url,
            "strategy": strategy,
            "fetch_time": datetime.now().isoformat(),
            "scores": scores,
            "core_web_vitals": cwv,
            "seo_audits": seo_audits,
            "status": "success"
        }

    except requests.exceptions.RequestException as e:
        return {
            "url": url,
            "strategy": strategy,
            "fetch_time": datetime.now().isoformat(),
            "status": "error",
            "error": str(e)
        }


def audit_url(url: str, output_path: str = None) -> dict:
    """Run Lighthouse audit for both mobile and desktop."""

    results = {
        "url": url,
        "audit_date": datetime.now().isoformat(),
        "mobile": run_lighthouse(url, "mobile"),
        "desktop": run_lighthouse(url, "desktop")
    }

    # Calculate overall status
    mobile_perf = results["mobile"].get("scores", {}).get("performance", 0)
    desktop_perf = results["desktop"].get("scores", {}).get("performance", 0)

    results["summary"] = {
        "mobile_performance": mobile_perf,
        "desktop_performance": desktop_perf,
        "mobile_lcp_ms": results["mobile"].get("core_web_vitals", {}).get("lcp"),
        "mobile_cls": results["mobile"].get("core_web_vitals", {}).get("cls"),
        "mobile_fid_ms": results["mobile"].get("core_web_vitals", {}).get("fid"),
        "overall_status": "Good" if mobile_perf >= 90 else "Needs Improvement" if mobile_perf >= 50 else "Poor"
    }

    # Save output
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n[Output] Saved to: {output_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Lighthouse/PageSpeed Insights Audit")
    parser.add_argument("--url", required=True, help="URL to audit")
    parser.add_argument("--output", help="Output JSON file path")
    parser.add_argument("--strategy", choices=["mobile", "desktop", "both"], default="both",
                        help="Device strategy to test")
    args = parser.parse_args()

    if args.strategy == "both":
        results = audit_url(args.url, args.output)
    else:
        results = run_lighthouse(args.url, args.strategy)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n=== LIGHTHOUSE SUMMARY ===")
    if args.strategy == "both":
        print(f"Mobile Performance: {results['summary']['mobile_performance']}/100")
        print(f"Desktop Performance: {results['summary']['desktop_performance']}/100")
        print(f"Mobile LCP: {results['summary']['mobile_lcp_ms']} ms")
        print(f"Mobile CLS: {results['summary']['mobile_cls']}")
        print(f"Overall Status: {results['summary']['overall_status']}")
    else:
        print(f"Performance: {results.get('scores', {}).get('performance', 'N/A')}/100")
        print(f"SEO: {results.get('scores', {}).get('seo', 'N/A')}/100")
        print(f"Accessibility: {results.get('scores', {}).get('accessibility', 'N/A')}/100")


if __name__ == "__main__":
    main()
