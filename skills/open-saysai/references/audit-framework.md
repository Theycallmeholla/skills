# AI Visibility Audit Framework

Use this deeper framework when a full audit or implementation plan is requested.

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

## 2. Indexability

Check whether the page is eligible for conventional search indexes that feed AI systems.

Evidence:
- `noindex`
- `X-Robots-Tag`
- canonical target
- sitemap inclusion
- search-engine discovery/index evidence
- accidental duplicate/canonical conflicts

Do not infer index status solely from a successful fetch.

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

## 6. Information gain

Classify major pages:

- **Primary source** -- original data, docs, research, tools, direct experience
- **Useful synthesis** -- materially better organization/analysis of external facts
- **Commodity** -- similar to hundreds of existing pages
- **Thin/derivative** -- adds little beyond paraphrase

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

- crawler requests in logs
- AI referrals
- conversions from AI referrals
- indexed pages
- citations/mentions from prompt testing
- Bing/Google AI reporting where available

## Priority logic

Prioritize in this order unless evidence says otherwise:

1. hard access/index blockers
2. wrong or contradictory crawler controls
3. missing unique/source-worthy information
4. weak retrieval structure on commercially important pages
5. poor entity/authority corroboration
6. topic/query-space gaps
7. freshness/measurement improvements
8. experimental extras such as `llms.txt`
