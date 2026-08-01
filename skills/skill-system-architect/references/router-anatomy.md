# Router Anatomy

Load this at Phase 4. Produces the `SKILL.md` skeleton that goes in the spec.

## What the router is

A dispatcher, not a document. It holds doctrine, a commands table, and routing rules — and nothing else. Every procedure lives in a reference file loaded on demand.

This asymmetry is the whole architecture: **adding a command is cheap, adding to the router is expensive.** The router is paid for on every single invocation; a reference file is paid for only when its command runs. A well-built system with twenty-plus commands can have a router under 100 lines.

## Frontmatter

**There are two dialects, and picking the wrong one fails validation.** Establish the target before writing the spec.

**Claude account / Cowork skills** — strict allow-list. Only these keys are permitted:
`name`, `description`, `allowed-tools`, `compatibility`, `license`, `metadata`.
Anything else (`version`, `user-invocable`, `argument-hint`) is rejected at packaging time.

```yaml
---
name: <kebab-case, matches the directory name>
description: >
  <the trigger surface — see below>
allowed-tools:
  - Bash(node scripts/*)
---
```

**Claude Code plugin skills** — accept the richer set, and `argument-hint` is what surfaces the subcommand menu at the call site:

```yaml
---
name: <kebab-case, matches the directory name>
description: >
  <the trigger surface — see below>
version: <semver>
user-invocable: true
argument-hint: "[cmd|cmd · cmd|cmd · cmd] [target]"
allowed-tools:
  - Bash(node .claude/skills/<name>/scripts/*)
---
```

When targeting account skills, the subcommand menu has to live in the **body** instead — put the command list in the first line or two after the heading, where it's read on every invocation. The system still works; the menu just isn't in the metadata.

If the system may be distributed both ways, write the spec against the account dialect (the stricter one) and note the plugin-only fields as an additive layer.

### `description` — the trigger surface

**This is the only thing the model sees when deciding whether to load the skill.** It is not a summary. It is a dense net of match targets, and it is the single highest-leverage field in the entire system.

Build it in four layers:

1. **The capability sentence** — what the system does, using every verb the commands cover. Every command contributes its verb here or it will only ever fire when typed explicitly.
2. **The domain sentence** — the nouns. What kinds of things this operates on, enumerated generously.
3. **The complaint sentence** — how users phrase the *problem* rather than the solution. This is the layer most descriptions skip and the one that catches the most real invocations, because people describe symptoms ("it never does what I mean", "these keep overlapping") rather than naming a tool.
4. **The boundary sentence** — "Not for X." Prevents firing on adjacent work owned by another skill.

Write it long. A dense 150-word description is correct; brevity here costs invocations.

### `argument-hint`

The call-site menu. Group by category with `·` separators so the shape of the system is visible in one line:

```
"[shape|init · audit|critique · polish|harden · report] [target]"
```

### Collision check

Before finalizing, compare the `description` against the user's other installed skills. Two skills whose descriptions overlap produce nondeterministic triggering, and the user experiences it as "sometimes it works."

When overlap is found, resolve it explicitly in the spec:

- **Absorb** — the other skill becomes a command in this system and is retired.
- **Delimit** — both survive with a boundary sentence added to each description naming the other.
- **Defer** — this system drops the overlapping capability entirely and points at the other skill.

Silently shipping an overlap is not one of the options.

## Body sections

```markdown
## <Doctrine>          the beliefs every command holds. Short. Named for the domain.
## Setup               what to load/run once per session, and the instruction not to redo it.
## Commands            the table.
## Routing             the four cases.
## State               one paragraph + a pointer to the state reference file.
```

### Doctrine vs. procedure

The recurring judgment call. Test each candidate block:

- **A belief the whole system holds** → router. Short, cheap, load it every time.
- **A procedure some commands run** → its own reference file that those commands load.

Doctrine bloat is the most common way a good router turns bad: everything that felt important got promoted, and now the dispatcher costs more than the playbooks it dispatches to.

### The commands table

| Command | Category | Description | Reads | Writes | Reference |
|---|---|---|---|---|---|

The Reads/Writes columns are unusual and worth keeping. They make the composition visible at a glance — a reader can see that one command's Writes is another's Reads — and they make a disconnected command obvious, since its row is conspicuously empty.

### Routing — four cases, always these four

1. **No argument** → load `references/routing.md`, present its context-aware menu. **Never auto-run a command.**
2. **Explicit or clearly implied command** → load its reference (suffix variant if applicable) and follow it. If two commands plausibly fit, ask once, then proceed.
3. **Otherwise** → treat it as general work in the domain and name the default command here.
4. **Aliases and deprecations** → declared inline, so old names keep working and the reason is visible.

Case 1's "never auto-run" matters more than it looks. A bare invocation means "what should I do?", and answering it by doing something is how a system loses trust early.

### The no-argument menu

`references/routing.md` makes the menu evidence-based rather than static. Read the registry, then lead with **two or three** picks, each with a one-line reason drawn from actual state:

- State missing → lead with whatever initializes it, one line on why, still show the rest.
- Open items on the current entity → lead with whatever resolves them, naming the count.
- Never evaluated → lead with whatever evaluates.
- Otherwise → group by category and present the table.

Two or three pointed picks with the exact string to type, then the full menu below. The recommendation is the lede; the menu is the fallback.

## Size budget

| File | Target | Why |
|---|---|---|
| `SKILL.md` | under ~120 lines | Loaded on every invocation. |
| `description` | dense, no filler | Every word is a match target. |
| `references/<command>.md` | whatever it takes | Loaded one at a time, only when invoked. |
| `references/routing.md` | short | Loaded on bare invocations, which are frequent. |
| registry file | small | Read every session. |

## Packaging

Distribution, when the system is ready to share:

```
.claude-plugin/
├── plugin.json         { name, version, description, skills: "./.claude/skills/" }
└── marketplace.json    wraps it for install-by-URL
```

A plugin may contain exactly one skill; that's a normal and common shape. Note it in the spec as an open decision rather than building it up front — packaging is trivially added later and pointless before the system works.

A frequently-used subcommand can be promoted to a standalone top-level shortcut once usage shows which ones deserve it. Defer that decision until the system has been used.
