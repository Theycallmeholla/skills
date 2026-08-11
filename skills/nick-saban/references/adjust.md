# Adjust

Works the findings whose remedy sits on the `prose`, `scoped-rule`, or `skill` rungs: trims what's paid for on every session, relocates instructions to the layer where they belong, and adds the non-obvious material that's genuinely missing.

**Reads:** latest `audits/` record filtered to those three rungs; `notes.md`; `references/ladder.md`
**Writes:** `CLAUDE.md`, `.claude/rules/`, `.claude/agents/`, `.claude/skills/<name>/SKILL.md` (a stub only — never a complete skill), `notes.md`
**Stops at:** Never writes executable code, hooks, CI config, or permission rules — that's `drill`'s job, and if a finding actually needs one of those, say so and point at `drill` rather than reaching for it. Never marks a finding resolved. Never authors a full skill body — write the stub (name, draft description, the prose being relocated) and hand off to `skill-creator` for the rest. Never writes `waived.json` directly — on a decline, load `references/decline.md` and follow it.

## Phase 1: Select

Take the `context`, `mechanism`-as-prose, and any `skill`-rung findings from the latest audit record. These are wording and placement problems, not enforcement problems — the whole batch can usually be worked in one pass, unlike `drill`'s per-mechanism gate.

## Phase 2: Plan the relocations

For each finding, decide the concrete edit:

- **Bloat / inferable content** → delete. Don't paraphrase it smaller; if it doesn't need to be said, remove it entirely. A shorter `CLAUDE.md` that says less is usually the correct fix, not a compression exercise.
- **Missing gotcha** → add, tersely, in the place someone would actually look for it.
- **Duplicated instruction** → pick the one authoritative location (usually the more specific file) and delete the other copy, or replace the duplicate with a pointer if both locations genuinely need to reference it.
- **Unscoped rule living in the root file** → move it into a new or existing file under `.claude/rules/`, scoped to the path or domain it actually applies to.
- **Procedure that should be a skill** → write the stub only (see the stop condition), and tell the user this needs a follow-up `skill-creator` session to finish.
- **Roleplay agent with no real isolation** → either give it genuine isolated context/tools that justify it as a subagent, or fold its instructions back into the main flow and remove the agent definition — whichever the finding's remedy actually called for.

## Phase 3: Show the diff

Even though this command can move faster than `drill`, still show the actual before/after for `CLAUDE.md` and any new or moved rule files before writing, especially when a deletion is involved — the user should see what's leaving, not just what's arriving.

## Phase 4: Apply

Write the changes. If the user declines a specific relocation mid-review, load `references/decline.md` for that one finding rather than silently skipping it and moving on — an unaddressed finding needs a recorded reason, not just an absence.

## Phase 5: Point at the next check

Don't claim anything is fixed. Say what changed and that `check-playbook` is what actually confirms it.

## Output

```
## Adjust — worked <N> findings

**Deleted:** <what, and why it was safe to remove>
**Relocated:** <what moved from where to where>
**Added:** <what gotcha or missing material went in, and where>
**Skill stub written:** <if applicable — name and next step>

### Next

**Do this:** `check-playbook`
Nothing above is resolved yet — these edits are changes, and only the next pass
observing the signals stop firing turns them into resolutions.

**Instead, if <a finding here needs a hook/permission rather than wording>:** `drill <id>`
<name the specific finding and why prose won't hold it>
```

## Confirm and stop

Writes no executable code, hooks, or permissions. Never authors a complete skill. Marks nothing resolved.
