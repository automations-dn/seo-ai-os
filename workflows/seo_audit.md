# Workflow: SEO Audit

## Objective
Run a full first-time SEO audit for a client. Produces a baseline report covering Technical SEO, On-Page health, AEO/GEO readiness, and Search Console performance.

## Required Inputs
- `CLIENT_NAME` — short slug used for file naming (e.g. `thedarenetwork`)
- `SITE_URL` — full URL with protocol (e.g. `https://thedarenetwork.com`)
- Client's Google Search Console must be accessible via the connected MCP tool

## Tools Used
1. `tools/seo_crawler.py` — crawls site for technical issues
2. `tools/on_page_analyzer.py` — scores on-page SEO for top pages
3. `tools/serp_scraper.py` — pulls keyword/competitor data
4. `tools/report_builder.py` — compiles everything into a markdown report
5. MCP: Search Console — pulls GSC performance data

## Steps

### Step 1 — Set Up Client Folder
Create `clients/{CLIENT_NAME}/brand_kit.json`:
```json
{
  "client_info": {
    "client_name": "Display Name",
    "website_url": "https://example.com",
    "domain": "example.com"
  }
}
```
Create `.tmp/` if it doesn't exist.

### Step 2 — Pull Search Console Data (90 days)
Use the GSC MCP tool:
- Site URL: `{SITE_URL}`
- Start: 90 days ago
- End: today

Save output to `.tmp/gsc_{CLIENT_NAME}_{YYYYMMDD}.json`

Interpret:
- Impressions and clicks give traffic baseline
- Avg position shows ranking health
- How many pages appear? If only 1–2, likely an indexing or content footprint problem

### Step 3 — Crawl the Site
```bash
python tools/seo_crawler.py \
  --url {SITE_URL} \
  --sitemap {SITE_URL}/sitemap.xml \
  --max-pages 200 \
  --output .tmp/crawl_{CLIENT_NAME}_{YYYYMMDD}.json
```

Check summary for:
- 404s > 0: fix broken pages
- Noindex pages: confirm all are intentional
- Missing H1/title/meta: flag for on-page work
- Redirect chains (301 on multiple hops)

**Edge case:** If sitemap fetch fails (404 or connection error), proceed without it — crawler will still discover pages via internal links.

**Edge case:** If environment blocks outbound HTTPS (proxy 403), skip crawl and note the gap in the report. Use GSC + manual inspection instead.

### Step 4 — On-Page Analysis (Top Pages)
```bash
python tools/on_page_analyzer.py \
  --client {CLIENT_NAME} \
  --top 10
```
This auto-loads crawl data and analyzes the 10 most-linked pages.

If no crawl data exists, pass URLs directly:
```bash
python tools/on_page_analyzer.py --urls "{SITE_URL},{SITE_URL}/about,..."
```

Scores below 70 are flagged for priority fixes.

### Step 5 — SERP & Keyword Data (Optional but Recommended)
```bash
# Top competitors for homepage keyword
python tools/serp_scraper.py --mode serp_top10 --keyword "{BRAND NAME}" \
  --output .tmp/serp_{CLIENT_NAME}_{YYYYMMDD}.json

# Autocomplete ideas
python tools/serp_scraper.py --mode autosuggest --keyword "{BRAND NAME}" \
  --output .tmp/autosuggest_{CLIENT_NAME}_{YYYYMMDD}.json
```

**Edge case:** If Google blocks scraping (CAPTCHA), skip for now and note in report. Try again from a residential IP.

### Step 6 — Build the Report
```bash
python tools/report_builder.py --client {CLIENT_NAME} --type audit
```

Output: `clients/{CLIENT_NAME}/reports/{YYYY-MM-DD}_audit_report.md`

After generation, manually enrich the report with:
- GSC data summary and interpretation (see Step 2)
- Any data gaps and what to run next
- Specific priority actions based on what was found

### Step 7 — Deliver
Share the report file with the client or paste into their preferred format (Notion, Google Doc, Slides).

## Expected Outputs
- `.tmp/gsc_{CLIENT_NAME}_{YYYYMMDD}.json` — GSC performance data
- `.tmp/crawl_{CLIENT_NAME}_{YYYYMMDD}.json` — full site crawl
- `.tmp/onpage_{YYYYMMDD_HHMMSS}.json` — on-page scores
- `clients/{CLIENT_NAME}/reports/{YYYY-MM-DD}_audit_report.md` — final report

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Crawl returns 0 pages | Check robots.txt, try with `--max-pages 50` first |
| Sitemap fetch fails | Remove `--sitemap` flag, crawler will use link discovery |
| Proxy blocks outbound HTTPS | Run crawler from local machine; save JSON to `.tmp/` manually |
| Google blocks SERP scraping | Use VPN or residential proxy; retry after 30 min |
| GSC shows only 1 page | Check for noindex, robots.txt blocks, or thin content |
| Report shows all N/A | Crawl/on-page data not in `.tmp/` — re-run Steps 3–4 first |

## Learned Notes
- 2026-03-09: The Dare Network audit — Claude Code web environment egress proxy blocks outbound HTTPS to non-allow-listed domains. Crawler and on-page tools cannot reach client sites from this environment. Use them from a local machine and drop the JSON outputs into `.tmp/` before running `report_builder.py`. GSC MCP tool works fine regardless.
