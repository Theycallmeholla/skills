# ADR Format

ADRs live in `docs/adr/`, numbered sequentially: `0001-slug.md`, `0002-slug.md`. Create the directory lazily with the first ADR. To number a new one, scan for the highest existing number and increment.

## Template

```md
# {Short title of the decision}

{1–3 sentences: the context, what was decided, and why.}
```

That's the whole template. An ADR can be one paragraph — the value is recording *that* a decision was made and *why*, not filling out sections. A heavyweight template is why most teams stop writing ADRs by week three.

## Optional sections — only when they earn their place

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`) — when decisions get revisited
- **Considered options** — when the rejected alternatives are worth remembering (someone WILL suggest GraphQL again in six months)
- **Consequences** — when non-obvious downstream effects need calling out

## What qualifies (given the three-part bar in SKILL.md)

- **Architectural shape.** "Monorepo." "Event-sourced write model, Postgres read projections."
- **Integration patterns between contexts.** "Ordering and Billing communicate via events, not synchronous HTTP."
- **Technology choices with lock-in.** Database, message bus, auth provider — the ones that take a quarter to swap, not every library.
- **Boundary decisions.** "Customer data is owned by the Customer context; others reference by ID only." Explicit no-s are as valuable as yes-s.
- **Deliberate deviations from the obvious path.** "Manual SQL instead of an ORM because X." These stop the next engineer from "fixing" something deliberate.
- **Constraints invisible in the code.** "No AWS — compliance." "Sub-200ms responses — partner contract."
- **Non-obvious rejections.** The considered-and-rejected option whose rejection reasoning would otherwise be relitigated.
