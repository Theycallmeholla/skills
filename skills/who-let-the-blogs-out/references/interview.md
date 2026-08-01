# Interview

Captures the author's real stance, evidence, specifics, voice, and boundaries for one topic, returning an Opinion Packet at `posts/<slug>/packet.md`, every measurable specific filed as a dated vault fact, and a grown opinion bank.

**Reads:** `clients/<c>/opinion-bank.md` · `clients/<c>/brand.md` · `clients/<c>/facts.json`
**Writes:** `posts/<slug>/packet.md` · `clients/<c>/opinion-bank.md` · `clients/<c>/facts.json` · `posts/<slug>/post.json` (status → `interviewed`) · `registry.json`
**Stops at:** Never drafts, not even a sample sentence. Never researches the SERP — that's `brief`. Never invents an answer the author didn't give; "no take on that" is recorded as a gap, honestly.

This is the command the doctrine's first belief depends on. Everything `write` is allowed to say in the author's voice traces back to a packet line captured here. A thin interview doesn't produce a thin article — it produces an article that has to fabricate to sound confident.

---

## 1. Load the bank

Read `opinion-bank.md`, `brand.md`, and `facts.json` for the client before asking anything.

If `.blog/` doesn't exist, say so and point at `brand`. Don't create a partial tree. If the client exists but has no bank yet, start from `assets/opinion-bank-template.md` — the first interview for a client legitimately covers the author-profile questions that later ones skip.

Then build two lists and keep them in front of you for the whole interview:

- **Already answered** — positions, stories, voice fingerprints, and boundaries in the bank that touch this topic, plus any live `facts.json` entries relevant to it.
- **Genuinely open** — what this topic needs that the bank doesn't have.

**Never re-ask what the bank already answers.** Show what's on record and ask "still true? anything new since?" This is not politeness. An author who gets asked the same question a third time learns that the interview is a form that ignores them, and starts skipping it — at which point the bank stops growing and the whole system degrades to a generic content generator with extra steps. Confirming takes one line and produces the dated supersede entries that make the bank valuable.

If a relevant fact is past its `reverifyBy`, surface it during the interview: *"You told me in March that a full rebuild runs 6–8 weeks (F-012). That's due for a re-check — still the number you'd quote?"* Report the staleness; don't silently repair or delete the entry.

---

## 2. Interview

Open with the topic, not the process. Don't explain the methodology or preview how many questions there are. First message: a one-line frame — *"Before I write this as you, I want your actual take — a few questions"* — the on-record summary if the bank has one, and the first batch.

### Cadence

- **8–12 questions total** for a post, asked in **batches of 2–3.** Twelve at once reads like a tax form and produces short, tired answers; two or three reads like a conversation and produces stories.
- **Roughly a third of the interview is unscripted follow-up.** When an answer contains a story fragment, a strong verb, a number, or an emotion, chase it before returning to the script. *"You said the client 'panicked' — what happened?"* beats the next scripted question every time. Behave like a good podcast host, not a form.
- **Never ask** anything the bank already answers (confirm instead), anything answerable from `brand.md`, or anything about SERP, competitors' rankings, or keywords — that's `brief`'s job and asking it here trains the author to expect homework.
- **Stop** when answers start repeating the bank, when replies shrink to one line, or when you have a thesis plus two pieces of first-hand evidence plus the boundaries. A short interview with two great stories outranks a complete one with none.

### Question bank

Pick and adapt — never read these verbatim, and never work through a category the bank already covers.

**Stance**
- If a client asked you point-blank about [topic] over coffee, what would you tell them?
- What's your one-sentence position on [topic]?
- Where do you land on [the main controversy within the topic]?

**Experience and stories**
- Tell me about a time this came up with a real client or project. What happened?
- What's a mistake you made — or watched someone make — related to this?
- What result are you proudest of that's relevant here? Rough numbers welcome.
- What did you believe about this a few years ago that you've since changed your mind on?

**Contrarian takes**
- What does the standard advice on [topic] get wrong?
- What's something you believe about this that would annoy other people in your industry?
- If you read your competitors' articles on this, what would make you roll your eyes?
- What do prospects constantly arrive believing that you have to un-teach?

**Specifics**
- What tools, vendors, or methods do you actually use for this? Any you'd warn people off?
- What numbers do you use in real conversations — prices, timelines, thresholds, failure rates?
- Where's the line? When is X worth it versus not? What's the cutoff?

**The reader**
- Who do you picture reading this? Describe the actual person, not a demographic.
- What are they afraid of or burned by? What have they already tried?
- What question do they ask you in real life that this article should answer?

**Boundaries**
- Anything you do NOT want said under your name — claims, promises, guarantees?
- Competitors, vendors, or clients to avoid naming?
- Any position you hold privately but don't want published?

**Voice**
- How would you explain this to a friend at dinner — what analogy would you reach for?
- Any phrases or expressions you find yourself repeating with clients?
- Read this sentence: [sample sentence about the topic]. Would you ever say that? How would you say it?

**Business angle**
- Why does your business want this article to exist?
- What should a reader do right after finishing it?
- Which of your services does this naturally lead to — or is this pure goodwill?

### Pushing past the first answer

First answers are safe and general. The second answer is the article.

- "It depends" → *"What does it depend on? Walk me through the fork."*
- A generality ("communication matters") → *"What's a moment where that was true?"*
- A hedge ("usually", "often") → *"How often? Ballpark is fine."*
- Received wisdom → *"Do you actually believe that, or is that just what everyone says?"*
- A number in passing → *"Where does that number come from — your own jobs, or something you read?"* The answer decides whether it becomes a first-hand vault fact or a claim for `verify`.
- A story with a real client in it → *"Can I name them, or should this be anonymized?"* Record the answer with the story.

Mirror their language back. If they say "franken-site" or "the phone has to ring," those exact phrases go in the packet's voice notes verbatim. Never translate their words into cleaner marketing language mid-interview — you'll train them to talk like a brochure, and the voice you were hired to capture disappears in the first five minutes.

### Red flags in your own conduct

- The author is answering in one-liners → your questions are too broad, or too many at once. Narrow and slow down.
- You're paraphrasing their answers into smoother prose in the packet → stop; quote them.
- You asked something the bank already answers → apologize in half a sentence, confirm instead of re-asking, and move on.
- Nothing about the planned article has changed → you're performing an interview, not conducting one. Ask the contrarian and boundary questions with more teeth.

---

## 3. Compile the packet

Write `posts/<slug>/packet.md` with exactly these sections, in this order:

```markdown
# Opinion Packet — <topic>
Client: <client-slug> · Post: <post-slug> · Interviewed: YYYY-MM-DD

## Thesis
## Defensible stances
## First-hand evidence
## Specifics
## Voice notes
## Boundaries — do not say
## Gaps
## Suggested angle
```

- **Thesis** — one sentence, the author's position, in their words.
- **Defensible stances** — claims they'd defend in a room. Include the contrarian ones; those are what make the piece pass the 500-companies test.
- **First-hand evidence** — stories, projects, mistakes, results, with the anonymization the author asked for. This section is the whitelist `write` draws from for anything phrased as experience; if it isn't here or in the vault, it can't be implied.
- **Specifics** — tools, vendors, methods, and the fact IDs for everything measurable. See below.
- **Voice notes** — exact phrases, analogies, and rhythms, quoted. `write` and `review` both load `voice-and-tells.md`; this section is the client-specific overlay on it.
- **Boundaries — do not say** — verbatim, unsoftened.
- **Gaps** — what the author had no take on, phrased as the open question.
- **Suggested angle** — one paragraph for `brief` to argue with, not an outline.

### Numbers leave the prose and become facts

Every specific with a number, price, timeline, threshold, or measurable result gets written to `clients/<c>/facts.json` as a vault entry — not typed into the packet's prose and not into the bank.

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

Then the packet's Specifics section references it: *"Floor price for a rebuild — F-018. Won't quote below it."*

The reason is that a number in prose is invisible to every later command. A number in the vault has an owner, a date, and an expiry, so `refresh` can answer "which published posts assert a price the author changed in March?" without re-reading a single draft. A price buried in a packet paragraph is stale the moment it changes and nobody ever finds out. Machine-checkable staleness is the entire payoff of the extra step.

Rules for writing vault entries here:

- Allocate IDs monotonically per client from the existing `facts.json`. Never reuse or renumber, not even to close a gap.
- `source: first-hand` only when the number comes from the author's own work. If they're repeating something they read, it does not enter the vault as first-hand — note it in the packet as needing verification and let `brief` put it in the claim ledger for `verify` to source. Interview does not research; a number laundered through an interview is still unsourced.
- Pick `kind` from the closed list in `state.md`: `statistic` · `price` · `timeline` · `threshold` · `tool` · `result` · `credential`.
- `verifiedOn` is today. Set `reverifyBy` by decay rate — prices and platform behaviors 12 months, process timelines and thresholds 12–24, physical or process facts longer but still dated.
- Use `status: qualified` when the author hedges ("usually around three weeks, but it's been five"). A qualified fact with the hedge preserved in `statement` beats a false precision.
- Add this post's slug to `usedIn`.

---

## 4. Update the bank

Move anything durable into `clients/<c>/opinion-bank.md` — standing positions, contrarian takes, war stories, voice fingerprints — dated `YYYY-MM`, in the author's wording. One-off details specific to this article stay in the packet.

Two rules from `state.md` that carry the weight:

- **Never delete a superseded position.** Mark it superseded with the date and add the new one beneath. A changed mind is the best article material an author has, and deleting it destroys the only record that it changed.
- **Numbers don't live here.** The bank's Specifics section holds tools, vendors, and methods; anything measurable is a fact ID reference.

**Boundaries go in both places.** The packet's boundary list protects this post; the bank's `Boundaries — never publish` section protects every future one, because `review` checks each draft for a client against the bank's list, not against whichever packet happens to be at hand. A boundary recorded only in one packet is a boundary the system forgets by the next article.

Add a line to the Topic log: date, topic, packet path. Then update `registry.json` — `bankEntries` and `updated` on the client, and the post's row.

---

## 5. Hand off

Set `post.json` `status` to `interviewed` and `updated` to today, and update `registry.json` in the same operation so the menu doesn't recommend an interview that already happened. If no post record exists yet — the interview was run without `plan` — create `post.json` at the reserved slug with `status: interviewed` and whatever identity fields are known, and say that keyword and intent are still unset for `plan` or `brief` to fill.

Close by naming the next command: `who-let-the-blogs-out brief <slug>`.

### When the author isn't available

Scheduled runs and no-response sessions happen. Build the packet from the bank alone, mark every section that had no interview behind it, and list the questions you would have asked in Gaps. Do not fill a single answer on the author's behalf, however obvious the answer seems — writing a plausible stance into a packet is worse than leaving it blank, because `write` treats packet contents as things the author actually said. That's the exact failure this whole command exists to prevent. Say plainly that the packet is bank-derived and un-interviewed, and that the article's original-value score will reflect it.

### When the interview changes the premise

If the author's real opinion contradicts the requested angle, or the topic turns out to be wrong — they think the keyword targets a question nobody asks, or their honest take is "we don't do this and here's why" — raise it before handing off. Put it in the packet's Suggested angle and say it in chat.

An interview that can't change the article is theater. The whole point of asking first is that the answers get to move something.

---

## Output

Two artifacts and one chat response.

**Files:** `posts/<slug>/packet.md` in the eight-section order above; new and updated entries in `clients/<c>/facts.json`; updated `clients/<c>/opinion-bank.md`; `posts/<slug>/post.json` at `interviewed`; `registry.json`.

**Chat response**, in this order:

1. **Thesis** — one line, quoted from the author.
2. **Captured** — counts: stances, first-hand stories, voice notes, boundaries.
3. **New facts** — each new ID with its statement and `reverifyBy`, one line each.
4. **Bank changes** — new entries, and any position marked superseded, with dates.
5. **Gaps** — the open questions, plainly, with a note that those sections will be sourced from research in a neutral voice.
6. **Premise check** — anything the interview surfaced that should change the planned article, or "nothing — the angle holds."
7. **Next** — `who-let-the-blogs-out brief <slug>`.

Keep it to a screen. The packet is the deliverable; this is the receipt.

## Confirm and stop

Never draft, never research the SERP, and never write an answer the author didn't give — record it as a gap instead, because a gap is a question you can go ask and a fabrication is a liability someone has to catch.
