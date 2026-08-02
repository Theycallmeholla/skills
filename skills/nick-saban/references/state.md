# State

Read this before running `kickoff` or `check-playbook`. Every other command trusts that these two got the schema right, so get it right by construction rather than by care: use the bundled script (`scripts/merge_pass.py`) to assemble and score a new audit record instead of hand-writing the JSON. The script exists specifically because signal matching and scoring are pure data transformations that are easy to get subtly wrong by hand and very expensive to get wrong silently — a slip here means a finding closes itself with nothing actually fixed, in the one system whose entire point is "detected, never asserted."

## Directory layout

```
.claude/nick-saban/
├── registry.json      cheap index, read every session
├── waived.json         declined findings, keyed by signal — the only file mutated in place
├── notes.md            free-text drawer, explains decisions that aren't formal waivers
├── audits/
│   ├── 001.json
│   ├── 002.json
│   └── NNN.json         append-only, one per check-playbook or kickoff pass
└── orders/
    ├── <slug>.md                    the work order (frontmatter + human body)
    └── <slug>.attest-N.json         one per watch-film run against that order
```

This whole directory is state, not source. `check-playbook` never scans it, scores it, or raises a finding about anything inside it.

## registry.json

```json
{
  "schema": 1,
  "currentAudit": 3,
  "lastAuditAt": "2026-08-02T14:22:00Z",
  "score": 58,
  "openHigh": 2,
  "orders": [
    { "slug": "resumable-imports", "title": "Resumable CSV imports",
      "created": "2026-07-28", "lastAttest": null, "criteriaUnmet": 2 }
  ]
}
```

Derived, not authored by hand — any command that writes a new `audits/NNN.json`, a decline, or an order updates this in the same operation (`scripts/build_registry.py` does this from the files on disk; run it after writing any state file rather than hand-editing `registry.json` in parallel).

## audits/NNN.json — the audit record

```json
{
  "schema": 1,
  "pass": 3,
  "created": "2026-08-02T14:22:00Z",
  "categoriesScanned": ["context", "mechanism", "enforcement", "verification", "permissions", "bounds"],
  "verificationSurface": {
    "test":      { "command": "npm test",          "source": "package.json#scripts.test", "runnable": true },
    "typecheck": { "command": "npm run typecheck", "source": "package.json#scripts",      "runnable": true },
    "lint":      { "command": null,                "source": null,                        "runnable": false },
    "build":     { "command": "npm run build",     "source": "package.json#scripts",      "runnable": true },
    "ci":        { "command": null,                "source": null,                        "runnable": false }
  },
  "score": {
    "context": 62, "mechanism": 70, "enforcement": 30,
    "verification": 85, "permissions": 45, "bounds": 55,
    "overall": 58
  },
  "findings": [
    {
      "id": "HN-007",
      "signal": "advisory-formatting:prettier",
      "detector": "advisory-formatting",
      "category": "enforcement",
      "rung": "hook",
      "severity": "medium",
      "location": "CLAUDE.md:34",
      "claim": "\"Always run Prettier after editing\" is advisory prose with no executing mechanism.",
      "consequence": "Formatting is applied inconsistently across sessions and reviewers spend review time on whitespace.",
      "evidence": "CLAUDE.md:34 · no PostToolUse hook in settings.json · no lint-staged config",
      "remedy": "PostToolUse hook running prettier --write on the edited path; delete CLAUDE.md:34",
      "mechanicalCheck": {"type": "claude_md_contains", "pattern": "Always run Prettier after editing"},
      "status": "open",
      "firstSeen": 1,
      "resolvedIn": null,
      "resolvedBy": null
    }
  ]
}
```

`verificationSurface` is what `gameplan` reads to bind acceptance criteria to commands that actually exist in this repo — populate it honestly even when most rows come back `"runnable": false`. A row that says "no lint command exists" is itself useful information.

### How to produce this record

You (the agent running `check-playbook` or `kickoff`) do the part that requires judgment — reading the repo and deciding what's wrong, using the detector registry below to know what to look for. You do **not** hand-compute IDs, resolved status, or scores. Instead:

1. For each thing you find, produce a raw finding object: `{signal, detector, category, rung, severity, location, claim, consequence, evidence, remedy}`, plus a `mechanicalCheck` wherever the finding is objectively checkable (see `findings.md`). No `id`, no `status`, no `firstSeen` — those come from the merge.
2. Run `scripts/verify_resolution.py` against your raw findings file. This independently re-checks any previously-open, mechanically-checkable finding your draft doesn't mention, and reinstates it if the underlying problem is still there — see `findings.md` for why this exists (an adversarial test proved a pass could otherwise omit a still-broken finding and have it silently resolve).
3. Run `scripts/merge_pass.py` with the prior record (if any), your (now spot-checked) raw findings list, `waived.json`, and the list of categories you actually scanned. It handles ID inheritance by signal, marks resolved findings whose signal stopped firing, applies waivers, and computes every score. It writes the final `audits/NNN.json`.
4. Run `scripts/build_registry.py` to refresh `registry.json` from the files now on disk.

If the scripts aren't usable for some reason (missing Python, sandboxed environment), fall back to doing the merge by hand using the matching rule below — but say so, since it's the least reliable part of this skill to do without the script.

## The detector registry — closed, six categories

Every finding you raise must map to exactly one row below. If you find a real problem that doesn't fit any row, that's a sign the registry needs a new detector — note it as an observation rather than forcing it into the nearest category, since a bad fit is exactly how the category-overlap bug (see the skill's design history) creeps back in.

| Detector id | Category | Default rung | Detects |
|---|---|---|---|
| `root-file-length` | `context` | `prose` | `CLAUDE.md` long enough that instructions get dropped or skimmed — roughly past 200 lines, but judge by density, not just line count |
| `inferable-content` | `context` | `prose` | Material a competent agent would derive from the repo itself (standard language conventions, a file-by-file tour, anything `ls` and a `package.json` read already tell you) |
| `missing-gotcha` | `context` | `prose` | Non-obvious environment, build, or deploy behavior that isn't written down anywhere in the harness and would trip up a fresh session |
| `duplicated-instruction` | `context` | `prose` | The same requirement stated in two or more files, so one can drift out of sync with the other |
| `unscoped-rule` | `mechanism` | `scoped-rule` | A path- or domain-specific instruction (e.g. "frontend components should...") living in the root file instead of a scoped rule |
| `procedure-in-root` | `mechanism` | `skill` | A multi-step playbook or checklist sitting in `CLAUDE.md` that should be an on-demand skill instead |
| `roleplay-agent` | `mechanism` | `prose` | A subagent defined with a persona ("senior backend engineer") but no isolated context or distinct tool access to justify being a separate agent |
| `mcp-over-cli` | `mechanism` | `prose` | An MCP server connected for something a plain CLI call would do more cheaply and with a narrower surface |
| `advisory-formatting` | `enforcement` | `hook` | "Always run X" / "always format" with nothing that actually executes X |
| `advisory-prohibition` | `enforcement` | `hook` | "Never do X" with nothing that actually prevents X |
| `command-missing` | `verification` | `ci` | A test/lint/typecheck/build command mentioned in the harness that is undocumented, wrong, or doesn't run as written |
| `no-success-signal` | `verification` | `ci` | No machine-readable pass/fail signal an agent can act on to know whether it succeeded |
| `gameable-tests` | `verification` | `prose` | No instruction against weakening, skipping, or deleting tests, or hard-coding to pass a specific fixture |
| `no-evidence-requirement` | `verification` | `prose` | Nothing requires naming commands-and-results before claiming a task done |
| `git-destructive-open` | `permissions` | `permission` | `git reset --hard`, `clean -fd`, force-push, or similar destructive operations with no restriction |
| `secrets-writable` | `permissions` | `permission` | No deny-rule protecting production config, `.env` files, or credentials from being read or edited |
| `bash-overbroad` | `permissions` | `permission` | A blanket `Bash` allow with no narrowing to the commands actually needed |
| `mcp-unvetted` | `permissions` | `permission` | Connected MCP servers with no stated review or scope limitation |
| `no-scope-convention` | `bounds` | `prose` | Nothing asks for the smallest viable diff, names out-of-scope areas, or warns against unrelated refactors |
| `no-worktree-discipline` | `bounds` | `prose` | No guidance on parallel sessions or worktrees in a repo that shows signs of needing it (multiple active branches, a monorepo, evidence of concurrent agent use) |

### Disambiguation, if a finding seems to fit two rows

The remedy tells you the category, not the symptom:

- Fix is editing text in place → `context`
- Fix is moving an instruction to a different layer → `mechanism`
- Fix is a `settings.json` permission rule → `permissions`
- Fix makes the success signal itself trustworthy → `verification`
- Fix makes an existing requirement actually execute → `enforcement`
- Fix limits what may change → `bounds`

## signal — the fingerprint, and why it matters more than anything else here

**Format: `<detector-id>:<subject-slug>`.** The category is never part of the signal and never chosen by judgment at write time — it's looked up from the detector table above. This is the single most important rule in this file: if the same real-world problem could be classified two different ways on two different passes, the signal changes, the old finding silently resolves, and a new one opens with no fix having happened. That's a false "closed" in a system whose whole premise is that closure means something. Keeping category out of the signal and tied to the detector is what prevents it.

The matching rule (implemented by `merge_pass.py`, described here so you understand what it's doing):

1. A finding whose signal matches the prior pass inherits that finding's `id`, `status`, and `firstSeen`.
2. A new signal gets the next monotonic id (`HN-` prefix), allocated once, never reused or renumbered.
3. A previously-open finding whose signal doesn't fire this pass becomes `status: "resolved"`, with `resolvedIn` set to this pass number.
4. A signal present in `waived.json` becomes `status: "waived"` regardless of whether it still fires, and contributes nothing to score.
5. Rule 3 only applies within `categoriesScanned` — a partial or targeted pass must never resolve a finding in a category it didn't even look at.

## rung — the enforcement ladder

```
prose → scoped-rule → skill → hook → permission → ci → test
```

Weakest to strongest, left to right. `adjust` owns `prose` / `scoped-rule` / `skill`. `drill` owns `hook` / `permission` / `ci` / `test`. This is how work routes — by rung, not by category — because rungs partition cleanly with no overlap and no gap, where category-based routing left at least one finding class with no reachable command in an earlier draft of this design.

The selection rule when deciding (or re-deciding) a rung: **the lowest rung that actually holds.** A requirement sits on the wrong rung when a weaker rung would still be enforced (over-engineered), or when its current rung visibly isn't holding (under-enforced, which is the far more common finding).

## severity

- **high** — actively causes wrong or unsafe behavior today: destructive git unrestricted, no runnable test command, a root file bloated past the point instructions get dropped.
- **medium** — degrades reliability or burns context, no safety exposure.
- **low** — improvement or taste.

## Score — always derived, never eyeballed

```
weight        = { high: 15, medium: 6, low: 2 }
categoryScore = max(0, 100 − Σ weight(f) for every OPEN finding f in that category)
overall       = round(mean of the six category scores)
```

Resolved and waived findings contribute nothing. `merge_pass.py` computes this — don't estimate it in prose.

## Write rules

1. A command touches only the paths it declares in its own reference file. Nothing else.
2. Never mutate a prior `audits/` or `orders/*.attest-*.json` file. New pass → new numbered file. The two deliberate exceptions: `waived.json` (mutated in place, it's a settings file with no meaningful history) and order frontmatter (`gameplan`/`watch-film` update fields in place on the same order).
3. IDs are allocated once, monotonically, per project, never reused: `HN-` for playbook findings, `AT-` for attestation findings, `AC-` for acceptance criteria.
4. `registry.json` is always derived from the files on disk after any write — run `scripts/build_registry.py` rather than hand-editing it.
5. Reporting drift is not repairing it. If you find a malformed or stale state file while doing something else, say so and continue — don't silently reformat it as a side effect. Repair is its own explicit action.
6. **Detected, never asserted.** `adjust` and `drill` never write a finding's `status`. Only `check-playbook` (via `merge_pass.py`) closes a finding, by observing its signal stop firing. The only other legitimate way a finding stops counting is `decline`, and only with a written reason attached. This rule's weak point is that "observing" still means an agent looked and reported honestly — `scripts/verify_resolution.py` exists specifically to spot-check that assumption for the subset of findings where it's mechanically possible, rather than trusting it unconditionally. It's a partial guard, not a full one; say so if you're ever explaining this system's limits.
