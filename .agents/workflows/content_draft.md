---
description: /content_draft - Write a full SEO-optimized article from an approved content brief
---

# Workflow: Content Draft Generation

## Trigger
```
/content_draft <client_name> [--brief <path_to_brief>] [--keyword "<target_keyword>"]
```
**Example:** `/content_draft acme_corp --brief active_campaigns/best_project_mgmt_brief.md`

## Objective
Generate a fully SEO-optimized, AEO/GEO-ready article in the client's brand voice, complete with internal/external links and JSON-LD schema markup. Paste result for review.

## Required Inputs
1. `<client_name>` — loads brand_kit for brand voice injection
2. `--brief` — path to an approved content brief OR
3. `--keyword` — if brief not provided, run `/content_brief` workflow first and wait for approval

## Step-by-Step Instructions

### Step 1: Load Context
- Read `clients/<client_name>/brand_kit.json`
- Extract: `tone`, `persona`, `writing_style_notes`, `cta_style`, `primary_keywords`, `negative_keywords`
- Read the brief file (or `.tmp/<client_name>_brief.md` if just generated)

### Step 2: Draft Section by Section (Following the Brief Structure)
For each H2 section in the brief:
1. Write content covering the topic thoroughly
2. Naturally include 1-2 LSI keywords from the brief
3. For FAQ section: write concise, quotable answers (2-3 sentences max per answer — optimized for AI snippet extraction)
4. For conclusion: use the client's `cta_style`
5. Keep tone aligned to `persona` and `writing_style_notes`

**Word count target:** Match estimated range from brief

### Step 3: Inject Internal & External Links
- For each internal link from the brief: find the most natural placement in the text and embed it
- For external links: cite 2-3 authoritative sources (gov sites, .edu, or high-authority industry sites)

### Step 4: Generate JSON-LD Schema
- Run: `tools/schema_gen.py --type <required_schema> --content <draft_file>`
- Generates valid, tested JSON-LD code blocks for the required schema types (Article, FAQ, etc.)
- Embed at the top of the draft in a `<script type="application/ld+json">` block

### Step 5: SEO Final Check
Before presenting draft, self-check:
- [ ] Primary keyword in H1, first 100 words, and at least 2 H2s
- [ ] Meta title is 50-60 characters
- [ ] Meta description is 120-160 characters
- [ ] No negative keywords from brand_kit used
- [ ] All internal links present
- [ ] Schema code is valid JSON
- [ ] At least one "direct answer" block exists (for AEO extraction)

### Step 6: Present Draft for Review
Save draft to: `clients/<client_name>/active_campaigns/<slug>_draft.md`
Then display the draft in chat (or a summary if very long) and ask:
**"Draft complete! Do you want to make any edits before I format this for WordPress/CMS publishing?"**

## Edge Cases
- If brief is missing required fields (e.g., no internal links section): proceed without them and flag the gap.
- If brand_kit has contradictory tone settings: default to the first tone listed and flag it to the user.
