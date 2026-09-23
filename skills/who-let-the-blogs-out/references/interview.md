# Interview

Captures what only the author knows — their stance, their real examples, their process, their boundaries — and returns an Opinion Packet at `posts/<slug>/packet.md`, measurable specifics filed as dated vault facts, and any durable positions added to the opinion bank with provenance.

**Reads:** `clients/<c>/opinion-bank.md` · `clients/<c>/brand.md` · `clients/<c>/facts.json` · `posts/<slug>/post.json`
**Writes:** `posts/<slug>/packet.md` · `clients/<c>/opinion-bank.md` · `clients/<c>/facts.json` · `posts/<slug>/post.json` (status → `interviewed`) · `registry.json`
**Stops at:** Never drafts. Never researches the SERP — that's `brief`. Never invents an answer the author didn't give. Never writes an opinion-bank entry from inference.

Load `references/governing-rules.md` first. Rules 5 (provenance), 6 (editorial autonomy), 8 (plain language), and 10 (workflow adaptation) all land hardest here.

---

## The job

**Collect what you cannot get any other way.** That is the entire scope:

- the author's **direct stance** on the topic
- relevant **first-hand experience**
- **actual examples** from their work
- **concrete numbers or details** where they can safely be given
- **business-specific process** — how they actually do the thing
- **useful boundaries** — what must not be said under their name

Everything else — structure, emphasis, what to lead with, whether the company appears in the body, what a section should be called — is yours to decide. See Rule 6. Asking about those things is not thoroughness; it is handing your job back.

---

## The question rules

These are hard limits, not guidance.

**Maximum 3 questions at once. Prefer 1 or 2.**

**Every question must pass the materiality test:**

> If the user answers this, will the article materially improve or change?

If no, do not ask it. Not "ask it later," not "ask it in a smaller form." Do not ask it.

**Every question must be plain enough to need no explanation afterward.** If your next message would have to explain what you meant, the question was wrong. Rewrite it before sending, not after.

**Ask about the reader and the work, never about the machinery.** The author is an expert on their business. They are not an expert on your editorial reasoning, your research findings, your framing anxieties, or what the skill's rules require. A question that requires them to decode what you are thinking is a bad question no matter how carefully it is worded.

### Question anti-patterns, with the actual failures

Each of these was really asked in a real session. Each is banned.

| Banned | Why it fails | Instead |
|---|---|---|
| "This post hands the reader a checklist they could use to reject YOU. Comfortable?" | Abstract, adversarial, asks them to model your worry. Real answer received: *"huh what do you mean?"* | Don't ask. Decide whether the company appears, per Rule 6. |
| "Should the post answer its own checklist about Cursive?" | A routine editorial decision dumped on the user. Real answer: *"WHAT ARE YOU SAYING???? I DONT UNDERSTAND WHAT YOU MEAN"* | Decide it. If Cursive is a real, factual example of the thing, use it. |
| "Who's right?" (author vs. a source) | Manufactures a conflict, then makes the author adjudicate it. Real answer: *"Google says the OPPOSITE??? WHAT??"* | Resolve the source reading yourself under Rule 3, and only raise it if it genuinely blocks the thesis. |
| "Does that distinction change what you'd tell a client?" | Asks them to reason about your research finding. Real answer: *"Bro this is still confusing as fuck to me."* | Ask what they tell clients. Full stop. Don't attach your finding to it. |
| "Before I told you that, what would you have said?" | Adversarial and useless — it tests them instead of collecting anything publishable. | Ask what they'd say now, once, plainly. |
| "Do you actually manage Google Business Profiles?" when the state already says so | Re-asking a known fact teaches the user the system doesn't read its own files. | Read the bank and the vault first. Confirm in one line at most, or skip. |
| "Someone finishes this post. What do you want them to do?" with option *"Book a call, bring the proposal"* | Option text written in your shorthand, not theirs. Real answer: *"Send us a pitch? wtf does that even mean? what pitch?"* | Write options in the author's own vocabulary, or ask open. |

### What a good question looks like

Concrete, answerable in one breath, and the answer is publishable material:

- "Google recommends checking a provider's experience. What experience would you tell a business owner actually matters?"
- "A client asks whether they have to respond to all their reviews. What do you tell them?"
- "Have you taken over a profile from someone else? What did you find?"
- "What do you charge for this, roughly, or what's the floor?"
- "What's the part of this that clients always get wrong?"
- "Anything about this you don't want said under your name?"

Note what these have in common: each one is a question the author could be asked at a bar by a customer. None requires knowing what a packet is.

### Multiple-choice options

When you offer options, each one must be a position **the author might actually hold**, written in **their vocabulary**, and none may be a straw man or a restatement of your own theory. An option list is a shortcut for them, not a survey of your hypotheses.

If you cannot write four honest options, ask open. Two honest options beat four padded ones.

---

## Two modes, decided by the argument

| Invocation | Mode |
|---|---|
| `interview <client-slug>` — no post | **foundational.** One deep session per client, across their whole field. No packet is written. |
| `interview <post-slug>` | **per-topic.** The session this file otherwise describes. Writes a packet. |

A slug matching both a client and a post is a real ambiguity — ask once.

### Foundational mode

Run once per client, at onboarding. Without it the bank grows one article at a time and every interview starts near-empty.

**What changes:** longer — 20 to 30 questions is normal, still in batches of **at most 3**. Everything durable goes to the bank with IDs and provenance. **No packet is written**; `post.json` isn't touched and `registry.json` gets `bankEntries` and `updated` on the client row only.

**Say the cost once up front:** this is an hour, before any article exists. Worth it for a client you will write for repeatedly; not worth it for one post.

---

## 1. Load the state, then work out what is actually open

Read `opinion-bank.md`, `brand.md`, `facts.json`, and the post record before asking anything.

If `.blog/` doesn't exist, say so and point at `brand`. If the client exists but has no bank, start from `assets/opinion-bank-template.md`.

Build two lists and keep them in front of you:

- **Already answered** — positions, stories, voice fingerprints, boundaries, and live facts that touch this topic.
- **Genuinely open** — what this topic needs that the state doesn't have, filtered through the materiality test.

**Never re-ask what the state already answers.** Not in a fresh phrasing, not as a "confirmation" that is the same question with a preamble. If a bank entry or vault fact covers it, it is covered. Where something is genuinely dated and material, surface it in one line — *"You said 6–8 weeks for a rebuild back in March. Still right?"* — and move on.

**When the bank already covers the topic, the interview may be one question or none.** Under Rule 10 this is the correct outcome, not a degraded one. Say what you already have, ask only what is open, and go. Do not run a ceremonial round to justify the command.

The one thing you may not do is **build a packet from the bank alone while pretending it was interviewed.** If nothing was asked, the packet says so in its provenance line.

---

## 2. Ask

Open with the topic, not the process. No methodology preamble, no question count, no explanation of what a packet is.

First message: one line of frame — *"Before I write this as you, I want your actual take"* — plus the first batch of at most three.

### Cadence

- **As few questions as get the job done.** For a well-stocked bank that may be two. For a new topic with no coverage, six to ten total, in batches of two or three. There is no completion target — a short interview with two real examples beats a complete one with none.
- **Chase what is alive.** When an answer has a story fragment, a number, or heat in it, follow that instead of the next scripted question. *"You said the client panicked — what happened?"*
- **Stop** when you have a stance, one or two pieces of first-hand evidence, and the boundaries. Not when a category list is exhausted.

### If the user shows confusion, Rule 8 fires immediately

Signals: "what do you mean" · "I don't understand" · "wtf are you saying" · all-caps · a question that hands your own jargon back to you.

The response is **shorter, not longer**:

1. Drop the current question. Do not re-explain it.
2. Say the concrete thing in one line.
3. Ask one simple question, or none.

If two consecutive answers are confusion rather than content, **stop asking**, write the packet from what you have, mark the rest as gaps, and move on. Confusion is a signal that the questions are wrong, not that the author is unhelpful.

### If the user corrects you, Rule 2 fires immediately

Apply the correction, restate the thesis in one sentence if it genuinely changed, and continue. Do not re-litigate. Do not spend the next batch exploring the disagreement.

If the correction lands on the article's thesis, **write it into the packet's `## Thesis` section verbatim in the same turn** — that section is what `brief` and `write` treat as authoritative, and a correction that lives only in chat is a correction that gets lost at the next command.

### The question bank

Pick and adapt. Never read verbatim. Never work through a category the state already covers.

**Stance**
- If a client asked you about [topic] over coffee, what would you tell them?
- What's your one-sentence position on [topic]?

**Experience and examples**
- Tell me about a time this came up with a real client. What happened?
- What's a mistake you made, or watched someone make, here?
- What result are you proudest of that's relevant? Rough numbers fine.
- What did you used to believe about this that you don't anymore?

**Specifics and process**
- What tools or methods do you actually use for this?
- What numbers do you use in real conversations — prices, timelines, thresholds?
- Where's the line? When is this worth it versus not?
- Walk me through how you'd actually do this for a client.

**The reader**
- Who do you picture reading this? The actual person.
- What have they already tried that didn't work?
- What do they ask you in real life that this should answer?

**Boundaries**
- Anything you do NOT want said under your name?
- Anyone — competitor, vendor, client — to avoid naming?

**Business purpose** *(feeds priority 4; capture it or `brief` guesses)*
- Why does the business want this article to exist?
- Which service does this lead to, or is it goodwill?
- What should a reader do right after finishing it?

**Disagreement questions are optional and go last.** "What does the standard advice get wrong?" is a fine question when the author has a real objection waiting. It is not a required beat, and an author with no quarrel is not a thin interview — Rule 4. Never phrase it as a challenge to the author, and never use their answer to overturn the thesis they already gave you.

### Pushing past the first answer

First answers are safe. The second is the article.

- "It depends" → *"On what? Walk me through it."*
- A generality → *"When was that true? What happened?"*
- A hedge ("usually") → *"How often, roughly?"*
- A number in passing → *"Is that from your own jobs, or something you read?"* — this decides vault fact versus claim for `verify`.
- A story with a real client → *"Can I name them, or anonymize?"* Record the answer with the story.

Mirror their language back. Their exact phrases go in the packet verbatim. Never translate their words into cleaner marketing language.

### Red flags in your own conduct

- Answers are one-liners → your questions are too abstract. Get concrete.
- You are about to explain a question you already asked → the question was wrong. Replace it.
- You are asking them to choose between editorial options → Rule 6. Decide it.
- You are asking them to react to your research finding → Rule 3. Resolve it yourself.
- You are paraphrasing their answers into smoother prose → stop; quote them.
- You are asking a fourth question in one batch → cut to three.

---

## 3. Compile the packet

Write `posts/<slug>/packet.md` with exactly these sections, in this order:

```markdown
# Opinion Packet — <topic>
Client: <client-slug> · Post: <post-slug> · Interviewed: YYYY-MM-DD

## Thesis
## Business purpose
## Defensible stances
## First-hand evidence
## Specifics
## Voice notes
## Boundaries — do not say
## Gaps
## Suggested angle
```

- **Thesis** — one sentence, the author's position, **in their words**, quoted where they gave one. This is the sticky thesis under Rule 1. If the user stated it directly, it is verbatim here and nothing downstream may replace it.
- **Business purpose** — who this is for, which service it connects to, what the reader should do next. Feeds priority 4. If the author didn't say and it is obvious from `brand.md`, write it and mark it inferred; if it is genuinely ambiguous, that is one of your questions.
- **Defensible stances** — claims they'd defend in a room. Include contrarian ones **only where the author actually holds them.** A stance list with nothing contrarian in it is a normal outcome.
- **First-hand evidence** — stories, projects, mistakes, results, with the anonymization asked for. This section is the whitelist `write` draws from for anything phrased as experience.
- **Specifics** — tools, methods, and the fact IDs for everything measurable.
- **Voice notes** — exact phrases and rhythms, quoted.
- **Boundaries — do not say** — verbatim, unsoftened.
- **Gaps** — what the author had no take on, phrased as the open question. Honest gaps are fine and are recoverable.
- **Suggested angle** — one paragraph for `brief` to work from. It elaborates the thesis; it never replaces it.

### Attribution inside the packet

**Every quoted line must be something the user actually said or selected.** Under Rule 5, that includes material the user pasted for you to read — a documentation excerpt, another tool's output, an article they forwarded. Those are the *source's* words. They are recorded as research or claims, never as *"in his words."*

When you are unsure whether a line came from the author or from something they pasted, it does not go in as a quote. Paraphrase it as research, or leave it out.

### Numbers leave the prose and become facts

Every specific with a number, price, timeline, threshold, or measurable result gets written to `clients/<c>/facts.json` as a vault entry, and the packet references the ID.

```json
{
  "id": "F-018",
  "statement": "We won't take on a rebuild under $6k — below that the discovery alone eats the margin.",
  "value": "$6,000",
  "kind": "price",
  "source": "first-hand",
  "sourceUrl": null,
  "verifiedOn": "2026-08-01",
  "reverifyBy": "2027-08-01",
  "status": "verified",
  "usedIn": ["local-seo-location-pages"]
}
```

Rules: allocate IDs monotonically per client, never reuse. `source: first-hand` **only** when the number comes from the author's own work — a number they are repeating from something they read is a claim for `verify`, not a vault fact. Pick `kind` from the closed list in `state.md`. `verifiedOn` is today; set `reverifyBy` by decay rate. Use `status: qualified` when the author hedges, preserving the hedge in `statement`.

---

## 4. Update the bank — provenance is mandatory

Move durable material into `clients/<c>/opinion-bank.md`: standing positions, real contrarian takes, war stories, voice fingerprints, boundaries. One-off details stay in the packet.

### Rule 5 is enforced here or nowhere

**No entry may be written from your inference.** Each entry needs one of four provenance values, recorded in the entry:

| `provenance` | What it means |
|---|---|
| `stated` | The author wrote the position themselves. |
| `selected` | The author picked an option that stated the position. |
| `confirmed` | You proposed a wording and they clearly agreed. |
| `demonstrated` | They gave an example that plainly carries the position. |

Not acceptable, ever: your inference · a research conclusion · your own recommendation · your reading of their confusion · "probably believes" · silence · absence of objection · **anything the user pasted for you to read.**

**The failure this prevents, exactly as it happened.** The author pasted a block of research he had gotten elsewhere, so the skill could read it. Inside that paste was the sentence *"I would not translate that into 'replying to every review increases rankings.' Google does not make that claim in its guidance."* The skill wrote that into the bank as position `P-002`, attributed to the author, annotated **"Drew the line himself, unprompted."** He had not. He was pasting a source. That entry would have shaped every future article for this client, and would have been quoted back at him as his own belief.

**When in doubt, don't write it.** A missing entry costs one question next time. A fabricated one is permanent.

### Entry format

IDs are monotonic per client, never reused, never renumbered. `P-###` for positions and contrarian takes; `S-###` for war stories.

```markdown
### The 40-page rollout that got manually actioned (S-004, 2026-03)
*Provenance: stated — described unprompted during the 2026-03 location-pages interview.*

<the story, in the author's words>
```

The `Provenance:` line is required on every `P-` and `S-` entry. Voice fingerprints and boundaries get no IDs and no provenance line — nothing cites them individually and they are quoted material by construction.

### Two standing rules

- **Never delete a superseded position.** Mark it superseded with the date and add the new one beneath. A changed mind is the best article material an author has.
- **Numbers don't live here.** Anything measurable is a fact ID reference.

**Boundaries go in both places** — the packet protects this post, the bank protects every future one.

Add a line to the Topic log: date, topic, packet path. Then update `registry.json` — `bankEntries` and `updated` on the client, and the post's row.

---

## 5. Hand off

Set `post.json` `status` to `interviewed` and `updated` to today, and update `registry.json` in the same operation. If no post record exists — the interview ran without `plan` — create `post.json` at the reserved slug with `status: interviewed` and whatever identity is known.

### When the author isn't available

Build the packet from the bank alone, mark every section that had no interview behind it, and list the questions you would have asked under Gaps. **Do not fill a single answer on the author's behalf.** Say plainly that the packet is bank-derived and un-interviewed.

### When the interview changes the premise

If the author's real opinion contradicts the requested angle, raise it before handing off — in the packet's Suggested angle and in chat, in one or two plain sentences.

**This is not licence to change the thesis yourself.** Under Rule 1, the author's stated thesis stands until the author changes it. What you may do is name the conflict and stop. What you may not do is quietly reinterpret the request into something that resolves it.

---

## Output

**Files:** `posts/<slug>/packet.md`; new and updated entries in `clients/<c>/facts.json`; updated `clients/<c>/opinion-bank.md` with provenance on every new entry; `posts/<slug>/post.json` at `interviewed`; `registry.json`.

**Chat response — short, and free of machinery under Rule 9.** Load `references/reporting.md`. What belongs:

1. **The thesis**, one line, in their words.
2. **What you got** — in sentences, not counts. "Your stance on coverage, the profile-takeover pattern, and two boundaries."
3. **Anything genuinely open** that the article will have to source neutrally instead.
4. **The next step**, one line.

No ID lists. No "captured 4 stances, 1 story, 3 voice notes." No new-facts table. No bank-changes ledger. If the author asks what got saved, show them everything.

## Confirm and stop

Ask only what matters, at most three at a time, in plain words. Never draft, never research the SERP, never write an answer the author didn't give, and never put a position in the bank that the author did not actually take.
