# Whiteboard body templates

## Board body

Open tickets are NOT listed in the body — they're open sub-issues, found by query. The body is the low-res view a session loads once.

```markdown
## Destination

<What "done" looks like — the spec, decision, or change this board is working
toward, and where the final artifact will live. One or two lines; every session
orients to this before choosing a ticket.>

## Notes

<Domain; skills every session should consult; standing preferences for this
effort. If execution is opted onto the board (rare), say so explicitly here.>

## Decisions so far

<!-- The index — one line per closed ticket: enough to judge relevance, then
follow the link for the detail the ticket holds. Never restate detail here. -->

- [<closed ticket title>](<link>) — <one-line gist of the answer>

## Parking lot

<!-- Questions you can tell are coming but can't yet write on one sticky.
Written as loosely or fully as the current view allows. Promoted into tickets
as answers sharpen them; a promoted item is deleted from here. -->

## Out of scope

<!-- Work consciously ruled past the destination. Never comes off this list. -->

- <gist> — <why it's out> (<link to closed ticket, if one existed>)
```

## Ticket body

```markdown
## Question

<The single decision or investigation this ticket resolves. Sharp enough that a
session with no other context knows when it's answered. Sized for one session —
if resolving it needs 3+ distinct sub-answers, it should be several tickets.>
```

The answer never goes in the body — it's a resolution comment at close time. Assets produced while resolving (research summaries, napkins) are linked from comments, not pasted in.

## Resolution comment

```markdown
## Answer

<The decision and the one-line why. If a hot-seat session produced a decision
log, paste the relevant lines here — this comment is the detail the board's
Decisions-so-far line points at.>

<Links to any assets: research summary, napkin branch, ADR.>
```

## Snapshot artifact (Snapshot mode)

Shape follows what the Destination named — a spec, a decision record, a handoff doc. Whatever the shape, it opens with:

```markdown
# <Effort name>

**Destination:** <the original destination line>
**Board:** <link to the closed board issue>

<The synthesis — organized by the shape of the answer, not the order the
tickets closed.>
```
