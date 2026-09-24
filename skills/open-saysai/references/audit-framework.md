# AI Visibility Audit Framework

Use this deeper framework when a full audit or implementation plan is requested.

Sections 1-3 decide whether AI systems *can* use the site. Sections 4-9 and the source-selection page review decide whether they *would* choose it as a source. A full audit needs both. The second half is the point.

## 1. Access

Check whether retrieval systems can request the page at all.

Evidence:
- HTTP status
- redirects
- robots rules by relevant user-agent
- WAF/challenge responses
- authentication
- rate limits
- geo/device restrictions

Label every crawler-access claim with its evidence tier, weakest to strongest:

1. **Synthetic UA** -- a request that presented the crawler's user-agent from the audit machine (`probe_site.py`). Shows how the site treats that UA from that IP only.
2. **UA-attributed logs** -- server/CDN log requests that claim the crawler's UA. Real traffic, unverified identity; spoofed crawler traffic is common.
3. **Verified crawler** -- log requests matched to the vendor's published IP ranges, or reverse/forward DNS where the vendor documents it.
4. **Webmaster tool** -- first-party platform reporting (e.g. Google Search Console crawl stats, Bing Webmaster Tools).

Claim that a real crawler can access the site only at tier 3 or 4. Below that, report what was observed ("requests presenting the PerplexityBot UA received 200"; "1,240 requests claiming ClaudeBot, not IP-verified").

## 2. Indexability

Check whether the page is eligible for conventional search indexes that feed AI systems.

Evidence:
- `noindex`
- `X-Robots-Tag`
- canonical target
- sitemap inclusion
- search-engine discovery/index evidence
- accidental duplicate/canonical conflicts

Do not infer index status solely from a successful fetch. A commercially important page verified as not indexed is an index blocker for that page (priority 1 below).

### Dataset reconciliation

Sitemap URL counts, Search Console totals, crawl counts, and index counts describe different populations. When they disagree materially, explain the difference before deriving any percentage. Common causes:

- a sitemap index and its child sitemaps both counted
- `/sitemap.xml` and a robots-declared sitemap being the same file
- child sitemaps the probe did not fetch
- URLs Search Console has not processed yet
- canonicalized, redirected, or `noindex` URLs dropped from one count
- Search Console reporting a different property, sitemap, or date range

If the gap can't be explained, report both numbers and mark coverage **Unknown**. Never write "X of Y indexed" when X and Y come from different populations.

## 3. Renderability

Check whether meaningful text survives extraction.

Look for:
- server-rendered/HTML text
- meaningful headings
- important content hidden behind JS-only states
- facts only inside images/video/canvas
- accordions/tabs that are inaccessible in the fetched representation

## 4. Retrieval fitness

Score qualitatively with evidence:
- direct answer near heading
- self-contained sections
- descriptive headings
- clean factual statements
- tables where appropriate
- dates/units/context attached to numbers
- low ambiguity in pronouns/references
- limited filler

**Passage lift test:** quote a 2-4 sentence passage from each reviewed page. Would it make sense, and be worth citing, if an AI showed it alone? Slogan headings and passages that depend on surrounding context fail.

## 5. Trust and evidence

Look for:
- primary-source citations
- methodology
- sample size
- limitations
- authorship
- editorial ownership
- contact/about transparency
- correction/update practices where relevant

State precisely what is missing (e.g. named operator, ownership, methodology, contact) and where you looked. Don't report the site as silent about itself when the homepage or footer already states the basics.

## 6. Information gain

Classify major pages:

- **Primary source** -- original data, docs, research, tools, direct experience
- **Useful synthesis** -- materially better organization/analysis of external facts
- **Commodity** -- similar to hundreds of existing pages
- **Thin/derivative** -- adds little beyond paraphrase

Compare against what the obvious competing sources already say: vendor docs, large publishers, aggregators, forums, and direct competitors. Content those sources already cover well is commodity, however polished.

Push strategy toward primary-source and useful-synthesis content.

## 7. Entity clarity

Can a machine reliably answer:

- Who/what is this entity?
- What does it do?
- Where is it based/available?
- Who created/owns/authors it?
- What products/services/topics is it associated with?
- Which external sources confirm those relationships?

## 8. Topic graph

Map the domain's strongest topics and missing subtopics. Prefer coherent clusters with real user value over mass programmatic pages.

## 9. Freshness

For changing subjects, inspect:

- visible published/updated dates
- whether dates are truthful
- stale pricing/features/screenshots
- accurate sitemap `lastmod`
- update cadence
- IndexNow/search notification where useful

## 10. Agent usability

Separate from ranking/citations. Check whether an AI agent can:

- identify controls
- understand form fields
- detect success/failure
- navigate menus/dialogs
- complete tasks without visual guesswork

## 11. Measurement readiness

Check whether the site can observe:

- crawler requests in logs (and whether they are IP-verified)
- AI referrals
- conversions from AI referrals
- indexed pages
- citations/mentions from prompt testing
- Bing/Google AI reporting where available

No tool reports citations across every AI product. Bing Webmaster Tools AI Performance covers Microsoft Copilot, Bing AI summaries, and select partners; controlled prompt tests cover the rest. Describe gaps as "measurement is incomplete" and name what is missing.

## Source-selection page review

Required for full audits; the page audit is this review applied to one URL.

Review at least 5 real pages spanning the types the site has: homepage, top commercial pages, the strongest content or data asset, a case study/proof page, and the about/author page. For each, record:

- page type and information-gain class (section 6)
- passage lift test result, with the quoted passage (section 4)
- the exact question that would make a retrieval system need this page
- which sources already answer that question, and whether this page is better
- the fix that would make it more worth citing

Then answer at site level:

- Which assets are primary sources?
- Which questions is this domain already the best answer for?
- Which questions should it be the best answer for, given what it knows first-hand?

## Completion gate (full audit)

Before finishing, mark each dimension **Evaluated** (with evidence), **Unknown** (with what would resolve it), or **Out of scope** (with the reason):

access · indexability · renderability · retrieval fitness · trust/evidence · information gain · entity clarity · topic graph · freshness · agent usability · measurement · prompt visibility

Also required: the source-selection page review is done, and content/source opportunities are listed or their absence is explained.

## Priority logic

Prioritize in this order unless evidence says otherwise:

1. hard access/index blockers, including important pages verified as not indexed
2. wrong or contradictory crawler controls
3. missing unique/source-worthy information
4. weak retrieval structure on commercially important pages
5. poor entity/authority corroboration
6. topic/query-space gaps
7. freshness/measurement improvements
8. experimental extras such as `llms.txt`

### Priority gate

The recommended first action is the top finding by this order. How easy, fast, or cheap a fix is never moves it up. Easy work can be listed beside it as "quick win (parallel)."
