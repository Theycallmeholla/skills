# Voice Rules

How to write ELI5 docs that are friendly and human without being patronizing or cringe-funny.

## The core balance

You're writing for someone who is **smart but busy**, has **never used this specific app**, and wants to **get the thing done and move on**. They're not a child. They're not technical. They appreciate when a doc respects their time.

The voice this produces:
- Direct, not bossy
- Friendly, not chummy
- Occasionally human, not constantly performing
- Plain, not dumbed-down

## Tone targets

| You want to sound like | You don't want to sound like |
|---|---|
| A coworker explaining something at their desk | A help-desk script written by committee |
| A friend who has the app open and is walking you through it | A motivational speaker |
| Someone who's done this 100 times and knows the gotchas | Someone trying really hard to seem approachable |

## On humor

**Allowed.** A light aside. A plain comparison. A dry observation. A tiny moment of acknowledgment that something is silly or unintuitive ("yes, this is a weird order — there's a reason, but you don't need to care about it").

**Not allowed.**
- Puns in headings
- "Buckle up," "let's dive in," "ready to level up?", "you've got this!"
- Exclamation points outside genuine "Done!" moments
- Emoji as decoration (functional emoji like ⚠️ in a callout are fine)
- Forced personality ("Our beloved closeout button is your new best friend!")
- Self-referential meta-jokes about being a help doc

**The rule of thumb:** if the joke would be in a corporate landing page from 2014, cut it.

## Examples

### Opening lines

**Bad** (forced personality):
> Welcome, friend! Ready to unlock the magical world of closeouts? Let's dive in! 🚀

**Bad** (sterile):
> The Closeout feature allows authenticated users with sufficient privileges to submit resolution data for assigned tickets.

**Good** (plain + light):
> Once you've finished work on a ticket, closing it out is how you hand it back to the client. It's the "I'm done, here's what I did" step.

### Explaining a constraint

**Bad** (apologetic and overwrought):
> Unfortunately, due to system limitations, you're only able to close out tickets that have been assigned to you. We know this might be frustrating!

**Bad** (legal):
> Closeout privileges are restricted to the assigned developer per the authorization policy.

**Good** (plain):
> You can only close out tickets assigned to you. If you don't see the Close Out button, that's why.

### A small acknowledgment of weirdness

**Bad** (forced):
> 😅 Okay, this part is a little weird, but stick with me!

**Good** (dry):
> Once you submit the closeout, the ticket goes to "Resolved Review" — not back to the client directly. An admin checks it first. (Yes, there are two approvals; it's intentional.)

### Error / problem situations

**Bad** (apologizing for the product):
> Oh no, something went wrong! We're so sorry about that!

**Bad** (terse):
> Closeout rejected.

**Good** (helpful):
> If the closeout doesn't go through, it's usually because one of the required fields is blank. Scroll up — the missing field will be highlighted in red.

## Sentence-level rules

- **Use "you."** ("You can close out a ticket once it's assigned to you.") Avoid "the user" — it's a help doc, not a research paper.
- **Active voice.** "Click Submit." Not "The Submit button should be clicked."
- **Short sentences when explaining a step.** Longer is okay when explaining the *why* behind something, but keep procedural lines tight.
- **Strong verbs.** "Pick a category" > "Make a selection from the category dropdown."
- **No "simply".** "Simply click Submit" — the word does nothing except imply the reader should already know. Cut it.
- **No "just".** Same reason. "Just go to Settings" is condescending in writing even if you meant it neutrally.

## Words to swap

| Don't write | Write instead |
|---|---|
| utilize | use |
| simply | (delete the word) |
| just | (delete the word, usually) |
| in order to | to |
| allows you to | lets you |
| navigate to | go to |
| validate | check |
| authentication | signing in / logging in |
| submit your input | send it / save it / post it (depends on the action) |
| the system | the app |
| an entity | (use the actual product term: ticket, post, customer, etc.) |
| terminate | end / close / cancel |
| facilitate | help / let |
| in the event that | if |
| at this point in time | now |
| via | through / using / by |
| respective | (delete the word, almost always unnecessary) |

## Address and perspective

- Speak to **the reader**, in second person ("you").
- Use first-person plural ("we") only when describing what the company/product does *for* them ("we send the client an email when you close it out") — sparingly.
- Don't refer to "developers," "admins," or any role unless the reader belongs to that role. If the doc is for clients, say "your team" or "the people working your ticket" instead of "the dev_admin."

## Long-form sections

Some sections (especially "What happens behind the scenes") run longer. Rules there:

- One paragraph per idea. Break it up.
- Front-load the takeaway. The first sentence of a paragraph should say what the paragraph is about — the reader can skim and still get the gist.
- Don't bury action items. If there's something the reader should *do*, pull it into a clear callout, not the middle of a paragraph.

## When in doubt

Ask: **"Would I write this in an email to a smart friend who'd never used the app?"**

If the answer is "no, this sounds like a help-desk macro," rewrite.

If the answer is "yeah but it feels a little plain," that's fine. Plain is better than performing.
