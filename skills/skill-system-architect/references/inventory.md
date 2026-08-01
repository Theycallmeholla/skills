# Consolidating Existing Skills

Load this at Phase 0 when the user has several skills that should become one system. Do this before the interview — what's already there constrains the design and often answers half the questions.

## 1. Enumerate

List every candidate skill with its `name`, its full `description`, and a one-line read of what it actually does. Include skills the user didn't mention but that touch the same domain — those are the collision risks.

Separate **authored** from **installed**. Only the user's own skills are candidates for folding; third-party and stock skills are fixed constraints to design around, not material to absorb.

## 2. Cluster by shared artifact, not by topic

The instinct is to group by subject matter — "these four are all about writing." That produces a folder, not a system.

Group instead by **what they'd hand each other**. Two skills belong in the same system when the output of one is a useful input to the other. Two skills about the same topic that never exchange anything belong in separate skills with sharper descriptions.

For each proposed cluster, complete the gate sentence from `state-schema.md`:

> "A writes ______, and B is more useful because it can read it."

Clusters that can't complete it aren't systems. Say so rather than forcing them together — a forced merge produces a skill with a vague description that triggers unreliably for all of its jobs instead of reliably for one.

## 3. Find the collisions

Compare descriptions pairwise within each cluster. Look for:

- **Duplicate triggers** — two skills claiming the same phrases. The model picks nondeterministically and the user experiences it as "sometimes it works."
- **Near-duplicate scope** — same job, different framing, usually from being written months apart.
- **Orphan triggers** — phrases in a description that no part of the body actually handles.
- **Stale duplicates** — an old version still installed alongside its replacement.

Report collisions explicitly. They're often the actual reason the user wants a system, even if they described the problem differently.

## 4. Decide each skill's fate

Every candidate gets exactly one:

| Fate | When |
|---|---|
| **Fold** | Becomes a command. Its playbook becomes `references/<verb>.md`, largely intact. |
| **Merge** | Two or more become one command. Reconcile the playbooks; note which content is dropped. |
| **Keep** | Stays standalone. Add a boundary sentence to both descriptions naming the other. |
| **Retire** | Superseded, stale, or never used. Recommend deletion; don't delete anything. |

Record the reason for each. The user will want to defend at least one, and "it doesn't share the state" is a better answer than "it seemed redundant."

**Folding preserves the playbook.** The point of consolidation is coherent triggering and shared state, not rewriting content that already works. Content changes are a separate decision, made deliberately, not smuggled into a migration.

## 5. Sequence the migration

Fold in dependency order (see `command-design.md`), and add one guarantee to the spec: **at every step, the skills not yet folded still work.** A migration that breaks the user's daily driver halfway through gets abandoned halfway through.

Concretely:

1. Build the system with the state-writing command first.
2. Fold one skill at a time; retire the original only after its command works.
3. Update the router `description` at each fold so triggers move over with the command.
4. Retire stale duplicates last, once nothing points at them.

## 6. What to put in the spec

Beyond the standard sections, a consolidation spec carries:

- **The inventory table** — every candidate, its fate, and the reason.
- **The collision report** — overlapping triggers found, and how each is resolved (absorb / delimit / defer).
- **The migration sequence** — ordered, with the "still works at every step" guarantee stated.
- **What gets dropped** — content in merged skills that didn't survive, listed explicitly so the user can object now rather than discover it later.
