#!/usr/bin/env python3
"""
Audit File Validation Tool

Validates that all required audit files exist with correct naming before report generation.
This prevents the "10/10 bug" where report_builder can't find framework_data due to naming mismatches.

Usage:
    python validate_audit_files.py --url https://metalbarns.in
    python validate_audit_files.py --url https://metalbarns.in --required framework,crawl_nojs,lighthouse
"""

import argparse
import sys
from pathlib import Path

# Add tools/ directory to path
sys.path.insert(0, str(Path(__file__).parent))
from utils import url_to_slug, validate_file_naming


# Standard required files for a complete audit
STANDARD_AUDIT_FILES = [
    "framework",           # Framework detection (STEP 0 - CRITICAL)
    "crawl_nojs",         # No-JS crawl (Google's perspective)
    "crawl_js",           # JS crawl (User's perspective)
    "lighthouse",         # Core Web Vitals
]

# Optional files (nice to have but not required)
OPTIONAL_AUDIT_FILES = [
    "onpage",             # On-page SEO analysis
    "keywords",           # Keyword research
    "serp",               # SERP analysis
    "competitors",        # Competitor analysis
    "entity_audit",       # Entity/Knowledge Graph audit
]


def validate_audit(url: str, required_files: list = None) -> dict:
    """
    Validate that all required audit files exist.

    Args:
        url: Website URL
        required_files: List of required file types (default: STANDARD_AUDIT_FILES)

    Returns:
        Dict with validation results
    """
    if required_files is None:
        required_files = STANDARD_AUDIT_FILES

    slug = url_to_slug(url)
    result = validate_file_naming(url, required_files)

    # Check optional files
    optional_result = validate_file_naming(url, OPTIONAL_AUDIT_FILES)

    return {
        "url": url,
        "slug": slug,
        "required": {
            "valid": result["valid"],
            "missing": result["missing"]
        },
        "optional": {
            "found": len(OPTIONAL_AUDIT_FILES) - len(optional_result["missing"]),
            "total": len(OPTIONAL_AUDIT_FILES),
            "missing": optional_result["missing"]
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Validate audit files before report generation")
    parser.add_argument("--url", required=True, help="Website URL")
    parser.add_argument("--required", help="Comma-separated list of required files (default: framework,crawl_nojs,crawl_js,lighthouse)")
    args = parser.parse_args()

    # Parse custom required files if provided
    required_files = None
    if args.required:
        required_files = [f.strip() for f in args.required.split(",")]

    # Run validation
    result = validate_audit(args.url, required_files)

    # Print results
    print("\n" + "="*60)
    print(f"AUDIT FILE VALIDATION")
    print("="*60)
    print(f"URL:  {result['url']}")
    print(f"Slug: {result['slug']}")
    print()

    # Required files
    if result["required"]["valid"]:
        print("[PASS] REQUIRED FILES: ALL PRESENT")
    else:
        print("[FAIL] REQUIRED FILES: MISSING")
        print("\nMissing required files:")
        for f in result["required"]["missing"]:
            print(f"  - {f}")

    # Optional files
    print(f"\n[INFO] OPTIONAL FILES: {result['optional']['found']}/{result['optional']['total']} present")
    if result["optional"]["missing"]:
        print("\nMissing optional files (audit will still work):")
        for f in result["optional"]["missing"]:
            print(f"  - {f}")

    print("\n" + "="*60)

    # Exit code
    if not result["required"]["valid"]:
        print("\n[ERROR] Cannot generate report - required files missing!")
        print("Run the audit workflow to generate missing files.\n")
        sys.exit(1)
    else:
        print("\n[OK] All required files present. Safe to generate report.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
