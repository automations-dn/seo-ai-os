#!/usr/bin/env python3
"""
Competitor Gap Analysis Tool
Compares a client's keywords against 3 competitors to find "Low-Hanging Fruit":
Keywords that competitors rank for, but the client does not.

Usage:
    python competitor_gap.py --client acme_corp
    python competitor_gap.py --client-url acme.com --competitor-urls comp1.com,comp2.com
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

def load_brand_kit(client_name):
    path = Path(f"clients/{client_name}/brand_kit.json")
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def mock_gap_data(client_url, competitors):
    """
    Since we don't have active DataForSEO credentials in this demo environment, 
    this function simulates pulling millions of rows of search data and finding the delta.
    In a live V2 environment with the DataForSEO MCP enabled, Claude Code would pull 
    this data dynamically via the MCP server beforehand and pass it in.
    """
    return [
        {"keyword": f"buy {competitors[0].split('.')[0]} alternatives", "volume": 1200, "kd": 14, "comp_rank": 3, "client_rank": 0},
        {"keyword": "best handloom brands in india", "volume": 5400, "kd": 28, "comp_rank": 2, "client_rank": 0},
        {"keyword": "premium ethnic wear online", "volume": 8100, "kd": 45, "comp_rank": 5, "client_rank": 0},
        {"keyword": "how to identify pure silk", "volume": 3600, "kd": 22, "comp_rank": 1, "client_rank": 0},
        {"keyword": "sustainable fashion d2c", "volume": 2900, "kd": 31, "comp_rank": 4, "client_rank": 0},
    ]

def main():
    parser = argparse.ArgumentParser(description="SEO Competitor Gap Analysis")
    parser.add_argument("--client", help="Client name to read from brand_kit.json")
    parser.add_argument("--client-url", help="Client domain")
    parser.add_argument("--competitor-urls", help="Comma-separated competitor domains")
    parser.add_argument("--output", help="Output JSON path")
    args = parser.parse_args()

    client_url = ""
    competitors = []

    if args.client:
        bk = load_brand_kit(args.client)
        if bk:
            client_url = bk.get("client_info", {}).get("website_url", "")
            comps = bk.get("seo_targets", {}).get("competitors", [])
            competitors = [c.get("website_url", "") for c in comps if c.get("website_url")]
            
    if args.client_url:
        client_url = args.client_url
    if args.competitor_urls:
        competitors = args.competitor_urls.split(",")

    if not client_url or not competitors:
        print("[Error] Must provide client URL and at least one competitor URL.")
        return

    print(f"[*] Running Gap Analysis...")
    print(f"[*] Analyzing Client: {client_url}")
    print(f"[*] Analyzing Competitors: {', '.join(competitors)}")
    
    # In V2, this function calls DataForSEO API. For now, it mocks the data structure.
    opportunities = mock_gap_data(client_url, competitors)

    # Filter for low-hanging fruit (KD < 35, Volume > 1000)
    low_hanging = [opp for opp in opportunities if opp["kd"] < 35 and opp["volume"] > 1000]

    result = {
        "analysis_date": datetime.now().isoformat(),
        "client": client_url,
        "competitors_analyzed": competitors,
        "total_gaps_found": len(opportunities),
        "low_hanging_fruit": low_hanging,
        "all_opportunities": opportunities
    }

    print(f"\n[+] Found {len(opportunities)} total gap keywords")
    print(f"[+] Found {len(low_hanging)} Low-Hanging Fruit targets (KD<35, Vol>1K)")
    
    print("\n--- TOP TARGETS ---")
    for t in low_hanging[:5]:
        print(f" • '{t['keyword']}' (Vol: {t['volume']}, KD: {t['kd']})")

    output_path = args.output or ".tmp/competitor_gap.json"
    Path(output_path).parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"\n[Output] Saved gap data to {output_path}")

if __name__ == "__main__":
    main()
