# SEO checklist: Shopify

Sources: Shopify Academy SEO path (2026-10-27). Items marked **[Extra]** come from agency theme work; the course leaves them out. Shopify admin paths and platform behaviour re-checked against help.shopify.com, shopify.dev, Google Search Central and web.dev on 2026-11-04.

## Technical (in this order)

### 1. Crawlability and indexing
- Sitemap index submitted in GSC **for each domain**; international domains need their own submission. If it was never submitted, that's the easiest fix in the audit. The index can also list `sitemap_agentic_discovery.xml` (it lists `/agents.md`) and a separate `sitemap_articles_N.xml` for blog posts (seen on live stores, November 2026); neither is an error.
- robots.txt: most GSC warnings can be ignored. The one that matters is a URL you want ranked being Disallowed. **[Extra]** If `robots.txt.liquid` is customised, find out why; look for leftover rules from migrations or apps. A custom template replaces Shopify's generated file, Shopify Support does not help with it, and Shopify recommends editing it with Liquid rather than replacing it with plain text.
- Canonicals: missing, pointing at a URL that is missing, or conflicting with a redirect or the sitemap.
- Status codes: 404, 403 or 410 on URLs with backlinks → 301 to the closest match. Internal links should point at the final 200 URL. Fix redirect chains during maintenance (low priority).
- 404 page: custom, on-brand, with navigation (`seo_checks.py` tests this).
- Orphans: a product in no collection → add it to one; a collection not linked anywhere → link it from nav or a related collection. **Important pages must be within 3 clicks of the homepage.**

### 2. Duplicate and conflicting signals
- **[Extra]** Product cards linking to `/collections/x/products/y` (from `| within: collection`). The canonical covers it, but link signals and crawl budget are split. → **LIQUID:** use `product.url` in card snippets.
- **[Extra]** 0, 2 or more Product JSON-LD blocks on a PDP (theme block plus reviews app plus SEO app), or price/availability that disagrees with the page. → **LIQUID:** keep one block and merge the rating in. Check with the Rich Results Test.
- **[Extra]** Organization/WebSite schema on the homepage, BreadcrumbList on collections and PDPs, Article on blog posts.
- `-1`/`-2` handles (products with duplicate titles) → **ADMIN:** use a descriptive handle, but only if the page is not already ranking.
- **[Extra]** Filter, sort and tag URLs (`?filter.`, `?sort_by=`, `/collections/x/tag`) indexable or in the sitemap; `/collections/all`, `/collections/vendors`, `/collections/types` and `/search` indexable and thin.
- **[Extra]** Page builder pages (PageFly, Shogun, Replo): missing or duplicate H1, missing meta, heavy JS.

### 3. Speed and mobile (use PageSpeed Insights; the script skips speed)
- Targets ("good" Core Web Vitals): **LCP 2.5 s or less, INP 200 ms or less, CLS 0.1 or less**, at the 75th percentile of real visits. Use field data first: lab tools such as Lighthouse cannot measure INP. INP replaced FID in 2024.
- Product photos **under 300 KB**; lazy loading only below the fold. **[Extra]** A lazy-loaded LCP image is a bug.
- Mobile: readable without zoom, tap targets big enough, no horizontal scroll, no intrusive pop-ups on entry.
- **[Extra]** Leftover scripts from uninstalled apps in `theme.liquid`.

### 4. International (only if Markets or multiple domains are in use)
- hreflang (language/region) and canonical work together. Shopify Markets generates both: each market version has a self-referencing canonical, and hreflang tags link the versions. Check that **Automatic hreflang tags** is still on (Online Store → Preferences → Social sharing image and SEO) or, if it is off, that the theme or app replacing it outputs no duplicates.

## On-page

### Universal
| Element | Rule |
|---|---|
| URL handle | Keyword-rich, hyphens, readable (`/collections/handmade-ceramic-mugs`). **Never change one that already ranks.** |
| Title tag | **≤ 60 characters**, most important words first: primary keyword + secondary keyword or attribute + benefit/offer. Dawn and Horizon add " – store name" unless the title already contains it; count it in the 60. |
| Meta description | **150–160 characters**: primary keyword, a call to action, plain language. Not a ranking factor, but it drives CTR. |
| Homepage title/meta | Set in **Online Store → Preferences** (Social sharing image and SEO section). Commonly missed. |
| H1 | Exactly one. Written for shoppers; the title tag can carry the extra keyword. |
| H2/H3 | Structure long copy; carry related terms (semantic search). |
| Alt text | Descriptive on every image; never "IMG_2947", never keyword-stuffed. The most common merchant mistake. **[Extra]** Hard-coded theme images need a LIQUID fix. |
| Copy | **≥ 250 words of original copy** on rankable pages; **≥ 500** on informational pages and blog posts. Never manufacturer copy. |
| Internal links | Descriptive anchors ("size chart", not "click here"). |

### By page type
- **Homepage:** keyword-rich section headings (not "Featured products" but "Shop our best-selling children's toys"); top collections linked; a categories/trends section; trust signals. An About section only if it serves users.
- **Collection:** descriptive name and handle; **a short copy paragraph above the grid** (CRO: keep it to 2 lines plus "Read more", or move the rest below the grid); links to related collections; longer copy as keyword sections or an FAQ; **collections built around long-tail terms** ("BBQ Spices", not "Spices"); every product in at least one collection.
- **PDP:** the name says the product type; distinct names for similar products; specs (size, material, care); related products (Search & Discovery) for internal links; reviews/UGC on the page.
- **Blog/content:** answers real customer questions; title matches intent; key posts updated within the last 12 months; links to products and collections. Fix PDPs, FAQs and collections before starting a blog.
