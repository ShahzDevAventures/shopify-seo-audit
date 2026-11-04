# Redesign SEO safeguard

Use on every theme rebuild or redesign. It answers the question "will the redesign kill our SEO?" and protects post-launch traffic.
Sources: Shopify Academy SEO path (auditing after a migration or redesign; preserving SEO during site changes) plus agency practice.

## At discovery (before design)
1. **URL inventory.** Run the crawler (SKILL.md, "Running the crawler") at `--per-type 1000` (slow: let it run in the background), or export the sitemap URLs. Add GSC Pages (12 months) and save the **top 50 landing pages by clicks** to `seo/baseline-pages.csv`.
2. **Baseline.** Record GSC clicks, impressions and indexed-page count, CWV pass/fail, and the current title/meta on the top 50 pages. Save as `baseline-<date>.md`.
3. **Handles are frozen.** Any IA change that renames a collection, page or product handle needs a line in `redirect-map.csv` (`old_path,new_path,reason`). Default answer: keep the handle and change only the display name.

## Build handoff (to the theme developer)
- Templates keep **exactly one H1** and **one Product JSON-LD** (no theme block duplicating an app's).
- Card snippets link with `product.url`, not `| within: collection`.
- Copy changes are fine and count as a freshness signal. Title/meta on the top 50 pages carry over unless deliberately improved.
- Homepage title/meta in Online Store → Preferences checked after the theme switch.
- No new section adds hard-coded images without alt text.

## Launch day
- Import the redirects from `redirect-map.csv` (Content → Menus → URL redirects → Import, using Shopify's sample redirect CSV as the format). When a handle is edited in the admin, Shopify offers a "Create a URL redirect" option (pre-selected on pages); handles changed through IA moves, imports or apps get no redirect unless one is added. A redirect only works when the old URL returns 404: if the old page still loads, the redirect is ignored.
- Update internal links (menus, sections, blog posts) to point at the **final** URLs, not through redirects.
- If the old theme had a custom `robots.txt.liquid`, check the new theme has it too: uploading a theme from the Themes page in the admin does not import `robots.txt.liquid`.
- Run the crawler on the live store and fix any H1, JSON-LD or canonical regressions the same day.

## After launch
| When | Check |
|---|---|
| Week 1 | Every one of the top 50 baseline URLs returns 200 or a single 301 hop; no new 404s in GSC; sitemap re-submitted |
| Week 2 | GSC indexing: indexed-page count within ±10% of baseline |
| Week 4 | Clicks and impressions vs baseline (allow for seasonality); CWV field data |
| Week 8 | Rankings on the top 20 queries; write a short report for the merchant |

Pages that lose more than 30% of clicks after 4 weeks: compare the old and new title, H1, copy length and internal links, and restore whatever was removed.
