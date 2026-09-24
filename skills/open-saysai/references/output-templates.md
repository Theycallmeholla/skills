# Output Templates

## Full/platform audit

### Executive finding
State the largest material reason the site is likely to be underused by AI retrieval systems, then the next 2-4 issues. Do not lead with cosmetic metadata.

### Platform access matrix

| Platform | Retrieval path | Robots | HTTP/WAF | Index/citation evidence | Action |
|---|---|---|---|---|---|
| ChatGPT | ... | Accessible / Blocked / Partial / Unknown | ... | ... | ... |
| Claude | ... | ... | ... | ... | ... |
| Google AI | ... | ... | ... | ... | ... |
| Copilot/Bing | ... | ... | ... | ... | ... |
| Perplexity | ... | ... | ... | ... | ... |

Keep training controls in a separate note/column only when relevant.

### Priority findings
Use P0, P1, P2, Experimental. For every item include:
- **Problem**
- **Evidence**
- **Consequence**
- **Exact fix**

### Retrieval/source readiness
Use specific page examples. Cover passage structure, source evidence, first-party information gain, entity clarity, freshness, and crawlable HTML.

### Content/source opportunities

| Opportunity | Why an AI would need it | Source advantage | Suggested asset |
|---|---|---|---|

### Prompt visibility
If tests ran, show actual results. If not, show the exact test suite and label it **Not run**.

### Measurement
Name the concrete dashboard/log/source and what it measures.

### Portable packet
Always append/save the `ai_visibility_packet` defined in `ai-visibility-packet.md`.

## Page audit

1. **Verdict** -- whether the page is a strong retrievable source and why.
2. **Cleanly extractable evidence** -- strongest passages/data.
3. **Retrieval failures** -- buried answers, vague headings, missing context, unsupported claims, render issues.
4. **Exact rewrite targets** -- sections to change.
5. **Source-worthiness gap** -- unique information missing.
6. **Technical issues** -- only observed issues.

## General strategy

When no site is supplied, explain:

1. discovery/index ecosystem
2. training vs retrieval distinction
3. crawl/index foundations
4. passage-level retrieval design
5. first-party information gain
6. entity/corroboration
7. measurement/prompt testing
8. low-priority/experimental tactics

Do not tailor to a specific company unless the user asks.
