# The run loop

**The rule: if the next takeable ticket needs the human, stop. If it doesn't, take it.**

A sign-off whose own *Next up* line reads "this needs none of your attention" is a bug. The user walked away; coming back to a session idling on a keystroke it never needed to ask is the failure this loop exists to prevent. Stopping is still correct — often. It's correct *because the human is the blocker*, never because a ticket ended.

## Eligibility — can the loop take this ticket alone?

Decided from the ticket's `whiteboard:<type>` label, before claiming it.

| Type | Loop takes it? | What it does |
|---|---|---|
| `research` | **Yes** | Resolves fully — docs, APIs, knowledge bases. Links the summary. |
| `task` | **Only if the body says `Runs: agent`** | Executes it, records what was done plus the facts later tickets need. |
| `napkin` | **Builds, doesn't judge** | Builds the artifact per the napkin skill, leaves the verdict block's ANSWER blank (`napkin/SKILL.md:46`), links it, adds it to *Waiting on you*, moves on. The ticket stays **open and unclaimed** — the verdict is the resolution, and that's the human's. |
| `hot-seat` | **No** | This is a question. Questions are the point — they go to the human. |

Two missing-data cases, both resolved the same way — **the human gets it**:

- **No `Runs:` on a `task` ticket.** Task tickets act on the world (provisioning access, moving data); guessing wrong is expensive and the field is cheap. Never infer it from the title.
- **No `whiteboard:<type>` label at all** (an issue filed by hand, or a sub-issue from before the board existed). Nothing says what it is, so nothing says a session can take it alone.

Both are ineligible, not errors. Skip, list under *Waiting on you* with what's missing, keep going. Don't stop the run to fix metadata, and don't add the label yourself — labelling it is a judgment about what kind of work it is.

## The loop

Work mode steps 1–5 unchanged. After step 5 (tend the board), before step 6:

1. **Re-fetch the board body.** Not cached — another session may have moved it (`github-ops.md:22`). Re-read *Destination* while it's in hand.
2. **Re-query up-next** (`github-ops.md:50`). Open, unblocked, unclaimed, in board order.
3. **Run the stop checks below.** Any one fires → terminal sign-off, done.
4. **Take the first eligible ticket.** Print one line — `✓ <resolved ticket> — <gist> · taking <next ticket>` — and go back to Work step 2. No sign-off between tickets; the sign-off is a stopping artifact.
5. **Skip, don't stall.** First up-next ticket ineligible but a later one eligible? Take the later one. The skipped ticket goes on *Waiting on you*. It is not claimed, not closed, not reordered.

Board order still decides among *eligible* tickets — the loop reorders nothing.

## Stop conditions

Checked between tickets, never mid-ticket. A half-resolved ticket left claimed and open is worse than one never started.

1. **Nothing eligible.** Up-next is empty, or every takeable ticket needs the human. The normal ending.
2. **Board is done.** No open tickets, empty parking lot → recommend Snapshot (Work step 6). Snapshot is still its own session — it's a synthesis judgment, not queue-draining.
3. **Fanout.** Cumulative tickets created > cumulative tickets closed this run. The board is diverging instead of converging; whether that's discovery or scope creep is a human call. Report both counts.
4. **Drift.** The next eligible ticket doesn't serve the *Destination* you just re-read. Don't resolve it and don't close it — say which ticket and which destination line disagree.
5. **Context.** Below.

## The context stop

A session boundary was also a context boundary. Ticket 5 resolved on a compacted view of tickets 1–4 is a quiet quality failure — and tickets 3–5 *act* on ticket 2's resolution: promoting parked items, wiring blockers, closing things. Bad resolutions compound and surface late. The fanout guard measures divergence in count; nothing measures it in quality.

There's no token gauge to read here, so the rule hangs on what's actually observable:

- **Hard signal — context was compacted this session.** Finish the ticket in hand, then stop. No estimation needed; you know when you've been summarized.
- **Soft signal — the next eligible ticket needs heavy reading** (research across large docs, a napkin build spanning many files) **and the session is already long.** Stop instead of starting it.

The soft signal will sometimes stop early. That costs one keystroke, which is the cheap direction to be wrong in.

Say context is why, in the sign-off. A run ending at 3 of 8 must not read as "the board is blocked on you" — the user's next move is `run the board` in a fresh session, not answering anything. The board is already the handoff: every decision is indexed and linked (`SKILL.md:15`), so a fresh run resumes from the tracker with nothing to hand over.

## Decisions that surface mid-ticket

An autonomous ticket hits a genuine choice. `hot-seat/SKILL.md:17` is absolute — it goes to the human, every time, even when you're sure. But stalling the whole run on question #1 wastes every autonomous ticket behind it.

**Write the question as a new hot-seat ticket** (sticky-sharp, wired to block what it blocks), add it to *Waiting on you*, resolve whatever on the current ticket is still answerable without it, and continue. If nothing on the ticket survives the question, leave the ticket open and unclaimed with a comment naming the blocker.

This is hard rule 6 (split, don't swell) applied at the AFK boundary. The user returns to every question at once instead of the first one.

## Bookkeeping

Carry across the whole run, for the sign-off:

- **Closed** — ticket names, one gist each
- **Created** — ticket names and why (fanout guard reads this)
- **Waiting on you** — every ticket skipped or raised, and what each needs from them
- **Stop reason** — which condition above fired

Template: [templates.md](templates.md#run-sign-off).

## Never, during a run

- **Never unclaim.** A stale claim is skipped, full stop. Hard rule 4 requires asking the human first, and there's no human to ask.
- **Never contest a claim.** Assignee appeared between check and claim → next eligible ticket (`github-ops.md:74`).
- **Never guess a `Runs:`.**
- **Never answer the human's side of a hot-seat.** A run that resolves a hot-seat ticket alone has broken the skill.
- **Never roll into Snapshot.**
