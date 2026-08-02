# Scouting-Report

Renders the last recorded pass as a scorecard: the delta since the previous version, the open backlog grouped by severity and by which command owns fixing it, declined findings collapsed out of the way, and any outstanding work orders.

**Reads:** `registry.json`, `audits/*.json`, `orders/*.md`, `orders/*.attest-*.json`, `waived.json`
**Writes:** nothing
**Stops at:** Writes nothing at all, including notes or waivers. Never re-runs detection — this is a report on the last pass, not a new one. If the last pass looks stale (older than recent commits touching `CLAUDE.md` or `.claude/`), say so explicitly rather than presenting stale numbers as current.

## Phase 1: Load

Read the registry and the latest two audit records (for the delta — if only one exists, there's no delta to show, which is fine to say plainly). Read every order file and its most recent attestation, if any.

## Phase 2: Diff against the prior pass

Compare findings by id: which resolved, which are newly open, which persisted unchanged. Persisted findings are worth calling out specifically if they've now survived more than one or two passes without action — that's a signal the recommended rung might be wrong (see `ladder.md`'s note on under-enforcement), not just that nobody's gotten to it yet.

## Phase 3: Render

State the age of the data up front — how long ago the last `check-playbook` ran, relative to the most recent relevant commit if that's determinable.

## Output

```
## Scouting Report

Last checked: <when>, pass <N>
**Score: <overall> (<delta>)**

### Since last pass
Resolved: <list, or "none">
New: <list, or "none">
Persisting <k>+ passes without action: <list, if any — this is worth flagging>

### Open backlog
| Severity | Owner (adjust/drill) | Finding |
|---|---|---|
[rows]

### Declined (<count>, collapsed)
<one line each: signal, reason>

### Work orders
| Slug | Criteria unmet | Last watch-film |
|---|---|---|
[rows, or "none open"]
```

## Confirm and stop

Writes nothing. Never re-runs detection — always says how old what it's showing actually is.
