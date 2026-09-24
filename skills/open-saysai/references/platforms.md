# Platform Verification Cache

Use this file to avoid re-researching every platform on every audit.

## Cache rule

- Reuse a platform entry for **90 days from its Verified date** unless evidence conflicts, the platform is central to a disputed finding, or the user explicitly requests a fresh check.
- Reverify only stale/unknown platforms that are actually in scope.
- When reverified, update the working audit/packet date and source. Do not silently treat this bundled file as eternal truth.
- The skill cannot rewrite this file at runtime. Refresh the dates and re-upload the skill roughly quarterly, or every audit after expiry will re-research every in-scope platform.
- First-party vendor documentation outranks blogs, SEO tools, and crawler directories.

## OpenAI / ChatGPT

**Verified:** 2026-09-24  
**Primary source:** https://developers.openai.com/api/docs/bots

Current baseline:
- `OAI-SearchBot` -- automatic crawler used for ChatGPT search visibility.
- `ChatGPT-User` -- user-directed fetching; not the automatic search crawler.
- `GPTBot` -- training-related crawler control.
- These controls are independent; do not equate GPTBot permission with Search inclusion.

Reverify if crawler names, robots behavior, or ChatGPT search guidance is central to the audit.

## Anthropic / Claude

**Verified:** 2026-09-24  
**Primary source:** https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler

Current baseline:
- `Claude-SearchBot` -- web-search crawler.
- `Claude-User` -- user-directed retrieval.
- `ClaudeBot` -- model-development/training crawler.
- Keep the three roles separate in recommendations.

## Google Search / AI Overviews / AI Mode / Gemini

**Verified:** 2026-09-24  
**Primary sources:**
- https://developers.google.com/search/docs/appearance/ai-features
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

Current baseline:
- Eligibility for supporting links in AI Overviews/AI Mode depends on ordinary Google Search indexing/snippet eligibility.
- Googlebot/normal Search controls govern Search AI features.
- There are no special technical requirements or special "AI schema" for inclusion in Search AI features.
- Query fan-out may retrieve multiple related subtopics.
- Treat `Google-Extended` as separate from ordinary Google Search crawling/ranking; reverify its exact current purpose before making Gemini-specific claims.

## Microsoft Bing / Copilot

**Verified:** 2026-09-24  
**Primary sources:**
- https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
- https://blogs.bing.com/webmaster/July-2025/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search

Current baseline:
- Bing Webmaster Tools AI Performance reports citations across Microsoft Copilot, Bing AI summaries, and select partner integrations.
- Bing recommends sitemaps plus accurate `lastmod` and IndexNow for fresh discovery.
- Do not interpret citation counts as rank/authority by themselves.

## Perplexity

**Verified:** 2026-09-24  
**Primary source:** https://docs.perplexity.ai/docs/resources/perplexity-crawlers

Current baseline:
- `PerplexityBot` -- automatic search crawler used to surface/link websites in Perplexity search results.
- `Perplexity-User` -- user-directed fetcher, separate from automatic crawling and foundation-model training.
- Perplexity publishes current IP ranges and recommends combining User-Agent plus IP verification for WAF allow rules.
- Perplexity documents that `Perplexity-User` generally ignores robots.txt because the fetch is user-requested. Keep that behavior separate from `PerplexityBot`.

## xAI / Grok

**Verified:** stale/verify-on-use  
**Primary domains:** https://x.ai/ and https://help.x.com/

Verify:
- current live web-search behavior
- X search integration
- whether xAI publishes dedicated crawler/robots controls

If no official dedicated crawler guidance exists, report that as undocumented. Do not invent a Grok crawler rule.

## Meta AI

**Verified:** stale/verify-on-use  
**Primary domains:** https://about.fb.com/ and official Meta developer/help properties

Verify:
- current web-grounding/search behavior
- any public crawler/user-agent guidance
- any webmaster controls relevant to AI answers

Do not infer ranking rules from Meta's general crawler ecosystem.

## Brave Search / AI retrieval infrastructure

**Verified:** stale/verify-on-use  
**Primary domains:** https://brave.com/ and https://search.brave.com/

Verify:
- current independent-index behavior
- crawler documentation
- Search API/LLM-context products
- robots behavior and publisher controls

Brave can matter indirectly when third-party AI products use its search APIs.

## Other systems

For DeepSeek, Mistral, You.com, Phind, Tavily-backed agents, new AI browsers, or search APIs:

1. determine whether the product has live web search/retrieval
2. identify the retrieval/search provider if publicly documented
3. identify official crawler/user-agent controls if any
4. distinguish the model vendor from the retrieval provider
5. mark undocumented architecture **Unknown**

## Evidence record

Capture these fields for each platform actually audited:

| Field | Value |
|---|---|
| Product | |
| Search/retrieval source | |
| Search/retrieval crawler | |
| User fetcher | |
| Training crawler | |
| Robots control | |
| Webmaster/indexing tool | |
| Citation/reporting tool | |
| Official source | |
| Verified date | |
| Confidence/notes | |
