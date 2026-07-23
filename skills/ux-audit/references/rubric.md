# Optional Scoring Rubric

Use this when the user asks for a score, or when a flow is complex enough that structured scoring sharpens judgment. Scoring is optional — most audits are fine with severities alone. Don't force a number onto something a sentence explains better.

## Scale

Score each category 1–5:

- **5** — clear, efficient, hard to misuse.
- **4** — understandable, minor friction.
- **3** — usable but noticeably confusing or inefficient.
- **2** — confusing, redundant, or fragile enough to cause drop-off.
- **1** — broken or unusable without guidance.

## Categories

1. **Goal clarity** — can the user tell what the flow is for and what result they'll get? (clear title/first instruction, obvious primary action, no unexplained jargon, visible success criteria)
2. **Next-step clarity** — at each point, is there one dominant next action with a specific label, and no competing equal-weight CTAs?
3. **Flow efficiency** — fewest reasonable steps; no redundant screens, repeated inputs, early choices, or setup-before-value.
4. **Cognitive load** — progressive disclosure, grouped choices, visible progress, sensible defaults; nothing the user must hold in memory across steps.
5. **Feedback & trust** — loading, success, validation, error recovery, reversibility, and explanation of risky/irreversible steps.
6. **Redundancy & duplication** — no duplicate routes/screens, no multiple components doing one job, no repeated or conflicting questions.
7. **Edge-state quality** — empty, validation-error, permission-error, expired-session, missing-data, partial-completion, and retry paths are coherent.
8. **Developer-to-user leakage** — no DB terms in labels, implementation-driven categories, internal status names, code-shaped steps, or admin concepts shown to normal users.
9. **Mobile** — tap targets, thumb reach, keyboard behavior, reflow on a phone-sized viewport.
10. **Accessibility essentials** — keyboard operability, visible/managed focus, programmatic labels, contrast, reduced-motion.

(Categories 9–10 extend the original eight; drop them only if the flow is genuinely desktop-only and accessibility is explicitly out of scope — and say so.)

## Deriving the verdict from scores

- **Clear** — mostly 4s and 5s, no high-severity issue.
- **Mostly clear** — at least one meaningful issue, but the user still finishes unaided.
- **Confusing** — several 2–3s, or one high-impact ambiguity likely to derail or drop users.
- **Broken** — any category at 1 that blocks completion, or contradictory instructions, or a hidden essential next step.

Report the per-category scores as a small table, then the derived verdict. The scores are a means to the verdict and the findings — not the deliverable themselves.
