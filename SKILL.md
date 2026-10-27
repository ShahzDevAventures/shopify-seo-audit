---
name: shopify-seo-audit
description: SEO audit for a Shopify store. Runs technical checks (sitemap, robots, canonicals, duplicate Product JSON-LD, H1s, product links via collection paths, -N handles, alt text, thin pages), page-type on-page checklists, keyword-to-page mapping and striking-distance queries from Search Console, then outputs a prioritised fix list split into Liquid fixes a developer ships in the theme and admin fixes the merchant makes. Use whenever the user asks for an SEO audit, SEO check, "why isn't X ranking", keyword research or a keyword map for a store, a collection-structure or meta-title pass, "will the redesign hurt SEO", a pre-launch or post-launch SEO check, a redirect map, or drops in a Search Console export. Also use for a pre/post-launch SEO safeguard on a theme redesign (see references/redesign-safeguard.md).
---

# Shopify SEO Audit

You turn a Shopify store URL (plus a Search Console export when one exists) into a ranked SEO fix list. The method follows Shopify's own SEO audit framework (Shopify Academy, "Search Engine Optimization with Shopify", read 2026-10-27), extended with Shopify technical checks that course leaves out.

Write all output to one directory per store; the examples below use `seo/` in the current working directory.

## Inputs (ask only for what is missing)

| Input | Needed for | If missing |
|---|---|---|
| Store URL | everything | ask |
| GSC Performance export (Queries + Pages, 3 or 12 months) | keyword baseline, striking distance, CTR | do a storefront-only audit and say so at the top; list the export in "Reports to request" |
| GSC Indexing → Pages report | coverage problems | skip that section; request it |
| Brand stage (new / growing / established) | scoping | infer from GSC branded-click share and catalog size |
| 3 competitor domains | SERP and gap analysis | take them from the client brief or the SERP itself |

## Workflow

1. **Crawl (machine).** Run the script; do not hand-check what the script checks.
   ```bash
   python3 -I ~/.claude/skills/shopify-seo-audit/scripts/seo_checks.py <store> seo --per-type 5
   ```
   `seo_checks.py` samples the sitemap per type and writes `seo-checks.md/.json`. Speed and Core Web Vitals are not measured by this script: take them from PageSpeed Insights or the Search Console Core Web Vitals report (field data first). If you get 429s, re-run with a smaller `--per-type`. Never report a 429 page as broken.
2. **Technical review.** Read `references/checklist.md` § Technical. Confirm each script finding by opening the page before reporting it: lab crawls without JS miss app-injected tags. Order: crawlability → structure → speed/mobile.
3. **On-page review by page type.** Use `references/checklist.md` § On-page on the homepage, the top 3 collections and top 3 products by traffic (GSC Pages, or failing that the main-nav order).
4. **Keywords.** Use `references/keywords.md`: baseline from GSC, intent → page-type map, 5-step SERP read for 3–5 target terms, striking-distance triage, and a keyword-to-page map where every target term has exactly one page.
5. **Off-page (light).** Referring-domain count and quality versus the 3 competitors, if a tool or export is available; otherwise list 2–3 link-worthy asset ideas (see keywords.md § Authority). Never sell link building as a deliverable.
6. **Prioritise and write.** Every finding gets:
   - **Fix type:** `LIQUID` (a developer ships it in the theme) / `ADMIN` (merchant edits a field or setting) / `CONTENT` (copy to write)
   - **Effort:** <0.5 d / 0.5–1 d / 2 d+
   - **Certainty:** H or L. Every H finding goes in "Fix now", never in a test plan.

   Order: anything blocking indexing → duplicate/conflicting signals (canonical, JSON-LD, collection-path links) → high-traffic page metadata and copy → keyword-map gaps (new collections or pages) → everything else.

## Output: `seo/seo-audit-<date>.md`

1. **Summary** (3 sentences): the biggest blocker, the biggest opportunity (usually striking-distance terms or collection copy), and what to do this week.
2. **Fix now:** a table with Finding | Evidence (URL + what) | Fix type | Effort | Owner.
3. **Keyword map:** Keyword | Volume | Difficulty | Intent | Target page (existing or "new") | Action.
4. **Striking distance:** each query at position 11–20 with its case (a) optimise, (b) maxed out, (c) ignore.
5. **Page-type findings:** home, collections, PDPs, blog.
6. **Technical appendix:** the script output, linked rather than pasted.
7. **Reports to request:** the exact GSC exports still missing.

## Rules
- **Never recommend changing a handle that already ranks.** If a URL must change, it gets a 301 and internal links updated to the final URL (see redesign-safeguard.md).
- **AI copy is a draft.** Meta descriptions, alt text and collection intros written by AI are proposals for a person to edit, using real product facts. Fully AI-generated, unedited content counts as spam under Google's policies.
- Shopify already handles sitemaps, default canonicals, HTTPS, and 301s on handle edits. Do not report these as wins or as work done.
- Script numbers are lab numbers without JS. Say so, and confirm anything headline-worthy in GSC or by viewing the page source.
- Fix PDP copy, FAQs and collection structure before recommending a blog.
- Expected timing to set with the merchant: first visibility movement in 4–6 weeks, traffic and revenue in about 6 months.

## Redesigns and theme rebuilds
- Run `references/redesign-safeguard.md` at discovery (URL inventory and baseline) and again after launch.
- The build handoff must preserve handles, keep exactly one H1 per template, and keep a single Product JSON-LD block.
