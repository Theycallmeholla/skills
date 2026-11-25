# Split

Partition a plan into parallel lanes by disjoint write-sets and return a lane file plus one ready-to-launch brief per lane, or a reasoned "run this sequentially."

**Reads:** the plan (any origin); the repo tree when one is available
**Writes:** `.agent-smiths/<plan-slug>.json` (creates it; split is the only command that creates state)
**Stops at:** Never executes a task in the plan. Never edits the source plan. Never spawns or launches agents. The briefs are the deliverable; the human or the host environment launches them.

Phases: **1 Ingest** → **2 Predict write-sets** → **3 Conflict map** → **4 Partition or refuse** → **5 Write state** → **6 Report and briefs**

Before Phase 2, read [write-set-analysis.md](write-set-analysis.md). Phase 2 and Phase 3 run on it.

---

## Phase 1: Ingest and normalize the plan

**Find the plan.** Accept any of these and record which in `source`:

| Source | Looks like | `source_ref` |
|---|---|---|
| `pasted` | A task list or prose plan in the message | `inline` |
| `file:<path>` | A plan file in the repo (`PLAN.md`, `docs/plan.md`, a spec) | the path |
| `whiteboard` | A whiteboard snapshot (decisions list, spec, or board issue URL) | the issue URL or snapshot path |
| `handoff` | A handoff doc from the handoff skill | the doc path |

If the message points at a plan without containing it ("split the plan from earlier", "split the board"), find it: earlier in the conversation, the repo, or the URL. If it can't be found, ask for it. Don't reconstruct a plan from memory.

**Check the plan is ready to build.** Split decides how to divide work, not what the work is. If the plan still has open decisions ("TBD: which payment provider", "decide whether to keep the old API"), the affected tasks can't get a write-set. Say which tasks are blocked and what decides them. If the source is a whiteboard with open tickets, point back at the board; if most of the plan is undecided, stop here and recommend finishing the plan first (whiteboard or hot-seat). Don't guess the decision to make the split work.

**Extract tasks.** Number them `T1..Tn` in plan order. Keep each task's text verbatim; it goes into the lane file and the briefs unchanged so nobody loses the plan's wording. Also capture:

- explicit order ("after X", "once the schema lands", numbered phases)
- acceptance criteria or done-definitions, per task if the plan has them
- anything the plan says about tests, review, or deploy

**Make the slug.** Short kebab-case from the plan's title or goal (`auth-refactor`, `pricing-page-v2`). If `.agent-smiths/<slug>.json` already exists, don't overwrite it: lane files are history, and land may still need the old one. Use `<slug>-2`, `-3`, and put `"supersedes <old-slug>"` in `notes`.

**Detect the environment** and record it in `environment`:

- `claude-code` — there's a shell and a repo: you can run `git`, list files, and the user can open worktrees and launch subagents
- `chat` — no repo access, or files only arrive as pastes or uploads
- `unknown` — can't tell

The environment changes how deep the briefs go (Phase 6). It never changes the stop line.

**Capture the base.** In a git repo, record `repo_root` (`git rev-parse --show-toplevel`) and `base_commit` (`git rev-parse HEAD`). If the working tree is dirty (`git status --porcelain` not empty, ignoring `.agent-smiths/`), say so in the report: lanes branch from the last commit, so uncommitted work won't be in any lane. Recommend committing or stashing first. Don't do it yourself.

---

## Phase 2: Predict write-sets

For every task, build a write-set using [write-set-analysis.md](write-set-analysis.md) sections 1 through 3: concrete paths first, the hidden-writes table on every task, resource tokens, a confidence level.

With repo access, ground every prediction in the real tree. Search for how the last similar change was made and copy its footprint. A predicted path you didn't check is a medium-confidence guess, not a high one.

Without repo access, predict from the plan text and say every write-set is at most medium confidence. Tell the user the split will be safer if they paste the file tree (`git ls-files` output, or the relevant folders).

Resolve unknowns now (section 3: read code, then one batched question, then isolate). Don't carry an unexamined unknown into Phase 3.

Also note **semantic dependencies**: task B uses something task A creates (calls A's new function, renders A's new component, queries A's new column). That isn't a write conflict, but B can't start until A is merged. It becomes a `depends_on` edge.

---

## Phase 3: Build the conflict map

1. Run the overlap test (write-set-analysis section 4) on every pair of tasks. Each overlap is an edge: these two tasks can't be in different lanes running at the same time.
2. Add the semantic dependency edges from Phase 2. Mark them as order edges, not conflict edges.
3. **Find the hotspots**: files in three or more tasks' write-sets, or any one file that, if it stayed shared, would collapse otherwise-separate lanes into one. Route registries, barrels, lockfiles, schema files and global styles are the usual ones.

Show your work briefly in the report: which pairs conflict and over what file. That's what makes the verdict checkable.

---

## Phase 4: Partition, or refuse

### Group

Tasks joined by conflict edges belong in the same lane: take connected groups. Each group is a candidate lane. Keep plan order inside a lane.

### Break up hotspots before accepting a lane that's too big

A hotspot usually looks like it forces a merge but doesn't have to. Try these, in order:

1. **Owner plus sequencing.** Give the shared file to one lane. Every other lane that needs a change to it leaves that change out and describes it in its report. The owning lane does its own edit last, so the file is only edited in one place. Record this in `shared_files` with the owner and the reason.
2. **Seam lane.** Pull all edits to the hotspot into one small lane that runs after the others (it `depends_on` them): it registers the routes, adds the dependencies, regenerates the types. The other lanes stay parallel. Good for registries, lockfiles and codegen.
3. **Restructure the task** (an amendment, see below): "T4 adds its route in a new `routes/billing.ts` instead of editing `routes/index.ts`" turns a conflict into a disjoint write.

You may reword or split tasks *inside the lane file* to make this work (for example, T3 becomes T3a in L-001 and T3b in the seam lane). Keep the original text alongside your version and keep the `T` number so the trail back to the plan is clear. The source plan itself is never edited.

### Dependencies: fold, pin, or wait

When task B needs something task A creates, pick the cheapest of these:

1. **Fold.** If either task is small, put both in the same lane, A first. The dependency disappears and nobody waits. Usually the right call.
2. **Pin the interface.** If B only needs A's *shape* (a function signature, a component's props, an endpoint's request and response), write that shape into both briefs: exact path, export name, signature. Now both can run at once, and the merge joins them. Only do this when the shape is simple enough to state in a few lines and unlikely to change once A is built.
3. **Wait.** Otherwise B's lane `depends_on` A's lane and starts after A lands.

### Unknowns

A task with an unknown write-set gets its own lane that runs alone: first (if the other lanes build on it) or last (otherwise). Express it with `depends_on`. Never put it in parallel with anything. Record its `write_set` as `["**"]` with `write_set_confidence: low`, so the overlap test and land both treat it as touching everything. Other lanes' briefs don't list `**` under "Do not change": that lane isn't running beside them.

### Decide whether parallel is worth it

Every lane costs something: an agent's setup and context, a branch or worktree, a merge, a land check. Parallelism pays only when lanes are similarly sized and the total work is big enough. Give `sequential` when any of these hold, and say which one in `verdict_reason`:

- after partitioning there's one lane
- the biggest lane is roughly 70% or more of the total work (the others finish early and wait)
- the whole plan is small: about three tasks, or under roughly half an hour for one agent
- the lanes are so chained by `depends_on` that at most one runs at a time anyway
- most write-sets are low confidence and the user can't resolve them

`sequential` is a real answer, not a failure. Say it plainly with the reason, still write the lane file (one lane, so land can check the run), and still give one brief.

Fold tiny lanes. A lane worth a few minutes of work costs more in setup and merging than it saves; join it to another lane (any lane works, since disjoint write-sets combine safely). Prefer a lane on a related topic so the brief stays coherent.

Cap the split at **five lanes** that run at the same time. Beyond that, merging and checking cost more than the wall time saved. If the plan naturally splits wider, group the smallest lanes together, or run it in waves using `depends_on`.

### Verdict

- `parallel` — two or more lanes can start at once and nothing has to run alone
- `partial` — some lanes run in parallel, plus a lane that runs alone first or last (a seam lane, an isolated unknown, a dependency chain)
- `sequential` — one lane

`verdict_reason` is one falsifiable sentence: something land or the user can check. Good: "L-001 and L-002 share no files; routes/index.ts is owned by L-003, which runs last." Bad: "the tasks are fairly independent."

`est_savings` is a rough wall-time estimate ("~40% across 3 lanes"), or `null` when you can't size the tasks. Don't invent precision.

### Amendments

Collect plan changes that would make the split better: a task that should be split, a file that should be created instead of edited, an ordering the plan didn't state, an open decision that blocks a lane. Put each one in `suggested_amendments` as one sentence saying what to change and what it unlocks.

Who applies an amendment depends on who owns the plan:

- `whiteboard` source: word it as a ticket or board comment for the whiteboard to apply
- `handoff` or `file:` source: address it to the user, quoting the line to change
- `pasted`: address it to the user

The lane file can already reflect an amendment (the restructured task), but the source plan stays as it is.

---

## Phase 5: Write state

Create `.agent-smiths/` at the repo root if it doesn't exist (or in the working directory in chat), then write `.agent-smiths/<slug>.json` with the schema below. Validate it parses (`python3 -m json.tool` or `jq .`) before reporting. A lane file that doesn't parse breaks land.

If `.agent-smiths/` isn't in `.gitignore`, tell the user they may want to add it. Don't add it yourself: `.gitignore` is outside this command's write-set.

In chat with no filesystem, put the full JSON in a code block in the report and tell the user to save it as `.agent-smiths/<slug>.json` in the project so land can find it later.

### State schema

```json
{
  "version": 1,
  "plan_slug": "auth-refactor",
  "source": "whiteboard | handoff | pasted | file:<path>",
  "source_ref": "path, issue URL, or 'inline'",
  "created": "ISO-8601",
  "environment": "claude-code | chat | unknown",
  "repo_root": "/abs/path or null",
  "base_commit": "sha or null",
  "verdict": "parallel | sequential | partial",
  "verdict_reason": "one falsifiable sentence",
  "est_savings": "e.g. '~40% wall time across 3 lanes' or null",
  "suggested_amendments": [
    "Plan changes that would improve the partition. Never applied to the source plan."
  ],
  "shared_files": [
    { "path": "src/routes.ts", "owner": "L-003", "reason": "L-001 and L-002 both register routes; L-003 owns it and runs last" }
  ],
  "lanes": [
    {
      "id": "L-001",
      "title": "Backend auth endpoints",
      "source_tasks": ["T1", "T3a"],
      "tasks": ["task text lifted from the plan, in order (reworded tasks keep the original in parentheses)"],
      "write_set": ["src/api/auth/reset.ts", "src/api/auth/__tests__/reset.test.ts"],
      "write_set_confidence": "high | medium | low",
      "read_set_notes": "free text; reads are unrestricted, this is context only",
      "depends_on": [],
      "branch": "agent-smiths/auth-refactor/L-001 or null",
      "brief": "the full ready-to-launch prompt for this lane",
      "status": "open",
      "landed_check": {
        "checked": null,
        "actual_files": [],
        "violations": [],
        "notes": ""
      }
    }
  ],
  "notes": "unstructured drawer: judgment calls, user corrections, supersedes"
}
```

`repo_root`, `base_commit`, `source_tasks`, `write_set_confidence` and `branch` were added to the original spec so land can attribute changes to lanes and trace lanes back to plan tasks. Everything else is as specified.

### Write rules (every command follows these)

1. Each command touches only the paths it declares. Everything else is off limits.
2. **land** never edits lane definitions, write-sets or briefs. It writes only `landed_check` blocks and `status` fields.
3. Lane IDs (`L-001`, `L-002`, ...) are allocated once per plan, in order, and never reused.
4. Reporting drift isn't repairing it. A command that finds a malformed lane file says what's wrong and stops. No silent migration.
5. The source plan is read-only to this system. Amendments go in `suggested_amendments`.

New lane files always start with every lane `"status": "open"` and an empty `landed_check`.

---

## Phase 6: Report and briefs

### Report

Lead with the verdict. Keep it short; the details live in the lane file.

```
**Verdict:** partial. 3 lanes, est. ~35% faster than one agent.
**Why:** L-001 and L-002 share no files; routes/index.ts is owned by L-003, which runs last.

| Lane | What | Writes | Confidence | Starts |
|---|---|---|---|---|
| L-001 | Reset-password API | src/api/auth/reset.ts, its test | high | now |
| L-002 | Reset email template | src/emails/reset/** | high | now |
| L-003 | Wire routes + deps (seam) | routes/index.ts, package.json, lockfile | high | after L-001, L-002 |

**Conflicts found:** T1 and T4 both edit routes/index.ts → moved to seam lane L-003.
**Suggested plan changes:** (only if any)
**Lane file:** .agent-smiths/auth-refactor.json
**Next:** launch L-001 and L-002 now. When they finish, run `/agent-smiths land`.
```

For `sequential`, replace the table with one line saying why, and give one brief.

### Briefs

Each lane gets one self-contained brief: an agent that has never seen this conversation must be able to do the lane from the brief alone. Put each brief in its own code block in the report (so it copies cleanly) and in the lane's `brief` field.

Every brief has these parts:

```
You are working lane L-00X of a split plan "<plan title>". Other agents are working other lanes in parallel. Staying inside your lane is what keeps everyone's work mergeable.

## Goal
<one or two sentences: what this lane delivers>

## Tasks
<the lane's tasks, verbatim from the plan, in order, with acceptance criteria if the plan had them>

## Setup
<environment-specific, see below>

## You may change
<the write-set, one path or token per line>

## Do not change
<every path in other lanes' write-sets and every shared file this lane doesn't own, explicitly listed>

If finishing a task needs a change outside "You may change", don't make it. Finish everything else, then describe the change you needed (file, what, why) in your report. Another lane or a later step will make it.

## Done when
<acceptance criteria; at minimum: tasks complete, this lane's tests pass, everything committed on your branch>

## Report back
- the list of files you changed (`git diff --name-only <the commit you branched from>...HEAD`, plus any uncommitted files)
- any change you needed outside your lane, and why
- anything you were unsure about
```

**Setup, by environment** (this is the only part that adapts):

- **claude-code:** one git worktree per lane, so parallel agents never share a branch, index or working tree (agents in one checkout collide even when their files don't):
  ```
  git worktree add <repo_root>/.claude/worktrees/<slug>-L-00X -b agent-smiths/<slug>/L-00X <base_commit>
  cd <repo_root>/.claude/worktrees/<slug>-L-00X
  ```
  Use the repo's own worktree convention if its CLAUDE.md or contributing docs name one. Record the branch name in the lane's `branch` field. Write the brief so it works as a Task-tool or subagent prompt: absolute paths, no "as we discussed."
- **chat / unknown:** the brief is paste-ready for a fresh session. Tell the agent to work on its own branch named `agent-smiths/<slug>/L-00X` (or its own copy of the project) and to return its changed-file list. Set `branch` to that name.

For a lane with `depends_on`, the Setup section says what must be merged first and to branch from the merged result, not from `base_commit`.

### Stop

The report and briefs are the end of split. Don't launch the lanes, start a task, or edit the plan, even if the user is clearly about to do it next. If the user asks you to launch them, that's a separate request outside this skill: say so, then do it only if they confirm.
