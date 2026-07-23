# Architecture & Design Checklist

Architecture findings tend to be the most consequential — they cost the most to fix later — but also the most subjective. Calibrate by impact, not by aesthetic preference.

## 1. Layering

Most non-trivial apps benefit from at least these layers:
- **Transport** (HTTP handlers, CLI parsers, message consumers): translate external requests into internal calls
- **Domain / business logic**: the actual rules of the system
- **Persistence**: how data is stored and retrieved

What to flag:
- **SQL queries inline in HTTP handlers.** No separation between transport and persistence.
- **Business logic in templates / view code.** Makes it untestable.
- **Handlers calling other handlers.** Indicates the domain logic was never extracted.
- **"Models" that are just ORM objects with no behavior.** Common, not always wrong, but if all logic ended up in services because models couldn't hold it, the layer is doing nothing.
- **Direct database access from anywhere in the codebase.** Makes the data access patterns impossible to reason about as a whole.

The layering doesn't need to be explicit packages or directories — but if you can't draw a layer diagram from reading the code, that's a finding.

## 2. Coupling

Heuristics for "too coupled":

- **Module imports >15 other modules** of similar level: probably a god module
- **Circular dependencies**: tooling can detect (`madge`, `pylint`). Always a layering violation.
- **Implicit dependencies via global state**: module A only works if module B was initialized first, with no explicit declaration
- **Shared mutable singletons**: registries, caches, "managers" — touching any of them couples you to anything else that does
- **Knowledge of internals**: module A reaching into module B's private state. In languages without enforced visibility (Python, JS), look for usage of conventionally-private names (`_foo`, `__private`).

To map coupling: for each module, count what it imports and what imports it. The skewed ones (imports everything / is imported by everything) are the hot spots.

## 3. Boundaries & trust

Where does external input become trusted?

- **Input validation at the edge.** Validation should happen once, at the layer that takes external input (HTTP handler, queue consumer, CLI). Internal functions can then assume validity.
- **Re-validation deeper in the stack** indicates the boundary isn't trusted. Either it should be (refactor), or each layer is doing defensive validation (verbose but safer).
- **Validation by stringly-typed shapes.** Functions taking `dict` / `any` / `Object` and pulling out fields — type system can't help you. Prefer typed structures.
- **Trust crossing service boundaries.** When this code calls an internal service, does it trust the response? Internal services compromised by attackers (or by bugs) shouldn't lead to your service trusting bad data.

## 4. State management

Where does state live? How does it flow?

- **Multiple sources of truth** for the same fact (cached in three places, never invalidated together)
- **State transitions implicit and unenforced** — should this entity be transitioning from `pending` to `cancelled`? The code allows it; there's no rule preventing it.
- **State changes scattered across many places** — finding "who moves orders to shipped state" requires grepping across the codebase
- **Optimistic vs pessimistic locking** chosen without analysis: race conditions on inventory deduction, double-charges, etc.

For each important state machine in the system, ask: can I draw the diagram from the code? If not, it's because the rules are emergent rather than declared.

## 5. Configuration

- **Hardcoded values that should be config.** Production URLs, threshold values, feature flags as boolean literals.
- **Config sprawl.** Twelve places to change one thing. New deployments break because someone updated 11 of 12.
- **No environment separation.** `if (env === 'prod')` scattered through code, with each branch testable only in production.
- **Config schema.** Is there a single declared schema for what config keys exist? Or is it discovered by grepping the codebase?
- **Secrets in config.** Should be referenced (env vars, secret manager), not embedded. See security.md.

## 6. Concurrency model

Map out: what's concurrent, what's serial, what synchronizes the boundary?

- **Async language used synchronously** (e.g., Node code that awaits everything serially when concurrency was available)
- **Sync language pretending to be async**: callbacks-of-callbacks, manual thread pools that should be a queue
- **Implicit assumptions about ordering** between concurrent operations (race conditions)
- **Locks held too long / too broadly**: process-level lock around every database write
- **Deadlock potential**: nested locks acquired in inconsistent order

In distributed contexts:
- **Cross-service transactions** assumed atomic that aren't (sagas missing)
- **Idempotency on retries**: if the operation runs twice, does it have the right effect?
- **Event ordering** assumed but not guaranteed by the queue/transport

## 7. Error handling philosophy

Inconsistency here is itself a finding:

- Some functions throw, others return error tuples, others return `null` or `undefined`. Pick one model.
- Errors lose context as they bubble up: stack traces show the throw site, but not the request ID, the user, the input that caused it.
- "Catch-all" handlers at the boundary (good) vs catch-and-swallow scattered through internals (bad).
- Recoverable vs unrecoverable errors not distinguished — code retries everything or nothing.

## 8. Modularity

- **Module API surface.** Does each module export 5 well-defined things, or 50 random helpers?
- **Internal modules vs public APIs.** In a library or service: is it clear what consumers can rely on vs. what's implementation detail?
- **Versioning.** If the project has versioned APIs (HTTP, gRPC), is there a story for breaking changes? Is the current version an artifact of "v1 is what we shipped" rather than a deliberate contract?

## 9. Cross-cutting concerns

Things that should be uniform but often aren't:

- **Logging**: structured, with request IDs, consistent levels?
- **Metrics**: any? Where? How exposed?
- **Tracing**: correlation IDs propagated across service calls?
- **Authn/authz**: applied at one place (middleware) or scattered (every handler does its own check)?
- **Input validation**: one library/pattern, or different per module?
- **Internationalization**: bolted on later vs designed in?

Inconsistency in cross-cutting concerns is more painful than the absence of any one of them.

## 10. Service / process boundaries (for distributed systems)

If the project spans multiple services:

- **Boundaries match domain boundaries**, or are they driven by org chart / accident?
- **Chatty interfaces**: services that need to call each other 5+ times to handle one request — that's a wrong-cut boundary
- **Shared databases across service boundaries** (each service hits the same DB) — usually a tightly-coupled monolith pretending to be services
- **Distributed monolith signs**: services that all must deploy together, or that share so much state they can't evolve independently
- **API contracts**: documented? Versioned? Changes communicated?

## 11. Frontend architecture

If applicable:

- **Component composition**: deeply nested, prop-drilled chains vs. composition. Component tree depth >10 levels usually indicates refactoring opportunity.
- **State management consistency**: some state in Redux, some in Context, some in component state, some in URL — what determines which?
- **Side effects**: where do they live? Components vs. hooks vs. middleware?
- **Routing**: declarative? Lazy-loaded for code-splitting?
- **Server-side rendering / hydration mismatches**: real concern for Next.js / Nuxt / SvelteKit apps

## 12. Data architecture

- **Schema migration story.** Is there a migrations system? Are schemas versioned alongside code?
- **Backward compatibility.** Can you deploy code that doesn't yet expect a new column, then add the column, then deploy code that uses it? Or are deployments coupled to migrations in lockstep?
- **Hard deletes vs. soft deletes.** Audit trail concerns; reversibility; cascading.
- **PII storage.** Encrypted at rest? Subject to right-to-erasure? Logged separately?
- **Schema evolution.** JSON columns / unstructured fields used as escape hatch — fine in moderation, dangerous as primary storage.

## 13. Testing architecture

- **Test pyramid balance**. Mostly unit, some integration, few E2E? Or upside-down?
- **Test isolation**. Tests that fail when run in parallel, or that depend on order, indicate hidden coupling.
- **Test database strategy**. Real DB with rollback? In-memory mock? Containerized? Each has tradeoffs; flag if missing entirely.

## 14. Build & deploy architecture

- **Reproducible builds**: same commit → same artifact?
- **Build vs runtime separation**: are dev tools shipping to production?
- **Deployment unit**: container? Single binary? Multiple processes? Is the choice intentional?
- **Rollback strategy**: blue/green? Canary? Or "redeploy last known good and pray"?
- **Health checks and readiness probes**: present and meaningful?

---

## Calibrating architecture findings

Architecture findings are easy to over-deliver. To avoid that:

- **Tie every architecture finding to a concrete current pain or near-future risk.** "Module X imports Y modules" is not a finding. "Module X imports Y modules including the database layer, which is why the route handlers can't be unit tested without spinning up Postgres" is a finding.
- **Don't recommend the architecture you would have built.** Recommend the smallest change that addresses the actual problem.
- **Account for stage.** A startup MVP should not have the same architecture as a 10-year-old enterprise system. "Premature abstraction" is as real a finding as "no abstraction."

If you find yourself writing "this should be microservices" or "this should use clean architecture," stop and ask: what concrete problem would that solve? If you can't name one, the finding isn't ready.
