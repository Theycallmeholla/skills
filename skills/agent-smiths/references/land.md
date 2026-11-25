# Land

After the lane agents run, check each lane's actual changed files against its declared write-set, flag anything that crossed a line, update statuses, and say what's still open and what can start next.

**Reads:** `.agent-smiths/<plan-slug>.json`; git (branches, worktrees, diffs), or changed-file lists the user supplies
**Writes:** `landed_check` blocks and `status` fields in that same file. Nothing else.
**Stops at:** Never merges, rebases, cherry-picks or resolves conflicts. Never modifies code. Never edits lane definitions, write-sets, briefs or the source plan. It reports; the human decides what to do.

Phases: **1 Locate** → **2 Gather actual changes** → **3 Adjudicate** → **4 Write results** → **5 Report**

Read [write-set-analysis.md](write-set-analysis.md) section 5 (the near-miss rubric) before Phase 3.

`land` with nothing new since the last check is the status view: same reads, report only, no writes.

---

## Phase 1: Locate the lane file

- A slug was given → `.agent-smiths/<slug>.json`.
- No slug → the most recently `created` lane file that still has a lane with `status: open`. If there are several candidates from the last day or so, list them and ask which one.
- No `.agent-smiths/` folder, or no lane file has open lanes → say so, and suggest `/agent-smiths split` if they meant to start one. Stop.
- In chat, if the user can't share the file, ask them to paste its contents.

**Validate before doing anything else.** The file must parse, have `version: 1`, and every lane must have `id`, `write_set`, `status` and `landed_check`. If anything is malformed, say exactly what (file, field, problem) and stop. Don't repair it: a hand-fixed lane file is how wrong write-sets slip through unnoticed. The fix is the user's call, or a fresh split.

---

## Phase 2: Gather actual changes per lane

The goal is a list of changed files **attributed to the lane that changed them**. Use the best source available, top to bottom, and record which one you used in each lane's `landed_check.notes`.

### A. Per-lane branches (the normal case after a Claude Code split)

For each lane with a `branch`:

1. Check the branch exists: `git rev-parse --verify <branch>`. Missing → the lane hasn't run, ran somewhere else, or was merged and its branch deleted. Leave it `open` and say so; if the user says it did run, check it from the agent's reported file list instead (source B).
2. Find where the lane started. The first entry in the branch's reflog is the commit it was created from:
   ```
   start=$(git reflog show --format=%H <branch> | tail -1)
   git merge-base --is-ancestor "$start" <branch> && echo ok
   ```
   This never looks at the dependency lanes, so it still works after they've been merged, squash-merged, or had their branches deleted.
   No reflog (the branch came from another clone), or the check fails (the branch was rebased) → fall back to `start=$(git merge-base <base_commit> <branch>)`. For a lane with `depends_on` that fallback is too early, so its dependencies' files will look like its own: don't flag a file one of its dependency lanes legitimately changed, and say in notes that attribution for this lane is approximate.
3. Committed changes, net:
   ```
   git diff --name-status -M "$start" <branch>
   ```
   Net means a change that was made and later reverted doesn't count. That's what lets a fixed violation clear on the next run. An `R` (rename) line counts as a change to both the old and the new path.
   If the lane merged another branch into itself (`git log --merges "$start"..<branch>` prints anything), the net diff also contains what it merged in. Use the lane's own commits instead, and say so in notes:
   ```
   git log --first-parent --no-merges --format= --name-only "$start"..<branch> | sort -u
   ```
4. Uncommitted changes, if the lane has a worktree. Find its path, then check it:
   ```
   git worktree list --porcelain | awk -v b="refs/heads/<branch>" '/^worktree /{w=substr($0,10)} $0=="branch "b{print w}'
   git -C "<worktree path>" status --porcelain
   ```
   Uncommitted files count as changed. Note them: the agent may not be finished, and they won't be in a merge yet.

### B. One shared checkout (agents didn't use branches)

Git can show the total change (`git diff --name-only <base_commit>` plus `git status --porcelain`) but not which lane made which change. Ask the user for each agent's "files I changed" list from its report. Then cross-check:

- a file in the total diff that no lane's report claims → **unattributed**: report it as a stray of unknown origin
- a file a report claims that isn't in the total diff → the report is wrong or the change was reverted. Note it; don't count it.

Say in the report that attribution here relies on what the agents reported, so it's weaker than branch-based checking, and recommend worktrees for next time.

### C. No git

Use the changed-file lists the user pastes, one per lane. Same cross-check isn't possible; say so.

### Drop noise

Before adjudicating, remove `.agent-smiths/**`, gitignored files and OS junk (write-set-analysis section 5). Don't list them anywhere.

### A lane with zero changes

Not run yet, or ran and did nothing. Either way it stays `open`. Don't mark it `landed`: an empty lane hasn't proven anything.

---

## Phase 3: Adjudicate

For each lane, split its actual files into **inside** (matches an entry in its own `write_set`, using the overlap test from write-set-analysis section 4) and **outside**. A lane whose `write_set` is `["**"]` (an unknown that split ran alone) has no outside files; it's only checked for collisions. Then:

1. **Cross-lane collisions first.** Any file changed by two or more lanes is a collision for every lane involved, whatever the write-sets say. These are the merges that conflict or quietly overwrite each other, so they go at the top of the report. One exception: two lanes ordered by `depends_on` (directly or through a chain), where the later one started from the earlier one's merged work, didn't run at the same time. A file both changed is then judged against write-sets like any other file, not as a collision.
2. **Classify every outside file** with the near-miss rubric: `violation`, `predictable-miss` or `stray`. Use the lane's tasks to judge: a lockfile change in a lane whose task added a dependency is a predictable miss; a lockfile change in a lane whose tasks never touch dependencies is a stray.
3. **Shared files.** A change to a file in `shared_files` by any lane other than its `owner` is a violation, even if no other lane touched it.
4. **Agent-reported needs.** If an agent's report says "I needed to change X but didn't" (the brief tells them to do this), list it under the lane as an open need, not a violation. These are the work the seam lane or a later step still owes.

### Status for each lane that has changes

| Result | Status |
|---|---|
| any collision or violation | `violated` |
| only predictable-misses or strays, or none | `landed` (misses and strays listed as warnings) |
| user said this lane was dropped | `abandoned` (only on the user's say-so) |

`landed` means the lane stayed inside its boundary. It does **not** mean the code works. Land doesn't judge whether the tasks were done well; tests, review and the prove-it skill (if installed) do that. Say this once in the report, not per lane.

Don't move a lane from `violated` back to `landed` on a later run unless the offending changes are actually gone from its branch (reverted, or moved to another lane by the user). Re-check, then update.

---

## Phase 4: Write results

For each lane you checked and that had changes (or that the user abandoned), update **only** these fields:

```json
"status": "landed | violated | abandoned",
"landed_check": {
  "checked": "<ISO-8601 now>",
  "actual_files": ["every attributed changed file, sorted"],
  "violations": [
    "src/routes.ts: collision, also changed by L-002",
    "package-lock.json: violation, owned by L-003 (shared file)"
  ],
  "notes": "source: per-lane branch. Warnings: yarn.lock predictable-miss (L-001 added zod). Needs: route registration for /reset left for L-003. 2 files uncommitted."
}
```

`violations` holds collisions and violations only, one line per file: path, class, why. Predictable-misses, strays, open needs, uncommitted files and the evidence source go in `notes`.

Lanes with no changes: leave their fields alone. Don't touch lane titles, tasks, `write_set`, `brief`, `depends_on`, `branch`, or any top-level field. Then re-validate the file parses.

If a re-check finds nothing new since the last `checked` time, write nothing. Report only.

---

## Phase 5: Report

Lead with whether it's safe to merge.

```
**Land check: auth-refactor**: 2 landed, 1 violated, 1 open
**Safe to merge now:** L-002
**Fix before merging:** L-001

**Collisions**
- src/routes.ts: changed by L-001 and L-003 (owner: L-003)

**Per lane**
| Lane | Status | Changed | Outside its lane |
|---|---|---|---|
| L-001 | violated | 4 files | src/routes.ts (collision) |
| L-002 | landed | 3 files | none |
| L-003 | landed | 2 files | yarn.lock (predictable miss) |
| L-004 | open | none yet | n/a |

**Still owed:** route registration for /reset (L-001 asked for it, L-003 should do it)
**Can start now:** L-004 (its dependencies L-002 and L-003 have landed)
**Merge order (suggested):** L-002, L-003, then L-001 once the collision is sorted
**Next:** fix L-001's routes.ts change (move it to L-003, or drop it), then run `/agent-smiths land` again.
```

How to fill the parts that need judgment:

- **Safe to merge now:** `landed` lanes whose `depends_on` lanes are all landed or already merged.
- **Can start now:** `open` lanes with no changes yet whose dependencies have all landed. This is what makes land useful mid-run, not just at the end.
- **Merge order:** dependency order first; within that, lanes that own shared files last; collided lanes after the collision is resolved. It's a suggestion. Don't run it.
- **Fixing a violation** is the user's call. Give the options in one line (move the change to the owning lane, revert it, or accept it and re-split the rest), with your pick. Don't make the change.
- **Predictable misses** are feedback for the next split. If the same kind keeps showing up (lockfiles, barrels), suggest the plan or the next split route that file category to a seam lane.

When every lane is `landed` or `abandoned`, say the plan is fully landed and the lane file is now a record. Don't delete it.
