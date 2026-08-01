---
name: whiteboard-help
description: Show the quick-reference guide for the whiteboard planning system (whiteboard, hot-seat, napkin, connotation-cop) — the flow, what to say, and the rules. Use when the user asks "whiteboard help", "how do I use the whiteboard", "what's the flow", "remind me how whiteboard works", "which skill do I use", or seems unsure how to start or continue a whiteboard effort. This skill only DISPLAYS the guide — it never starts a board, resolves tickets, or does any work.
---

# Whiteboard Help

Display the guide below to the user, adapted to what they asked. If they asked a specific question ("how do I close a board?"), answer it from the guide and show just the relevant part. If they asked generally, show the whole thing. **Do not start any work** — this skill is a cheat-sheet, nothing else. If they want to actually begin, tell them what to say and let them say it.

---

## The one-liner

Big fuzzy idea → put it on the **whiteboard** → work tickets **one per session** → **snapshot** the board into a spec when nothing's left to decide.

## The flow

**1. Draw** — one session, run once per effort
Say: **"whiteboard this: [your idea]"** (in a repo with GitHub Issues)
What happens: Claude hot-seats you to pin the destination, creates the board issue + tickets, parks the blurry stuff in the parking lot. Then stops.

**2. Work** — one session per ticket, repeat until done
Say: **"work the board"** (or "work the board, ticket [name]")
What happens: Claude claims the next open ticket and resolves it with you. Ticket type decides the tool:

- hot-seat ticket → Claude questions you, one at a time, with its pick attached
- napkin ticket → Claude builds a throwaway sketch you react to
- research ticket → Claude reads docs alone, links a summary
- task ticket → someone does a prep chore that unblocks a decision

Then it updates the board and stops. One ticket per session — always.

**3. Snapshot** — one session, run once at the end
Say: **"snapshot the board"**
What happens: Claude verifies nothing's left (no open tickets, empty parking lot), writes the spec from all the decisions, links it, closes the board. Done — hand the spec to whoever builds.

## Solo use (no board needed)

- **"hot seat me on [decision]"** — stress-test any plan, one question at a time
- **"napkin this: [design question]"** — throwaway code that answers one question
- **"connotation-cop: [term fight]"** — settle what a word means, book it in the glossary

## The rules that matter

- **The sticky test:** can you write the question on one sticky note, precisely? Yes → it's a ticket. Still a paragraph of maybes → parking lot.
- **One ticket per session.** Never two. The board must sharpen between sessions.
- **The board plans, it doesn't build.** Open decision left? That's the next ticket. None left? Snapshot.
- **Claim before work.** Assignee on the ticket = claimed. Unassigned + unblocked = up for grabs.
- **Decisions live on tickets.** The board only gists and links — never holds detail.
- **Every session ends with a sign-off:** board count, what was decided, the next ticket, and what to say. You should never have to ask "what's next" — if a session ends without the sign-off, say "sign off" and you'll get it.

## Where things live

- The board: a GitHub issue labelled `whiteboard:map`; tickets are its sub-issues
- Decisions: resolution comments on closed tickets, indexed on the board
- Big permanent decisions: ADRs in `docs/adr/` (connotation-cop writes them)
- Vocabulary: `CONTEXT.md` at the repo root
- The final spec: wherever the board's Destination says

## Stuck?

- "Which ticket next?" → say "work the board" — Claude picks the first unblocked, unclaimed one
- "Ticket feels huge" → it was mis-sized; Claude splits it into sharp sub-tickets
- "Someone abandoned a ticket" → claimed + 3 days silent = presumed dead; Claude asks you before unclaiming
- "New idea mid-effort but it's past the destination" → it goes to Out of scope, not the board
