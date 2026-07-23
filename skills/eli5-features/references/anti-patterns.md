# Anti-Patterns

Words, phrases, and patterns that don't belong in an ELI5 doc. Search for these in your draft before finalizing — if any are present, rewrite.

## Jargon to translate

These are developer terms that have no place in user docs. The translation depends on context — find the user-facing equivalent.

| Developer term | Translate to |
|---|---|
| endpoint | (drop it; describe the action: "When you click Save, the app sends your changes...") |
| API | (drop it; describe the action) |
| schema | (drop it; describe the data: "the fields you filled in") |
| validation | (drop it; describe the check: "the app makes sure all required fields are filled in") |
| actor / authenticated user | "you" |
| tenant / organization (in code sense) | use the product term (workspace, team, company) |
| backend / frontend / server / client | (almost always drop; describe what the *user* sees) |
| persisted | "saved" |
| serialize / deserialize | (drop; describe behavior) |
| DTO / payload | (drop; describe the data) |
| middleware | (drop; describe the effect) |
| token / JWT / session | "your sign-in" / "you stay signed in" |
| webhook | (rare in user docs; if it must appear, describe the trigger: "when X happens, we send Y") |
| query / mutation (GraphQL) | (drop; describe the action) |
| migration (DB) | (drop; describe the schema change as a UX change) |
| state machine | (drop; describe the statuses: "tickets move through these stages...") |
| handler / controller / route | (drop; describe what happens when the user clicks) |

## Marketing words to cut

These add nothing and make the doc feel like ad copy.

- **"seamlessly"** — almost never accurate, always smarmy
- **"powerful"** — meaningless
- **"intuitive"** — if it's intuitive, the doc shouldn't be needed
- **"robust"** — corporate filler
- **"streamlined"** — corporate filler
- **"world-class"** — please
- **"best-in-class"** — please
- **"unlock"** — overused beyond rescue
- **"empower"** — corporate filler
- **"leverage"** — corporate filler
- **"revolutionary"** / **"game-changing"** — never
- **"effortlessly"** — usually a lie
- **"cutting-edge"** — no
- **"next-generation"** — no
- **"innovative"** — no

## Filler phrases to delete

These add length without information.

- "It's important to note that..." → just say it
- "Please be aware that..." → just say it
- "As you can see..." → they can or can't, doesn't matter
- "Don't worry,..." → makes them worry
- "Simply..." → cut, always
- "Just..." → cut, almost always (exception: "just" meaning "only", e.g., "just the comments")
- "Basically..." → cut
- "At the end of the day..." → cut
- "In order to..." → "To"
- "Due to the fact that..." → "Because"
- "In the event that..." → "If"
- "At this point in time..." → "Now"
- "Going forward..." → cut, or "From now on"
- "Please find attached..." → "Here's"
- "Should you have any questions..." → "If you have questions"
- "Per our..." → just describe it
- "As per..." → just describe it
- "First and foremost..." → "First"
- "It goes without saying..." → then don't say it
- "Needless to say..." → then don't say it

## Patronizing patterns

- "Don't worry, it's super easy!" — let the simplicity speak for itself
- "We've made it as simple as possible" — sounds like you're bragging about basic competence
- "Even your grandma could do this!" — gross, ageist
- "Don't be afraid to..." — they're using software, not skydiving
- "It's okay to make mistakes!" — true but unnecessary
- "Take a deep breath..." — what?
- "You've got this!" — save it for actual achievements

## Performative friendliness

- "Hey there! 👋"
- "Welcome, friend!"
- "Hello, fellow human!"
- "Greetings, traveler!"
- Multiple emojis in opening lines
- "Buckle up!"
- "Strap in!"
- "Let's get this party started!"
- "Ready to rock?"

## Heading rules

- **No puns in headings.** "Closeout-tastic!" — no.
- **No questions phrased as user thoughts.** "So, you want to close out a ticket?" — no.
- **No exclamation points in headings.** "Submitting Your Closeout!" — no.
- **No "Pro tip:" labels everywhere.** One or two in a doc is fine if they're actually pro tips. Sprinkled on every section it becomes noise.

Headings should be:
- Verb + object ("Closing out a ticket") or
- Noun phrase ("The quick version", "Common situations") or
- A user question, deadpan ("I don't see the Close Out button" — used in Common Situations, fine there)

## Things that lie

- **Don't claim features that don't exist.** If you see a button labeled "Export to PDF" but the handler is empty, don't write the export section.
- **Don't promise behavior the code doesn't deliver.** "The client always gets an email." — actually, only if their email preferences allow it. So say *that*: "The client gets an email if they've kept those notifications on."
- **Don't pretend complexity is simple if it isn't.** If a flow has 12 steps, the doc has 12 steps. Compressing into 4 vague steps misleads.

## Code-block anti-patterns

- **No code blocks in end-user docs**, except:
  - Showing the exact text of a button or field label (use **bold** instead, almost always)
  - Showing an error message the user might see (`> "Required field missing"` or as a quote)
  - Showing a literal name/value the user types (e.g., a coupon code, a config value) — use inline `code` formatting

If you're tempted to put a JSON snippet, an HTTP example, or a code function in the doc, you're writing developer docs by accident. Stop and reframe.

## Examples of fixed sentences

| Before | After |
|---|---|
| "Utilize the Closeout functionality to facilitate the resolution submission process." | "Use Close Out to send your finished work to the client." |
| "Simply navigate to the dashboard and click on the appropriate button." | "Go to your dashboard and click **Close Out**." |
| "It's important to note that closeouts cannot be edited once submitted." | "You can't edit a closeout once it's submitted." |
| "We've designed this feature with you in mind!" | (cut it; show, don't tell) |
| "Welcome to the world of ticket management! Let's dive in!" | "Tickets are how your team tracks work." |
| "Please be aware that this action is irreversible." | "Heads up — you can't undo this." |
| "The system will validate your input and persist the changes to the database." | "We'll save your changes." |

## Self-check before finalizing

Run through this list against your draft. If any of these are true, revise:

- [ ] Are there any words from the "Marketing words to cut" list?
- [ ] Are there any filler phrases?
- [ ] Is there a "simply" or "just" anywhere?
- [ ] Are there developer terms not in the translation table?
- [ ] Are there exclamation points outside genuine "Done" moments?
- [ ] Are there more than 2 emojis in the doc (not counting the media callouts)?
- [ ] Are there any patronizing patterns?
- [ ] Is the opening line trying to be funny instead of trying to be useful?
- [ ] Does any paragraph start with "Don't worry"?
- [ ] Does any section claim something the code doesn't do?

If yes to any: rewrite that section before delivering the doc.
