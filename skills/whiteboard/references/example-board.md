# Worked example — one small board, full lifecycle

The loose idea: *"We should probably move off session cookies to JWTs."* Too big for one session, half of it still blurry. Here's the whole lifecycle at small scale.

## After Draw mode

**Board issue** — `JWT auth migration board` (label `whiteboard:map`):

```markdown
## Destination

A migration spec in docs/specs/jwt-migration.md that an engineer can execute
without further product decisions.

## Notes

Express app, auth in src/auth/. Consult the connotation-cop skill — "session",
"token", and "login" are overloaded in this codebase.

## Decisions so far

## Parking lot

- Something about token revocation — depends entirely on where refresh tokens
  land; can't write the question on a sticky yet.
- Mobile app impact? Unclear if the mobile client even uses cookie auth today.

## Out of scope
```

**Tickets** (sub-issues), wired in the second pass:

- `Pick the token lifetime strategy` — hot-seat. **Up next.**
- `What does the mobile client actually use for auth today?` — research (AFK). **Up next.**
- `Where do refresh tokens live — httpOnly cookie or body?` — hot-seat. **Blocked by** lifetime strategy.
- `Sign up for the Auth0 tenant so its token API can be judged` — task, `Runs: human` (needs a credit card and an email nobody else owns). **Up next.**

Note what stayed parked: revocation is *known to be coming* but fails the sticky test — it can't be phrased until the refresh-token ticket resolves. Tempting to create a "Figure out revocation" ticket now, but that's a paragraph of maybes, not a sticky. It parks.

## A Work session

Session loads the board, takes the first up-next ticket in board order — `Pick the token lifetime strategy` — and claims it (assignee). A hot-seat session runs: one question at a time, a pick attached to each. The human lands on 15-minute access tokens + 30-day refresh.

Resolution comment on the ticket:

```markdown
## Answer

15-minute access tokens, 30-day rolling refresh tokens. Short access window
because the app serves billing pages; 30-day refresh matches current session
length so users notice no change.
```

Ticket closed. Board's *Decisions so far* gains:

```markdown
- [Pick the token lifetime strategy](link) — 15-min access / 30-day rolling refresh
```

Tending the board: the answer unblocks `Where do refresh tokens live` (it joins up-next automatically — its only blocker is now closed). Revocation *still* fails the sticky test — it needed the refresh-token *location* too. It stays parked.

**Then the continue check.** Re-fetch the board, re-query up-next — three takeable tickets now:

| Ticket | Type | Loop takes it? |
|---|---|---|
| `Where do refresh tokens live` | hot-seat | No — that's a question |
| `What does the mobile client actually use for auth today?` | research | **Yes** |
| `Sign up for the Auth0 tenant` | task, `Runs: human` | No — credit card |

Something's takeable, so no sign-off. One line — `✓ Pick the token lifetime strategy — 15-min access / 30-day rolling refresh · taking What does the mobile client actually use for auth today?` — and it keeps going. The mobile-client research resolves alone: the client uses the same cookie endpoint, so the migration breaks it.

*Now* up-next is hot-seat + a human task, and nothing else. The human is the blocker, so it signs off:

```markdown
**Board:** 2 closed / 3 open
**This session:** Pick the token lifetime strategy — 15-min access / 30-day rolling refresh
                  What does the mobile client use for auth — same cookie endpoint; migration breaks it
**Stopped because:** the human is the blocker
**Waiting on you:** Where do refresh tokens live — a call between httpOnly cookie and response body
                     Sign up for the Auth0 tenant — needs a card and an email
**Next up:** Where do refresh tokens live — it unblocks the revocation question still parked
**Say:** "run the board"
```

Two tickets closed, zero keystrokes in between. The old rule would have stopped after the first one and asked the human to type "work the board" so it could read some docs.

## A later Work session — a parked item promotes, scope gets ruled

`Where do refresh tokens live` resolves to *httpOnly cookie*. NOW revocation fits on a sticky — the session promotes it into a ticket: `Do we need server-side refresh-token revocation for the billing pages, or is the 15-min access window enough?` (hot-seat), deleting the revocation line from the *Parking lot*.

The same hot-seat surfaced "should we also add OAuth social login while we're in here?" — appealing, but past the destination (the destination is a *migration* spec). It goes to *Out of scope*:

```markdown
- OAuth social login — new capability, not part of the cookie→JWT migration; its own board if wanted
```

## Snapshot mode

Eventually: up-next empty, parking lot empty, no open tickets. A Snapshot session verifies the board is done (no open claimed tickets — nobody mid-flight), then walks *Decisions so far*, zooming into each resolution comment, and writes `docs/specs/jwt-migration.md` — organized as a spec (auth flows, token handling, rollout), not in ticket-close order. The board body gets a link to the spec; the board issue closes with:

> Board snapshotted. Artifact: docs/specs/jwt-migration.md

Closed board, linked snapshot: anyone who finds the board later has the front door to the whole decision trail.
