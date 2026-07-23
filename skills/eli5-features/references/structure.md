# Doc Structure Reference

Default section structure for an ELI5 feature doc, with guidance on when to include each.

The full default ordering:

1. Title + one-line subtitle
2. What is it / when would you use it
3. The quick version (TL;DR steps)
4. Step by step
5. What you'll see
6. Common situations
7. What happens behind the scenes *(optional)*
8. Need help?

## Section-by-section guidance

### Title + one-line subtitle

Format:

```markdown
# Closing out a ticket

*How to hand your finished work back to the client.*
```

Title is a noun phrase or "How to X" — match the style guide if it specifies.
Subtitle is one short line in italics, explaining the user's goal.

### What is it / when would you use it

One paragraph. Two if absolutely needed. Answers:
- What does the feature do for me, in plain words?
- When would I use it?
- Who can use it (if there's a permission constraint)?

Don't explain the *internals*. Don't list every option. Just enough that the reader knows they're in the right doc.

**Example:**
> Closing out a ticket is how you tell the client your work is done. Once you're finished on a ticket assigned to you, this is the final step before the client sees it back. You'll write a short summary of what you did, attach anything they should look at, and submit it for review.

### The quick version

Numbered list. 3-6 steps. Just the verbs. No explanation.

If a step needs a screenshot to make sense ("click the blue button in the top right"), use the action label exactly from the UI ("Click **Close Out** in the top right").

**Example:**
```markdown
## The quick version

1. Open the ticket you've been working on.
2. Click **Close Out** in the top right.
3. Fill in **Summary**, **What changed**, and **What the client should check**.
4. Click **Submit for review**.

That's it — the ticket goes to admin review, then back to the client.
```

End with one short sentence confirming what just happened ("That's it" / "Done" / "And you're done.").

### Step by step

The same steps, expanded. Each step has:
- The action (in **bold** if it's a click)
- What happens / what you see
- Any gotchas

Use H3 (`###`) for each step or numbered bold lines, depending on how chunky the steps are.

**Example:**

```markdown
## Step by step

### 1. Open the ticket

Find the ticket on your dashboard. It needs to be assigned to you — if you didn't pick it up yourself, an admin assigned it. Either way, it should show up under "My Tickets."

### 2. Click **Close Out**

The button is in the top right of the ticket page. You'll only see it if the ticket is in "In Progress" or "Resolved Review" — if it's still in "Triage" or already "Closed," there's nothing to close out.

> 📸 **Screenshot opportunity:** ticket detail page with the Close Out button highlighted

### 3. Fill in the closeout form

You'll see three fields:
- **Summary** — one sentence. What's the high-level result?
- **What changed** — what did you actually do? (The client sees this, so write for them, not for an engineer.)
- **What the client should check** — where should they look to confirm the work?

All three are required.

### 4. Submit

Click **Submit for review**. The page reloads, the ticket status changes to "Resolved Review," and an admin gets a notification to approve it.
```

### What you'll see

Catalog of UI elements the reader will interact with. Use when a section has more than 3-4 distinct controls.

**Example:**

```markdown
## What you'll see

- **Close Out button** — top right. Only visible when you're the assignee and the ticket isn't already closed.
- **Summary field** — short, one sentence.
- **What changed** — longer. The client reads this. Aim for plain language.
- **Attachments** — drag files in or click to browse. Visible to the client.
- **Internal notes** — only admins see this. Use for "this took longer because of X" or other context you wouldn't want the client to read.
- **Submit for review** — sends it on. Once you click this, you can't edit the closeout.
```

Skip this section if everything was already explained well in "Step by step."

### Common situations

Q&A format. Each is a thing the reader might run into. Frame them as the reader would search for them.

**Examples:**

```markdown
## Common situations

### I don't see the Close Out button

Three reasons:
1. The ticket isn't assigned to you. Only the assigned developer can close out.
2. The ticket is in a state where closeout doesn't apply (it's still in Triage or it's already Closed).
3. You're signed in as a client. Clients accept closeouts; they don't submit them.

### I clicked Submit but the page just sat there

Scroll up. One of the required fields is probably blank, and the field will be highlighted in red. Once you fill it in, click Submit again.

### Can I edit a closeout after I submit it?

No. Once it's submitted, it goes to admin review. If you submitted something wrong, ask an admin to reject it — that puts the ticket back in your court and you can re-submit.

### What does the client see?

They see the **Summary** and **What changed** fields, plus any attachments you added. They don't see **Internal notes**.
```

### What happens behind the scenes *(optional)*

Include only when it helps the user understand a non-obvious downstream effect. Skip if the feature is self-contained.

**When to include:**
- Other people get notified ("The client gets an email when you submit.")
- It affects something outside the immediate page ("Your ticket count on the dashboard drops by one.")
- The next step is invisible from the current page ("After admin review, the ticket goes back to the client — you don't have to do anything else.")

**When to skip:**
- The feature is pure UI (filtering, search, etc.) with no side effects
- The "behind the scenes" is the same as "what you see" — would just be repeating

**Example:**

```markdown
## What happens behind the scenes

When you submit a closeout, three things happen:

- The ticket status changes to "Resolved Review."
- The admin team gets an alert to approve or reject your closeout.
- Nothing goes to the client yet — they only see it after admin approval. (That's why there's a "review" step: it's the safety check.)

If admins approve it, the client gets an email and the ticket moves to "Awaiting Acceptance." If they reject it, you'll see the ticket bounce back to "In Progress" with the reviewer's feedback in the comments.
```

### Need help?

One short closing line. Use the contact info from the style guide.

**Example:**

```markdown
## Need help?

Ping your team lead, or open a ticket in the #help channel.
```

## Variations

### Tiny features

A feature like "change your avatar" needs almost no doc. Just title + one paragraph + 3-step list. Don't pad it.

### Multi-flow features

A feature like "the closeout flow" actually has three flows: developer submits, admin approves, client accepts.

Two options:
1. **One doc, three sections.** Use H2 to divide. Title is plural or general ("The closeout flow").
2. **Three docs.** Each is one short doc. Title is the action ("Closing out a ticket", "Approving a closeout", "Accepting a closeout").

The style guide says which to default to. If it's silent, choose based on whether the same user does multiple of the flows. Same user → one doc. Different roles → separate docs.

### Reference-heavy features

For features that have lots of options (filter panels, settings pages), the structure shifts:

- Drop "Step by step" (it's not a procedure)
- Expand "What you'll see" — it's the bulk of the doc
- Replace "The quick version" with "The basics" — what does the average person need to know?
- Keep "Common situations" — these are gold for settings pages where users get stuck

### Diagrams when state is involved

For features with multiple states (lifecycles, workflows), a diagram callout is almost always worth it:

```markdown
> 📊 **Diagram opportunity:** state flow showing New → Triage → In Progress → Resolved Review → Awaiting Acceptance → Closed
```

Don't try to draw the diagram in ASCII; just call out the opportunity.
