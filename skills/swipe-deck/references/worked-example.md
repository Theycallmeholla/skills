# A full run, end to end

One complete trace: vague prompt → pool → the message that comes back → the brief. Read this once before your first deck; the shape transfers to any topic.

---

## The prompt

> i want to build something for my clients so they stop emailing me asking where their project is at

## What the prompt already answered

Before writing a single card, subtract what you know. This kills a third of the candidates:

- there are **clients**, plural, and existing ones — not a lead-gen thing
- the pain is **status visibility**, not billing or file delivery
- they're currently doing this over **email**, so email is the baseline to beat
- "build something" — they expect to have a thing at the end

So: no card asking whether it's for clients. No card asking whether the problem is status. Cards that re-ask a known fact are how this starts feeling like a form.

## The facets

Run the lenses, keep what bites, name them in the user's words:

`what it fixes` · `where it lives` · `how much v1` · `budget & time` · `look and feel` · `who touches it` · `dealbreakers`

Seven facets, six to nine cards each, plus wildcards — that lands around 75 cards. They'll swipe maybe 45 of them; the rest is headroom in case I've misjudged them.

## The pool

The thing to internalise is the *shape*, not the volume. Here is one facet written out in full so you can see the ladder, both poles, and the honest predictions:

```json
{ "id": "w1", "q": "It lives inside your existing website",
  "facet": "where it lives", "depth": 1, "style": "preference", "predict": "yes" },
{ "id": "w2", "q": "A separate app they download",
  "facet": "where it lives", "depth": 1, "style": "provocation", "predict": "no" },
{ "id": "w3", "q": "Just a link you paste into an email",
  "facet": "where it lives", "depth": 2, "style": "instance", "predict": "yes" },
{ "id": "w4", "q": "It should feel like signing into a portal",
  "facet": "where it lives", "depth": 2, "style": "preference", "predict": "no" },
{ "id": "w5", "q": "You'd put it behind your own domain, not a tool's",
  "facet": "where it lives", "depth": 3, "style": "constraint", "needs": "w1",
  "predict": "yes" }
```

Five cards, one facet. `w1` and `w2` are opposite poles, so a rejection has somewhere to land. `w3` is the concrete twin — if `w1` gets a *not sure*, the engine reaches for it. `w5` sits under `w1` via `needs`, so it disappears entirely if the in-your-site idea dies. And the predictions are real guesses, including two nos.

Now multiply that across all seven facets and add the off-axis cards:

```json
{
  "topic": "the thing that stops the status emails",
  "facets": ["what it fixes", "where it lives", "how much v1",
             "budget & time", "look and feel", "who touches it", "dealbreakers"],
  "carry": { "swiped": 0, "hits": 0, "decided": 0, "deep": 0, "coverage": {} },
  "cards": [
    { "id": "f1", "q": "Clients log in and check for themselves",
      "facet": "what it fixes", "depth": 1, "style": "preference", "predict": "yes" },
    { "id": "f2", "q": "You'd rather it just email them an update weekly",
      "facet": "what it fixes", "depth": 2, "style": "tradeoff", "predict": "no" },
    { "id": "s1", "q": "One shared page for all clients is enough to start",
      "facet": "how much v1", "depth": 1, "style": "preference", "predict": "yes" },
    { "id": "s2", "q": "A single list: project, stage, what's next, updated when",
      "facet": "how much v1", "depth": 2, "style": "instance", "predict": "yes" },
    { "id": "s3", "q": "Clients can comment and you reply in there",
      "facet": "how much v1", "depth": 2, "style": "provocation", "predict": "no" },
    { "id": "b2", "q": "Rough and live in three weeks over polished in three months",
      "facet": "budget & time", "depth": 1, "style": "tradeoff", "predict": "hot" },
    { "id": "b3", "q": "Three weeks still holds if it means no per-client logins",
      "facet": "budget & time", "depth": 3, "style": "tradeoff", "predict": "yes" },
    { "id": "p1", "q": "You'll be the one updating it",
      "facet": "who touches it", "depth": 1, "style": "mirror", "predict": "yes" },
    { "id": "p2", "q": "Whoever updates it would do it from their phone",
      "facet": "who touches it", "depth": 2, "style": "context", "predict": "yes" },
    { "id": "d1", "q": "It's a failure if a client needs you to explain it",
      "facet": "dealbreakers", "depth": 1, "style": "anti-goal", "predict": "hot" },
    { "id": "d3", "q": "No login at all — each client gets a secret link",
      "facet": "dealbreakers", "depth": 3, "style": "tradeoff",
      "hint": "the cheapest way to need zero explanation", "predict": "hot" },
    { "id": "d4", "q": "You'd accept a login if clients saw only their own work",
      "facet": "dealbreakers", "depth": 3, "style": "tradeoff", "predict": "no" },
    { "id": "x1", "q": "In a year you'd want clients paying invoices in here too",
      "facet": "what it fixes", "depth": 3, "style": "wildcard" }
  ]
}
```

`d3` and `d4` are the pair that earns its keep: they force the collision between "zero explanation" and "clients see only their own work", which nothing else in the pool resolves. A card that makes two strong preferences fight is worth five new questions. And `x1` has no `predict` at all — a genuine unknown, which is exactly when to omit it rather than guess.

## What comes back

One message, when the meter fills:

```
SWIPE DECK — 47 swiped on "the thing that stops the status emails"
(The meter filled. I'm done swiping.)

ABSOLUTELY (lock this direction in)
- [dealbreakers] It's a failure if a client needs you to explain it
- [budget & time] Rough and live in three weeks over polished in three months
- [dealbreakers] No login at all — each client gets a secret link

YES
- [what it fixes] Clients log in and check for themselves
- [where it lives] It lives inside your existing website
- [how much v1] A single list: project, stage, what's next, updated when
- [budget & time] Three weeks still holds if it means no per-client logins
- [who touches it] Whoever updates it would do it from their phone
  … and 19 more

NO (wrong direction)
- [where it lives] A separate app they download
- [how much v1] Clients can comment and you reply in there
- [who touches it] You'll be the one updating it
- [dealbreakers] You'd accept a login if clients saw only their own work
  … and 8 more

NOT SURE (ask something more specific here)
- [how much v1] One shared page for all clients is enough to start

EDITED CARDS (the user rewrote the premise, then answered THEIR version — each rewrite corrects an assumption of yours)
- "Rough and live in three weeks over polished in three months" → "Rough and live in six weeks over polished in three months" → ABSOLUTELY

NOTES (typed by the user — treat as direct statements)
- You'll be the one updating it → <<my PM does the updates>>

COVERAGE: what it fixes 6 · where it lives 5 · how much v1 8 · budget & time 6 ·
          look and feel 6 · who touches it 5 · dealbreakers 7
SIGNAL METER: 89% (I think I've got it)
  facets at full depth: 7/7
  swipes you predicted correctly: 38/44
  share of swipes below the surface: 47%
TOTAL SWIPED: 47
→ METER IS FULL — you stopped being surprised and every facet is covered.
  Write the brief now. Do not send more cards.
```

## Reading it

Work verdict by verdict, and write down what each one *forbids* as well as what it suggests:

- **The three absolutelys** — zero-explanation UX, speed over polish, secret links. Together they've already decided the architecture: no accounts, no onboarding, nothing that takes a quarter.
- **The no on a downloadable app** closes `where it lives`. The no on comments is a scope signal, not a feature signal — they want one-way broadcast.
- **`d3` up and `d4` down** resolves the collision the pool was built to force. Privacy-by-obscurity is acceptable here; per-client accounts are not. Say so in the brief, and flag it if any client work is confidential.
- **The no on "you'll be the one updating it"** plus the note is the most valuable line in the message. A PM does the updates, so someone else's daily workflow is in scope. Notice that the pool caught this only because `p2` was written facet-first ("whoever updates it") rather than assuming the answer.
- **The lone not-sure on "one shared page"** means that card was too abstract — and the engine did its job, reaching for `s2`, the concrete version, which landed a yes. That pair is why the brief can be specific about the layout.
- **The edit on the timeline card** is a counter-offer: three weeks was wrong, six is right — and then an *absolutely* on their own number. The brief says six weeks, in their words, not yours. (The widget already scored your prediction on that card as a miss.)

The six missed predictions are where the real information was. If you'd been right about all 44, you'd have learned nothing and the meter would have filled on nothing.

## The brief

```markdown
# Client status page — what you actually want

**The shape of it**
A single page on your existing site where each client sees their own projects —
stage, what's next, and when it was last touched — reachable by a secret link
with no login. Your PM updates it from her phone. Live in six weeks — your number, from the card you rewrote — under $5k.

**Locked in**
- Zero explanation required — if a client has to ask how it works, it failed
- Rough and live in six weeks beats polished in three months (you rewrote the timeline card yourself)
- Lives inside your current site, styled as yours rather than as a tool
- Secret per-client links, no accounts
- One-way: status out, no comments or replies

**Ruled out**
- A downloadable app
- Comment threads or approvals in v1
- You personally doing the updates

**Still fuzzy**
- Whether progress photos are core or a nice-to-have — one yes, no follow-up
- Invoices later: you swiped yes on the year-out wildcard, but that was one card

**The tension I'm reading**
"No explanation" and "clients see only their own work" pulled against each other.
The secret-link card won and the login card lost, so I'm reading privacy-by-obscurity
as acceptable. Worth a sanity check if any client work is confidential.

**First thing I'd do**
Mock the single client view and put it in front of your PM before anything gets
built. She's the one who has to keep it alive.
```

Then stop and ask whether to proceed. The brief is the deliverable; building is a separate decision.

## If the pool runs dry first

Occasionally someone out-swipes the whole pool without filling the meter — usually because your predictions kept missing, which caps the meter at 80% no matter how good the coverage is. The message then ends with *"Send ONE more batch of 60+ cards, no announcement, no recap."*

Do exactly that. Copy the `carry` block verbatim, build a fresh pool weighted toward whatever is holding the meter down — thin coverage means a facet you under-built, low predictability means your model of them is still wrong, low depth means your ladders were too short — and reply with the widget and nothing else. Not a word of commentary. From their side the cards simply keep coming.
