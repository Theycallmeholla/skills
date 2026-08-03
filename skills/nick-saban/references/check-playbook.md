# Check-Playbook

Inspects the standing playbook against the closed detector registry, inherits finding IDs by signal across passes, and writes a new versioned record with a derived score.

**Reads:** `CLAUDE.md`, `.claude/**` except `nick-saban/`, `.github/workflows/**`, `package.json`, `Makefile`, git config, latest `audits/` record, `waived.json`, `notes.md`; `references/ladder.md`; `references/findings.md`
**Writes:** `audits/NNN.json`, `registry.json`
**Stops at:** Edits no source file — this command only observes and records. Resolves nothing by assertion, only by a signal genuinely not firing. Resolves nothing in a category it didn't scan this pass.

## Phase 1: Load prior state

Read `registry.json` if it exists, and the highest-numbered file in `audits/`. If neither exists, this is effectively a first pass — treat every finding as new (this is also what `kickoff` does internally when it writes `audits/001.json`).

Read `waived.json` and `notes.md`. A decline means don't re-raise that specific signal as a live concern — but do still check whether it fires, since `merge_pass.py` needs to know either way to keep the record accurate. `notes.md` may explain something as a deliberate choice that was never formally declined; treat that as context, not as suppression — if it looks like a real gap, still raise it and let the user decide whether to formalize it with `decline`.

## Phase 2: Probe the verification surface

Before running detectors, work out what verification commands actually exist and run in this repo: check `package.json#scripts`, `Makefile` targets, any CI config. For each of test / typecheck / lint / build / ci, record the command, where you found it, and whether you actually confirmed it runs (or at minimum that it's syntactically present and the underlying tool is installed — running the full suite isn't required, but don't claim `"runnable": true` on faith). This becomes `verificationSurface` in the record and it's what `gameplan` will later use to bind acceptance criteria to real commands, so getting this right saves real work downstream.

## Phase 2b: Map the tool surface

Before evaluating any permission or enforcement finding, establish what tools this agent actually has, because a guard only guards the surface it's registered against.

1. List the native tools available (Bash, Read, Edit, Write, …).
2. List connected MCP servers and their tools — check `.mcp.json`, `settings.json`, and the user's global config.
3. Mark every tool capable of: shell execution, file read, file write, git operations, network calls, database access.
4. For each existing guard in the repo, record which of those surfaces it intercepts and which it doesn't.

Record the result in the audit as `toolSurface`:

```json
"toolSurface": {
  "shell": { "Bash": "guarded", "mcp__desktop-commander__execute_command": "unguarded" },
  "fileRead": { "Read": "restricted-by-deny-rule", "mcp__filesystem__read_file": "unguarded" }
}
```

Any guarded/unguarded split like the one above is an `enforcement-bypass-surface` finding. This is not a hypothetical: a hook registered on `"Bash"` does not see an MCP shell tool, so a repo can hold a carefully written guard and have every one of its protections be one tool-choice away from irrelevant. **Never describe a guard as repo-wide, global, or enforced when an equivalent unguarded surface exists** — say which surface it covers.

## Phase 3: Run the detectors

Load `references/state.md`'s detector table if you haven't already this session. Go through each category and look for the specific things each detector describes — don't freelance new categories of concern; if something doesn't fit, note it separately as an observation rather than forcing a category (see `state.md`'s note on this).

Decide which categories you're actually able to scan this pass — normally all six, but if the user asked for a narrower check ("just look at permissions"), scan only those and pass exactly that list to `merge_pass.py`. Scanning a narrower set is fine; claiming to have scanned more than you did corrupts the resolved-detection logic for categories you didn't actually look at.

For each real problem found, write a raw finding object per `references/findings.md`'s guidance: `signal`, `detector`, `category`, `rung`, `severity`, `location`, `claim`, `consequence`, `evidence`, `remedy`, and a `mechanicalCheck` wherever the finding is objectively checkable (see `findings.md` for the three types and when to skip it).

## Phase 4: Verify, then merge and score

Before scoring, run the independent spot-check gate — this is not optional busywork, it's what stops this pass from silently mis-resolving something the way an adversarial test of this skill proved could happen:

```
python3 <skill-path>/scripts/verify_resolution.py \
  --project-dir <project-root> \
  --raw-findings <temp-file>
```

This reads the prior audit record and, for any previously-open finding that carries a `mechanicalCheck` and that your raw findings list doesn't mention, independently re-checks whether the underlying condition is actually gone. If it isn't, the finding gets reinstated into your raw findings automatically and the script tells you so — read that output. If it reports anything reinstated, that's a real signal your detection pass just missed something; don't just proceed silently, mention it in your summary to the user.

The script also lists any **judgment-mode** findings that were open and that your raw findings don't mention. Those can't be re-checked mechanically, so they will not close on their own. For each one, either re-raise it or write a resolution claim into a resolutions file:

```json
[{ "signal": "inferable-content:framework-tour",
   "basis": "The file-by-file tour was deleted from CLAUDE.md by adjust in pass 4.",
   "evidence": "CLAUDE.md is now 61 lines; the '## Project structure' section is gone." }]
```

Hold that `evidence` to the same bar as a finding's: point at the thing so someone can confirm it in ten seconds. "Cleaned up the bloat" is not a basis for closing anything.

Then merge and score:

```
python3 <skill-path>/scripts/merge_pass.py \
  --project-dir <project-root> \
  --raw-findings <temp-file> \
  --categories-scanned <comma-separated list from phase 3> \
  --verification-surface <temp-file-with-verificationSurface> \
  --resolutions <temp-file-with-resolution-claims>
```

`merge_pass.py` refuses to run if `verify_resolution.py` hasn't run against this raw-findings file. That's deliberate — the gate is only a guarantee if it actually ran, and an optional gate is not a gate. `--skip-verify-gate` exists for a genuinely script-less environment; using it means saying plainly in your summary that the false-resolution guard was bypassed.

This handles ID inheritance, resolved-detection, waiver application, and scoring — see `references/state.md` for why this must not be done by hand. Then run `scripts/build_registry.py --project-dir <project-root>` to refresh the index.

If the scripts genuinely can't run (no Python available), do the merge manually following the matching rule in `state.md` exactly, and tell the user you fell back to a manual merge — that's a real caveat on the reliability of the result, not a formality.

## Phase 5: Summarize the delta

Don't just say "audit complete." Compare this pass to the prior one and lead with what changed:

- How many findings resolved since last time (name them, however briefly)
- How many are newly open
- The overall score and its direction
- The single highest-severity open finding, named specifically, since that's usually what the user actually wants to act on next

## Output

```
## Check-Playbook — pass <N>

**Score: <overall> (<delta from last pass, if any>)**

Resolved since last pass: <list, or "none">
New this pass: <list, or "none">

### Open findings, by severity
[table or list: id, category, rung, one-line claim]

**Highest priority:** <the one finding worth acting on first, with its consequence>

<If verify_resolution.py reported anything, one line here — reinstated findings mean
this pass missed something; unverifiable ones mean the gate is blind there.>

### Next

**Do this:** `<drill|adjust> <the specific finding id>`
<why that finding first — its severity and its actual consequence, from this pass>

**Instead, if <that finding is a deliberate trade-off you already made>:** `decline <id>`
```

Pick the `Next` command by rung-owner of the highest-severity open finding, and name the id. "Run drill or adjust" with no id is the failure this contract exists to stop — the user just read a whole table and still can't tell which row to act on.

## Confirm and stop

This command only observes and records. It never edits `CLAUDE.md`, never touches `.claude/rules/`, `.claude/hooks/`, or `settings.json`, and never marks a finding resolved by anything other than the signal genuinely not firing.
