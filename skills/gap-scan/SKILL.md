---
name: gap-scan
description: Scan a codebase, live app, or site and find the features that obviously should exist but don't — missing exports, bulk actions, search/filter, undo, history, notifications, dead-end workflows, data collected but never surfaced, backend endpoints with no UI, and half-built features that stopped partway. Produces an evidence-backed, ranked punch list (top 10 max) with a portable gap_packet JSON. Use whenever the user asks "what features are missing", "what's this app lacking", "find gaps", "run gap-scan", "what should this have", "feature audit", "what would users expect here", or wants proposal ammo from a prospect's app. Trigger even on casual phrasings ("anything obviously missing from this?"). This skill flags ABSENCE only — broken code goes to code-audit, confusing flows to ux-audit, weak persuasion to conversion-audit, underexploited existing assets to a WWBD-style analysis. If something exists but is bad, it's not a gap — hand it off.
---

# Gap-Scan

Find the features a product is obviously missing. Not what's broken (code-audit), not what's confusing (ux-audit), not hidden value in what exists — what's **absent** that users of this kind of product would reasonably expect.

The output is a punch list a client or team can act on: each gap cites the evidence that proves it, ranked by user value × effort, capped at 10. The report's credibility comes from what it refuses to include — no speculative wishlists, no "you could add AI."

## Modes

Ask which mode if not obvious from context; default to QA mode for the user's own repo, PROSPECT mode when the target is a lead's site/app.

- **PROSPECT mode** — fast pass on a lead's app or site. Goal: proposal ammunition. Top 5–8 gaps, each phrased as a client-facing line item ("Your customers can't reorder past purchases — every competitor offers this"). Lighter evidence bar (observed from the outside is fine), but still cite what you observed.
- **QA mode** — deep pass on a repo you have code access to. Goal: roadmap input. Full inventory, file-path evidence required for every finding, up to 10 gaps.

## Process

### 1. Inventory once, reason many times

Do ONE scan of the target and build a capability map. Do not re-crawl files per lens — every lens below reasons against the map, not the repo.

For a repo, the map covers:
- Routes/pages and what each lets the user do
- Models/entities and their fields (especially fields written but never read/displayed)
- CRUD coverage per entity: create / read / update / delete / duplicate / archive / export / import / bulk
- Endpoints with no consuming UI; UI elements with no working backend
- TODOs, commented-out blocks, disabled buttons, feature flags that are off, dead routes
- Background jobs, events, and data being collected

For a live app (no code), the map comes from walking the UI: every screen, every action available per entity, every dead end.

### 2. Run the gap lenses against the map

Each lens is a question asked of the map — cheap reasoning, no new scanning:

1. **CRUD symmetry** — user can create but not duplicate/archive/export/bulk-edit? Lists with no search, filter, or sort where the data volume clearly demands it?
2. **Dark data** — fields or events collected but never surfaced anywhere. (Timestamps stored but no "last updated" shown; analytics events fired into nothing.)
3. **Orphans** — backend capability with no UI; UI promising something the backend can't do; endpoints nothing calls.
4. **Half-built** — TODOs, disabled controls, dead-end screens, flags stuck off. Features that stopped partway are the cheapest gaps to close.
5. **Table stakes** — what does this *category* of product normally have that this one lacks? (A CRM without activity history; an e-commerce app without order status; a SaaS without password reset.) Name the category explicitly before applying this lens, so the comparison set is honest.
6. **Workflow dead ends** — a user completes step N and there's no step N+1 where one obviously belongs (created an invoice, can't send it; finished a report, can't share it).

### 3. Evidence gate

Every finding must cite proof or it's cut:
- QA mode: file path(s), route, or model field that demonstrates the absence ("`orders.ts` has create/get/update — no export or bulk endpoint exists; `OrdersList.tsx` renders single-row actions only")
- PROSPECT mode: what was observed ("Products page lists 200+ items, no search input present")

"Users probably want X" with no anchor in the map is not a finding. The table-stakes lens still needs an anchor: name the comparable category norm AND confirm the map shows the absence.

### 4. Rank and cap

Score each surviving gap on two axes, no fake precision:
- **User value**: High / Medium / Low — how often would real users hit this absence?
- **Effort**: S / M / L — S if the surrounding infrastructure already exists (single-record action → bulk is usually S; a whole notification system is L)

Sort: High-value + S-effort first. **Hard cap: 10 findings** (5–8 in PROSPECT mode). Everything else gets one line in an appendix or gets cut. Resist padding — a 6-gap report that's all real beats a 10-gap report with filler.

## Report structure

ALWAYS use this shape:

```
# Gap-Scan: [target]
Mode: [PROSPECT | QA] · Category baseline: [what kind of product this is]

## Top gaps
For each (max 10):
### N. [Gap name]
- What's missing: [one sentence]
- Evidence: [file paths / observed behavior]
- Why it matters: [one sentence, user-anchored]
- Effort: [S/M/L] — [one line on why, citing existing infra if S]
- Suggested MVP: [smallest version that closes the gap]

## Appendix: minor gaps (one line each)

## Out of scope (handoffs)
[Anything found that belongs to code-audit / ux-audit / conversion-audit — one line each, don't elaborate]
```

In PROSPECT mode, add a `## Proposal framing` section: each top gap restated as a client-facing benefit line.

## gap_packet output

Alongside the report, always emit `gap_packet.json` so other skills and swarm agents can consume the results:

```json
{
  "packet_type": "gap_packet",
  "version": 1,
  "target": "repo path or URL",
  "mode": "prospect | qa",
  "category_baseline": "e.g. local-service business site",
  "scanned_at": "ISO date",
  "gaps": [
    {
      "name": "Bulk actions on contacts",
      "lens": "crud_symmetry",
      "value": "high",
      "effort": "S",
      "evidence": ["src/api/contacts.ts", "src/components/ContactList.tsx"],
      "mvp": "Multi-select + bulk delete/tag on the contacts list"
    }
  ],
  "handoffs": [{"skill": "ux-audit", "note": "checkout flow confusing"}]
}
```

## Boundaries — what gap-scan never does

- Never reports something that exists but is broken, slow, or insecure → code-audit
- Never critiques the usability of what exists → ux-audit
- Never evaluates persuasion or conversion of existing pages → conversion-audit
- Never proposes productizing existing internal assets → that's opportunity-mining (WWBD), a different question
- Never recommends features with no evidence anchor ("add AI", "add a mobile app") — if the map doesn't imply it, it doesn't ship in the report
