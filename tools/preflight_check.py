#!/usr/bin/env python3
"""
Pre-flight Check Tool
Validates environment, dependencies, and prerequisites before running workflows.
Prevents cascading failures and gives clear error messages.

Usage:
    python tools/preflight_check.py --workflow audit --url https://example.com
    python tools/preflight_check.py --workflow content_draft --check-only
"""

import argparse
import sys
import subprocess
import importlib.util
from pathlib import Path
import json

# Color codes for terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class PreflightChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []

    def check_python_version(self):
        """Ensure Python 3.10+"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            self.errors.append(f"Python 3.10+ required, found {version.major}.{version.minor}")
            return False
        self.passed.append(f"Python {version.major}.{version.minor}.{version.micro}")
        return True

    def check_required_packages(self, workflow: str):
        """Check if required Python packages are installed"""
        requirements = {
            "audit": ["playwright", "beautifulsoup4", "requests", "extruct", "w3lib", "python-docx"],
            "content_draft": ["openai", "anthropic", "requests"],
            "keyword_research": ["requests", "beautifulsoup4"],
            "serp_scraper": ["requests", "beautifulsoup4"],
            "crawler": ["playwright", "beautifulsoup4", "extruct", "w3lib"],
            "all": ["playwright", "beautifulsoup4", "requests", "extruct", "w3lib", "python-docx", "lxml"]
        }

        packages = requirements.get(workflow, requirements["all"])
        missing = []

        for pkg in packages:
            # Normalize package names (python-docx → docx)
            import_name = pkg.replace("-", "_").replace("python_docx", "docx")

            if importlib.util.find_spec(import_name) is None:
                missing.append(pkg)

        if missing:
            self.errors.append(f"Missing packages: {', '.join(missing)}")
            self.errors.append(f"Fix: pip install {' '.join(missing)}")
            return False

        self.passed.append(f"All {len(packages)} required packages installed")
        return True

    def check_playwright_browsers(self):
        """Check if Playwright browsers are installed"""
        try:
            result = subprocess.run(
                ["playwright", "install", "--dry-run", "chromium"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "chromium" in result.stdout.lower() and "already installed" not in result.stdout.lower():
                self.warnings.append("Playwright chromium not installed")
                self.warnings.append("Fix: playwright install chromium")
                return False

            self.passed.append("Playwright browsers installed")
            return True

        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.errors.append("Playwright CLI not found")
            self.errors.append("Fix: pip install playwright && playwright install chromium")
            return False

    def check_tmp_directory(self):
        """Ensure .tmp directory exists"""
        tmp_dir = Path(".tmp")
        if not tmp_dir.exists():
            tmp_dir.mkdir(parents=True, exist_ok=True)
            self.warnings.append("Created missing .tmp directory")
            return True

        # Check if .tmp has stale files (>7 days old)
        import time
        stale_files = []
        for file in tmp_dir.glob("*"):
            if file.is_file():
                age_days = (time.time() - file.stat().st_mtime) / 86400
                if age_days > 7:
                    stale_files.append(file.name)

        if stale_files:
            self.warnings.append(f"{len(stale_files)} stale files in .tmp (>7 days old)")
            self.warnings.append("Fix: python tools/cleanup_tmp.py --older-than 7")

        self.passed.append(".tmp directory exists")
        return True

    def check_audit_prerequisites(self, url: str):
        """Check if audit has all required files"""
        from utils import url_to_slug, validate_file_naming

        required_files = ["framework"]  # Minimum for audit
        result = validate_file_naming(url, required_files)

        if not result["valid"]:
            self.warnings.append(f"Missing audit files for {result['slug']}: {', '.join([Path(f).name for f in result['missing']])}")
            self.warnings.append("These will be generated during audit workflow")
        else:
            self.passed.append(f"Cached audit data found for {result['slug']}")

        return True  # Not an error, just informational

    def check_env_file(self):
        """Check if .env exists with required keys"""
        env_path = Path(".env")
        if not env_path.exists():
            self.warnings.append(".env file not found (API integrations will fail)")
            self.warnings.append("Fix: Copy .env.example to .env and add API keys")
            return False

        # Check for critical keys
        with open(env_path) as f:
            env_content = f.read()

        critical_keys = ["GOOGLE_API_KEY", "ANTHROPIC_API_KEY"]
        missing_keys = [key for key in critical_keys if key not in env_content or f"{key}=" in env_content and not env_content.split(f"{key}=")[1].split("\n")[0].strip()]

        if missing_keys:
            self.warnings.append(f"Empty API keys in .env: {', '.join(missing_keys)}")
            self.warnings.append("Some features (PageSpeed MCP, etc.) may not work")
        else:
            self.passed.append(".env configured with API keys")

        return True

    def check_utils_import(self):
        """Verify utils.py is importable"""
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from utils import url_to_slug

            # Test the function
            test_url = "https://example.com"
            result = url_to_slug(test_url)

            if result != "example":
                self.errors.append(f"utils.url_to_slug() malfunction: expected 'example', got '{result}'")
                return False

            self.passed.append("utils.py working correctly")
            return True

        except ImportError as e:
            self.errors.append(f"Cannot import utils.py: {e}")
            self.errors.append("Critical system file missing or corrupted")
            return False

    def run_checks(self, workflow: str = "all", url: str = None):
        """Run all pre-flight checks"""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}PRE-FLIGHT CHECK — SEO AI OS{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")
        print(f"Workflow: {workflow}")
        if url:
            print(f"Target:   {url}")
        print()

        # Core checks (always run)
        self.check_python_version()
        self.check_tmp_directory()
        self.check_utils_import()
        self.check_env_file()

        # Workflow-specific checks
        if workflow in ["audit", "crawler", "all"]:
            self.check_required_packages(workflow)
            self.check_playwright_browsers()

        if workflow == "audit" and url:
            self.check_audit_prerequisites(url)

        # Print results
        print(f"{GREEN}✓ PASSED ({len(self.passed)}){RESET}")
        for msg in self.passed:
            print(f"  {GREEN}✓{RESET} {msg}")

        if self.warnings:
            print(f"\n{YELLOW}⚠ WARNINGS ({len(self.warnings)}){RESET}")
            for msg in self.warnings:
                print(f"  {YELLOW}⚠{RESET} {msg}")

        if self.errors:
            print(f"\n{RED}✗ ERRORS ({len(self.errors)}){RESET}")
            for msg in self.errors:
                print(f"  {RED}✗{RESET} {msg}")
            print(f"\n{RED}[BLOCKED] Cannot proceed until errors are fixed.{RESET}\n")
            return False

        print(f"\n{GREEN}[READY] All checks passed. Safe to proceed.{RESET}\n")
        return True


def main():
    parser = argparse.ArgumentParser(description="Pre-flight check for SEO AI OS workflows")
    parser.add_argument("--workflow", default="all",
                       choices=["all", "audit", "content_draft", "crawler", "keyword_research"],
                       help="Workflow to check")
    parser.add_argument("--url", help="URL to check (for audit workflow)")
    parser.add_argument("--check-only", action="store_true", help="Only check, don't fail")
    args = parser.parse_args()

    checker = PreflightChecker()
    passed = checker.run_checks(args.workflow, args.url)

    if not passed and not args.check_only:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
