# Case Study Output Template

Two deliverable files per case study. Use these structures; adapt section wording to the industry, never to the point of losing the skeleton.

## File 1: `<client-slug>-case-study.md` (web-ready copy)

```markdown
---
title: [SEO title — result-first, e.g. "How a Houston Plumber Doubled Service Calls After a Website Rebuild"]
slug: [client-slug-case-study]
meta_description: [under 160 chars, states client type + outcome]
client: [Name, or anonymized descriptor]
industry: [industry]
services: [list]
---

# [Headline: outcome + relatable client type. Formula: "How [client type] got [concrete result]". The client's name can be in it if they're big enough to matter; the *type* always is, because the reader is matching themselves.]

[Subhead: one sentence of situation + turnaround, no jargon.]

**[Stat 1]** · **[Stat 2]** · **[Stat 3]**
[Three stats max in a results bar. Real ones only. If only one exists, one big stat beats three weak ones. If none exist yet: skip the bar, don't fake it.]

## Meet [client]

[2-3 sentences. Who they are, what they do, one humanizing detail. Written warmly — the reader should like them.]

## The problem

[The section prospects read in the mirror. Their situation before: what was broken, what it was costing, what finally made them act. Concrete and specific — "the site didn't load on phones, and 70% of their visitors were on phones" beats "their online presence was underperforming." 1-2 short paragraphs.]

## What we did

[Short and scannable — prospects skim this part. A brief paragraph on the approach, then 3-6 bullets of the concrete pieces. If there was a clever/unusual move, it gets its own sentence. No agency jargon: "made the site show up when people search 'plumber near me'" beats "implemented local SEO strategy."]

## The results

[The payoff. Lead with the strongest number, phrased with honest precision ("calls roughly doubled" vs "112% increase" depending on the source). Then the softer wins: how the client felt, what changed day-to-day. Numbers make it credible; the human reaction makes it real.]

> "[QUOTE — real client words only. If none yet, leave this placeholder and see quote request below.]"
> — [Name, role, company]

## [CTA heading — mirrors the reader: "Sound familiar?" / "Your site should be doing this for you"]

[1-2 sentences + the action. Match the CTA the user's site actually uses.]
```

### Media plan (goes at the bottom of the case study file, clearly marked as production notes, not page copy)

A table with one row per visual the page needs. Every row has three fallback tiers so missing media never blocks publishing:

| Where on page | What to show | Tier 1 — provide | Tier 2 — find / create | Tier 3 — generate / stock |
|---|---|---|---|---|
| Hero | New site on devices | Client photoshoot | Screenshot the live site, frame in a device mockup | Generated mockup scene |
| The problem | The "before" | Old-site screenshot if archived | Wayback Machine capture | Skip — describe it in words |
| Results | The numbers | Analytics screenshot | Chart built from the real numbers | Don't generate — real data or nothing |
| ... | ... | ... | ... | ... |

Rules: recommend the visuals this specific story needs (before/after is almost always the strongest for website work). Mark which tier you recommend and what the user's next action is. Never generate fake "results" imagery — charts come from real numbers or don't exist. A short video (even a 30-second phone testimonial) is worth suggesting when the client relationship is warm; give the user the exact ask to send.

## File 2: `<client-slug>-intake.md` (working notes / resume point)

```markdown
# [Client] — case study intake
Updated: [date]  ·  Status: [gathering / drafted / awaiting client OK / ready to publish]

## Confirmed facts
- [fact] (source: [where it came from])

## Numbers
- [metric]: [value] — confidence: [verified / client-said / rough memory]

## Open questions
- [ ] [question] (asked? answer?)

## Permissions
- Name/logo use: [status]
- Quote: [status]

## Quote request (ready to send)
[A short, friendly message the user can text/email the client asking for a 1-2 sentence quote — pre-written with this client's context, so sending it is one paste.]
```

## Placeholder conventions

- `[NEED: description]` — a fact that's missing; the draft reads fine without it but is better with it.
- `[QUOTE]` — testimonial pending.
- `[CONFIRM: thing]` — written in the draft but unverified (e.g. client name usage).

Placeholders must be greppable and visually loud — the user should be able to find every remaining gap in ten seconds.
