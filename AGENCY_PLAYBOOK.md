# 🚀 SEO AI OS: The Complete Agency Playbook

Welcome to the **SEO AI Operating System**. This guide is written for agency owners and SEO managers. If you follow this playbook, this single system (driven by Claude Code) can replace 80% of manual SEO labor, turning a solo operator into the equivalent of a 5-person SEO team.

---

## 📅 The Master SEO Campaign SOP (Dependency Chains)

As a Senior SEO Expert managing a team (the tools and workflows), you don't just say "write an article." You enforce a strict, systematic process where one output feeds into the next. 

This playbook defines the **Dependency Chains**—the exact order of operations the OS must follow to guarantee a #1 ranking result.

---

### ⛓️ Dependency Chain 1: The Content Engine (From Idea to Publication)
*Never write an article blindly. This is the exact sequence to creating content that actually ranks and drives revenue.*

**Step 1: Data Gathering (The Researcher)**
- **Tool:** `competitor_gap.py` or `/keyword_research`
- **Action:** Pull the raw data. Find out exactly what keywords the client's competitors rank for that the client does not. Export this raw, high-volume/low-difficulty data to `.tmp/`.

**Step 2: Semantic Grouping (The Strategist)**
- **Tool:** `keyword_clusterer.py`
- **Action:** Take the raw data from Step 1 and run it through the Machine Learning NLP clusterer. This groups 500 random keywords into 10 logical **Pillar Topics**. 

**Step 3: Architecture & Intent (The Editor)**
- **Tool:** `/content_brief <client_name> --topic "<Topic from Step 2>"`
- **Action:** Before a single word of the article is written, the editor must define the H1, the H2s, the exact LSI keywords to hit, and the required internal links. This brief is saved and reviewed.

**Step 4: Humanized Execution (The Writer)**
- **Tool:** `/content_draft <client_name> --brief <path_to_brief_from_step_3>`
- **Action:** Now, and only now, do we write the article. The writer uses the approved brief, the client's established `brand_kit.json` (for tone), and strictly adheres to the 100% humanized, anti-AI word list.

**Step 5: Technical Injection (The Developer)**
- **Tool:** `schema_gen.py`
- **Action:** The developer takes the finalized draft and injects valid JSON-LD `Article` and `FAQPage` (if applicable) schema so the search engine can digest it instantly.

---

### ⛓️ Dependency Chain 2: The Master Audit (Technical, UI/UX, & AI Readiness)
*A Senior Audit is not just running a crawler. It is a multi-layered diagnostic looking at Code, Content, Trust, and AI Search. This is the exact sequence to execute `/audit` comprehensively.*

**Step 1: The Identity Baseline**
- **Tool:** `/add_client` -> `brand_kit.json`
- **Action:** Establish the client's industry, core competencies, and tone. *Why?* Because an audit for a B2B SaaS requires different E-E-A-T signals (Whitepapers, LinkedIn Authors) than a Local Plumber (Google Reviews, LocalBusiness Schema).

**Step 2: Site Architecture & Deep Crawl (The Technical Foundation)**
- **Tool:** `seo_crawler.py`
- **Action:** Crawl the site (up to 500 pages) to map the internal link graph, find orphaned pages, check HTTP status codes (404s, 301 chains), and verify canonical tag hygiene. This outputs `.tmp/crawl.json`.

**Step 3: Performance & Core Web Vitals (The User Experience)**
- **Tool:** Google PageSpeed API / Lighthouse (via Python integration)
- **Action:** Analyze the top 5 highest-traffic URLs. Check LCP, FID, and CLS. A site failing CWV will bleed the conversions we work so hard to generate. 

**Step 4: Page-Level Optimization & Trust (On-Page SEO)**
- **Tool:** `on_page_analyzer.py`
- **Action:** For the top 10 URLs, aggressively check Title/Meta length, H1 presence, and Image Alt Attributes. Crucially, scan the body text for "Missing Trust Signals" (Phone numbers, Policy links, Author bios) which are massive E-E-A-T ranking factors.

**Step 5: Advanced AI & Semantic Search (AEO/GEO Readiness)**
- **Tool:** `schema_gen.py` & Crawl Data Review
- **Action:** Scan the raw HTML for valid JSON-LD. Does the site have `Organization` schema with a declared `SameAs` array linking to their social profiles? Do they have `LocalBusiness` for local targeting? Provide the exact missing code blocks to inject.

**Step 6: The Executive Synthesis**
- **Tool:** `report_builder.py` -> `/audit` final output
- **Action:** Synthesize Steps 2-5 into a branded Word document. The AI formats this so you can present the issues *and* the immediate solutions to the client.

---

### ⛓️ Dependency Chain 3: Programmatic SEO (Scalable Architecture)
*Programmatic SEO can result in an algorithmic penalty if done poorly. We follow a strict, gated process.*

**Step 1: The Seed Data**
- **Tool:** `/keyword_research`
- **Action:** Identify the high-volume modifier. Example: "SaaS Marketing Agency in [City]" or "Alternative to [Competitor]". 

**Step 2: The Quality Gate Architect**
- **Tool:** `/programmatic_seo <client_name>`
- **Action:** The AI strictly enforces *Rule 10: Quality Gates*. It designs a 5-column database schema that guarantees at least 60% of the content on every single programmatic page will be completely unique (e.g., pulling local APIs, specific case studies, unique H2s).

**Step 3: Template Design**
- **Tool:** Human/AI Collaboration
- **Action:** Build the master template where the variables from Step 2 will be injected. Add breadcrumb schema dynamically. 

---

### ⛓️ Dependency Chain 4: The Outbound Engine (Link Building)
*Links are still the #1 off-page ranking factor. We automate the outreach preparation.*

**Step 1: Target Acquisition**
- **Tool:** DataForSEO MCP / `competitor_gap.py` (Backlink mode)
- **Action:** Identify which high-Domain Authority (DA) sites are linking to the client's competitors but not to the client.

**Step 2: The Contact Sniper**
- **Tool:** `/link_building` -> Hunter.io API integration
- **Action:** Take the target URLs from Step 1, ping Hunter.io, and retrieve the exact email address of the Content Manager or Editor for that specific site.

**Step 3: Personalized Outreach**
- **Tool:** `/link_building` -> AI Writer
- **Action:** Generate a highly personalized email pitch offering a specific value exchange (a guest post, a broken link fix, or a data-backed resource), styled in the client's tone from their `brand_kit.json`.

---

## 🔌 Connecting The Required Tools

To unlock the full power of this OS, you need to connect three APIs. The system works without them, but runs *much* better with them.

1. **Google Search Console & GA4 (Free)**
   - **Why:** Allows `/audit` and `/monthly_report` to pull live impression, click, and ranking data instead of guessing.
   - **How:** Go to Google Cloud Console, create a project, enable the Search Console API and Analytics API. Generate OAuth credentials. Put the `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_PROJECT_ID` in your `.env` file.
2. **Hunter.io (Free Tier Available)**
   - **Why:** Supercharges the `/link_building` workflow by automatically finding the email addresses of the websites we want to pitch.
   - **How:** Create a free account at Hunter.io, get your API key, and put it in `HUNTER_API_KEY=` in your `.env`.
3. **Claude Code / Anthropic (Paid via Claude)**
   - **Why:** This is the brain of the operation.
   - **How:** Because you are running this inside your IDE using Claude Code, you just need an active Anthropic subscription. *No API key required in the `.env`*.

---

## 🧠 V2 Upgrades: Installing MCP Servers

To upgrade this OS from replacing 80% to replacing 95% of manual labor, you need to give Claude Code direct access to real-time search data and JavaScript rendering. You do this by installing **MCP Servers** directly into Claude Code.

### 1. The DataForSEO MCP (Required for V2)
**Why:** Replaces Ahrefs/Semrush. Gives Claude Code exact search volumes, Keyword Difficulty (KD), and live backlink profiles for the `/competitor_gap` and `/keyword_research` workflows.

**How to install:**
1. Create a free account at [DataForSEO](https://dataforseo.com/).
2. Get your API Login and API Password from their dashboard.
3. Open your IDE terminal and run:
   ```bash
   claude mcp add dataforseo -- npx @dataforseo/mcp-server
   ```
4. Claude Code will ask for your login and password. It only costs fractions of a cent per API call (pay-as-you-go).

### 2. The Playwright MCP (Highly Recommended)
**Why:** Standard Python scrapers only see raw HTML. The Playwright MCP allows Claude Code to open a headless browser, see JavaScript-rendered content (React, Next.js, Shopify templates), and take visual screenshots for your audit reports.

**How to install:**
1. Open your IDE terminal and run:
   ```bash
   claude mcp add playwright -- npx @playwright/mcp-server
   ```
2. No API keys needed! It runs locally on your machine.

---

## 🛡️ Why Trust This System? (The 80% Rule)

Can one person with this Operating System replace a 5-person SEO team? **Yes, absolutely.**

Here is why you can be confident:

1. **Separation of Reasoning vs. Execution (WAT Framework):** AI is terrible at blindly scraping websites. It hallucinates data. This OS uses Python (`BeautifulSoup`, `requests`) to do the hard mathematical data gathering. The AI is only used to *read* that perfect data and make strategic decisions. 
2. **No "Thin Content" Penalties:** We implemented **Quality Gates** (Rule 10). If you try to spam 50 location pages, the OS will physically stop you to protect the client's domain from Google's spam updates.
3. **Current to 2026 Standards:** Most human SEOs are still recommending obsolete tactics (like `FAQPage` schema on commercial sites, which Google restricted in 2023). This OS is hardcoded with the exact Sept 2025 E-E-A-T guidelines, INP Web Vitals targets, and GEO (Generative Engine Optimization) rules.

**The 20% you still have to do:**
This system does 80% of the work. Your 20% as the agency owner is:
- **Strategy & Client Communication:** Holding their hand, presenting the Word documents.
- **Copy-Pasting & Publishing:** Putting the titles, metas, and articles into Shopify/WordPress.
- **Relationship Building:** Actually sending the emails the AI drafts for link building.

Follow this playbook, and you will output the volume of an enterprise agency from a single laptop.
