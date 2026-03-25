---
description: /content_draft - Write a full SEO-optimized article from an approved content brief
---

# Workflow: Content Draft Generation (100% Humanized & Ranking-Optimized)

## Trigger
```
/content_draft <client_name> [--brief <path_to_brief>]
```

## Objective
Generate a fully SEO-optimized, AEO/GEO-ready article that ranks #1. The output MUST bypass AI detectors (100% humanized) through high burstiness, varied sentence lengths, and the absolute elimination of standard AI jargon. It must include exact Titles, Metas, and CMS-ready formatting.

---

##  CRITICAL RULE: The "100% Human" Writing Guidelines

You must write like a Senior Subject Matter Expert, not an AI. 

**1. BANNED AI VOCABULARY:**
Do NOT use these words under any circumstances: *delve, moreover, furthermore, tapestry, paramount, seamless, dynamic, robust, landscape, testament, elevate, unleash, unlock, navigate, symphony, beacon, in today's digital age, in conclusion, to summarize.*

**2. Burstiness & Perplexity:**
- Vary your sentence lengths drastically. Use very short, punchy sentences (3-5 words). Follow them with longer, descriptive sentences.
- Avoid perfectly symmetrical paragraph lengths. Humans write in asymmetrical blocks.

**3. Tone & Voice:**
- Use active voice only. Avoid passive voice.
- Limit transition words (like "however," "therefore"). Humans use them sparingly.
- Sound opinionated, authoritative, and direct. Get straight to the point. No fluff.

**4. E-E-A-T Elements (Experience & Expertise):**
- Phrase concepts using first-hand terminology where appropriate to the brand: *"In our experience,"* *"When we tested this,"* *"What we usually see is..."*

---

## Step-by-Step Instructions

### Step 1: Load Context
- Read `clients/<client_name>/brand_kit.json`.
- Internalize the `tone`, `persona`, and `target_audience`.
- Read the content brief provided.

### Step 2: The SEO Package (CMS Metadata)
Before writing the article, you must generate the exact metadata and technical code the user will copy/paste into their CMS:
- **Title Tag:** Exactly 50-60 characters. Primary Keyword at the front.
- **Meta Description:** Exactly 120-160 characters. End with a Call to Action (CTA).
- **URL Slug:** `primary-keyword-format`
- **JSON-LD Schema Script (Articles + FAQ + HowTo):** 
    - Generate a consolidated `@graph` JSON-LD block.
    - **Instructions for User:** Include a clear note: *"Copy this block into your CMS <head> section or dedicated Schema field."*

### Step 3: Write the Draft (Section by Section)

**The TL;DR / Key Takeaways:**
- Place a boxed summary section immediately below the intro or at the very top.
- 3–5 bullet points summarizing the article for AI search engines.

**The Table of Contents:**
- Create a linked Table of Contents targeting the H2/H3 anchors defined in the brief.

**The Body:**
- Follow the H2 and H3 structure from the brief.
- Naturally weave in LSI / Semantic secondary keywords. Do not keyword stuff.
- **Comparison Tables:** If comparing concepts (e.g., "X vs Y"), you MUST use a Markdown table.
- **Formatting:** Use bullet points, bolded text for emphasis, and short paragraphs to make the content highly scannable (which decreases bounce rate, increasing rankings).
- **Internal/External Links:** Embed links naturally. Stats MUST be hyperlinked to authoritative sources.

**The FAQ Section:**
- Format as Q&A for Featured Snippet optimization. (Triggers FAQ Schema).

**The Glossary (Ending):**
- Append a "Glossary of Terms" defining 3-5 technical concepts used in the article.

**The Conclusion:**
- Do not write a summary. Write an actionable next step with the client's CTA.

### Step 4: SEO Final Checking
Perform a strict check before outputting:
- [ ] Is the primary keyword in the H1, URL, Title, and Meta?
- [ ] Are all banned AI words eliminated?
- [ ] Is there a TL;DR box and a linked Table of Contents?
- [ ] Are all statistics hyperlinked to external sources?
- [ ] Is the JSON-LD `@graph` schema included with instructions?
- [ ] Is there a Glossary section?
- [ ] Are internal links included naturally?

### Step 5: Output Generation
Present the final draft in clean Markdown format in the chat so the user can literally "select all, copy, and paste" into WordPress/Shopify.

**CRITICAL RULE:** Do NOT attempt to save this output to a file. The user specifically requested that content drafts only be outputted into the chat interface an not saved into the `clients/` directory.

### Step 6: Mandatory Human Review Checklist
Append this exact checklist to the very bottom of your response so the human team member must review it before publishing:

```markdown
---
###  HUMAN QA REQUIRED BEFORE PUBLISHING:
1. [ ] **Internal Links:** Did you manually test the internal links to ensure they make sense in context?
2. [ ] **Brand Tone:** Did you verify the CTA matches the exact offer this month?
3. [ ] **Media:** Did you insert the custom client images/videos into the CMS before hitting publish?
4. [ ] **AEO Check:** Does the first paragraph directly answer the user's query in <50 words for AI Overviews?
---
```

Ask the user: 
**"Here is the 100% human-optimized draft and CMS package. Please complete the QA checklist above before publishing!"**