# shopify-seo-audit

A Claude Code skill that turns a Shopify store URL, plus a Search Console export when you have one, into a prioritised SEO fix list. It pairs a stdlib-only Python crawler with checklists that follow Shopify's own SEO audit framework (Shopify Academy, "Search Engine Optimization with Shopify"), extended with Shopify-specific technical checks the course leaves out.

Built at Sirge, a Shopify agency, by Shahz Siddiqui.

## What it checks

`scripts/seo_checks.py` reads `robots.txt` and the sitemap index, samples N URLs per type (home, products, collections, pages, blogs) and reports, per page:

- HTTP status and final URL after redirects
- title length (target 60 characters or fewer) and meta description length (target 150 to 160)
- H1 count (should be exactly one)
- canonical present and matching the final URL
- `meta robots noindex`
- number of Product JSON-LD blocks on product pages (should be exactly one; theme plus review app plus SEO app often gives two or three)
- invalid JSON-LD
- product links that go through `/collections/<x>/products/<y>` instead of `product.url`
- images without alt text
- visible word count, flagging collections, pages and blog posts under 250 words

And at store level:

- sitemap missing or empty
- handles ending in `-N` (products or collections with duplicate titles)
- sitemap URLs that match a `Disallow` rule
- missing pages that return something other than 404, and whether the 404 page is custom
- `/collections/all` indexable
- homepage with no meta description

The reference files cover what the script cannot:

- `references/checklist.md`: technical review order (crawlability, duplicate signals, speed and mobile, international) and on-page rules by page type (home, collection, product, blog).
- `references/keywords.md`: GSC baseline, intent-to-page-type map, a five-step SERP read, striking-distance triage (position 11 to 20), and the keyword-to-page map format.
- `references/redesign-safeguard.md`: what to record before a theme rebuild, what the build handoff must preserve, launch-day steps, and a week 1/2/4/8 post-launch check table.

## Install

Clone into your Claude Code skills directory:

```bash
git clone https://github.com/ShahzDevAventures/shopify-seo-audit ~/.claude/skills/shopify-seo-audit
```

For a single project, clone into `.claude/skills/shopify-seo-audit` inside the repo instead. Claude Code picks up `SKILL.md` on the next session.

Requirements: Python 3.9 or later. The script uses only the standard library.

## Run

In Claude Code, ask for an SEO audit of a store and give the URL. Attach a Search Console Performance export (Queries and Pages) if you have one; without it the skill produces a storefront-only audit and says so.

The crawler can also run on its own:

```bash
python3 -I scripts/seo_checks.py https://example-store.com seo --per-type 5
```

Arguments: store URL, output directory, `--per-type` (URLs sampled per sitemap type, default 5), `--timeout` (seconds, default 20). The script waits 1.5 seconds between requests and backs off on 429. It never submits forms, logs in or adds to cart.

## Output

The script writes `seo/seo-checks.json` and `seo/seo-checks.md`. The Markdown file has a store-level section followed by a per-page table:

```
| Type | URL | Title len | Meta len | H1 | Product LD | No-alt imgs | Issues |
|---|---|---|---|---|---|---|---|
| home | / | 48 | 0 | 1 |  | 3 | no meta description; 3/41 images without alt |
| products | /products/example-mug | 71 | 155 | 1 | 2 | 0 | title 71 chars (>60); 2 Product JSON-LD blocks |
```

The skill then writes `seo/seo-audit-<date>.md` with:

1. a three-sentence summary (biggest blocker, biggest opportunity, this week's action)
2. a "Fix now" table: finding, evidence, fix type (`LIQUID` for theme code, `ADMIN` for a merchant setting, `CONTENT` for copy), effort, owner
3. the keyword map (keyword, volume, difficulty, intent, target page, action)
4. striking-distance queries, each marked optimise, maxed out, or ignore
5. page-type findings
6. a link to the technical appendix
7. the Search Console exports still missing

## Limits

- The crawl is a lab crawl without JavaScript. App-injected tags (reviews schema, SEO apps) will not appear; confirm findings by viewing the page source or in Search Console before reporting them.
- Speed and Core Web Vitals are not measured. Use PageSpeed Insights or the Search Console CWV report.
- Word counts include navigation and footer text, so they are an upper bound for body copy.
- The sitemap sample is the first N URLs per type, not a random sample.
- Keyword volume and difficulty need a third-party tool; the skill only structures them.
- Shopify storefronts rate-limit bursts. Keep `--per-type` small on a first run.

## Author

Shahz Siddiqui

- https://shahzsiddiqui.vercel.app
- https://www.linkedin.com/in/shahz-siddiqui-lead

## License

MIT. See `LICENSE`.
