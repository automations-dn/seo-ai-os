#!/usr/bin/env python3
"""
Keyword Clusterer Tool
Uses NLP (TF-IDF + DBSCAN/AffinityPropagation) to group hundreds of disparate keywords 
into semantic "Topic Clusters" for building Pillar + Cluster content strategies.

Usage:
    python keyword_clusterer.py --input .tmp/keywords.txt --output .tmp/clusters.json
    python keyword_clusterer.py --client acme_corp
"""

import argparse
import json
import os
import re
from pathlib import Path
from collections import defaultdict

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import DBSCAN
    import numpy as np
except ImportError:
    print("Installing required machine learning packages (scikit-learn)...")
    import subprocess
    subprocess.run(["pip", "install", "scikit-learn", "numpy"], check=True)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import DBSCAN
    import numpy as np


def clean_keyword(kw):
    """Normalize keyword for clustering."""
    kw = str(kw).lower().strip()
    kw = re.sub(r'[^a-z0-9\s]', '', kw)
    return kw


def cluster_keywords(keywords, eps=0.5, min_samples=2):
    """
    Cluster a list of strings using TF-IDF and DBSCAN.
    """
    if not keywords:
        return {}
        
    cleaned_kws = [clean_keyword(kw) for kw in keywords]
    
    # Vectorize keywords using n-grams (1 to 3 words)
    vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), stop_words='english')
    
    try:
        X = vectorizer.fit_transform(cleaned_kws)
    except ValueError:
        # Happens if keywords are completely barren/stop words
        return {"Unclustered": [{"keyword": kw, "intent": "unknown"} for kw in keywords]}

    # DBSCAN clustering
    # eps = max distance between two samples for them to be in same neighborhood
    # Lower eps = tighter clusters. Higher eps = broader clusters.
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(X)
    
    clusters = defaultdict(list)
    
    for i, label in enumerate(clustering.labels_):
        kw_original = keywords[i]
        
        if label == -1:
            clusters["Unclustered (Long-tail)"].append({
                "keyword": kw_original,
                "volume": 0 # Would be populated by DataForSEO in real flow
            })
        else:
            # We don't have a name for the cluster yet, so use label ID
            clusters[f"Topic_Cluster_{label}"].append({
                "keyword": kw_original,
                "volume": 0
            })
            
    # Rename clusters based on the shortest, most generic keyword inside it
    renamed_clusters = {}
    for cluster_name, items in clusters.items():
        if cluster_name.startswith("Topic_Cluster_"):
            # Find the most general keyword (usually the shortest one by word count)
            sorted_items = sorted(items, key=lambda x: len(x["keyword"].split()))
            best_name = sorted_items[0]["keyword"].title()
            renamed_clusters[best_name] = items
        else:
            renamed_clusters[cluster_name] = items
            
    return renamed_clusters


def main():
    parser = argparse.ArgumentParser(description="SEO Keyword Clustering via Machine Learning")
    parser.add_argument("--input", help="Path to text file with one keyword per line")
    parser.add_argument("--client", help="Client name to read keywords from brand kit")
    parser.add_argument("--eps", type=float, default=0.5, help="Clustering strictness (0.1 to 1.0). Lower = tighter clusters.")
    parser.add_argument("--output", help="Output JSON path")
    args = parser.parse_args()

    keywords = []
    
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
    elif args.client:
        brand_path = Path(f"clients/{args.client}/brand_kit.json")
        if brand_path.exists():
            with open(brand_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                kws = data.get("seo_targets", {})
                primary = kws.get("primary_keywords", [])
                secondary = kws.get("secondary_keywords", [])
                keywords = primary + secondary
    
    if not keywords:
        print("[Error] No keywords found to cluster.")
        return

    print(f"[*] Vectorizing and clustering {len(keywords)} keywords...")
    clusters = cluster_keywords(keywords, eps=args.eps)
    
    total_clusters = sum(1 for k in clusters.keys() if k != "Unclustered (Long-tail)")
    
    print(f"[*] Found {total_clusters} semantic topic clusters.")
    for name, items in clusters.items():
        print(f"\n[Cluster: {name}] ({len(items)} keywords)")
        for item in items[:5]:
            print(f"  - {item['keyword']}")
        if len(items) > 5:
            print(f"  ... and {len(items)-5} more")
            
    output_path = args.output or ".tmp/keyword_clusters.json"
    Path(output_path).parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(clusters, f, indent=2, ensure_ascii=False)
        
    print(f"\n[+] Saved complete cluster mapping to {output_path}")

if __name__ == "__main__":
    main()
