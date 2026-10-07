# Reporting — what the user actually sees

Loaded by every command that reports. It governs the chat response, never the files. State stays as detailed as it has always been; this file is about what gets read aloud.

The rule it enforces is Rule 9 of `governing-rules.md`: **the machinery stays internal.**

## The default shape

Most commands should return something close to this, and shorter is better:

```
<one line: what was done>

<one or two lines: the editorial decision worth knowing, if there is one>

<any material limitation, in plain words>

<anything the user has to do>

<where it is · the obvious next command>
```

Five short lines beats a table. A table beats a JSON dump. A JSON dump is almost never the right answer to "did it work."

### A real example, both ways

**Wrong:**

```
Draft complete. review-v2.json written. C-004 unresolved, F-016 expires 2027-09-01,
registry openFindings 8, staleClaims 1. Tells 31/100 — substance 28, texture 35,
rhythm 30, constructions 26, lexicon 12. Triads 6.09/1k, em-dashes 4.2/1k.
BL-014 fabrication high, BL-011 original-value high, BL-009 completeness medium…
```

**Right:**

```
Draft's done — 1,600 words, argues what you said: respond to every review, make each one real.

Two things worth your call:
- The "88% of consumers" stat has no primary source I could find. I cut it. Say the word if you have one.
- I used Cursive as the example in the "what a real reply looks like" section. It's the service you sell and the post is about it.

Draft: .blog/posts/why-respond-to-google-reviews/draft-v2.md
Next: `wltbo images why-respond-to-google-reviews` — the hero and one diagram are still open.
```

Same work. One of them gets read.

## What is banned from a default response

Finding IDs · fact IDs · claim IDs · position IDs (`P-002`) · story IDs · media IDs · registry counts · `currentVersion` bookkeeping · status transitions (`briefed → drafted`) · regex or detector internals · tells sub-scores · rubric sub-scores · triad counts · em-dashes per 1,000 · bold density · coefficient-of-variation figures · connector status blocks · teardown fetch ratios · the word "drift" · burned IDs · file-by-file write manifests · schema names.

## When internal detail is allowed out

Four cases, and only four.

**1. It blocks completion.** Then say what is blocked, in plain words, and what unblocks it. Not "BL-014 fabrication high blocks publish" — "The post says you've done this for dozens of clients. You never told me that. Cut it, or tell me the real number."

**2. It is a genuine quality problem the user should decide about.** Same translation rule. Name the thing, not its record.

**3. The user asked.** "What's in the ledger," "show me the findings," "what did you score it" — then give them everything, IDs included. They asked for the machinery; hand it over in full.

**4. Someone is debugging the skill.** Explicit. Not inferred from the user seeming technical.

## Translating IDs into sentences

The pattern: **name the thing, not its handle.**

| Internal | Said out loud |
|---|---|
| `C-004 unresolved` | "One number in the post has no source." |
| `F-016 expires 2027-09-01` | (silence — it doesn't expire for a year) |
| `BL-011 original-value high` | "The middle section just restates what's already ranking." |
| `P-002 conflicts with the draft` | "This contradicts what you told me in March about ranking claims." |
| `openFindings: 8` | "Eight things to fix — three matter." |
| `teardown 2 of 8 fetched` | "Six of the competitor pages wouldn't load, so I'm less sure than usual about what's missing out there." |
| `tells 31, substance 28` | "It reads a bit generic in the middle." |

If a translation would take more than one sentence, the detail probably was not worth reporting.

## Length

A completion report is a **screen at most**, and usually a third of one. If the report is longer than the thing it is reporting on is interesting, it is too long.

Two exceptions where the user genuinely wants the artifact itself:

- `plan` returns candidates, which are the deliverable — that table earns its space.
- `review` in explicit-ask mode returns findings, which are the deliverable.

Even there: lead with the two or three that matter, and let the rest be a list underneath.

## Confusion mode

Once the user signals confusion (Rule 8), every subsequent report in the session tightens further: no headers unless there are genuinely three separate things, no tables, no parenthetical qualifications, one idea per line. Concrete noun first.

This does not expire after one message.

## Never do these

- Do not open with a recap of what the user asked for.
- Do not narrate the procedure you followed. Nobody wants the phase numbers.
- Do not report that state was written unless the path is useful to them.
- Do not report "nothing drifted" or "no findings in category X." Silence covers it.
- Do not append a status block to a conversational answer. If they asked a question, answer the question.
- Do not congratulate the work, yours or theirs.
