import json
import logging

logger = logging.getLogger(__name__)

def get_free_ai_answer(query: str) -> str:
    """
    Uses DuckDuckGo's free AI chat feature to get a synthesized answer for AEO/GEO analysis.
    This is COMPLETELY FREE and requires no API key.

    Updated to use the new 'ddgs' package (formerly duckduckgo_search).
    """
    try:
        # Import the new package name
        try:
            from ddgs import DDGS
        except ImportError:
            # Fallback to old package name with warning
            try:
                from duckduckgo_search import DDGS
                print("[Warning] Using deprecated 'duckduckgo_search' package. Update with: pip uninstall duckduckgo_search && pip install ddgs")
            except ImportError:
                return json.dumps({
                    "error": "DDGS package not installed",
                    "solution": "Install with: pip install ddgs"
                }, indent=2)

        # Try AI chat first
        try:
            with DDGS() as ddgs:
                # Using the 'gpt-4o-mini' model which is free on DDG
                results = ddgs.chat(query, model='gpt-4o-mini')
                # The chat response is a string
                return json.dumps({
                    "source": "DuckDuckGo AI (Free)",
                    "query": query,
                    "answer": results
                }, indent=2)
        except AttributeError:
            # chat() method doesn't exist in this version
            logger.warning("DDG AI chat not available, falling back to search")

    except Exception as e:
        logger.error(f"Error fetching free AI answer: {e}")

    # Fallback to regular search
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            return json.dumps({
                "source": "DuckDuckGo Search (Fallback)",
                "query": query,
                "results": results,
                "note": "AI Chat not available, providing top search results instead."
            }, indent=2)
    except Exception as e2:
        return json.dumps({
            "error": f"Free AI retrieval failed: {str(e2)}",
            "solution": "This is an experimental feature. Consider using Google Search API or manual research instead."
        }, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    print(get_free_ai_answer(args.query))
