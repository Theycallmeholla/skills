# ELI5 Feature Doc Style Guide

This file controls how the `eli5-features` skill writes user-facing feature documentation for this repo. Edit anything below to tune voice, structure, or output for your product.

The skill reads this file every time it runs. Defaults are below — change what you want and the skill will follow.

---

## Product

**Product name:** [fill in — e.g., "Cursive ASAP Ticketing"]

**Who reads these docs:** [e.g., "operations team and clients using the ticketing portal", "small business owners using our app"]

**Technical level of readers:** non-technical
*(options: non-technical / basic computer literacy / power users)*

---

## Voice

**Tone:** friendly and direct, occasionally dry, no exclamation points outside genuine "done!" moments.

**Default address:** "you" (second person)

**Humor:** allowed in small doses — light asides, dry observations, plain comparisons. Never puns in headings. Never "buckle up" / "let's dive in" / forced enthusiasm.

**Forbidden phrases for this product:**
- (add any product-specific terms you don't want — e.g., "innovative", "best-in-class", or anything else)

---

## Default doc sections (in order)

The skill uses these section headers by default. Comment out (with `<!-- -->`) or delete any you don't want.

- What is it / when would you use it
- The quick version
- Step by step
- What you'll see
- Common situations
- What happens behind the scenes *(optional — include only when there are non-obvious side effects)*
- Need help?

---

## Vocabulary

The skill scans the codebase for UI strings on each run. If you want to lock in specific terms, list them here and the skill will use these exactly.

**Always use these terms (UI words, not developer words):**
- (the skill will fill these in by reading the UI on the first feature doc — review and adjust as needed)
- *Example:* "ticket" — never "case", "issue", "record"
- *Example:* "Close Out" — the button label, capitalized

**Never use these terms in user-facing docs:**
- endpoint, schema, API, actor, tenant, DTO, payload, handler
- (add any product-specific terms that leak from code into docs accidentally)

---

## Output location

Feature docs are written to: `docs/features/<feature-slug>.md`

*(change the path or template if your docs live elsewhere — e.g., `help/`, `support/`, `docs/help-center/`)*

---

## Media callouts

When the skill spots a place where a visual would help, it adds an inline callout in the doc:

- `> 📸 **Screenshot opportunity:** description`
- `> 🎥 **Video opportunity:** description`
- `> 📊 **Diagram opportunity:** description`
- `> 🖼️ **Image opportunity:** description`

These are placeholders — you drop in real media later. The doc reads fine without them.

**Want different callout symbols or wording?** Change them here:

```
Screenshot prefix: > 📸 **Screenshot opportunity:**
Video prefix:      > 🎥 **Video opportunity:**
Diagram prefix:    > 📊 **Diagram opportunity:**
Image prefix:      > 🖼️ **Image opportunity:**
```

---

## Multi-flow features

When a feature has multiple user roles (e.g., developer submits → admin reviews → client accepts), the skill can either:

- (default) Make **one doc** with sections for each role
- Make **separate docs** that link to each other

**Current setting:** one doc with sections per role

*(change to "separate docs" if you prefer)*

---

## Title style

**Default:** "How to X" or noun phrase ("Closing out a ticket").

*(alternatives: "Working with X", "X 101", or anything else — set your preference)*

---

## "Need help?" closing line

The skill ends every doc with a short fallback line. Default:

> If you get stuck, reach out to support.

Change this to your actual support contact / channel:

```
Need help line: [your line here]
```

Examples:
- "Ping your team lead, or open a ticket in #help."
- "Email support@yourcompany.com or use the in-app chat."
- "If anything looks off, check with your admin first."

---

## Approval flow

Should the skill ask for review before writing the doc, or write directly and let you review the file?

- [ ] Ask before writing
- [x] Write directly to the output path

---

## Notes for the skill

(Anything project-specific the skill should know — common shortcuts, things to always mention, things to never mention.)

- Example: "Always mention that mobile is fully supported — users often assume it isn't."
- Example: "Never document features marked `__experimental__` in the code."
- (add your own)
