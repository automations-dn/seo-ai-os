# 🚀 SEO AI OS: The Complete Agency Playbook

Welcome to the **SEO AI Operating System**. This guide is written for agency owners and SEO managers. If you follow this playbook, this single system (driven by Claude Code) can replace 80% of manual SEO labor, turning a solo operator into the equivalent of a 5-person SEO team.

---

## 📅 The Monthly Agency Routine

To get "100x better results" for your clients, you don't need to do *more* random tasks; you need to do the *right* tasks consistently. Here is the exact order of operations to run your clients through the SEO AI OS.

### 1. The Onboarding Phase (Month 1, Week 1)
When you close a new client, your first step is bringing them into the AI OS context.

**Action:** Type `/add_client <client_name>` in your IDE terminal.
**What happens:** I will ask you a series of questions to build their `brand_kit.json`. I need to know their target audience, competitors, voice/tone, and primary keywords. Do not skip these—this is what makes the AI generate *good* content instead of generic content.

### 2. The Comprehensive Audit (Month 1, Week 2)
You need a baseline of where the client currently stands, and you need to find the critical blockers immediately.

**Action:** Type `/audit <client_name> --type first_time`
**What happens:** 
1. I automatically crawl the site, evaluating Technical SEO, On-Page SEO, Core Web Vitals (INP, LCP, CLS), and Schema.
2. I auto-detect their industry (SaaS, E-comm, Local, etc.) and tailor the grading scale.
3. I generate a beautiful, branded Word document (`.docx`) matching the Dare Network template.
4. **Your job:** Send this Word doc to the client. It looks like you spent 10 hours on it. It took 3 minutes.

### 3. Deep-Dive Page Optimization (Month 1, Weeks 3-4)
Identify the client's top 5 most important pages (e.g., core service pages, category pages).

**Action:** Type `/page <client_url> --keyword "<target_keyword>"`
**What happens:**
1. I do a focused, aggressive breakdown of that single page.
2. I check against the Sept 2025 E-E-A-T Quality Rater Guidelines.
3. I evaluate Image SEO (alt text, WebP, sizes).
4. I check AEO (Answer Engine Optimization) to ensure the page will get cited by Google's AI Overviews and ChatGPT.
5. **Your job:** Take my generated replacement `<title>`, meta description, and H1 tags, and paste them into their CMS. Implement the image fixes.

### 4. Content Generation (Month 2+)
Now you start driving new organic traffic. You need an article brief and then the article itself.

**Action 1:** Type `/content_brief <client_name>`
**What happens:** I look at their brand kit, competitors, and keywords, and generate a highly structured outline. Review this with the client to get approval.

**Action 2:** Type `/content_draft <client_name>`
**What happens:** I write the full, SEO-optimized article based on the brief, fully formatted in markdown, matching their brand voice.

### 5. Link Building & Outreach (Month 3+)
To increase Domain Authority, you need backlinks.

**Action:** Type `/link_building <client_name>`
**What happens:** I find link opportunities and draft highly personalized outreach emails.
*(Note: Requires connecting Hunter.io API in `.env` for finding contact emails).*

### 6. The Monthly Report (End of Every Month)
Retention is driven by communication. 

**Action:** Type `/monthly_report <client_name>`
**What happens:** I compile all the work done, pull the latest data from GSC/GA4 (if connected), and generate a clean monthly summary report.

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
