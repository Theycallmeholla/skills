---
name: agent-smiths
description: >-
  Split a plan into parallel agent lanes by disjoint write-sets, write a ready-to-launch brief per
  lane, then verify after the agents run that each stayed in its lane. Works on any plan (pasted task
  list, plan file, whiteboard snapshot, handoff doc) against a codebase. Use when the user wants to
  parallelize a plan, run several agents or sessions at once, fan work out, generate agent prompts
  from a plan, or check that parallel work merged cleanly. Also use on "can these run in parallel",
  "will the agents step on each other", "agents keep working over each other", "two agents touched the
  same file", "was this worth parallelizing". Commands: split, land. Not for creating plans
  (whiteboard) or writing handoff docs (handoff). It decides how work splits and whether the split
  held; it never does the work itself.
---

# Agent Smiths

Split plans into parallel agent lanes; verify the lanes held.
**Commands: split · land** (bare invocation shows the menu; never auto-run)

## Doctrine

- **Parallelism is a property of write-sets, not tasks.** Two tasks can run at once only if they can't change the same file or resource. Reads are free; writes partition.
- **"Run it sequentially" is a first-class verdict**, not a failure. Splitting work that collides costs more than it saves.
- **The source plan is read-only.** Changes to it are suggested in the lane file, never applied. Whoever owns the plan (the user, the whiteboard) applies them.
- **An unknown write-set conflicts with everything.** It runs alone, never beside another lane.
- **Briefs are the deliverable.** This skill never executes plan tasks, launches agents, merges branches or edits code.

## Commands

| Command | What it does | Reads | Writes | Reference |
|---|---|---|---|---|
| split | Partition a plan into lanes with declared write-sets, plus one brief per lane (or a reasoned sequential verdict) | the plan, repo tree | `.agent-smiths/<slug>.json` (creates) | [references/split.md](references/split.md) |
| land | Check what each lane actually changed against what it declared; flag collisions and violations; update statuses; say what can merge or start next | `.agent-smiths/<slug>.json`, git | `landed_check` + `status` only | [references/land.md](references/land.md) |

Both commands use the shared procedure in [references/write-set-analysis.md](references/write-set-analysis.md). Read the command's reference before doing anything; it tells you when to load the shared one.

## Routing

1. **No argument** (bare `/agent-smiths`) → read [references/routing.md](references/routing.md) and show the menu. Don't run a command.
2. **A command named or clearly implied** → read its reference and follow it.
   - split: "split", "parallelize", "shard", "fan out", "break this into agents", "can these run in parallel", a plan pasted with a question about running it at once
   - land: "land", "reconcile", "check the merge", "did they stay in their lanes", "the agents are done", "two agents touched the same file"
3. **Ambiguous between the two** → ask once, in one line.
4. **Anything else that clearly belongs to this skill** → split. It's the common job.

## State

One JSON file per plan at `.agent-smiths/<plan-slug>.json` in the user's project (never in the skill folder). Schema and write rules: [references/split.md](references/split.md), Phase 5. No registry. land defaults to the most recent lane file with open lanes.

## Boundaries with other skills

- Plan not decided yet (open questions, TBDs) → that's whiteboard or hot-seat work. split says which tasks are blocked and stops short of guessing.
- After land says "landed", correctness is still unproven. Point to tests, review, or the prove-it skill if it's installed.
- Launching the agents is outside this skill. If the user asks for it after split, treat it as a separate request and confirm first.
