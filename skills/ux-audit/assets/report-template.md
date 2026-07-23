# UX Audit — [Flow / Product Name]

**Audited:** [what flow, e.g. "Signup → first dashboard"]
**Input(s) used:** [code / live app via browser / spec+screenshots — and which]
**Date:** [date]
**Auditor's stance:** First-time user, mobile-first, no prior knowledge of the product.

---

## Executive summary

[5–8 lines. What was audited and how. The single biggest takeaway. The top 3 issues by user/business cost. An overall verdict: ready / needs work before launch / actively losing users. Lead with the verdict — the owner reads this paragraph and skims the rest.]

**Top 3 issues:**
1. [severity] — [one line]
2. [severity] — [one line]
3. [severity] — [one line]

**Overall verdict:** [clear / mostly clear / confusing / broken] — [one sentence why]

---

## The flow, as mapped

[The Phase 1 step map. The reader needs to see what you evaluated.]

1. **Entry:** [how the user arrives]
2. **Step 1 — [name]:** [what's shown / asked]
3. **Step 2 — [name]:** [...]
4. ...
- **Branches:** [logged-out / error / empty / returning-user paths]
- **Exits:** [success state(s); ways to fall out]

---

## Findings

| ID | Severity | Category | Title | Location | Summary |
|----|----------|----------|-------|----------|---------|
| U1 | Critical | Flow logic | [title] | [file:line / step / frame] | [one line] |
| U2 | High | Comprehension | [title] | [...] | [...] |
| U3 | Medium | Copy clarity | [title] | [...] | [...] |
| U4 | Low | Consistency | [title] | [...] | [...] |

Severity: Critical > High > Medium > Low > Info. Sorted by user/business cost.

---

## Detailed findings

### U1 — [Title]  ·  Critical  ·  [Category]

**What it is.** [The issue, concretely.]
**User impact.** [Who hesitates or quits, and why. The drop-off story.]
**Evidence.** [`file:line` / "Step 4, `step-04.png`" / quoted spec line — the specific pointer.]
**Heuristic.** [Which usability heuristic it violates, if applicable.]
**Recommended fix.** [Specific, actionable. Not "improve UX."]
**Effort.** [S / M / L]

### U2 — [Title]  ·  High  ·  [Category]

[same structure]

---

## What's good

[Genuine strengths — at least a few. This calibrates the report and proves you went through the whole flow. Be specific: "The progress bar with step labels sets expectations well," not "nice design."]

---

## Prioritized next steps

You shouldn't have to re-prioritize these — here's the order:

**Fix first (highest cost, lowest effort):**
1. [U#] — [why first]
2. [U#] — [...]

**Then:**
3. [U#] — [...]
4. [U#] — [...]

**Worth doing eventually:**
- [U#], [U#] — [polish-tier]

---

## Suggested next pass

[The specific next file, route, screen, or screenshot worth inspecting — so the audit iterates instead of ending flat. E.g., "Walk the returning-user branch in the live app; the code suggests it skips onboarding but the success copy still says 'welcome'."]

---

*Notes on coverage:* [What you could and couldn't verify — e.g., "Audited from code; dynamic loading behavior not confirmed against a running instance. Error branches enumerated from the validation schema." So the owner knows the report's edges.]
