# Whiteboard for ChatGPT

Plan work too large for one session as a GitHub Issues decision map. Use ChatGPT's GitHub connector for all tracker reads and writes. Do not reference local skill folders or Claude-specific tools.

## Core model

- One board issue labeled `whiteboard:map`
- One child issue per unresolved decision
- One ticket per working session
- The board is an index; ticket comments hold detail
- Planning ends when nothing remains to decide

## Sub-skill routing

When another skill is required, invoke it through ChatGPT's skill system before continuing. If it is unavailable, reproduce only its essential behavior:

- hot-seat -- ask one decision question at a time and include a recommended answer
- napkin -- create the cheapest concrete artifact that can settle one question
- connotation-cop -- settle conflicting terminology or record a hard-to-reverse decision

Do not read `~/.claude/skills` or assume filesystem access to installed skills.

## GitHub operations

Use the connected GitHub tools to:

1. create and read the board issue
2. create decision issues
3. apply labels and assignees
4. add resolution comments
5. close resolved issues
6. update the board's decision index

If GitHub is not connected, produce a complete markdown board and ticket set for manual creation. Do not pretend writes occurred.

## Modes

### Draw

1. Establish the destination.
2. Surface open decisions breadth-first.
3. Create the board issue.
4. Create one issue per sharp decision.
5. Record blockers in issue bodies or comments when native dependency fields are unavailable.
6. Stop after drawing the board.

### Work

1. Read the board and current open children.
2. Select the named ticket or first unblocked, unclaimed ticket.
3. Claim it by assigning the authenticated user when possible.
4. Resolve exactly that ticket.
5. Add the resolution comment, close the ticket, and update the board index.
6. Re-read the board before recommending the next ticket.

### Snapshot

1. Verify there are no open decision tickets or unresolved parking-lot items.
2. Synthesize the decisions into the destination artifact.
3. Link or paste the artifact into the board.
4. Close the board.

## Session sign-off

End every session with:

```markdown
**Board:** <X> closed / <Y> open
**This session:** <ticket name> -- <one-line result>
**Next up:** <ticket name> -- <why it is next>
**Say:** "work the board" or "snapshot the board"
```

Never resolve more than one ticket in a session. Never claim a write or status change without tool evidence.