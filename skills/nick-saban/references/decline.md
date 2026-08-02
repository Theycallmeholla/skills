# Decline

Records a finding as a deliberate, accepted choice, keyed by its signal, so no future pass raises it again — and revokes that decision cleanly when asked.

**Reads:** latest `audits/` record
**Writes:** `.claude/nick-saban/waived.json`
**Stops at:** Never edits the finding itself, never touches config, never recomputes a score directly (that happens naturally on the next `check-playbook`, since `merge_pass.py` reads `waived.json`). Refuses to decline a `high` severity finding without a written sentence naming the actual risk being accepted — a one-word "sure" is not enough for that severity.

## Why this is the only writer of waived.json

`adjust` and `drill` can both surface findings the user chooses not to act on right now. Rather than let either of them quietly record that choice, they load this file and follow it — so there's exactly one place the reason requirement and the high-severity guard live, instead of two copies that could drift apart.

## Phase 1: Resolve the finding to a signal

The user (or the calling command) will usually reference a finding by its `HN-` id. Look it up in the latest record to get its `signal` — declines are keyed by signal, not id, so the decision survives even if the id changes across a rebuild.

## Phase 2: Require the reason

Always ask for (or, if called from `adjust`/`drill` mid-review, capture) a short, specific sentence: why is this an acceptable risk, not just "not now." For `high` severity findings this is a hard requirement, not a nicety — write the finding's severity into the confirmation prompt so nobody declines a high-severity risk without noticing it was high-severity.

Bad reason: "don't need this."
Good reason: "All three MCP servers are internal, reviewed quarterly by platform — the exposure this flags doesn't apply here."

## Phase 3: Write

Add or update the entry in `waived.json`:

```json
{
  "schema": 1,
  "signals": {
    "<the signal>": {
      "reason": "<the sentence from Phase 2>",
      "by": "<user, if known>",
      "date": "<today, ISO date>",
      "severityAtWaiver": "<the finding's severity at the time>"
    }
  }
}
```

## Phase 4: Confirm the effect

Tell the user plainly what this does: the finding will show as declined (not resolved) on the next `check-playbook`, it stops counting against the score, and it'll appear under a collapsed "Declined" section in `scouting-report` rather than disappearing entirely.

## Revocation

If asked to un-decline something, remove its entry from `waived.json` entirely — nothing else. The next `check-playbook` will pick it back up as open if the underlying signal still fires, exactly as if it had never been declined.

## Output

```
Declined <finding id> (<signal>).
Reason on record: "<reason>"

This stops counting against your score starting with the next check-playbook.
```

## Confirm and stop

Edits no finding, no config file, no score directly. Refuses a high-severity decline with no written reason. Revocation touches only the one entry being removed.
