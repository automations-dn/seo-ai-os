---
description: /programmatic_seo - Generate architecture for 50+ unique location or category pages safely
---

# Workflow: Programmatic SEO & Location Pages

## Trigger
```
/programmatic_seo <client_name>
```
**Example:** `/programmatic_seo local_plumbers`

## Objective
Design the schema, content template, and URL structure for building scalable programmatic SEO pages (e.g., location pages, feature vs. feature pages, directory listings) **without triggering Google's Thin Content penalties.**

---

##  CRITICAL AWARENESS: CLAUDE RULE #10
You MUST enforce **Rule 10 (Quality Gates)** during this workflow. 
Google's Helpful Content Updates (2023-2025) aggressively penalize "doorway pages" where only the City Name/Keyword is swapped out in a template. Your job is to ensure the architecture relies on **unique, database-driven value**.

## Step-by-Step Instructions

### Step 1: Gather the Strategy
Ask the user what they are trying to programmatically build:
1. *Location Pages* (e.g., Plumbers in Austin, Plumbers in Dallas)
2. *Comparison Pages* (e.g., Client vs Competitor A)
3. *Category Intersections* (e.g., Best CRM for Real Estate)

### Step 2: Ensure the 60% Unique Rule
Once you know the target, design a **Database Schema** that ensures >60% of the page content will be entirely unique to that specific URL.

**BAD (Spam):**
- Page title: Plumber in [City]
- Content: "We are the best plumber in [City]. Call us today for plumbing in [City]."

**GOOD (Helpful Content):**
- Requires variables: `[City_Name]`, `[Local_Landmarks]`, `[City_Specific_Regulations]`, `[Local_Team_Member_Profile]`, `[Specific_Completed_Jobs_In_City]`, `[City_Reviews]`.

Present the required database variables to the user. Tell them: *"To safely generate these pages without penalty, we need a dataset containing these specific unique variables for every page."*

### Step 3: Design the Content Template
Draft a markdown skeleton for how the programmatic page will look. 
Include sections that pull from the database variables you defined in Step 2.

### Step 4: Quality Gate Enforcement 
Ask the user: **"How many of these pages are you planning to generate?"**

- If **< 30**: "Looks safe. Proceed with building the database."
- If **30 - 50**: "[WARNING] WARNING: You are approaching the threshold for doorway page penalties. Ensure your database variables provide genuine unique value."
- If **> 50**: " HARD STOP: Launching 50+ programmatic pages simultaneously is highly risky for this domain. I strongly recommend rolling out a batch of 10 pages first, waiting for indexing and ranking data, and then expanding."

### Step 5: Output Generation
If the user passes the quality gates, save the Database requirements and Content Template as a `.md` blueprint inside `clients/<client_name>/active_campaigns/programmatic_blueprint.md`.

---

## Edge Cases
- If the user explicitly demands that you just "swap the city name" and ignore the unique content warnings, you must still document the severe risk of ranking collapse in the blueprint file so it is permanently logged.