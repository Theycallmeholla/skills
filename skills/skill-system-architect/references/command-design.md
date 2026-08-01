# Command Design

Load this at Phase 3, after the state schema exists.

## Derive, don't brainstorm

Commands are the transitions on the state. With the schema in hand, most of the map falls out of four questions:

1. **What creates state?** Something has to write the first record. This is usually the system's entry point and the thing the no-argument menu leads with when state is missing.
2. **What changes the source based on state?** The record says what's wrong; something acts on it. This is where most of the system's value is.
3. **What re-evaluates?** Something re-runs the assessment and produces the next version, so progress is visible as a diff.
4. **What reads without writing?** Reports, comparisons, menus. Cheap to add, and they're what makes the system feel like a system to the user.

Everything past those four is a specialization: the same transition with a narrower target, a different medium, or a different intensity. Specializations earn a command only when their playbook genuinely differs — see *Splitting* below.

## The five fields

Every command needs all five before it's real.

| Field | Rule |
|---|---|
| **Verb** | One word if possible. Imperative. It's the literal string the user types. |
| **Category** | Groups the table and menu. 3–6 categories total across the system. |
| **Reads** | Exact state paths, or "nothing". |
| **Writes** | Exact state paths, or "nothing". |
| **Stops at** | The boundary it must never cross. |

### Naming

- **Verbs, not nouns.** `audit`, not `auditor`. `polish`, not `polishing`.
- **The verb should imply the boundary.** `critique` obviously doesn't rewrite; `plan` obviously doesn't build. A well-chosen verb enforces the stop boundary for free.
- **No two commands whose names are synonyms.** If you need a sentence to explain the difference between `check` and `verify`, the user will need one too, and they'll guess wrong.
- **Reserve the plainest verb for the most common job.** It's what people type when they don't remember the menu.

### "Stops at" is the load-bearing field

Without it, commands drift into each other: an audit quietly starts fixing, a planner quietly starts building, and within a few sessions the system is one blob with several entrances.

Write it as a prohibition, not a description:

- ✅ "Never modifies the source file. Never writes a new version."
- ❌ "Focuses on analysis."

The command file restates this in its closing line, because the last thing in context is the thing most likely to hold.

## Splitting

**Merge when:** two commands read the same state, write the same state, and stop at the same boundary. They're one command with a parameter.

**Split when:** a single playbook contains "if the user wants X, do this; if they want Y, do that." That's two commands sharing a file.

**Intensity variants** (`bolder` / `quieter`, `expand` / `compress`) earn separate commands only when each has a materially different procedure. If the only difference is a number in the prompt, it's one command with an argument.

**Target or platform variants** are *not* new commands. Same verb, different loaded guidance, expressed as a suffix file:

```
references/audit.md          the base playbook
references/audit.native.md   loaded instead when the target is a native app
```

The commands table shows one row with both references listed. The router picks based on state or an obvious signal, not on the user typing a different word.

## Shared procedure

When several commands need the same non-trivial procedure — a quality floor, a verification pass, an output convention — it becomes its own reference file that each of them loads. It does **not** go in the router.

The test: is it a *belief the whole system holds* (router) or a *procedure some commands run* (shared reference file)? Beliefs are short and cost nothing on every invocation. Procedures are long and should only load when needed.

Name shared files so they read as non-commands — `craft-floor.md`, `output-contract.md` — so nobody mistakes one for a playbook.

## The command file skeleton

Every command file, however long, has the same five parts. Specify the headers in the architecture spec; leave the bodies for `skill-creator`.

```markdown
# <Command>

<One sentence: what it does and what it returns, written as a contract.>

**Reads:** <state paths, or "nothing">
**Writes:** <state paths, or "nothing">
**Stops at:** <the prohibition>

## Phase 1: <name>

<Numbered, imperative steps.>

### Cadence
<Only if it asks the user questions: how many per round, when to stop asking,
what never to ask. Most command files leak into being annoying right here.>

## Phase 2: <name>

## Output

<The literal shape of what comes back. Named sections, exact ordering,
code-block-or-not. Not "a summary" — the structure.>

## Confirm and stop

<Restate the prohibition in one line.>
```

Length is nearly free — reference files load one at a time, only when their command runs. A 40KB playbook next to a 500-byte one is normal and fine. Do not compress a playbook to look tidy; compress the router instead.

## Build order

Order the commands for the spec by dependency, not importance:

1. Whatever **writes** the state first — nothing can be tested until state exists.
2. Whatever **reads** it and does the main job — this is where the system proves its worth.
3. The re-evaluation pass — makes progress visible.
4. Read-only conveniences (menus, reports, comparisons) — last, because they're the easiest to get right and the easiest to change.

Say this order explicitly in the spec. Users otherwise build the fun command first and discover it has nothing to read.
