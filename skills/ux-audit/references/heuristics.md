# UX Evaluation Framework

The reference behind the audit phases. Use it to ground findings in recognized usability principles rather than personal taste — a finding that cites a heuristic is harder to wave away than one that says "I don't like it."

## Contents
1. Nielsen's 10 usability heuristics
2. Flow-logic checklist
3. Forms checklist
4. Conversion & trust checklist
5. Mobile checklist
6. Cognitive-load principles

---

## 1. Nielsen's 10 usability heuristics

The canonical lens. Most findings map to one of these:

1. **Visibility of system status** — the system always keeps users informed through timely feedback (loading, progress, confirmation, current location).
2. **Match between system and the real world** — speaks the user's language, follows real-world conventions, info appears in a natural and logical order. Violations: jargon, unfamiliar metaphors, illogical step order.
3. **User control and freedom** — clearly marked "emergency exits," undo and redo, no forced paths. Violations: dead ends, no back, no cancel, progress lost on exit.
4. **Consistency and standards** — same words/actions mean the same thing throughout; follow platform conventions. Violations: a "Done" button that sometimes saves and sometimes discards.
5. **Error prevention** — design that prevents problems beats good error messages. Constrain inputs, confirm destructive actions, eliminate error-prone conditions.
6. **Recognition rather than recall** — minimize memory load; make options, actions, and info visible. Violations: making users remember a value from a previous step, hidden navigation.
7. **Flexibility and efficiency of use** — accelerators for experienced users (autofill, defaults, shortcuts) without burdening novices.
8. **Aesthetic and minimalist design** — no irrelevant or rarely-needed info competing with what matters. Every extra element dilutes the signal.
9. **Help users recognize, diagnose, and recover from errors** — error messages in plain language, state the problem precisely, suggest a solution, sit next to the cause.
10. **Help and documentation** — when needed, help is easy to search, focused on the user's task, lists concrete steps, and isn't too large. Best when not needed at all.

When writing a finding, name the heuristic it violates. It makes the report credible and teaches the owner the principle.

---

## 2. Flow-logic checklist

For auditing the *sequence* (Phase 3):

- **Right order** — each step has the context to be answerable when it's reached. No "choose shipping speed" before the cart total exists.
- **Value before ask** — the user sees a reason to continue before being asked for effort, money, or personal data.
- **No premature gates** — don't force signup/login/permission before the user has any reason to grant it. Let them experience value first; ask to save it after.
- **No redundancy** — never ask for the same thing twice; merge steps that don't need separating; cut confirmation screens that add nothing.
- **No dead ends** — every state has a forward path and an exit. Empty states, error states, and "no results" all lead somewhere.
- **Reversible** — earlier choices are editable without restarting. The classic failure: a typo in the email at a final confirmation step that forces starting over.
- **All branches resolve** — logged-out, returning-user, error, empty, and edge branches each lead somewhere sensible. The unhappy paths are where flows quietly break.
- **Length justified by payoff** — step/field count is proportionate to what the user gets.

---

## 3. Forms checklist

Forms concentrate UX risk. Full list (Phase 8):

- **Labels** persistent, above or beside the field — never placeholder-only (placeholders vanish on focus, fail accessibility, and increase errors).
- **Input types** correct: `type="email"`, `type="tel"`, `inputmode="numeric"`, date pickers — so mobile shows the right keyboard and validation is automatic.
- **`autocomplete` attributes** set so browsers/password managers can fill fields.
- **One column** for primary flows; users read top-to-bottom. Multi-column invites skipped fields and confused tab order.
- **Group related fields** (address block, payment block) with clear sub-headings.
- **Required vs optional** explicitly marked. Default to marking optional fields when most are required (or vice versa) — don't make users guess.
- **Validation on blur**, not only on submit; success states as well as errors where helpful.
- **Errors** next to the field, in plain language, stating the fix (Phase 6).
- **Forgiving input** — normalize spaces, dashes, casing rather than rejecting.
- **Smart defaults** — pre-select the most common option; detect what you can.
- **Save / resume** so an interruption or refresh doesn't destroy progress.
- **Submit button** describes the outcome ("Create my account"), is disabled-with-feedback during submission, and there's exactly one obvious primary action.
- **Field count discipline** — every field is a tax. Ask: is this needed now? Needed at all? Can it be derived?

---

## 4. Conversion & trust checklist

For flows whose job is to convert (signups, funnels, checkout):

- **Single clear primary action** per screen; secondary actions visually subordinate.
- **Friction at the value moment, not before** — let users get value, then ask for the commitment.
- **Trust signals at the point of hesitation** — security/privacy reassurance next to sensitive fields, social proof near the decision, a clear "who we are."
- **Justify sensitive asks** — say *why* you need a phone number or SSN-like data right where you ask, or expect abandonment.
- **Money/commitment step is the most polished, least surprising** — no hidden costs revealed late, no unexpected steps after "Buy."
- **Exit cost is honest** — don't trap users to inflate a metric; dark patterns convert once and lose trust forever. Flag any you see (forced continuity, confirmshaming, hidden unsubscribe).

---

## 5. Mobile checklist

Audit mobile as primary for funnels (Phase 9):

- **Tap targets** ≥ ~44×44px, with spacing so adjacent targets aren't mis-tapped.
- **Thumb zone** — primary actions in the lower/center reach, not stranded top-corner.
- **Keyboard behavior** — the focused field and the submit button stay visible above the on-screen keyboard.
- **No horizontal scroll**; content reflows to a single column; text legible without zoom.
- **Sticky elements** don't eat the small viewport; modals are dismissible with a visible control, not just a tiny X.
- **Performance feel** — heavy hero animations and large images hurt most on mobile; note if they delay the first meaningful interaction.

---

## 6. Cognitive-load principles

The why behind "reduce friction":

- **Hick's law** — decision time grows with the number and complexity of choices. Reduce options, group them, or reveal progressively.
- **Miller's ~7±2** — people hold only a few items in working memory. Don't make them carry data between steps; show it instead (recognition over recall).
- **Goal gradient** — motivation rises closer to the goal. Progress indicators exploit this; their absence makes a flow feel endless.
- **Peak-end rule** — users judge an experience by its most intense moment and its end. A rough error mid-flow or a flat, confirmation-less ending colors the whole memory. Make the ending clear and rewarding.
- **The paradox of the blank field** — every input is a small interrogation. The shortest path to "done" that still gets what you truly need almost always wins.
