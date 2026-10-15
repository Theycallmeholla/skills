# Intake

Research everything a source can answer, drop everything this post doesn't need, and send the client **one** questionnaire with whatever is left. Returns `posts/<slug>/intake.md` — the researched answers with their sources, the dropped questions with why, and the questionnaire, ready to forward to the client as written.

**Reads:** `registry.json` · `clients/<c>/brand.md` · `clients/<c>/opinion-bank.md` · `clients/<c>/facts.json` · the client's live site and sitemap · public sources (manufacturer and dealer spec sheets, state business records, the client's own blog, Google Business Profile)
**Writes:** `posts/<slug>/intake.md` · `posts/<slug>/post.json` (created at `idea` if missing) · `registry.json` — and, on a brand-new client, the `.blog/` scaffold **by running `brand` Phase 1 exactly as written**, never its own way
**Stops at:** Never writes the brand profile, the packet, the bank, or the vault itself. Research answers land in `intake.md` marked with their source. The client's replies are filed in Phase 5 by running the commands that own those files.

Load `references/governing-rules.md` first. **Rule 11 is this command.** Rules 5 (provenance), 6 (editorial autonomy) and 8 (plain language) shape the questionnaire.

---

## Why this exists

The failure, as it happened: a post about a client's new machine asked the user about 22 questions across six separate rounds — brand gaps, an interview, a fact check, a review. About seven had answers sitting on dealer spec sheets, the client's own site, or public records. Two were out of scope for the post. The rest all needed the client, and every one of them was knowable on day one. Spread across rounds, some answers came back as pasted AI research instead of the owner's words, which then had to be untangled.

One researched pass and one questionnaire would have cost the user a single forward to the client.

---

## Phase 1 — List every question the pipeline will need

Before researching or asking anything, write the full list for this client and this post. Pull from every command that would otherwise ask later:

- **`brand` gaps** — what they sell, who buys it, proof (with receipts), competitors, tone samples, never-say. Skip sections `brand.md` already fills.
- **`interview`** — the author's stance, why this topic matters to them, **one real example** (a job, a customer, a mistake), the business purpose, boundaries.
- **`brief` and `verify`** — every fact about the company the post will assert: founding year, the named person's role, capabilities, locations, hours, and specs of any named product, machine or service.
- **`write` and `review` repeat asks** — who a named person is, a concrete example behind the main claim, photos and assets.

Skip anything the opinion bank or the vault already answers and that hasn't expired.

## Phase 2 — Triage: research it, drop it, or ask it

Put every question in exactly one bin.

**Research it** — a public source can answer it:

| Question type | Where to look first |
|---|---|
| Product, machine or equipment specs | Manufacturer page; if none exists, two dealer spec sheets that agree |
| Founding year, owners, officers | State business-entity records (e.g. Texas Comptroller / SOS), then the client's About page |
| Services, capabilities, hours, address | Every page of the client's own site, **including old blog posts** |
| What a service or process is, or how two compare | Primary or reputable industry sources |
| What the client already claims publicly | Their site, Google Business Profile, reviews |

Record each answer in `intake.md` with its URL and date. The client's own marketing is their claim, not proof. Mark it `[client site]` and turn it into a one-line yes/no confirm in the questionnaire.

**Drop it** — it doesn't change this post. The test: *if the client answered, would a sentence in this article change?* No → drop it and write one line saying why. The user's stated thesis sets the scope. A post about one machine doesn't need shop-wide turnaround times.

**Ask it** — only the client can settle it:

- opinions, reasons, motives ("why did you buy it?")
- stories and examples from their own work
- internal process and capacity that isn't published
- permissions: names, photos, customers, numbers they'll stand behind
- boundaries: what never goes under their name
- assets: photos, video, drawings

**A search that fails is not a reason to ask yet.** Try a second source type first. Only after two honest attempts does a researchable question move to "ask," and then it goes in with your best guess attached.

## Phase 3 — Write the questionnaire

One message, built to be forwarded to the client unedited.

- **Group by topic, not by command.** "About the business" · "About this post" · "What not to say" · "Photos." Never use the words packet, brand profile, claims, or vault.
- **Plain, concrete, answerable in a breath.** The question bank and the banned anti-patterns in `interview.md` apply.
- **Attach a best guess or options wherever you have one**, so "yes" is a full answer. *"Still running the Blanchard grinder? (Your 2023 blog says yes.)"*
- **Include the research confirms** as one-line yes/no items, so the client checks what you found in the same pass instead of in a later round.
- **Always include the three asks later commands keep coming back for:** one real example behind the post's main claim, the named person's role, and anything they won't say.
- **No fixed cap**, but every question has passed Phase 2. Six to twelve is normal for a first post with a new client. Two or three is normal once the bank has filled.
- **Ask for the client's own words.** One line at the top: *"Short answers in your own words are perfect. Please don't paste in anything from another tool."*

## Phase 4 — Hand off

Write `intake.md` with three sections: **Researched** (each question, answer, source, date) · **Dropped** (each question, one-line reason) · **Questionnaire** (exactly as sent). Create `post.json` at `idea` if it doesn't exist, and update `registry.json`.

Chat response: the questionnaire, ready to copy, plus one line saying how many questions research answered and how many were dropped. Nothing else.

## Phase 5 — File the answers

When the replies come back, **hand them to the commands that own the files**. `intake` writes nothing here but a one-line note in `intake.md` saying the replies arrived.

- Brand facts go through `brand` Phase 4: written to `brand.md` with its marking (`[unconfirmed]`, `[unproven]`) and source traces.
- Stance, stories, boundaries and company numbers go through `interview` steps 3–5 in **no-questions mode**: compile the packet from the replies, add bank entries with provenance, and file numbers in `facts.json` with dates. Nothing is asked. A gap stays a gap in the packet's `## Gaps`.

**Pasted or tool-generated text is a source, not the client.** If a reply reads like research, with hedged generalities, "they offer…" written about the client in the third person, or headers and bullet essays, file it as research under Rule 5 and say so in one line: *"Your answer on gate valve sizes reads like it came from another tool. I've kept it out of anything said in the owner's name. Is it his?"*

Then go straight to `brief`. `interview` runs only if the replies left a real gap, and then only on that gap.

---

## Downstream contract

After intake has run for a post, `interview`, `brief`, `verify`, `write`, `review` and `revise` **do not ask the user anything the Phase 1 list should have caught.** If one of them genuinely needs to:

1. Ask it, once, with a best guess attached.
2. Log it in `posts/<slug>/notes.md` as `intake miss: <question> — <which command needed it>`.

Those log lines are how this command's Phase 1 list gets better. A question that later commands keep needing belongs in Phase 1.

Questions that are **not** misses: anything triggered by the user changing the thesis, by new information they supplied mid-flow, or by a draft finding no one could have predicted.

## Confirm and stop

Research first, drop what's out of scope, ask the rest once. Never ask what a source can answer, never ask what the post doesn't need, and never file research as the client's own words.
