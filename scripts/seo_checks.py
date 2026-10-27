#!/usr/bin/env python3
"""Shopify technical + on-page SEO checks for a live store. Stdlib only; Shopify pages are server-rendered, so no browser.

Reads robots.txt and the sitemap index, samples URLs per type (home, products, collections, pages, blogs),
then checks each page: status, title/meta length, H1 count, canonical, robots meta, Product JSON-LD count,
product links that go through /collections/, images without alt, visible word count. Store-level: `-N`
duplicate handles in the sitemap, Disallow rules hitting real pages, custom 404, /collections/all indexability.
Never submits forms, never logs in, never adds to cart.

Usage:
  seo_checks.py https://store.com out_dir [--per-type 5] [--timeout 20]
Writes:
  out_dir/seo-checks.json
  out_dir/seo-checks.md
"""
import argparse, json, pathlib, re, sys, time, urllib.error, urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 ShopifySEOAudit"
TITLE_MAX, META_MIN, META_MAX = 60, 150, 160
WORDS_MIN = 250
PAUSE = 1.5


def get(url, timeout, tries=4):
    """GET with backoff: Shopify storefronts answer bursts with 429."""
    for i in range(tries):
        time.sleep(PAUSE)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, r.geturl(), r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                time.sleep(min(30, int(e.headers.get("Retry-After") or 0) or 5 * (i + 1)))
                continue
            return e.code, url, e.read().decode("utf-8", "replace") if e.fp else ""
        except Exception as e:
            return 0, url, str(e)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self.canonical, self.robots = "", None, None, ""
        self.h1, self.imgs, self.imgs_no_alt, self.links, self.jsonld = 0, 0, 0, [], []
        self.words, self._in, self._skip, self._buf = 0, None, 0, ""

    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag in ("script", "style", "noscript"):
            self._skip += 1
            if tag == "script" and a.get("type") == "application/ld+json":
                self._in, self._buf = "ld", ""
        elif tag == "title":
            self._in = "title"
        elif tag == "meta":
            n = (a.get("name") or "").lower()
            if n == "description":
                self.meta = (a.get("content") or "").strip()
            elif n == "robots":
                self.robots = (a.get("content") or "").lower()
        elif tag == "link" and "canonical" in (a.get("rel") or "").lower():
            self.canonical = a.get("href")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "img":
            self.imgs += 1
            if not (a.get("alt") or "").strip() and a.get("role") != "presentation":
                self.imgs_no_alt += 1
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = max(0, self._skip - 1)
            if self._in == "ld":
                self.jsonld.append(self._buf)
                self._in = None
        elif tag == "title" and self._in == "title":
            self._in = None

    def handle_data(self, d):
        if self._in == "ld":
            self._buf += d
        elif self._in == "title":
            self.title += d
        elif not self._skip:
            self.words += len(re.findall(r"[A-Za-z0-9][\w'-]*", d))


def ld_types(blobs):
    types = []
    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            types.extend(t if isinstance(t, list) else [t] if t else [])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for b in blobs:
        try:
            walk(json.loads(b))
        except Exception:
            types.append("INVALID_JSON")
    return types


def sitemap_urls(base, timeout):
    """Return {type: [urls]} from the Shopify sitemap index."""
    out = {}
    s, _, body = get(urljoin(base, "/sitemap.xml"), timeout)
    if s != 200:
        return out
    for sm in re.findall(r"<loc>([^<]+)</loc>", body):
        kind = next((k for k in ("products", "collections", "pages", "blogs") if f"sitemap_{k}" in sm), "other")
        s2, _, b2 = get(sm.replace("&amp;", "&"), timeout)
        if s2 == 200:
            out.setdefault(kind, []).extend(u for u in re.findall(r"<loc>([^<]+)</loc>", b2)
                                            if "/cdn/" not in u and urlparse(u).path.strip("/"))
    return out


def check_page(url, kind, base, timeout):
    s, final, body = get(url, timeout)
    r = {"url": url, "type": kind, "status": s, "final_url": final, "issues": []}
    if s != 200:
        r["issues"].append(f"status {s}")
        return r
    p = Page()
    try:
        p.feed(body)
    except Exception:
        pass
    title = re.sub(r"\s+", " ", p.title).strip()
    types = ld_types(p.jsonld)
    host = urlparse(base).netloc
    coll_links = sorted({l for l in p.links if re.search(r"/collections/[^/?#]+/products/", l)
                         and (urlparse(l).netloc in ("", host))})
    r.update(title=title, title_len=len(title), meta=p.meta, meta_len=len(p.meta or ""), h1=p.h1,
             canonical=p.canonical, robots=p.robots, jsonld_types=types, product_ld=types.count("Product"),
             imgs=p.imgs, imgs_no_alt=p.imgs_no_alt, words=p.words, collection_path_links=len(coll_links))
    iss = r["issues"]
    if not title: iss.append("no title")
    elif len(title) > TITLE_MAX: iss.append(f"title {len(title)} chars (>{TITLE_MAX})")
    if not p.meta: iss.append("no meta description")
    elif not META_MIN - 30 <= len(p.meta) <= META_MAX + 10: iss.append(f"meta {len(p.meta)} chars (target {META_MIN}-{META_MAX})")
    if p.h1 != 1: iss.append(f"{p.h1} H1s")
    if not p.canonical: iss.append("no canonical")
    elif p.canonical.split("?")[0].rstrip("/") != final.split("?")[0].rstrip("/"): iss.append(f"canonical -> {p.canonical}")
    if "noindex" in p.robots: iss.append("meta robots noindex")
    if kind == "products" and r["product_ld"] != 1: iss.append(f"{r['product_ld']} Product JSON-LD blocks")
    if "INVALID_JSON" in types: iss.append("invalid JSON-LD")
    if coll_links: iss.append(f"{len(coll_links)} product links via /collections/ path")
    if p.imgs_no_alt: iss.append(f"{p.imgs_no_alt}/{p.imgs} images without alt")
    if kind in ("collections", "pages", "blogs") and p.words < WORDS_MIN: iss.append(f"thin: ~{p.words} words incl. nav/footer")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("store"); ap.add_argument("out")
    ap.add_argument("--per-type", type=int, default=5); ap.add_argument("--timeout", type=int, default=20)
    a = ap.parse_args()
    base = a.store if a.store.startswith("http") else "https://" + a.store
    base = base.rstrip("/") + "/"
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    store = {"store": base, "checked_at": time.strftime("%Y-%m-%d %H:%M"), "issues": []}

    s, _, robots = get(urljoin(base, "/robots.txt"), a.timeout)
    disallows = [l.split(":", 1)[1].strip() for l in robots.splitlines() if l.lower().startswith("disallow:")] if s == 200 else []
    store["robots_status"], store["disallow_count"] = s, len(disallows)

    sm = sitemap_urls(base, a.timeout)
    store["sitemap_counts"] = {k: len(v) for k, v in sm.items()}
    if not sm: store["issues"].append("sitemap.xml missing or empty")
    dup = sorted(u for u in sm.get("products", []) + sm.get("collections", []) if re.search(r"-\d+$", urlparse(u).path))
    store["dash_n_handles"] = dup[:50]
    if dup: store["issues"].append(f"{len(dup)} handles ending in -N (likely duplicate titles)")
    blocked = [u for k in sm for u in sm[k] for d in disallows
               if d and d != "/" and "*" not in d and urlparse(u).path.startswith(d)]
    if blocked: store["issues"].append(f"{len(blocked)} sitemap URLs match a Disallow rule, e.g. {blocked[0]}")

    s404, _, b404 = get(urljoin(base, "/seo-check-404-test"), a.timeout)
    store["custom_404"] = s404 == 404 and len(b404) > 2000
    if s404 != 404: store["issues"].append(f"missing page returns {s404}, not 404")
    sall, _, ball = get(urljoin(base, "/collections/all"), a.timeout)
    if sall == 200 and "noindex" not in ball.lower()[:20000]:
        store["issues"].append("/collections/all is indexable (check it is not thin or duplicating the catalog)")

    targets = [(base, "home")] + [(u, k) for k in ("collections", "products", "pages", "blogs") for u in sm.get(k, [])[: a.per_type]]
    pages = []
    for u, k in targets:
        pages.append(check_page(u, k, base, a.timeout))
    home = pages[0]
    if home["status"] == 200 and not home.get("meta"):
        store["issues"].append("homepage has no meta description (Online Store > Preferences)")
    if any(p["status"] == 429 for p in pages):
        store["issues"].append("some pages rate-limited (429); re-run with a smaller --per-type")

    (out / "seo-checks.json").write_text(json.dumps({"store": store, "pages": pages}, indent=2))
    md = [f"# SEO checks: {base}", f"Checked {store['checked_at']}. Sampled {len(pages)} pages, {a.per_type} per type. "
          "Lab crawl without JS; verify findings in GSC before reporting.", "", "## Store-level",
          f"- Sitemap: {store['sitemap_counts'] or 'none'}", f"- robots.txt: status {store['robots_status']}, {store['disallow_count']} Disallow rules",
          f"- Custom 404: {'yes' if store['custom_404'] else 'no / unclear'}"]
    md += [f"- **{i}**" for i in store["issues"]] or ["- No store-level issues"]
    md += ["", "## Pages", "| Type | URL | Title len | Meta len | H1 | Product LD | No-alt imgs | Issues |", "|---|---|---|---|---|---|---|---|"]
    for p in pages:
        md.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
            p["type"], urlparse(p["url"]).path or "/", p.get("title_len", "-"), p.get("meta_len", "-"), p.get("h1", "-"),
            p.get("product_ld", "-") if p["type"] == "products" else "", p.get("imgs_no_alt", "-"),
            "; ".join(p["issues"]).replace("|", "/") or "ok"))
    (out / "seo-checks.md").write_text("\n".join(md) + "\n")
    print(f"{len(pages)} pages, {len(store['issues'])} store issues, {sum(1 for p in pages if p['issues'])} pages with issues -> {out}")


if __name__ == "__main__":
    sys.exit(main())
