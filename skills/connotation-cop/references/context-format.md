# CONTEXT.md Format

## Structure

```md
# {Context Name}

{One or two sentences: what this context is and why it exists.}

## Language

**Order**:
A confirmed request from a customer to buy specific items.
_Avoid_: purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: client, buyer, account
```

## Rules

- **Be opinionated.** When multiple words exist for one concept, pick the best and list the rest under `_Avoid_`. A glossary that lists synonyms without ruling settles nothing.
- **Keep definitions tight.** One or two sentences. Define what it IS, not what it does — behavior belongs in code and specs.
- **Only project-specific terms.** General programming concepts (timeout, retry, handler) don't belong even if used everywhere. Test before adding: is this concept unique to this domain, or would it mean the same thing in any codebase? Only the former belongs.
- **Group under subheadings** when natural clusters emerge; a flat list is fine until then.
- **No implementation details, ever.** The moment `CONTEXT.md` mentions a table name or a library, it has started becoming a spec, and specs rot differently than glossaries.

## Single vs multi-context repos

**Single context (most repos):** one `CONTEXT.md` at the root. Start here; split only when two areas of the code genuinely use the same word to mean different things.

**Multiple contexts:** a `CONTEXT-MAP.md` at the root lists the contexts, where each lives, and how they relate:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments

## Relationships

- **Ordering → Billing**: Ordering emits `OrderPlaced`; Billing consumes it to open an invoice draft
- **Ordering ↔ Billing**: shared types for `CustomerId` and `Money`
```

## Which structure applies

- `CONTEXT-MAP.md` exists → multi-context; read the map to find the right glossary
- only root `CONTEXT.md` exists → single context
- neither exists → create a root `CONTEXT.md` lazily when the first term is resolved

In a multi-context repo, infer which context the current topic belongs to; if genuinely unclear, that ambiguity is itself a domain question — ask.
