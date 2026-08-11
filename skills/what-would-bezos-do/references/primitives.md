# Primitives and Economic Shapes

Reference for WWBD. Read during the inventory and economic-shape passes.

## Contents
1. What makes something a primitive
2. Primitive catalog — what to look for in code
3. Economic shapes — what code evidence makes each plausible
4. Adjacency distance
5. Common false positives

---

## 1. What makes something a primitive

A primitive is a **general capability many things can be built on top of**, as opposed to a feature that serves one workflow.

The test:

> If usage of this increased 100×, would the rest of the company get stronger?

- A password-reset email flow: 100× more resets makes nothing stronger. Feature.
- The engine underneath it that routes any event to any channel on any schedule: 100× more usage means more features shipped cheaper. Primitive.

Two secondary signals:
- **Generality gap** — the implementation is meaningfully more general than its current use. Someone built for the abstract case and then wired up one instance.
- **Reimplementation pressure** — other parts of the codebase solve the same problem separately, badly. That's the primitive announcing itself.

---

## 2. Primitive catalog

Look for these during inventory. Presence alone isn't an asset — apply the maturity tag from SKILL.md.

**Identity & access** — auth, sessions, roles, permissions, org/team structures, invitations, SSO. Rich permission models often imply collaboration or admin products that were never built.

**Payments & billing** — Stripe/PayPal integration, subscription logic, invoicing, proration, usage metering, credit systems. Metering plus tenant boundaries is the strongest evidence for a usage-priced offering.

**Multi-tenancy** — org scoping, per-tenant config, data isolation, custom domains, theming. Tenant isolation + config layering is the structural basis for white-label.

**Orchestration & workflow** — queues, schedulers, state machines, retry logic, job pipelines, event buses. Frequently the most under-recognized primitive in an app.

**Communications** — email, SMS, push, in-app notifications, templating, channel routing, digesting.

**Generation engines** — PDF/document builders, image or video pipelines, report renderers, LLM-backed generators, static site builders.

**Search & retrieval** — indexes, full-text search, embeddings/vector stores, filtering and faceting infrastructure.

**Structured proprietary data** — anything accumulated that would be expensive or impossible for a competitor to assemble: normalized third-party data, scraped and cleaned datasets, labeled outcomes, historical pricing, geographic or regulatory records, user-contributed corpora. This is the most defensible asset class and the most often ignored.

**Analytics & instrumentation** — event tracking, funnels, dashboards, aggregation pipelines. Events fired but never analyzed are dark data.

**Integrations** — authenticated connections to third-party systems, OAuth apps, API clients, webhook receivers/senders. Each working integration is paid-for surface area.

**Distribution & acquisition** — SEO surface, embeds, public pages, referral mechanics, email lists, marketplace listings, existing customer relationships.

**Import/export & interoperability** — parsers, mappers, format converters, migration tooling. Import tooling built for onboarding is often a competitive wedge in disguise.

**Reusable operational processes** — documented human workflows, checklists, agent pipelines, QA procedures. Not code, still an asset; treat encoded process as a primitive when it's repeatable and produces consistent output.

---

## 3. Economic shapes

For each opportunity, name one. The right column lists what makes it *structurally* plausible — never what makes it commercially likely.

| Shape | Code evidence that supports it |
|---|---|
| **Internal leverage** | Multiple features reimplementing the same thing; engine with one consumer. Usually the best default answer. |
| **Premium feature** | Capability exists behind no paywall; billing tiers already modeled |
| **Usage pricing** | Metering, quotas, or per-event accounting already implemented |
| **API / developer surface** | Clean service boundaries, existing auth, stable schemas, webhooks |
| **Data product** | Accumulated proprietary dataset, aggregation pipelines, export tooling |
| **Cross-sell** | Adjacent capability serving the same authenticated customer |
| **White label** | Tenant isolation, theming, custom domains, per-tenant config |
| **Marketplace** | Two distinct participant roles already modeled; matching or listing logic |
| **New acquisition wedge** | Standalone-usable capability with low activation cost, public surface |
| **Standalone product** | High-maturity, general capability with a clear non-overlapping audience — the highest bar; require Operational or Proven maturity |

Classify every shape as **evidenced**, **supported hypothesis**, or **business context required**. Code proves feasibility. It never proves demand.

---

## 4. Adjacency distance

Order from closest to furthest. The further out, the higher the evidence bar and the smaller the number of findings that should survive.

1. **Same customer, same problem** — deeper solution for people already served. Lowest risk, most common right answer.
2. **Same customer, adjacent problem** — next thing they need. Cross-sell territory.
3. **Same capability, new customer** — the AWS move. Requires Operational or Proven maturity, no exceptions.
4. **New industry** — almost never justified from a repo scan alone. If it appears, label it business-context-required and keep it to one line.

---

## 5. Common false positives

Cut these on sight:

- **Framework or library capability mistaken for company asset.** Using Next.js middleware is not an asset; Next.js built it.
- **Commodity integration treated as a moat.** A Stripe integration is table stakes, not leverage — unless something non-obvious was built on top.
- **Volume mistaken for proprietary data.** A lot of rows isn't a dataset. Ask whether a competitor could assemble the same thing in a week.
- **"We could add AI."** Not an asset-derived opportunity unless the asset is the data or the pipeline, and you can name which.
- **Prototype dressed as capability.** If it has never run in production, it's Prototype maturity — the ceiling is "supported hypothesis."
- **Generic SaaS ideas that don't touch the inventory.** If the finding would read identically for any other company, it isn't a finding.
