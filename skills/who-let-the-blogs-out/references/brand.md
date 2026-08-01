# Brand

Builds or updates a client's brand profile and initializes `.blog/`, returning a profile in which every unknown is explicitly marked rather than plausibly filled.

**Reads:** `.blog/registry.json` · `.blog/clients/<client>/brand.md` · an optional `.blog/clients/<client>/import.json`
**Writes:** `.blog/clients/<client>/brand.md` · `.blog/registry.json` — plus, on first run for a client, the initialization scaffold: `.blog/clients/<client>/opinion-bank.md`, `facts.json`, `notes.md`
**Stops at:** Never writes post content. Never captures opinions, stances, or war stories — that's `interview`, and an opinion recorded here lands in a file no packet ever reads. Never audits the site — that's `website-audit`.

This is the only command permitted to create `.blog/`. Every other command that finds it missing says so and points here, because a half-formed state tree is harder to reason about than none.

## Phase 1 — Locate or initialize

Settle the slug first. It is lowercase and hyphenated, derived from the domain or the business name — `cursivemedia.com` → `cursive-media`. It appears in every path this system will ever write for this client and is never renamed, so decide it deliberately and show it to the user before writing anything.

Read `.blog/registry.json`. Three cases:

**No `.blog/` at all.** Create the tree:

```
.blog/
├── registry.json              {"version": 1, "clients": [], "posts": []}
└── clients/<slug>/
    ├── brand.md               frontmatter + the seven headings from state.md, sections empty
    ├── opinion-bank.md        assets/opinion-bank-template.md
    ├── facts.json             {"version": 1, "facts": []}
    └── notes.md               a single `# Notes — <name>` heading
```

Copy `opinion-bank-template.md` as-is except for its `## Specifics` section — drop it. Numbers live in `facts.json`, where they carry a `reverifyBy` date and can expire; a number parked in prose expires silently and gets published two years later as if it were current.

Leave `posts/` alone. `plan` creates it when there is a post to put in it.

**`.blog/` exists, this client doesn't.** Create `clients/<slug>/` with the same four files and add a registry entry. Creating the client directory whole rather than file-by-file means `interview` never has to guess whether a missing `opinion-bank.md` means "new client" or "file lost."

**The client already exists.** This is an update, not a rewrite. Read the existing `brand.md` and treat it as the base — carry every populated section forward verbatim unless the user corrects it. Rewriting a profile someone spent an hour on because a second pass had less information is the fastest way to make a system untrustworthy.

Report drift and continue: a client directory with no registry entry, a registry entry with no directory, `brand.md` missing frontmatter fields, a `facts.json` that doesn't parse. Name the file and the field, then proceed with what you were asked. Repair is a deliberate act, requested explicitly.

## Phase 2 — Ingest existing signals

Gather before asking. Every question you ask that the user already answered somewhere costs goodwill you'll need in Phase 3.

**1. An `import.json`, if one exists.** If an upstream tool has already analyzed this site, its output belongs at `.blog/clients/<slug>/import.json` in the shape `state.md` defines. That file is the whole contract — this skill never names or calls the tool that produced it, so anything that can write the shape can feed it. Ingest it rather than re-deriving — re-deriving costs a crawl and produces a second, differently-worded answer to a question already answered, after which two files disagree and nobody knows which is current. Check that path first. If the file isn't there and the site is live, ask whether any upstream tool in their setup can produce one and drop it there; don't crawl the site yourself.

Map it like this:

| `import.json` field | brand.md section |
|---|---|
| `offers[]` | What they sell |
| `audience` | Who buys it |
| `proofPoints[]` | Proof points on record |
| `competitors[]` | Competitors — named, with what each does better |
| `tone` | Tone: how they talk |
| `gaps[]` | stay gaps — carry them into Phase 3 |

Only `domain`, `tone`, `offers[]`, `proofPoints[]`, `competitors[]` and `source` are required; `audience` and `gaps[]` are honoured when present. Unknown fields are ignored, so a producer can write a richer file without this skill needing to change.

The one trap: an import's "differentiators" are usually the homepage's adjectives — *trusted*, *premium*, *results-driven*. Those are evidence of how the client talks, so they belong under **Tone**. They are not proof, so they do not belong under **What makes them different**. Filing them in the wrong section is how a profile becomes confidently wrong.

**2. Documents the user hands over.** Proposals, an about page, a pitch deck, an existing style guide, a testimonials file. Quote from them; don't summarize them into adjectives.

Every line ingested keeps a trace of where it came from — `(site copy, parsed 2026-07-18)`, `(client, 2026-08-01)`, `(2024 capabilities deck)`. Six weeks from now `write` reads this file and has to know whether "sites ship in three weeks" is something the client said or something the homepage claimed. Those are different levels of authority and the file is useless if it flattens them.

Set `source` in the frontmatter accordingly: `import` if the profile came from an `import.json` alone, `interview` if it came from the conversation alone, `both` when an import was ingested and then confirmed or extended in Phase 3.

**Recording a proof point here does not authorize anyone to assert it.** `evidence-rules.md` governs what `write` may claim, and it draws first-hand license from the Opinion Packet and the fact vault — not from this file. When a proof point is a number, note it here and flag it for `verify` to promote into `facts.json` with a date. This command doesn't write facts; it points at the ones worth verifying.

## Phase 3 — Interview the gaps

Ask only about what is still empty. Where the packet gave you an answer, show it and ask "still true?" — confirmation is a five-second question, and it is how the packet earns its keep.

**What they sell.** One sentence a stranger would understand, in their words. A category — "digital marketing" — is not an answer. Push until it names the thing sold and who pays for it.

**Who buys it.** "Small businesses" is not a buyer. "Owner-operated home-services companies in Houston doing $500k–$3M with nobody in-house handling marketing" is a buyer. The gap between those two is the gap between a post that lands and one that doesn't.

**What makes them different — proof, not adjectives.** The section that decides whether the whole profile is worth anything. Ask for the claim, then ask for the receipt:

> "Fast turnaround" → *How fast, and what tells you that?* → "Sites ship in three weeks. The last eight did."

The test: if a competitor could paste the sentence onto their own site without it becoming false, it's an adjective. That's the 500-companies test applied to the brand instead of the article, and it's the same failure — a differentiator anyone can claim differentiates nobody.

When the receipt doesn't exist, keep the claim and mark it `[unproven]`. A belief the client can't yet evidence is genuinely useful: it tells `interview` what to dig for and tells `review` not to wave it through as fact. Dropping it loses that; writing it unmarked creates a fabrication four commands downstream.

**Proof points on record.** Named clients, results with numbers and dates, credentials, review counts, years in business, volume. Each one needs a date and a separate answer to *can we say this publicly?* — permission and truth get conflated constantly, and the one that causes trouble is a true thing the client wasn't allowed to publish.

**Competitors — named, with what each does better.** The second half is the point. A competitor list where the client wins on everything is a list of nothing; it means nobody has thought about positioning. Ask: *if a good-fit client picked them over you, what would the honest reason be?*

**Tone: how they talk, with real examples.** Collect sentences, not adjectives. "Professional but approachable" gives `write` nothing to imitate. Two paragraphs the client wrote themselves are worth more than a page of tone words. Ask for something they wrote that sounded like them, and something published under their name that didn't — the contrast is more instructive than either alone.

**Never say.** Load-bearing: `review` checks every draft against this list, so an empty section means that check silently does nothing on every post this client ever publishes. "Anything we shouldn't say?" reliably returns "no, nothing comes to mind." Ask concretely instead:

- Words competitors use that make you cringe? (*cutting-edge, solutions, passionate, seamless*)
- Any guarantee or number you won't stand behind? (*#1 in Houston, guaranteed rankings, a specific ROI*)
- Client names you can't mention, or industries you don't want to be seen serving?
- Anything published under your name that you had to take down, or wished you could?
- Claims about competitors you won't make?
- Formatting you hate — emoji, exclamation points, *in today's fast-paced world*?

If it's still empty after all six, write that outcome into the file rather than leaving a blank heading: `None recorded — review's Never-say check is inactive for this client.` A blank heading reads like a pass.

### Cadence

Two or three questions per round, grouped by section. Seven sections asked in one message is a wall, and a wall gets skipped — permanently, because people remember which commands were tedious.

Order by leverage, because rounds four and five may never happen: what they sell and who buys it, then differentiators, then Never say, then proof points, then competitors. Tone comes last and often needs no questions at all — ask for two writing samples instead.

Stop after roughly four rounds, or earlier when answers start shortening. A one-word reply to a question that needs a paragraph means the interview is over, not that the question needs rephrasing. Write what you have, mark the rest, and say the profile can be extended any time. A partial profile finished today beats a complete one abandoned in round six.

Never ask about the site's performance, speed, or design — that's `website-audit`. Never ask for opinions, hot takes, or client stories — that's `interview`, and capturing them here files them where no packet will ever find them. Never re-ask what the packet or the existing profile already answers.

Never fill an answer on the client's behalf between rounds. This is the whole reason the command exists: a profile full of plausible filler is worse than one full of gaps, because filler gets read by four downstream commands as if it were true, and nobody ever goes back to check.

## Phase 4 — Write the profile

Write `brand.md` with the frontmatter and the seven headings from `state.md`, in that order and with that wording. `brief`, `write`, and `review` locate sections by heading; reordering or renaming them breaks reads that give no error.

Set `sitemap` only if you have confirmed one exists. Guessing `https://<domain>/sitemap.xml` is exactly the kind of plausible fill this command is built to refuse — leave it `null`.

Mark every unknown explicitly:

- An empty section gets a line, never blank space: `**Not captured.** Ask in the next brand pass.` Blank space reads to the next command as "nothing to say here," which is a different claim from "nobody asked."
- `[unproven]` — a claim the client makes with no receipt yet.
- `[unconfirmed]` — inferred from site copy or a document, not confirmed by a person.
- `[client to supply]` — promised in conversation, not delivered.

Concretely, do not infer the buyer from the industry, do not write a tone description from the site's visual design, and do not name competitors from a search you ran. Any of those produces a sentence indistinguishable from one the client said, which is the failure.

Then set `brandProfile` in the same operation that writes the file:

- `complete` — all seven sections carry real content, differentiators have proof, and Never say is populated.
- `partial` — anything less. Most first passes land here honestly.
- `missing` — the entry exists but no profile has been written yet.

`complete` is a claim, not a compliment. Marking a profile complete while Never say sits empty means `review` runs a check against nothing and reports a pass, which is worse than reporting a gap. When in doubt, `partial`.

Update the registry entry in the same operation — `slug`, `name`, `domain`, `brandProfile`, `updated`. Set `bankEntries` to `0` on a fresh scaffold; on an update leave it as it stands, since `interview` owns that count and this command doesn't read the bank. Don't touch `posts[]`.

## Output

A chat response in four named parts, in this order. The profile file is the artifact — don't paste it back in full.

1. **Written** — the literal paths created or updated, one per line.
2. **Profile** — the seven section names, each with a one-line summary of what's recorded or the word `empty`.
3. **Gaps** — every unknown, numbered, each paired with the question that would close it, so the user can reply "2 and 5" and finish the profile in one message.
4. **Status and next** — the `brandProfile` value with the reason for it in one clause, then the next command: `who-let-the-blogs-out interview <topic>` when there's a topic in mind, `who-let-the-blogs-out plan <client>` when there isn't.

If drift was found in Phase 1, add a fifth line naming the file and field. Reported, not repaired.

## Confirm and stop

Brand records who the client is, what they can prove, and what they may never say. It does not capture opinions or stories (`interview`), does not audit the site (`website-audit`), and never writes a word of post content — and it marks every gap rather than filling one.
