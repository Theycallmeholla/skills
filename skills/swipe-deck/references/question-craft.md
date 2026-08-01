# Question craft

How to find the right facets for any topic and write cards people can swipe on instinct.

- [Finding the facets](#finding-the-facets)
- [Worked facet sets](#worked-facet-sets)
- [The eight card styles](#the-eight-card-styles)
- [Composing the pool](#composing-the-pool)
- [Card rewrites](#card-rewrites)

---

## Finding the facets

Don't reach for a template — templates are why clarifying questions feel like paperwork. Instead run the topic through a fixed set of **lenses** and keep the 5–7 that actually bite. The lenses are stable; what they produce is completely different every time, which is exactly what you want.

| Lens | The question behind it |
|---|---|
| **Outcome** | What's different in the world once this is right? |
| **Form** | What shape does the thing take? |
| **Scope** | How much, how many, how far — and what's out? |
| **Constraints** | Money, time, skill, tools, rules, other people |
| **Context** | Where, when, with whom, on what device, in what mood |
| **Taste** | Style, tone, vibe, references they'd point at |
| **Tradeoffs** | What would they sacrifice, and for what |
| **Anti-goals** | What would make this a definite failure |
| **Stakes** | Who it's for, who judges it, what happens if it's wrong |

Two rules when you instantiate them:

**Rename them in the topic's language.** The user sees these as labels on the coverage meter and as chips on the cards. `dealbreakers` reads better than `anti-goals` for a dinner; `guardrails` reads better for a compliance project. Plain nouns, lowercase, one or two words.

**Drop the lenses that don't bite.** Picking a lunch spot has no meaningful *stakes* lens. Hiring your first employee has an enormous one. Forcing all nine produces filler cards, and filler cards are what make someone stop swiping.

## Worked facet sets

The same nine lenses, four wildly different topics. Notice that no two facet sets share a single name.

**"What should I eat tonight?"**
`hunger` (how big a deal is this meal) · `effort` (cook, pickup, delivery, sit down) · `craving` (cuisine, heavy vs light) · `spend` · `who's eating` · `dealbreakers` (waiting, driving, dishes)

**"I want to build a client dashboard."**
`what it fixes` · `where it lives` (in the site, standalone, an app) · `how much v1` · `budget & timeline` · `look and feel` · `who touches it` · `dealbreakers` (maintenance load, client confusion)

**"Help me hire my first employee."**
`the gap` (what work leaves your plate) · `shape of the role` (FT, contract, part-time) · `must-haves vs teachables` · `pay range` · `how you'd manage them` · `culture fit` · `what would make this a mistake`

**"Plan a family vacation."**
`the point of the trip` (rest, adventure, seeing people) · `how far` · `pace` (packed vs slow) · `spend` · `who's coming` · `non-negotiables` (nap times, dietary, accessibility) · `what would ruin it`

The pattern: the lens set is the ladder, the topic supplies the rungs. When you write the facets down, they should read like the categories a thoughtful friend would naturally cover — not a schema.

## The eight card styles

A deck of all one style is a survey with better graphics. Keep all eight in rotation across the pool; the `style` field shows on the card as a small muted label, which quietly tells the user what kind of reaction is wanted.

**preference** — a plain leaning.
> Dark, dense, keyboard-driven

**constraint** — a limit to accept or reject.
> Hard stop before September 1

**tradeoff** — two goods, one card, forcing a pick. The single most efficient card type — lean on it hard.
> Rough in three weeks over polished in three months

**anti-goal** — a failure condition. People are far more decisive about what they hate.
> It's a failure if clients need a tutorial

**instance** — a specific, nameable example instead of an adjective. Converts vague taste into hard signal.
> Something like Stripe's docs

**provocation** — a deliberate overshoot to find where the line is. Expect a no; the no is the point.
> Charge $500 a month for it

**mirror** — restates what you believe you already know, to verify rather than assume. Use sparingly, and only where being wrong would be expensive.
> This is mainly for your existing clients, not new leads

**wildcard** — off the stated axis entirely, testing an assumption nobody voiced. Scatter a few through the pool. This is where the surprises come from.
> You'd be fine if this never had a logo

## Composing the pool

There is one deck, 70 to 110 cards, written before the person swipes a single one. It has to stay interesting for however long they keep going, and it has to have an answer ready wherever they take it. Think of it as a *terrain*, not a list.

**Cover every facet, three deep.** A facet needs three decisive swipes before the meter counts it as covered, so a facet with two cards can hold the whole session under 70%. Give each one six to nine — and remember *not sure* doesn't count toward coverage, so vague cards leave holes.

**Build ladders, not rows.** Under each broad card, write the more specific and more committing version, and under that the one that actually costs something. The engine only surfaces the lower rungs if the upper one lands, so unused ladders cost nothing:

- depth 1 — "Mobile matters"
- depth 2 — "Mobile is the primary surface"
- depth 3 — "Desktop can look unfinished at launch"

Each rung asks for more than the last. That's what makes the top rung informative — and it's what makes an *absolutely* worth something, since the engine's response to one is to climb.

**Give every no somewhere to land.** When a direction gets rejected, the engine cools that facet and prunes anything wired to it. If the pool has no opposite-direction card, it just goes quiet there. Write both poles.

**Give every abstraction a concrete twin.** A *not sure* means the card was too vague to react to, and the engine responds by reaching for something more specific in that facet. If nothing more specific exists, the vague card was a dead end. Pair adjectives with instances: "clean and modern" gets "closer to Notion than Squarespace" sitting underneath it.

**Mix the styles throughout, not in blocks.** Across the whole pool: at least eight tradeoffs, at least six anti-goals, at least four wildcards, and a healthy run of provocations you expect to be rejected. A pool that drifts into all-preference cards halfway through is where people stop swiping.

**Use `needs` only for genuine dependencies.** `needs: "sc1"` drops a card when `sc1` is swiped left. It's for cards that stop making *sense*, not for branching taste. Over-wiring starves the pool and the deck runs dry early.

**Lead with the card that changes the most.** It's shown first and sets the tone; everything else is ordered by the engine.

**Predict every card.** Set `predict` to how you actually expect it to be swiped. The meter scores you against it, so a pool full of cards you're certain about will fill the meter without teaching you anything — which is exactly why you should be writing cards you *can't* call. A prediction you get wrong is the most valuable card in the pool.

## Card rewrites

| Weak | Why | Strong |
|---|---|---|
| Would you like it to be modern and easy to use? | Compound, and nobody says no | Clean over characterful |
| What's your budget? | A swipe can't answer a number | Under $5k all in |
| Do you have a timeline? | Yes/no tells you nothing | Live before the end of the quarter |
| Should the design be good? | No possible no | You'd delay launch two weeks for better design |
| Tell me about your audience | Not a card at all | Your users are more technical than you |
| Do you want it to be user-friendly? | Abstract, unanimous | A first-timer gets it with no explanation |
| Modern clean minimal aesthetic? | Three ideas, all adjectives | Closer to Notion than to Squarespace |
| Are you flexible on scope? | Invites a shrug | You'd cut half the features to launch a month sooner |

The through-line: a good card is something a person could **disagree with**. If a card can't lose, it isn't asking anything.
