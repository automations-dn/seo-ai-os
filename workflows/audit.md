---
description: Run a full SEO and GEO audit for a website with explicit tool orchestration and error handling.
---

# Workflow: Complete SEO + GEO Audit

## Trigger
```
/audit <url> [--client <name>]
```
**Example:** `/audit https://thedarenetwork.com --client thedarenetwork`

---

## Objective
Produce a comprehensive, downloadable `.docx` audit report that combines:
1. **Technical SEO** (crawlability, speed, indexation)
2. **On-Page SEO** (titles, metas, content quality)
3. **GEO/AEO Readiness** (AI citability, llms.txt, brand mentions)
4. **Actionable 90-Day Roadmap** (prioritized by business impact)

**Output:** `reports/{ClientName}_Audit_{YYYY-MM-DD}.docx` — Dare Network branded template

---

## Prerequisites

**Before starting:**
1. Confirm you have access to the URL (not password-protected)
2. If `--client` flag provided, verify `clients/{client}/brand_kit.json` exists
3. If new URL (no client record), this is an **audit-only** request — DO NOT create a client folder unless explicitly asked

---

## Step-by-Step Execution

### Step 1: Industry Auto-Detection (MANDATORY FIRST STEP)

**Execute:**
Use WebFetch to analyze the homepage and detect business type.

```bash
# Fetch homepage
WebFetch: {url}
```

**Extract signals:**
- Navigation menu items (reveals site structure)
- Footer content (address, phone → Local Business)
- URLs in nav: `/products`, `/collections` → E-commerce
- URLs in nav: `/pricing`, `/features` → SaaS
- URLs in nav: `/case-studies`, `/portfolio` → Agency
- Schema.org markup (Organization, LocalBusiness, etc.)
- Meta description keywords

**Classify as ONE of:**
- **E-commerce** (product listings, shopping cart, "Add to cart" buttons)
- **Local Service** (address, phone, Google Maps embed, service area pages)
- **SaaS** (pricing page, "Free trial" CTA, integrations page)
- **Publisher/Blog** (blog-heavy nav, article schema, author pages)
- **Agency/B2B Services** (case studies, client logos, "Our Work" section)
- **Hybrid** (combination — classify by dominant pattern)

**Set context variable:**
```
SITE_TYPE = {detected_type}
```

**Important:** All subsequent recommendations MUST be tailored to this site type. Never give e-commerce advice to a SaaS site.

---

### Step 2: Technical SEO Audit — Full Site Crawl

**Tool:** `seo_crawler.py` (Playwright-powered, renders JavaScript)

**Execute:**
```bash
python tools/seo_crawler.py \
  --url "{url}" \
  --max-pages 50 \
  --timeout 300 \
  --output ".tmp/{client}_crawl.json"
```

**Parameters:**
- `--url`: Target website
- `--max-pages`: Limit to 50 pages (prevents 10+ minute crawls)
- `--timeout`: 5-minute maximum (300 seconds)
- `--output`: Save results to `.tmp/{client}_crawl.json`

**Validate output:**
```bash
# Check file exists
if [ ! -f ".tmp/{client}_crawl.json" ]; then
  echo "[ERROR] Crawl failed, file missing"
  # Fallback: WebFetch homepage + key pages only
fi

# Check file is not empty
if [ ! -s ".tmp/{client}_crawl.json" ]; then
  echo "[ERROR] Crawl file is empty"
  # Fallback: WebFetch homepage only
fi

# Check pages_crawled > 0
# Use Read tool to parse JSON and verify structure
```

**Parse results (Read the JSON file):**
- Total pages crawled
- HTTP status codes (200, 301, 404, 500)
- Pages missing canonical tags
- Redirect chains (301 → 301 → 200)
- Broken internal links (404s)
- Pages with duplicate title tags
- Pages missing H1 tags
- Schema types found per page

**If crawl fails (timeout or 403 blocked):**
1. Reduce `--max-pages` to 25 and retry
2. If still fails: Use WebFetch for homepage, `/about`, pricing/product pages only
3. Document in report: `[WARNING] Full crawl blocked by site, analyzed {N} key pages manually`

**Flag Critical Issues:**
- [ERROR] Site returns 5xx errors on key pages
- [ERROR] Robots.txt blocks Googlebot
- [ERROR] All pages have `noindex` meta tag
- [ERROR] No sitemap.xml found
- [ERROR] > 10% of pages return 404

---

### Step 3: Core Web Vitals Audit

**Tool:** `lighthouse_audit.py` (or PageSpeed MCP if available)

**1st Choice: MCP (if configured)**
Just ask: "Analyze {url} with PageSpeed for mobile and desktop"

**2nd Choice: Python tool**
```bash
python tools/lighthouse_audit.py \
  --url "{url}" \
  --strategy both \
  --output ".tmp/{client}_cwv.json"
```

**Parameters:**
- `--strategy both`: Runs mobile + desktop audits
- `--timeout`: 120 seconds (Lighthouse can be slow)

**Validate output:**
```bash
# Check file exists and contains required metrics
# Use Read tool to parse JSON
```

**Parse results:**
```json
{
  "mobile": {
    "lcp": 2.1,  // Largest Contentful Paint (target: < 2.5s)
    "inp": 180,  // Interaction to Next Paint (target: < 200ms)
    "cls": 0.08, // Cumulative Layout Shift (target: < 0.1)
    "performance_score": 85
  },
  "desktop": { ... }
}
```

**Flag if:**
- LCP > 2.5s → [ERROR] Critical
- INP > 200ms → [ERROR] Critical (NEVER reference FID — it's deprecated)
- CLS > 0.1 → [WARNING] High Priority
- Performance score < 70 → [WARNING] Medium Priority

**If tool fails:**
- Fallback: WebFetch `https://pagespeed.web.dev/analysis?url={url}` and parse HTML table
- Or: Ask user to run PageSpeed Insights manually and share screenshot

---

### Step 4: On-Page SEO Analysis

**Tool:** `on_page_analyzer.py`

**Execute:**
```bash
python tools/on_page_analyzer.py \
  --url "{url}" \
  --keyword "{primary_keyword_from_brand_kit}" \
  --output ".tmp/{client}_onpage.json"
```

**If no brand_kit (audit-only mode):**
- Infer primary keyword from homepage `<title>` tag
- Or: Extract from H1 heading

**Parse results:**
- Title tag (length, keyword placement, uniqueness)
- Meta description (length, CTA presence, keyword)
- H1 heading (uniqueness, keyword match)
- H2-H6 structure (logical hierarchy)
- Image alt tags (missing, generic, keyword-stuffed)
- Internal link count (too few = < 3, too many = > 100)
- Word count (thin content if < 300 words)
- Keyword density (flag if > 3% — keyword stuffing)

**Flag issues:**
- [ERROR] Missing title tag or meta description
- [ERROR] Duplicate title tags across pages
- [WARNING] Title > 60 characters (truncated in SERP)
- [WARNING] Meta description > 160 characters
- [WARNING] Images missing alt text
- [WARNING] Generic filenames (image001.jpg → flag for rename)

---

### Step 5: Schema Markup Validation

**Tool:** `schema_checker.py`

**Execute:**
```bash
python tools/schema_checker.py \
  --url "{url}" \
  --output ".tmp/{client}_schema.json"
```

**Parse results:**
- Schema types found (Organization, LocalBusiness, Article, Product, etc.)
- Validation errors (missing required fields, incorrect format)
- Warnings (recommended fields missing)

**CRITICAL: Reference Rule 7 from CLAUDE.md**
- [ERROR] NEVER recommend FAQPage schema for commercial sites (restricted to gov/healthcare since Aug 2023)
- [ERROR] NEVER recommend HowTo schema (deprecated Sept 2023)
- [OK] Valid types: Organization, LocalBusiness, Service, BreadcrumbList, Article, Product, Review, VideoObject

**Tailor to SITE_TYPE:**
- **E-commerce**: Check for Product schema, AggregateRating, Offer
- **Local Service**: Check for LocalBusiness, GeoCoordinates, OpeningHours
- **SaaS**: Check for Organization, SoftwareApplication
- **Publisher**: Check for Article, Person (author), BreadcrumbList
- **Agency**: Check for Organization, Service, Review

**Flag if:**
- No schema found at all → [ERROR] Critical
- Schema has validation errors → [WARNING] High Priority
- Missing site-type-appropriate schema → [WARNING] Medium Priority

**Fallback if tool fails:**
- Manual check: Suggest user run `document.querySelectorAll('script[type="application/ld+json"]')` in browser console
- Or: Use Google Rich Results Test (renders JavaScript correctly)

---

### Step 6: Image SEO Audit

**Use crawl data from Step 2**

**Analyze:**
```python
# From .tmp/{client}_crawl.json
images_analyzed = 0
images_missing_alt = 0
images_generic_filename = 0
images_large_filesize = 0

for page in crawl_data["pages"]:
    for img in page["images"]:
        images_analyzed += 1
        if not img["alt"]:
            images_missing_alt += 1
        if re.match(r"image\d+\.(jpg|png)", img["src"]):
            images_generic_filename += 1
        if img["size_kb"] > 100:
            images_large_filesize += 1
```

**Check for:**
- Missing `alt` attributes → flag count and example URLs
- Not in WebP/AVIF format → recommend conversion
- Not lazy-loaded → check for `loading="lazy"` attribute
- File size > 100KB → recommend compression
- Generic filenames (`image001.jpg`) → recommend descriptive names

**Flag if:**
- > 20% images missing alt text → [WARNING] High Priority
- > 50% images not in modern format (WebP/AVIF) → [WARNING] Medium Priority
- Hero images > 300KB → [WARNING] High Priority (impacts LCP)

---

### Step 7: E-E-A-T Evaluation

**Reference Rule 8 from CLAUDE.md**

**Use WebFetch to analyze:**
- Homepage
- About page (if exists)
- Author pages (if Publisher/Blog)
- Contact page
- Privacy policy / Terms pages

**Score each dimension (Low / Medium / High):**

**Experience:**
- First-hand photos/videos present?
- Real case studies with client names?
- Original data or research?
- Score: Low | Medium | High
- Improvement: "{Specific action}"

**Expertise:**
- Author credentials visible?
- Claims backed by data/sources?
- Industry certifications shown?
- Score: Low | Medium | High
- Improvement: "{Specific action}"

**Authoritativeness:**
- Brand cited by others? (Check: Google search "site:wikipedia.org {brand_name}")
- Press mentions? (Check: Google search "{brand_name} news")
- Backlinks from industry sites?
- Score: Low | Medium | High
- Improvement: "{Specific action}"

**Trustworthiness:**
- HTTPS active? (check URL scheme)
- Clear contact info? (email, phone, address visible)
- Privacy policy exists?
- Refund/returns policy? (E-commerce only)
- About page with team info?
- Score: Low | Medium | High
- Improvement: "{Specific action}"

**Output format:**
| Dimension | Score | Current State | Specific Improvement |
|-----------|-------|---------------|---------------------|
| Experience | Medium | Has 2 case studies but no client photos | Add before/after photos with client permission |
| Expertise | Low | No author bios on blog posts | Create author pages with LinkedIn credentials |
| Authoritativeness | Low | No Wikipedia page, no press mentions | Create "As Seen In" page, pitch to industry blogs |
| Trustworthiness | High | HTTPS, clear contact, privacy policy | None needed |

---

### Step 8: GEO/AEO Readiness Audit

**8a. AI Crawler Access Check**

Use WebFetch to get `/robots.txt`:
```
WebFetch: {url}/robots.txt
```

**Check for AI crawler blocks:**
- GPTBot (OpenAI)
- Claude-Web (Anthropic)
- Google-Extended (Google Gemini training)
- PerplexityBot
- CCBot (Common Crawl)

**Flag if:**
- All AI crawlers blocked → [ERROR] Critical (site invisible to AI)
- Some blocked → [WARNING] Document which ones and why it matters

**8b. llms.txt Check**

Use WebFetch to get `/llms.txt` or `/llms-full.txt`:
```
WebFetch: {url}/llms.txt
```

**If exists:**
- Parse structure (markdown format)
- Check for: site description, key pages, sitemap reference
- Validate format

**If missing:**
- [WARNING] High Priority issue
- Recommendation: Generate with `python tools/llmstxt_generator.py --url {url}`

**8c. AI Citability Score**

**Tool:** `citability_scorer.py`

```bash
python tools/citability_scorer.py \
  --url "{url}" \
  --output ".tmp/{client}_citability.json"
```

**Parse results:**
- Citability score (0-100)
- Quotable passages found
- Answer block quality
- Statistical density

**Flag if:**
- Score < 40 → [WARNING] Content not optimized for AI citation
- No question-answer blocks found → Recommend FAQ sections
- Low statistical density → Recommend adding data/numbers

**If tool fails:**
- Manual check: Look for H2/H3 structured as questions
- Check for concise answer paragraphs (50-150 words)
- Check for numbered lists, tables, data points

**8d. Entity & Knowledge Graph Check**

**Tool:** `entity_auditor.py`

```bash
python tools/entity_auditor.py \
  --brand "{client_name}" \
  --domain "{url}" \
  --output ".tmp/{client}_entity_audit.json"
```

**Parse results:**
- Wikipedia presence
- Wikidata presence
- Knowledge Panel eligibility
- Crunchbase profile
- Consistent NAP (Name, Address, Phone)

**Flag if:**
- "Unknown Entity" → [WARNING] Recommend Wiki/Crunchbase profile creation
- Missing Wikidata → [WARNING] The brand cannot be strongly connected in the semantic graph without it.

---

### Step 9: SEO Health Score Calculation

**Reference Rule 6 from CLAUDE.md**

Calculate weighted score:

| Category | Weight | Current Score (0-100) | Weighted |
|----------|--------|----------------------|----------|
| Technical SEO | 25% | {score} | {weighted} |
| Content Quality | 25% | {score} | {weighted} |
| On-Page SEO | 20% | {score} | {weighted} |
| Schema/Structured Data | 10% | {score} | {weighted} |
| Core Web Vitals | 10% | {score} | {weighted} |
| Image SEO | 5% | {score} | {weighted} |
| AI Search Readiness | 5% | {score} | {weighted} |
| **Overall SEO Health** | **100%** | | **{total}** |

**Scoring guidelines:**
- **Technical SEO**: Deduct points for crawl errors, 404s, slow speed, indexation issues
- **Content Quality**: Deduct for thin content (< 300 words), duplicate content, low E-E-A-T
- **On-Page SEO**: Deduct for missing/duplicate titles, poor meta descriptions, weak H1s
- **Schema**: Deduct if no schema, validation errors, missing site-type-appropriate markup
- **Core Web Vitals**: Deduct if LCP/INP/CLS exceed thresholds
- **Image SEO**: Deduct for missing alt text, large file sizes, generic filenames
- **AI Search Readiness**: Deduct for blocked crawlers, no llms.txt, low citability

---

### Step 10: Competitor Research (MANDATORY)

**Reference Rule 14 from CLAUDE.md**

**Execute:**
1. Search Google for: `"{primary_keyword} {city/region}"` (if Local) OR `"{primary_keyword}"` (if national/SaaS)
   - Use WebSearch tool
   - Example: "digital marketing agency Bangalore"

2. Extract top 4 organic results (skip paid ads, skip Google Maps)

3. For each competitor:
   - Use WebFetch to get homepage
   - Estimate Domain Authority (look for age, backlink indicators)
   - List pages they have that client doesn't (use site navigation)
   - Identify their strongest keyword (from title tag)
   - Name one thing they do better
   - Name one exploitable gap

**Produce this table:**

| Metric | Client | Comp 1 | Comp 2 | Comp 3 | Comp 4 |
|--------|--------|--------|--------|--------|--------|
| Estimated DA | {DA} | {DA} | {DA} | {DA} | {DA} |
| Blog/Resources | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] |
| Case Studies with Metrics | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] |
| Pricing Page | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] |
| FAQ on Service Pages | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] |
| Partner/Certification Badges | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] |
| Schema Markup | {types} | {types} | {types} | {types} | {types} |
| Interactive Tools/Calculators | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] | [OK]/[ERROR] |
| **What they do better** | - | {detail} | {detail} | {detail} | {detail} |
| **Exploitable gap** | - | {detail} | {detail} | {detail} | {detail} |

**Never use placeholders.** This must be real competitive intelligence.

---

### Step 11: Growth Innovation Ideas (Brand-Specific)

**Reference Rule 13 from CLAUDE.md**

**Process:**
1. Re-read homepage, About page, blog (if exists)
2. Identify: industry, buyer persona, geographic market, unique angle
3. Search: `"{industry} content ideas"` and `"{competitor} blog"` to see what exists
4. Identify the gap: what's missing from the market

**Generate 3+ innovative ideas:**

**Example format (BAD — too generic):**
[ERROR] "Start a blog and post consistently"

**Example format (GOOD — specific to Dare Network):**
[OK] **Idea 1: "The SEO Encyclopedia of 2026"**
- **What:** 50-page glossary covering every SEO term (INP, GEO, LLMO, Citability Score, Entity Graphing, etc.) with origin stories, formulas, and real examples
- **Why:** Each term targets long-tail searches like "what is INP in SEO" (2,100 monthly searches). Link opportunities: Wikipedia citations, SEO school resources, agency toolkits
- **How:** Write 1 term page per week, interlink heavily, promote to SEO Twitter
- **Effort:** Medium (requires SEO expertise, ~2 hours per term)
- **Time to result:** 3 months to start ranking, 6 months for backlinks

[OK] **Idea 2: "The Dare Network AI Search Report"**
- **What:** Quarterly report analyzing which brands are being cited most by ChatGPT/Claude/Perplexity in {industry}. Publicly release as PDF.
- **Why:** Original research = press mentions + backlinks. Brands will share their own rankings.
- **How:** Test 50 prompts in ChatGPT/Claude/Perplexity, track citation frequency, visualize as leaderboard
- **Effort:** High (requires testing infrastructure, data viz)
- **Time to result:** 1 month for first report, immediate social traction

[OK] **Idea 3: "{Industry}-Specific Content Calendar"**
- **What:** 12-month table of content ideas tied to real industry events, budget cycles, competitor gap months
- **Why:** Answers "when should I post about X?" — saves agencies 10+ hours of planning
- **How:** Research industry conferences, fiscal year patterns, seasonal trends; build Google Sheet template
- **Effort:** Low (one-time research, templatized)
- **Time to result:** Immediate (can be a lead magnet)

**Each idea must include:**
- What it is (specific, named)
- How it drives traffic/links
- Effort level (L/M/H)
- Time to first result

---

### Step 12: Assemble Audit Data for Report

**Collect all data into a structured JSON:**

```json
{
  "client": "{client_name}",
  "url": "{url}",
  "audit_date": "{YYYY-MM-DD}",
  "site_type": "{E-commerce|SaaS|Local|Publisher|Agency}",
  "seo_health_score": {
    "overall": 72,
    "technical": 65,
    "content": 80,
    "on_page": 75,
    "schema": 50,
    "core_web_vitals": 70,
    "image_seo": 60,
    "ai_readiness": 40
  },
  "critical_issues": [
    {"issue": "...", "severity": "Critical", "finding": "...", "fix": "..."}
  ],
  "high_priority": [ ... ],
  "medium_priority": [ ... ],
  "low_priority": [ ... ],
  "competitor_analysis": { ... },
  "growth_ideas": [ ... ],
  "90_day_roadmap": {
    "phase_1_quick_wins": [ ... ],
    "phase_2_authority": [ ... ],
    "phase_3_scale": [ ... ]
  }
}
```

Save to: `.tmp/{client}_audit_data.json`

---

### Step 13: Generate Final Report (.docx)

**Tool:** `report_builder.py`

**Execute:**
```bash
python tools/report_builder.py \
  --client "{client}" \
  --template audit \
  --data ".tmp/{client}_audit_data.json" \
  --output "reports/{client}_Audit_{YYYY-MM-DD}.docx"
```

**Validate output:**
```bash
# Check file exists
if [ ! -f "reports/{client}_Audit_{date}.docx" ]; then
  echo "[ERROR] Report generation failed"
  # Retry once
fi

# Check file size > 50KB (not empty)
if [ $(stat -f%z "reports/{client}_Audit_{date}.docx") -lt 50000 ]; then
  echo "[WARNING] Report file seems too small, may be incomplete"
fi
```

**Report structure (auto-generated by tool):**
1. Executive Summary
2. SEO Health Score Breakdown (table)
3. Critical Issues
4. High Priority Issues
5. Medium Priority Issues
6. Technical SEO Deep Dive
7. Content Quality Analysis
8. Competitor Analysis
9. Growth Innovation Ideas
10. 90-Day Action Plan
11. How Dare Network Adds Value (specific to findings)

**Reference Rule 15 from CLAUDE.md:**
- Lead with Business Impact vs. Effort (not just severity)
- Use 90-Day Roadmap structure
- Minimum 4,000 words of actual content

---

### Step 14: Present to User

**Output in chat:**

```
[OK] Audit Complete: {client_name}

🏆 Overall SEO Health Score: {score}/100

📊 Category Breakdown:
  • Technical SEO: {score}/100
  • Content Quality: {score}/100
  • On-Page SEO: {score}/100
  • Core Web Vitals: {score}/100
  • AI Readiness: {score}/100

🔴 Critical Issues Found: {count}
🟡 High Priority Issues: {count}
🟢 Quick Wins Identified: {count}

📄 Download Full Report:
[{client}_Audit_{date}.docx](file:///full/path/to/report.docx)

Next Steps:
Would you like me to:
1. Generate a Content Brief for the top keyword opportunity? (/content_brief)
2. Run a Competitor Gap Analysis? (/competitor_gap)
3. Run an Entity Audit (if brand authority is weak)? (/entity_audit)
4. Run a Topical Authority Audit (if content gaps identified)? (/topical_audit)
5. Start Brand Monitoring (to track mentions & reviews)? (/brand_monitor)
6. Create a monthly reporting schedule? (/monthly_report)
```

**Ask:** "What would you like to tackle first?"

---

## Workflow Integration Triggers

**After completing audit, automatically suggest related workflows based on findings:**

### IF Entity Score <30 → Suggest /entity_audit
```
[RECOMMENDATION] Your brand has weak entity signals (Entity Score: {score}/100).

Run a full entity audit to:
- Check Wikipedia/Wikidata eligibility
- Generate entity schema
- Audit NAP consistency
- Build Knowledge Graph presence

Execute: /entity_audit {client_name}
```

### IF Topic Coverage Identified as Weak → Suggest /topical_audit
```
[RECOMMENDATION] Content gaps detected in your industry topic cluster.

Run a topical authority audit to:
- Map semantic topic graph for your core niche
- Identify missing pillar pages
- Generate 90-day content roadmap

Execute: /topical_audit "{core_topic}" {domain}
```

### IF AI Citability Score <40 → Suggest /aeo_optimize
```
[RECOMMENDATION] Your content isn't optimized for AI search engines (AEO Score: {score}/100).

Optimize for ChatGPT, Perplexity, and Gemini citations:
- Add answer blocks and structured data
- Improve statistical density
- Generate llms.txt governance file

Execute: /aeo_optimize {url}
```

### IF Brand is Established (>3 years) → Suggest /brand_monitor
```
[RECOMMENDATION] Track your brand's online reputation and mentions.

Set up brand monitoring to:
- Discover unlinked mentions (convert to backlinks)
- Track review velocity and sentiment
- Monitor competitor brand health
- Increase AI search visibility

Execute: /brand_monitor {client_name}
```

### IF Programmatic Pages Detected → Suggest Quality Check
```
[WARNING] Detected {X} location/programmatic pages on site.

Run quality scorer to prevent Google penalties:
- Check boilerplate ratio (<40% required)
- Verify unique variables (≥3 per page)
- Monitor indexing status

Execute: python tools/programmatic_quality_scorer.py --sitemap {sitemap_url}
```

---

## Error Handling & Fallback Logic

**If seo_crawler.py times out:**
- Reduce `--max-pages` from 50 to 25
- If still fails: Crawl homepage + 5 key pages with WebFetch
- Document: "[WARNING] Full crawl unavailable, analyzed {N} pages"

**If lighthouse_audit.py fails:**
- Fallback to PageSpeed Insights web interface (WebFetch)
- Or: Ask user to run manually and share screenshot
- Never skip Core Web Vitals — infer from site type if needed

**If competitor research finds no competitors:**
- Expand search to broader keywords
- Include 1-2 indirect competitors (adjacent industries)
- Never leave competitor table empty

**If schema_checker.py fails:**
- Manually parse HTML with Read tool
- Look for `<script type="application/ld+json">` tags
- Validate with Google Rich Results Test (give user the URL)

**Rate limiting:**
- If SERP scraping hits 429: Wait 30 seconds, retry once
- If WebFetch fails: Wait 10 seconds, retry
- Document any degraded data sources

---

## Expected Outputs

**Files Created:**
- `.tmp/{client}_crawl.json` — Full site crawl data
- `.tmp/{client}_cwv.json` — Core Web Vitals scores
- `.tmp/{client}_onpage.json` — On-page SEO analysis
- `.tmp/{client}_schema.json` — Schema validation results
- `.tmp/{client}_citability.json` — AI citability score
- `.tmp/{client}_audit_data.json` — Aggregated audit data
- `reports/{client}_Audit_{YYYY-MM-DD}.docx` — **Final deliverable**

**User-Facing Deliverable:**
Branded `.docx` report with clickable download link in chat.

**Next Action Prompt:**
Ask user what they want to tackle first (content brief, gap analysis, monthly reporting).

---

## Quality Gates

**Before delivering report:**
- [ ] Overall SEO Health Score calculated correctly (weighted average)
- [ ] All sections reference SITE_TYPE-specific recommendations
- [ ] Competitor analysis has real data (no placeholders)
- [ ] Growth ideas are brand-specific (not generic "start a blog")
- [ ] 90-Day Roadmap prioritizes by Business Impact × Effort
- [ ] Report is 4,000+ words
- [ ] Schema recommendations follow Rule 7 (no FAQPage for commercial sites)
- [ ] Core Web Vitals use INP (not deprecated FID)
- [ ] E-E-A-T scored with specific improvements
- [ ] Image SEO includes counts and example URLs
- [ ] .docx file generated successfully and downloadable

---

## Related Workflows

- `/competitor_gap` — Deep keyword gap analysis
- `/content_brief` — Generate SEO content brief from audit findings
- `/monthly_report` — Set up recurring performance reporting
- `/on_page` — Deep dive on specific page optimization

---

## Notes

**This workflow is 100% deterministic:**
- Every tool call has explicit syntax
- Every output has validation logic
- Every failure has a fallback method
- Every recommendation is tailored to SITE_TYPE

**No guesswork. No placeholders. No N/A.**
