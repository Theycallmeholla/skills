# Output Templates

## Full/platform audit

### Executive finding
Answer the central question: why would AI systems pass over this site as a source, and what would change that? Lead with a technical issue only if it is a verified blocker. Then give the next 2-4 issues. Do not lead with cosmetic metadata.

### Platform access matrix

| Platform | Retrieval path | Robots | Synthetic-UA HTTP | Access evidence tier | Search index evidence | AI citation evidence | Action |
|---|---|---|---|---|---|---|---|
| ChatGPT | ... | Accessible / Blocked / Partial / Unknown | ... | Synthetic UA / UA-attributed logs / Verified crawler / Webmaster tool | ... | ... | ... |
| Claude | ... | ... | ... | ... | ... | ... | ... |
| Google AI | ... | ... | ... | ... | ... | ... | ... |
| Copilot/Bing | ... | ... | ... | ... | ... | ... | ... |
| Perplexity | ... | ... | ... | ... | ... | ... | ... |

Search index evidence and AI citation evidence are separate columns because being indexed doesn't mean being cited. Mark AI citation evidence **Unknown / not tested** unless prompt tests or a citation report show it.

Keep training controls in a separate note/column only when relevant.

### Priority findings
Use P0, P1, P2, Experimental. For every item include:
- **Problem**
- **Evidence**
- **Consequence** -- which link of the visibility chain (reachable → indexed → retrieved → cited → recommended) it weakens
- **Exact fix**

### Recommended first action
The top finding by the audit-framework priority order. Name it and say why it outranks the others. List easier items separately as "quick win (parallel)."

### Retrieval/source readiness
Report the source-selection page review from `audit-framework.md`:

| Page | Type | Information-gain class | Passage lift test | Question it could win | Already answered by | Fix |
|---|---|---|---|---|---|---|

Then cover passage structure, source evidence, first-party information gain, entity clarity, freshness, and crawlable HTML using those pages as examples.

### Content/source opportunities

| Opportunity | Target question | Why an AI would need it | Source advantage | Suggested asset |
|---|---|---|---|---|

### Prompt visibility
If tests ran, show actual results. If not, show the exact test suite and label it **Not run**.

### Measurement
Name each concrete dashboard/log/source, what it measures, and what it misses.

### Coverage check
List each completion-gate dimension as Evaluated / Unknown / Out of scope, with a few words on the evidence or reason.

### Incidental site issues
Bugs found along the way that don't affect AI discovery, retrieval, or source selection. One line each. These are not findings.

### Portable packet
Always append/save the `ai_visibility_packet` defined in `ai-visibility-packet.md`.

## Page audit

1. **Verdict** -- whether the page is a strong retrievable source and why.
2. **Cleanly extractable evidence** -- strongest passages/data.
3. **Retrieval failures** -- buried answers, vague headings, missing context, unsupported claims, render issues.
4. **Exact rewrite targets** -- sections to change.
5. **Source-worthiness gap** -- unique information missing, the question this page could win, and who answers it now.
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
