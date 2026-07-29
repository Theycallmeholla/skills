# Voice and AI-Tells

Generation-side rules for writing that survives close reading. Detection lists describe symptoms; these rules prevent them. Apply during Stage 3 drafting; run the checklist at the bottom during Stage 4 verification.

The governing principle: **no single phrase marks writing as AI — a cluster of patterns does, and the strongest tells are absences, not words.** No stance, no texture, no evidence trail, no audience awareness. Specificity is the tell-killer; lexicon fixes are cosmetics on top. Every article must pass two tests:

1. **The 500-companies test.** Could this article be published by 500 different companies after swapping the company name and city? If yes, rewrite — it has no voice and no value regardless of how clean it reads.
2. **Information gain.** Does the reader learn something not available on page one of the SERP? (Enforced by the research protocol; restated here because it is also the strongest anti-tell.)

## Point of view (most important)

- Take **at least one defensible stance** a competitor's article wouldn't publish: which option is overrated, which common advice fails in practice, which tradeoff most articles ignore. An expert risks being wrong; a content mill doesn't.
- Don't equal-weight weak positions. If one approach is better for most readers, say so and say for whom the exception applies.
- Replace hedges with conditions. Not "results typically vary" but "if your lot is under a quarter acre, skip this entirely." "Typically", "in most cases", "more often than not" are hedge-flags — each one should become a concrete condition or a confident claim.
- Measured criticism is allowed and valuable. Relentless positivity — every option an "exciting opportunity" — is a tell in itself.

## Texture and substance

- **Specifics over adjectives**: numbers, dates, prices, tool names, durations, edge cases. "Fast turnaround" is filler; "usually 4–6 business days, 10+ in March" is texture.
- Include at least one **edge case, failure mode, or tradeoff** a generalist wouldn't know — sourced from client evidence or verified research, never invented. This is what "shallow expertise" detection actually measures: correct terminology with all the hard parts avoided.
- **No placeholder-people anecdotes.** "Imagine Sarah, a small business owner..." is an instant tell. Use real, verifiable examples or none — the anti-fabrication rules in SKILL.md govern.
- **Audience calibration**: never define terms the intended reader already knows. Answer their actual objections instead. Explaining the obvious while ignoring the real question is a double tell.
- Banned filler: "Studies have shown" without a named, dated citation; "This is an important area"; "More research is needed"; precise-sounding claims with no source, date, or example attached.

## Rhythm and structure

- **Uneven on purpose.** Mix one-sentence paragraphs with five-sentence ones. Follow a long winding explanation with a short punchy claim. If every paragraph has the same length and internal shape (topic sentence → two supports → mini-conclusion), break the pattern.
- **Asymmetric sections.** Depth follows value: spend 400 words on the section where the real expertise lives and compress the obligatory ones. Five evenly-sized H2s read like quota-filling.
- **Prose-first.** Bullets only when items are genuinely parallel and scannable. Narrative wherever causality or judgment matters. If more than roughly a third of the article is list-form, convert some back to prose.
- **No signposted transitions.** "Moreover", "Furthermore", "Additionally", "Let's dive in", "But here's the thing", "It's worth noting" — delete the signpost and let the content connect. If two paragraphs don't connect without a signpost, the problem is the order, not the missing transition.
- **No summary conclusion.** Never restate the article; never "By understanding X, businesses can unlock Y and achieve long-term success." End on the CTA, a specific forward-looking point, or the sharpest claim — then stop.
- One brief aside is allowed where it earns its place. Rigid adherence to a symmetrical outline is its own tell.

## Constructions and tics (ration, don't just ban)

- "It's not just X — it's Y" contrast frame: banned.
- Rule of three ("saves time, boosts productivity, and increases ROI"): maximum one deliberate triad per article.
- Rhetorical-question openers: banned.
- Em dashes: powerful, currently a flagged tic — keep under roughly one per 300 words.
- Bold: only for genuinely load-bearing phrases. Bolding every other line reads generated.
- Uniform parallel bullets (every item "**Verb**: sentence"): vary the shapes or use prose.
- Colon-heavy sentence stacking: same rationing as em dashes.

## Lexicon (least important — fix last)

Banned outright: delve, tapestry, landscape (metaphorical), robust, leverage (verb), foster, navigate (metaphorical), underscore, pivotal, seamless(ly), nuanced, testament to, beacon, realm, plethora, multifaceted, game-changer/game-changing, revolutionize, unlock, unleash, empower, elevate, crucial, synergy, "in today's [anything]", "ever-evolving", "fast-paced digital world", "whether you're a X or a Y", "the ultimate guide to", "it's important to note/remember", "in conclusion", "ultimately" (as a wrap-up signal), "to sum up", "in essence".

This list is a moving target — models migrate to new safe words as old ones get flagged. The durable rule: **any sentence that could appear unchanged in any article on any topic gets cut or made specific.**

## What NOT to do

- **No fake typos or deliberate errors.** Manufactured mess is dishonest and hurts the client. Human texture comes from specificity and stance, not sloppiness.
- **No detector-chasing.** AI detectors are unreliable in both directions; Google penalizes scaled low-value content, not AI production. Optimizing to fool a classifier is optimizing for the wrong reader.
- **No forced sass.** Over-corrected "edgy" voice is as recognizable as omniscient-neutral. The target is a knowledgeable practitioner talking to a peer.

## Stage 4 tells checklist

Run against the finished draft; fix before delivering:

- [ ] 500-companies test passed — swap the name and the article breaks
- [ ] At least one real stance taken; no silly position given equal weight
- [ ] At least one edge case / failure mode / tradeoff covered
- [ ] Every "typically"-class hedge converted to a condition or confident claim
- [ ] No placeholder-name anecdotes; no "studies show" without a citation
- [ ] Paragraph lengths visibly uneven; sections asymmetric where value is asymmetric
- [ ] Under ~1/3 of the article in list form; bullets genuinely parallel
- [ ] No paragraph opens with a signpost transition
- [ ] Conclusion doesn't restate the intro; no "unlock long-term success" close
- [ ] ≤1 triad; em-dash and bold density spot-checked
- [ ] Zero banned-lexicon hits; no sentence that fits any article on any topic
- [ ] Basics the intended reader knows are not explained
