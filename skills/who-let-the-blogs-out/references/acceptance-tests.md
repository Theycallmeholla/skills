# Acceptance Tests

Regression cases for the governing rules. Every one is drawn from a real failure in a live session — the transcript is the source, not a hypothetical.

**Run these against any change to `governing-rules.md`, `interview.md`, `evidence-rules.md`, `review.md`, `quality-rubric.md`, or `voice-and-tells.md` before shipping it.** A change that makes any test fail is a regression regardless of how much better the prose reads.

They are also the diagnostic set. When someone says "it did the thing again," find the test that covers it.

---

## Test 1 — Sticky thesis

**Setup.** User: *"I want a blog on why businesses should respond to Google reviews."* Research then finds that Google's local-ranking documentation names review count and rating but does not separately name reply rate as a ranking factor.

**PASS**
- The article still argues why businesses should respond.
- The SEO claim is qualified: *"Google names review count and rating as ranking inputs; it doesn't name reply rate, so don't buy a pitch that sells replies as an SEO play."*
- The finding appears as a section or a sentence, sized to what it is.

**FAIL**
- The article becomes *"Why responding to reviews doesn't help rankings."*
- The article becomes *"Two of the three reasons you were given are wrong."*
- The thesis in `packet.md` and the argument in `draft-vN.md` disagree.

**Rule:** 1. **Enforced by:** `brief` (thesis copied verbatim to frontmatter, angle must be compatible), `write` (self-check 0), `review` (Phase 4 thesis fidelity → `intent` at `high`).

---

## Test 2 — No fake contradiction

**Setup.** Source says: *"Instead of sending the same 'thank you' to everyone, focus on reviews where you can share a helpful update or answer a question."*

**PASS**
- *"Google recommends meaningful, personalized replies."*
- *"Google's objection is to the copy-paste, not to the coverage."*

**FAIL**
- *"Google says don't reply to every review."*
- *"Google discourages full response coverage."*
- *"Google contradicts the advice to answer all of them."*

**Rule:** 3, limit #3 — a scoped instruction never becomes a general prohibition. **Enforced by:** `evidence-rules.md` source-interpretation hierarchy; `review` Phase 4 source over-reach → `accuracy` at `high`.

**Related sub-case.** Source is silent on X. PASS: *"Google doesn't name X."* FAIL: *"X doesn't affect rankings."* (Limit #1 and #2.)

---

## Test 3 — User correction

**Setup.** The assistant has developed a contrarian angle across several turns. User: *"No. The post is about why responding matters."*

**PASS**
- The angle is replaced in the next message.
- One sentence at most restating the new understanding.
- Work continues immediately.
- Any state already written on the rejected reading — packet, brief, bank entry — is corrected in the same turn, with one line saying which file changed.

**FAIL**
- Any defense or explanation of the previous interpretation.
- Continued optimization of the rejected angle in later output.
- A fresh round of questions about the disagreement.
- An apology paragraph.
- State left carrying the rejected reading.

**Rule:** 2. **Enforced by:** `governing-rules.md` Rule 2; `interview.md` §2 correction handling.

---

## Test 4 — Opinion-bank provenance

**Setup.** During research the assistant concludes: *"Replies aren't an SEO play."* The user never states this position. In the real incident, the user **pasted a research summary** containing a sentence to that effect, so that the assistant could read it.

**PASS**
- Nothing is written to `opinion-bank.md`.
- The finding lives in `claims.json` or `research-vN.md`, with its real source recorded.
- If it matters for the article, it becomes a question for the next interview, recorded as a gap.

**FAIL**
- A `P-###` entry is created from assistant inference.
- A `P-###` entry is created from text the user pasted, attributed to the user.
- Any entry annotated *"drew the line himself, unprompted"* when the line came from a paste, a research finding, or a proposed option the user did not pick.
- Any entry with no provenance line.

**Rule:** 5. **Enforced by:** `interview.md` §4; `state.md` opinion-bank schema; `state.md` write rule 6.

---

## Test 5 — Simple interview

**Setup.** State already records that Cursive manages Google Business Profiles for paying clients (`F-015`, and the fact is current).

**FAIL question:** *"Do you actually manage Google Business Profiles?"*

**PASS**
- The question is not asked.
- If genuinely dated, one line: *"Still managing profiles for paying clients?"* — and nothing more.

**Also FAIL, from the same session:**
- Four or more questions in one batch.
- *"This post hands the reader a checklist they could use to reject YOU. Comfortable?"* (abstract, adversarial, requires decoding the assistant's worry)
- *"Does that distinction change what you'd tell a client?"* (asks the author to reason about the assistant's research finding)
- *"Who's right?"* (manufactures a conflict, then makes the author adjudicate it)
- Any question that needs a follow-up message to explain what it meant.
- Any option written in the assistant's shorthand rather than the author's vocabulary — the real one was *"Book a call, bring the proposal,"* answered with *"Send us a pitch? wtf does that even mean?"*

**Rule:** 6, 8, 10. **Enforced by:** `interview.md` question rules, materiality test, anti-pattern table.

---

## Test 6 — Editorial autonomy

**Setup.** The article is about how to choose someone to manage your Google Business Profile. Cursive provides that service.

**PASS**
- Cursive is used as a real example where it is factually apt — how they actually do the thing, what they'd tell a buyer to check.
- Every claim about Cursive traces to the packet, the vault, or `brand.md`.
- The decision is made and mentioned in one line, not asked about.

**FAIL**
- Asking the user whether Cursive is allowed to appear, absent any real ambiguity.
- *"Should the post answer its own checklist about Cursive?"*
- Deciding "Cursive stays out of the body until the CTA" on an article about Cursive's own service.

**Rule:** 6. **Enforced by:** `governing-rules.md` Rule 6; `write.md` experience section; `brief.md` cadence.

---

## Test 7 — Plain-language recovery

**Setup.** User: *"I don't understand what you're saying."* Or *"talk to me like I'm an idiot."* Or all-caps confusion.

**PASS**
- The next response is **shorter** than the last one.
- Concrete noun first, one idea at a time, no jargon.
- The mode persists for the rest of the session.
- After two consecutive confused replies during an interview, questioning stops and the work proceeds from what exists.

**FAIL**
- A longer explanation.
- More terminology than the previous message.
- Re-explaining the same question instead of replacing it.
- Reverting to the old register two messages later.

**Rule:** 8. **Enforced by:** `governing-rules.md` Rule 8; `interview.md` §2; `reporting.md` confusion mode.

---

## Test 8 — Proportionality

**Setup.** A user-supplied image has correct numbers but visually imperfect bar lengths.

**PASS**
- One sentence: *"The bar lengths don't match the labels. The numbers are right. I'll fix the bars or use it as-is."*
- Then one action.

**FAIL**
- Pixel coordinate measurement.
- Bar-track percentage calculation.
- An explanation of the implied axis.
- More than one request for approval.
- Any multi-turn investigation of a cosmetic issue.

**Escalation is permitted only for material factual error** — a chart whose numbers are wrong publishes a false claim and is worth stopping for.

**Rule:** 7. **Enforced by:** `governing-rules.md` Rule 7; `images.md` proportionality section.

---

## Test 9 — Workflow adaptation

**Setup.** The assistant presented a list of topic ideas. User: *"let's get started on the first one."*

**PASS**
- The topic is treated as selected.
- The slug is reserved, the post record written, and work moves to the next useful step — interview if nothing is on record for the topic, brief if the bank already covers it.
- If two first-hand facts are missing, those two questions get asked and then the work continues.

**FAIL**
- Re-running candidate generation.
- Re-presenting the list.
- Asking the user to confirm the choice they just made.
- Routing a command that carries intent to the bare no-argument menu.

**Rule:** 10. **Enforced by:** `plan.md` opening; `routing.md`; `SKILL.md` routing case 3.

---

## Test 10 — Internal machinery stays internal

**Setup.** Any command completes normally.

**PASS**
- *"Draft complete. One claim I couldn't independently verify — the 88% consumer figure. Cut it, or tell me where it came from."*
- *"Six of the competitor pages wouldn't load, so I'm less confident than usual about what's missing out there."*

**FAIL**
- *"C-004 unresolved, F-016 expires, registry 8, triads 6.09…"*
- Score tables in a default completion response.
- Finding IDs, fact IDs, position IDs, or media IDs in a default response.
- Status transitions, version bookkeeping, connector blocks, teardown ratios, or a file-by-file write manifest.
- The word "drift" said to a user.

**Always allowed:** everything, when the user asks for it. **Always required:** the state itself, written in full to disk, exactly as detailed as before.

**Rule:** 9. **Enforced by:** `reporting.md`; the output section of every command file.

---

## Test 11 — Original value without manufactured contrarianism

**Setup.** The draft is competent but generic. `review` raises an `original-value` finding.

**PASS**
- The fix names what to add: the author's real example, a number from the vault, the actual process, a clearer framework, a diagram.
- An article that agrees with the consensus and adds practitioner specifics scores as passing.

**FAIL**
- The fix is *"take a contrarian position."*
- `revise` closes the finding by reframing the article as an argument against a source.
- `review` penalizes `substance` because the draft agrees with the consensus.
- A stance appears in the draft that exists nowhere in `packet.md` or the opinion bank, and is scored as voice rather than as `fabrication`.

**Rule:** 4. **Enforced by:** `governing-rules.md` Rule 4; `quality-rubric.md` original value; `voice-and-tells.md`; `review.md` Phase 2; `revise.md` Phase 3 trap list.

---

## Test 12 — Business purpose is not sabotaged

**Setup.** The client sells reputation management. The article exists partly to support that service. Research surfaces a genuine nuance that qualifies one common reason for the service.

**PASS**
- The nuance is written accurately and narrowly.
- The article still helps the reader the service is for, and still argues its thesis.
- `businessPurpose` is recorded in the brief and shapes which objections get answered and where the CTA goes.

**FAIL**
- The article ends up arguing against a core reason businesses buy the service, because a clever angle presented itself.
- The nuance is suppressed or softened to protect the sale.

Both failures are the same mistake in opposite directions: letting the commercial frame and the evidence fight instead of holding both. Truth outranks purpose; purpose outranks cleverness.

**Rule:** 2 and 4 in the priority order. **Enforced by:** `brief.md` Phase 5b; `write.md`.

---

## How to run these

There is no automated harness — these are judgment tests over a conversation, and a script that could score them would have to be able to write the articles.

Run them by walking a real or simulated session against the rule files and checking each PASS/FAIL list. Two shortcuts that catch most regressions cheaply:

1. **Grep for the retired doctrine.** `500-companies test outranks` should appear nowhere. Any surviving instance is a Test 11 regression waiting to happen.
2. **Read the output section of every command file.** If any of them prints an ID, a score, or a count in its default response, that is a Test 10 regression.
