# Website Audit Checklist

Severity in brackets. Deterministic items (D) come from `audit.mjs` / curl; judgment items (J) come from your review of screenshots and content.

## Availability & Security

- [CRITICAL] (D) Site reachable, homepage returns 200
- [CRITICAL] (D) Valid SSL certificate (no browser security errors)
- [MAJOR] (D) HTTP redirects to HTTPS
- [MAJOR] (D) No mixed-content warnings (http assets on https pages)
- [MINOR] (D) www / non-www resolve consistently (single canonical host)
- [MAJOR] (D) Custom 404 page exists (not a raw server default)

## Crawl health

- [CRITICAL] (D) No broken internal links on homepage or primary nav
- [MAJOR] (D) No broken internal links anywhere crawled
- [MINOR] (D) No broken external links
- [MAJOR] (D) No broken/missing images on crawled pages
- [MINOR] (D) sitemap.xml present and parseable
- [MINOR] (D) robots.txt present and not blocking the whole site
- [MAJOR] (D) No pages with JS console errors that break functionality
- [MINOR] (D) No pages with console errors at all (QA mode)

## SEO basics

- [MAJOR] (D) Every page has a unique, non-empty `<title>` (10–60 chars)
- [MAJOR] (D) Every page has a meta description (50–160 chars)
- [MAJOR] (D) Exactly one H1 per page
- [MINOR] (D) Images have alt text
- [MINOR] (D) Canonical tags present
- [MINOR] (D) Open Graph tags on homepage (title, image, description)
- [MINOR] (D) Structured data / LocalBusiness schema (local businesses)
- [MINOR] (D) Favicon present

## Mobile

- [CRITICAL] (J) Site is usable on mobile — nav works, text readable, no horizontal scroll
- [MAJOR] (D) Viewport meta tag present
- [MAJOR] (J) No overlapping/overflowing elements in mobile screenshots
- [MAJOR] (J) Tap targets (buttons, links) large enough and spaced
- [MAJOR] (J) Phone number is click-to-call (`tel:` link) — local businesses

## Performance

- [MAJOR] (D) Homepage loads < 3s on the crawler; PSI mobile performance ≥ 50 (QA: ≥ 70)
- [MINOR] (D) Total homepage weight < 3 MB
- [MINOR] (D) Images served in modern formats / reasonably sized

## Design & content (judgment)

- [MAJOR] (J) Design looks current — not visibly dated (era check)
- [CRITICAL] (J) A first-time visitor can tell what the business does + where it operates within 5 seconds of the hero
- [MAJOR] (J) One clear primary CTA above the fold
- [MAJOR] (J) No placeholder / lorem ipsum / template leftovers
- [MAJOR] (J) No stale content (old copyright year, expired promos, "coming soon" older than the crawl)
- [MINOR] (J) No duplicated info oddities (same phone 3× in header, restated bullet lists) — see ui-oddity-scan skill
- [MAJOR] (J) Contact path works: form present and short (≤5 fields), or prominent phone/email
- [MINOR] (J) Trust signals present: reviews/testimonials, credentials, real photos
- [MINOR] (J) NAP (name, address, phone) consistent across all pages

## QA-mode extras (sites we built)

- [CRITICAL] (D) All forms submit successfully (test with obviously-fake data flagged as test)
- [CRITICAL] (D) No links to staging/localhost/dev URLs
- [MAJOR] (D) Analytics/tracking installed and firing
- [MAJOR] (J) Every page matches the approved structure_packet sitemap — no orphaned or missing pages
- [MINOR] (D) Redirects from the old site's top URLs in place (relaunches)
- [MINOR] (J) Legal pages present (privacy policy at minimum)
