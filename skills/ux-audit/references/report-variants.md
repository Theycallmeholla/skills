# Report Variants

The detailed default lives in `assets/report-template.md`. Use one of these instead when it fits the request better. All three open with the same verdict enum (clear / mostly clear / confusing / broken).

## Concise — when the user wants a fast answer

```markdown
# UX Flow Audit: [flow]

## Verdict
[clear / mostly clear / confusing / broken] — [1–2 sentences]

## Biggest problem
[one direct paragraph]

## Main issues
1. [issue] — [user impact] — [fix]
2. [issue] — [user impact] — [fix]
3. [issue] — [user impact] — [fix]

## What I'd change first
[the single highest-leverage change — subtraction-first]

## Questions that matter
- [only if an answer would change a recommendation]
```

## Ticket-ready — when the user wants to action it with a team

Maps findings to implementable work. Each ticket is self-contained so it can be pasted into an issue tracker.

```markdown
# UX Flow Audit: [flow]

## Verdict
[direct assessment]

## Priority fixes

### Ticket 1: [title]
- **problem:** [specific UX issue + who it hurts]
- **change:** [specific implementation change]
- **affected files/components:** [list, with paths]
- **acceptance criteria:**
  - [testable outcome]
  - [testable outcome]

### Ticket 2: [title]
- **problem:** [...]
- **change:** [...]
- **affected files/components:** [...]
- **acceptance criteria:**
  - [testable outcome]

## Open questions
- [only decision-changing questions]
```

Order tickets by leverage (subtraction-first: remove → consolidate → rename → reorder → add feedback → add new UI). Make acceptance criteria observable from the user's side ("after submitting an invalid email, an inline message names the fix") — not implementation details.
