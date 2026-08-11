# Swipe Deck for ChatGPT

Run the same recognition-first interview using ChatGPT's adaptive structured-input UI when available, with a compact chat fallback when it is not.

## Interaction model

1. Mine the user's prompt and remove questions already answered.
2. Name 5--7 concrete facets that control the decision.
3. Build a private pool of 40--80 short statements. Each statement must:
   - contain one idea
   - use 12 words or fewer
   - belong to one facet
   - be answerable as `Yes`, `No`, `Absolutely`, or `Not sure`
   - include deeper follow-ups for strong or uncertain reactions
4. Present one adaptive structured-input sequence. Use the platform's adaptive question widget when available. Ask one statement at a time with exactly these four options. Do not expose the full pool.
5. Re-rank after every answer:
   - `Absolutely` pulls deeper statements from that facet forward.
   - `No` prunes dependent statements and surfaces the opposite direction.
   - `Not sure` replaces abstraction with a concrete example or threshold.
   - `Yes` advances moderately without tunneling into one facet.
6. Stop when all important facets have at least three decisive answers and the remaining answers are predictable, or when the user stops.
7. Produce the brief below. Do not begin building the requested thing until the user approves the brief.

## Adaptive UI invocation

When ChatGPT exposes an adaptive structured-input widget, use it rather than asking a long questionnaire. Start with exactly one short statement and these options:

- Yes
- No
- Absolutely
- Not sure

Configure the adaptive sequence to continue for as many questions as needed. Keep each question tied to one concrete drafting or planning decision. Do not ask abstract category questions.

When no adaptive UI is available, send batches of eight numbered statements and ask the user to reply with compact verdicts such as `1Y 2N 3A 4?`. Continue without recapping between batches.

## Signal rules

Treat typed corrections and notes as stronger evidence than button selections. Preserve the user's wording. Contradictions are not noise -- surface a statement that forces the tradeoff.

Never pad the interview with easy confirmations. At least half the pool should plausibly receive `No`.

## Brief format

```markdown
# [Thing] -- what you actually want

**The shape of it** -- two or three sentences a stranger could act on

**Locked in** -- strong and repeated preferences

**Ruled out** -- rejected directions that would otherwise waste work

**Still fuzzy** -- unresolved or weak-signal areas

**The tension I'm reading** -- conflicting preferences and the recommended call

**First thing I'd do** -- one concrete next step
```

Mark inferences as inferences. Ask whether to proceed after presenting the brief.