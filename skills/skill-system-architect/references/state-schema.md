# The State Layer

Load this at Phase 2, before naming any command. This file decides whether there is a system at all, and if there is, what its memory looks like.

## The gate test

A system exists only if you can complete this sentence with something concrete:

> "Command A writes ______, and command B is more useful because it can read it."

Run all three checks. All three must pass.

1. **Persistence** — does something survive the end of a session? If every command starts from a blank slate and ends by handing text back to the user, there is no state and no system.
2. **Asymmetry** — do at least two commands relate to that artifact differently? If every command reads it and none writes it, it's a config file, not a system's memory. If every command writes and none reads, they're independent tools that happen to log.
3. **Consequence** — does reading it change behavior? "Command B prints what A wrote" is not composition. B should *do something different* because of what A found.

### When the gate fails

Say so directly. The useful failure message names which of the three checks failed and why:

- *Persistence failed* → these are stateless transformations. They may still deserve one skill with modes, but modes are not a system; say that plainly.
- *Asymmetry failed* → the shared thing is configuration or reference material. It belongs in the skill directory as a reference file, not in a state layer.
- *Consequence failed* → the artifact is a log. Logs are fine; they just don't make commands compose.

Then offer the honest alternatives: separate skills with sharpened, non-overlapping descriptions; or a re-scope, since the real system is often one level up (the workflow these tasks sit inside) or one level down (the single artifact they all edit).

**Never invent state to pass the gate.** A registry nothing reads is worse than no registry — it adds setup cost, drift, and a migration burden in exchange for nothing.

## Where state lives

**In the user's project, not in the skill directory.** The skill is a read-only package that may be installed in a shared or system location; the state is per-project and mutable.

```
<user's project>/
└── .<system-name>/
    ├── registry.json
    └── <entities>/
        └── <slug>/
            ├── …
```

Consequences worth stating in the spec:

- The system must behave sanely when `.<system-name>/` does not exist yet. Decide which command initializes it, and make the no-argument menu lead with that command when it's missing.
- State is per-project by design. Two projects using the system share nothing. If the user expects cross-project memory, that's a different design and needs to be flagged.

## Shape

Two files do almost all the work.

### The registry — a cheap index

Read on every invocation, so it stays small. It holds the identity of each tracked entity and just enough denormalized summary to drive a menu without opening anything else.

```json
{
  "version": 1,
  "entities": [
    {
      "slug": "kebab-case-stable-id",
      "title": "human label",
      "source": "path/to/the/real/thing",
      "created": "ISO-8601",
      "updated": "ISO-8601",
      "currentVersion": 3,
      "<domain-summary-field>": 2
    }
  ]
}
```

The domain-summary field is what makes the no-argument menu smart — an open-issue count, a score, a staleness flag. Pick exactly one or two. Every field here is a field that can go stale, so earn each one.

### The record — the atom of the system

One per meaningful unit of work. This is where the actual findings live, and it is the single most important thing to get right, because it's the thing every future command will speak.

```json
{
  "version": 1,
  "created": "ISO-8601",
  "items": [
    {
      "id": "XX-001",
      "category": "closed-enum-value",
      "severity": "high | medium | low",
      "location": "where in the source this points",
      "claim": "the specific assertion, written so it could be wrong",
      "status": "open | resolved | accepted",
      "resolvedIn": 2,
      "resolvedBy": "what changed",
      "acceptedReason": null
    }
  ]
}
```

## Five schema rules

**1. IDs are stable and never reused.** `XX-004` refers to the same finding forever, across every version. This is what lets a later command say "you closed six of nine, these three are still open" without re-deriving anything. Allocate monotonically per entity.

**2. Categories are a closed enum, fixed now.** Everything downstream — filtering, grouping, scoring, comparing two entities — depends on the vocabulary being finite and stable. An open-ended `category: string` field produces forty near-synonyms within a month and nothing can group them. If the domain already has a taxonomy in prose, lift it verbatim; that's a solved problem you don't need to re-solve.

**3. Status needs an "accepted" value.** `open` / `resolved` is not enough. Some findings are deliberate choices the user has already made, and without a way to record "yes, I know, leave it," every command re-flags them forever and the system turns into a nag. This single field is the difference between a tool people keep using and one they abandon.

**4. Claims must be falsifiable.** Require a field that states the specific consequence — the concrete failure, the hostile reading, the thing that breaks. A finding you can't write a consequence for isn't a finding, and requiring the field enforces that at the schema level instead of hoping a playbook says it convincingly enough.

**5. Every schema needs one unstructured drawer.** A `notes.md` per entity, free text. Judgment calls, user corrections, context that doesn't fit a field. Without it people jam prose into structured fields and the enums rot.

## Versioning

Prefer **append-only**. New pass → new version file; never mutate a prior one.

- Cheap to implement, no migration logic, and the history is the diff.
- Lets a command answer "what changed since last time" by reading two files.
- Costs disk, which is free.

Mutate in place only when the entity has no meaningful history (a settings file, a cache).

## Write rules

State these in the spec and have every command file cite them:

1. A command declares in its own header exactly what it reads and writes. Undeclared paths are untouchable.
2. Never mutate a prior version. New pass → new file.
3. IDs are allocated once, monotonically, per entity. Never reused, never renumbered.
4. The registry is derived — any command that writes a record updates the index in the same operation.
5. **Reporting drift is not repairing drift.** A command that notices stale or malformed state says so and continues. It does not silently migrate, reformat, or clean up as a side effect of doing something else. Repair is its own command, run on request.

Rule 5 is the one that gets violated first and hurts most: a user runs a small command and discovers it rewrote six files.

## Sizing

| System | State |
|---|---|
| 2–4 commands, one entity type | A single JSON or markdown file. No registry, no directory. |
| 5+ commands, many entities | Registry plus per-entity directories. |
| Many entities, expensive reads | Registry plus records plus a denormalized summary field per entity so the menu never opens a record. |

Start at the smallest shape that passes the gate. Growing a single file into a registry later is a contained change; splitting a badly-designed record schema is not.
