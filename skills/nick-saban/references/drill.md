# Drill

Works the findings whose remedy sits on the `hook`, `permission`, `ci`, or `test` rungs — moving each requirement down to the lowest rung that actually holds, and deleting the prose it supersedes. In `permissions` scope, works the repo's whole defensive surface as one system rather than one finding at a time.

**Invocation:**
- `drill <finding-id>` — work one specific finding.
- `drill permissions` — establish or harden the complete permission surface as a single coordinated package. Open findings are *inputs* to this, not its boundary. It runs against a repo with twenty findings, two, or none at all — including a fresh setup where `check-playbook` has never run.

**Reads:** latest `audits/` record (if one exists); `verificationSurface`; `notes.md`; `references/ladder.md`; `references/permission-baseline.md` in `permissions` scope
**Writes:** `.claude/hooks/**`, `.claude/settings.json`, `.github/workflows/**` (or wherever CI is actually configured), `package.json#scripts` or `Makefile`, `notes.md`
**Stops at:** Never writes anything without showing the exact file diffs, the test matrix result, and getting approval — one connected system per round. Never weakens or removes an existing guard. Never writes application tests — drafts one and stops. **Never edits application source**; when a finding's real fix lives there, hand off per Phase 3c instead of continuing. **Never claims a mechanism enforces more than its tested surface**, and never describes a partial command denylist as resource protection. Never marks a finding resolved; that's `check-playbook`'s job alone. Never writes `waived.json` directly — if the user declines a proposed mechanism, load `references/decline.md` and follow it instead of just moving on silently.

## Why this one is slower than `adjust`

A hook that's subtly wrong doesn't just fail to help — it can block every future session until someone notices and removes it. A `settings.json` permission rule that's too broad does nothing; one that's too narrow can lock the user out of their own repo mid-task. This is the entire reason `drill` gets a stricter approval discipline than `adjust`: the failure modes here are worse than doing nothing, where `adjust`'s worst case is a slightly-off sentence.

Slower does not mean more rounds. Reviewing one coherent defense once is a better review than approving fifteen fragments of it across ninety minutes — fragmented approval produces fatigue, and fatigue produces rubber-stamping.

## Phase 1: Select the scope

**`drill <id>`** — that finding alone. Everything below still applies to it.

**`drill permissions`** — the full surface. Findings are one input among several:

1. Every open finding where `category` is `permissions`, **plus** every open finding where `category` is `enforcement` and `rung` is `hook` or `permission`. Enforcement-category findings routinely *are* permission work filed under a different category; excluding them is how a pass closes four of five routes to the same resource.
2. Independently of any finding, inspect the live surface: `settings.json` allow/deny, every registered hook and what it actually matches, protected paths, git restrictions, data and database locations, secret handling, paid-API routes, MCP and alternate tool surfaces, existing waivers and overrides.
3. `references/permission-baseline.md` — the standing default policy, which applies whether or not a finding named it.

An absent finding is not evidence of an absent gap. This scope exists precisely so the permission surface can be established up front rather than discovered one hole at a time by successive audits.

## Phase 2a: Policy in resources, enforcement at the strongest available layer

**Define policy in terms of protected resources and forbidden operations. Enforce each policy at the strongest available layer. Where only command-text inspection is available, normalize and support explicit command families, test them mechanically, and state all unsupported surfaces as residuals. Never claim full resource protection from a partial command denylist.**

Start with the table, not the commands:

| Resource | Forbidden operations | Operations that stay allowed |
|---|---|---|
| `data/`, `*.sqlite` | delete, move, truncate, overwrite | read, query, copy-for-backup |
| git history | history rewrite, force-push, stash/reflog destruction | branch, commit, dry-run, `--force-with-lease` |
| `.env`, credentials | read, write | — |
| paid APIs | any billable call without approval | dry-run, local fixtures |

Then place each policy on the strongest layer that can actually hold it:

1. **Tool deny / approval rules** — `settings.json` deny entries, per-tool approval gates. Strongest, because they act on the tool call itself and don't depend on parsing anything.
2. **Filesystem or sandbox isolation** — permissions, read-only mounts, keeping the resource outside the workspace. Holds against every tool at once, including ones the harness never sees.
3. **Hook enforcement for supported command families** — a PreToolUse hook covering an explicitly enumerated, normalized set of command forms.
4. **Explanatory instructions** — prose telling the agent what not to do. Real, but unenforced.
5. **Explicit recorded residuals** — the surfaces nothing above covers, written down.

Layer 3 is where the honesty has to be exact. A hook receives command *text*. It cannot in general determine what a command will do: variables, symlinks, interpreters, custom scripts, command substitution, and indirect execution all defeat text inspection, and MCP or other tools may never reach the hook at all. So a hook covers **named command families you enumerated and tested** — `rm`, `mv`, `find -delete`, `git reset --hard` — after normalizing quoting, flag order, and path forms. It does not cover "destroying `data/`."

Write that distinction into the prose the mechanism ships with. "Blocks `rm`/`mv`/`find` deletion of `data/` from Bash; `python -c`, MCP filesystem tools, and shell scripts are not covered" is a true sentence. "Protects `data/` from deletion" is not, and a false guarantee is worse than a missing one — the user stops watching the thing they were told was handled.

## Phase 2: Pick the rung (re-confirm, don't just trust the record)

The finding already suggests a rung, but confirm it's still the right one given `ladder.md`'s "lowest sufficient" rule — a finding recorded weeks ago might be better served by a lighter mechanism than the one that seemed necessary at the time, or the repo might have grown enough that something originally fine as a hook now needs to be a CI gate to hold across contributors.

## Phase 2c (permissions scope): Discover first, then ask only what's undecidable

Load `references/permission-baseline.md`. It carries the standing default policy — protect secrets, gate paid calls, restrict destructive git, prevent broad staging, protect data destruction, deny untrusted alternate tool surfaces. Those defaults apply unless the owner says otherwise; don't re-derive them per repo and don't ask whether the user wants secrets protected.

**Find the facts yourself before asking anything.** Everything below is visible in the repo, and asking the owner to enumerate it is asking them to do your reading:

- **Data paths** — `*.sqlite`/`*.db` files, `data/`, dump and export directories, whatever `.gitignore` already protects, database paths in config
- **Paid services** — API clients in source, keys in `.env.example`, billable CLIs in `package.json#scripts`, anything the repo's own docs call metered
- **MCP and alternate tools** — `.mcp.json`, `settings.json`, global config; every tool offering shell, filesystem, or network access
- **Existing overrides** — env-var escape hatches, `--force`-style conventions, comments describing an intended bypass
- **Secret files** — `.env*`, credential files, keychains, service-account JSON
- **What's already guarded** — existing hooks, existing deny rules, and what they actually match

Then present findings and ask only what's genuinely the owner's call:

```
Detected:
- data/ holds two SQLite databases (app.db, sessions.db)
- DataForSEO and Anthropic clients are billable; both invoked via bin/seo.mjs
- Two MCP servers provide filesystem access: desktop-commander, filesystem
- No override convention exists yet

Decisions needed:
1. Trust or deny those two MCP tools in this repo?
2. Destructive git and data deletion — blocked outright, or override-gated?
3. If override-gated, what should trigger it?
4. Any path in the detected list that ISN'T sensitive, or any I missed?
```

That last question is how the owner corrects your detection cheaply, instead of producing the inventory from scratch.

Ask in **one round**. Do **not** ask about regexes, shell quoting, matcher syntax, hook file layout, or normalization — those are engineering decisions this command owns. Asking the owner to adjudicate a regex is how ninety minutes disappears and how the review stops being a review.

## Phase 3: Draft the mechanism

Write the actual hook script, permission rule, or CI step — not a description of one. For a hook, include what event it binds to and exactly what it runs. For a permission rule, show the literal `settings.json` diff. For a test, draft it and explicitly hand it to the user rather than adding it yourself (see the stop condition above) — name the specific behavior it should assert and let them place it in their suite.

Pair the new mechanism with the removal of the prose it **supersedes** — which is narrower than "the prose about this topic."

**Delete:**
- Instructions telling the agent to do what the mechanism now does automatically
- Any sentence claiming enforcement the prose never provided ("never run X" with nothing preventing X)
- Coverage claims the mechanism doesn't actually deliver
- Steps obsoleted by the mechanism

**Keep:**
- *Why* the policy exists — "paid API calls bill the live account" survives the guard that enforces it, because a future reader deciding whether to loosen the rule needs the reason
- The override procedure, if one exists
- Known residuals — the surfaces the mechanism doesn't cover
- Anything the mechanism can't say for itself

Installing enforcement should not erase the explanation for the policy. A repo whose rules are all mechanism and no rationale is one where the next person deletes a guard because nothing recorded what it was for. What has to go is any sentence that *falsely implies the prose itself enforces something*.

## Phase 3b: Adversarial matrix over the whole package — before approval, not after

A guard that passes the examples its own author wrote has demonstrated nothing except that its author was consistent. In `permissions` scope the matrix covers the **entire package at once**, not each mechanism in isolation — the point is to find the route around the defense, and routes don't respect which file you're editing.

Write a **package manifest** and run `scripts/test_guard_matrix.py --manifest`. The manifest lists every mechanism in the package — hooks, `settings.json` deny rules, denied MCP/alternate tools — and the script returns one package result. Never report one mechanism's result as the package's.

Two properties of that script matter to how you write the manifest:

- **It verifies wiring, not files.** Each hook is checked as *registered* — right event, right matcher, command pointing at the expected file, file present and executable — and then invoked exactly as `settings.json` invokes it. A hook that passes every case while nothing calls it **fails the package**. That failure mode (`guard passes 20/20` above `settings.json never calls it`) is the same false confidence this whole phase exists to prevent, one level down.
- **Every case carries context.** `cwd`, `env`, and `tool` are part of the case, because a command's meaning depends on where it runs. `cd sub && rm -rf data` targets `sub/data`, not the root `data/` — the case that actually tests the root directory from a subdirectory is `rm -rf ../data` with `"cwd": "sub"`. A case that passes for the wrong reason is worse than a missing one; it's a green row that means nothing.

**Passing the manifest is not proof of coverage.** It proves the enumerated families behave as specified against the mechanisms as currently wired. The script prints supported families and uncovered surfaces alongside the counts, and in strict mode refuses to pass a mechanism that declares no enforcement layer, no supported families, or no residuals — an empty `uncoveredSurfaces` needs a written justification, because "nothing is uncovered" is a strong claim and should have to be made deliberately.

Work the dimensions that apply, per protected resource — the unit is the resource and its forbidden operations, not the command you first thought of:

| Dimension | Ask |
|---|---|
| Operation spellings | for deletion of `data/`: `rm -rf data`, `rm -rf "data"`, `rm -rf data*`, `rm -rf $PWD/data`, `rm -rf ./data/`, `mv data data-old`, `find data -delete`, `truncate` |
| Git destruction forms | `reset --hard`, `reset HEAD~1 --hard`, `switch -f`, `checkout .`, `restore .`, `clean -xfd`, `stash clear`, `reflog expire`, `push --force` |
| Invocation aliases | `node bin/x.mjs`, `npx x`, bare `x`, an npm script wrapping it |
| Flag placement | `-xfd`, `-fdx`, split flags, flags after operands, `--flag=value` vs `--flag value` |
| Shell composition | `cd sub && …`, pipes, subshells, `$(…)`, `;`-chains |
| Wrappers | `npm run`, `tsx`, `node -e`, a shell script that calls it |
| Direct imports | importing the underlying client/library instead of going through the CLI at all |
| Global options | `git -C <dir>`, `git -c key=value`, env-var equivalents |
| Alternate tools | MCP shell, MCP filesystem, browser terminal — anything from the tool-surface map |
| False positives | the string appearing in a commit message, a doc, an `echo`, a test fixture |
| Allowed equivalents | dry runs, read-only forms, `--force-with-lease` — things that must NOT be blocked |
| Regression | everything the previous version of this guard correctly allowed and blocked |

Record it on the package:

```json
"coverage": {
  "resources": [], "supportedCommandFamilies": [], "enforcementLayer": [],
  "alternateTools": [], "falsePositiveCases": [], "knownResiduals": []
}
```

A foreseeable bypass has exactly three acceptable outcomes, and "mention it in passing while claiming the guard works" is not among them:

1. **Fix it** before asking for approval — and prefer fixing it a layer up (Phase 2a) over adding a pattern. One `settings.json` deny rule beats six regexes and cannot be spelled around.
2. **Narrow the claim** so the prose matches the mechanism: name the supported command families and the layer, not the resource.
3. **Record it as a residual** in `knownResiduals`, and say it out loud in the approval ask.

If you find yourself adding a seventh pattern for the same resource, stop — that's the signal the policy is on the wrong layer, not that the regex needs another branch.

A mechanism whose stated guarantee is wider than its tested coverage is worse than no mechanism, because the user stops watching for the thing it doesn't actually stop.

## Phase 3c: Stop if the fix crosses into application code

This command's writes are hooks, permissions, CI, and build scripts. When working a finding reveals that the real fix is in application source — moving a secret out of a config module, changing how a client is constructed, rewriting a credential precedence chain — **stop, and hand off**:

1. Say plainly that the finding can't be fixed within `drill`.
2. Say why: the change belongs to code the user owns, not the harness.
3. Name the next mode — an ordinary implementation task, or `gameplan <slug>` if it deserves a contract first.
4. Get explicit approval to leave this command before doing any of it.
5. Record the handoff in `notes.md`. Do not perform the application work inside `drill`.

> "HN-006 can't be fixed from here — the fix is in `src/lib/google.ts`, which is application code this command doesn't write. Run `gameplan move-google-secrets`, or tell me to drop out of the skill and just implement it."

A one-word "yes" to some earlier question is not approval for this. The command boundary is the whole reason a user can trust what `drill` will and won't touch, and a boundary that dissolves under momentum isn't one.

## Phase 4: Test the package — before approval, and again after writing

Before asking for approval, run the matrix against the proposed mechanisms and validate `settings.json` parses. A mechanism you've verified is a materially different approval ask than one you haven't touched.

Then **run the same matrix again against the files actually on disk after writing.** A matrix that passed against a draft says nothing about what got installed, and "the written rules claimed coverage the live hook didn't have" is the exact failure that makes this non-negotiable. Report the post-write run, not the pre-write one.

## Phase 5: Approve — one connected system per round

The unit of approval is **one coherent system**, not one file and not one mechanism. A permission package touching `settings.json`, two hooks, an override rule, and the prose they supersede is one round, because it is one defense. Reviewing a defense in fragments produces a worse review, not a safer one — ninety minutes of approving individual clauses isn't diligence, it's how people learn to approve without reading.

Still one round per *system*: a permission package and an unrelated CI gate are two rounds.

The package is only reviewable if it arrives whole. Show, together:

- The policy decisions from Phase 2c, as decided
- Every file changing, with its exact diff
- What becomes blocked, and **at which layer**
- What stays allowed (the false-positive cases you tested)
- The override procedure, if any
- The full matrix result, including supported families and uncovered surfaces
- Every known residual, stated plainly rather than buried

Striking an item from the package is a revision of the same round, not a new one — expect to iterate once or twice inside a round and don't restart the approval each time.

Outside `permissions` scope, single mechanisms still go one at a time; the batching rule is about connected systems, not about lowering the bar generally.

## Phase 6: Write, then re-test

On approval:

1. **Back up to `.claude/nick-saban/backups/<ISO-timestamp>/`**, preserving relative paths — never a `.bak` file beside the live one. An adjacent `guard.sh.bak` is repo clutter that gets staged by accident, can carry stale credentials, and is exactly the kind of file a future scan mistakes for an active mechanism. Ensure the backups path is in `.gitignore`, and that nothing registers or scans it.
2. Write the whole package, removing only the prose it supersedes (Phase 3).
3. Re-run the package manifest against the live files (Phase 4).
4. Report anything that now fails, anything unwired, and anything still uncovered.

Do not touch any finding's status in the audit record — that's `check-playbook`'s, once, afterward.

## Output

For a single-finding drill:

```
### <finding id>: <one-line description of the mechanism>

**Adds:** <file path and what it does>
**Removes:** <the CLAUDE.md line(s) it replaces>

[the actual diff]

Approve to write this?
```

For a `permissions` package — one block, everything at once:

```
## Permission package

**Policy decided:** <the Phase 2c answers, one line each>

**Changes** (<N> files)
[every diff, in full]

**Blocked, and where:**
| Operation | Layer | Mechanism |
|---|---|---|

**Still allowed:** <the false-positive cases, tested>
**Override:** <procedure, or "none">

**Matrix:** <pass>/<total> — supported families: <list>
**Not covered:** <every residual: interpreters, MCP tools, unguarded surfaces>

Approve this package?
```

After writing:

```
Wrote <N> mechanisms across <M> files. Post-write matrix: <pass>/<total>.

**Residual, uncovered:** <list — or "none identified", which is itself a claim
worth being sure about>

### Next

**Do this:** `check-playbook`
Nothing here marks anything resolved — the next pass does that by observing the
signals stop firing. Run it once now, against the whole package.

**Instead, if <a residual above needs an owner decision>:** `decline <signal>`
<name the residual and what accepting it means>
```

## Confirm and stop

One connected system per approval round — never one file at a time within a system, never two unrelated systems in one round. Never weakens an existing guard. Never writes an application test outright. Never asserts a finding is resolved. **Never describes a command-family guard as protecting a resource.**
