# Case Design Rubric

How to design test cases that catch real bugs instead of just hitting code coverage targets.

## What makes a case worth suggesting

Every case must answer: **"What breaks in production if this case isn't covered?"** If you can't answer that in one sentence, the case isn't worth writing.

Bad cases (avoid these):
- "Test that the function returns the right type" — TypeScript already does this
- "Test that the constructor doesn't throw" — almost never the failure mode
- "Test the happy path" without specifying what the happy path is
- "Test all the methods" — listing methods isn't designing tests
- "Test with valid input" — vague; valid by what definition?
- "Test error handling" — error handling for what error?

Good cases:
- Tied to a specific failure that would actually happen
- Specify enough that the writer doesn't need to re-read the source
- Cover something the type system *can't* catch
- Test behavior, not implementation

## The five things to look for in any target

When inspecting a function/class/module, walk through these in order:

### 1. Branches

Every `if`, `switch`, ternary, early `return`, `||`/`&&` short-circuit, optional chain that affects flow.

For each non-trivial branch, there should be a case for both sides. Not the trivial ones — `if (!user)` returning early doesn't need a separate test if the function's contract makes that path obvious. But branches that produce different outputs based on input shape definitely do.

**Example:**
```ts
function authorize(user, resource) {
  if (user.role === 'admin') return true;
  if (resource.ownerId === user.id) return true;
  return false;
}
```
Three cases minimum: admin path, owner path, unauthorized path. Each tied to a real authorization failure mode.

### 2. Throws and rejects

Every place the code can throw — `throw new Error(...)`, `assert`, `panic`, rejected promise, custom error class.

For each, suggest a case that triggers the throw and verifies the error type/message. Not a generic "throws on bad input" — specify *which* bad input and *which* error.

**Why this matters:** Callers rely on error types for branching (e.g., `catch (e) { if (e instanceof AuthError) ... }`). If the error type changes silently, the caller's catch is a no-op.

### 3. Boundary inputs

Boundaries that are likely to break things:
- Empty string `""` vs `null` vs `undefined`
- `0`, `-1`, `Number.MAX_SAFE_INTEGER`
- Empty array `[]` vs single-element vs huge
- Whitespace-only strings
- Non-ASCII / unicode / RTL text where relevant
- Strings with the delimiter the code parses with (commas in CSV, quotes in JSON, etc.)
- Dates: epoch, far future, DST transitions, leap years
- Floats where integers are expected, and vice versa

Don't suggest all of these for every function. Pick the ones that are *plausibly* a bug. A username field probably needs empty/long/unicode tests; a counter probably just needs zero/negative.

### 4. Side effects

Things the code does *to the world*: DB writes, HTTP calls, file writes, in-memory mutations of arguments, event emissions, log writes (if logs are checked downstream).

For each side effect, the suggestion should specify what the test will assert about it. Examples:
- "Assert `db.users.create` was called exactly once with `{ email: 'x', role: 'user' }`"
- "Assert no Set-Cookie header appears in the response"
- "Assert `audit.log` was called with action='delete' and the user's id"

If the side effect is irreversible (sends email, charges card), the test should verify it's *not* called in error paths.

### 5. Contracts the code commits to

What does this code promise to its callers? Examples:
- "Returns user object without password field" → test that `password` is never in the response
- "Always sets X-Request-Id header" → test that the header is present
- "Idempotent for the same (userId, eventId)" → test calling twice produces one effect
- "Validates input before any DB writes" → test that invalid input doesn't write

These contracts are usually documented in comments, function names, or the surrounding code. They're often the *most important* tests because they're what callers rely on.

## Specificity bar

Each case must be specific enough that someone writing it doesn't need to re-read the source. Compare:

**Too vague:**
> Test that the rate limiter rejects too many attempts.

**Right specificity:**
> 6th call to `attempt(userId)` within the lockout window throws `AccountLockedError`. Verify the 5 prior calls succeeded.

The second one tells the writer:
- The exact API call to make
- The exact number of iterations
- The exact error class to catch
- That earlier calls should succeed (which is part of the contract being tested)

If your suggestion can't be expanded to that level of specificity from your reading of the source, you don't understand the source well enough yet — read more before suggesting.

## When to suggest one case vs many

**One case per behavior, not per input.** If a function has the same behavior across `null`, `undefined`, and `""`, that's *one* case ("rejects empty inputs") with a parameterized test, not three separate cases.

**Separate cases per outcome.** If the same input produces different outputs depending on state, those are separate cases — different setup, different assertions, different rationale.

## What not to test

Don't suggest cases for:

- **Trivial getters/setters** — unless they have logic
- **Pure type narrowing** — TypeScript handles it
- **Generated code** — unless you're testing the generation
- **Framework behavior** — testing that React renders is testing React, not your code
- **Library wrappers with no logic** — `function getUser(id) { return db.users.findUnique({where: {id}}) }` doesn't need a unit test; an integration test of the calling code does
- **Console.log calls** — unless logging is a contract (audit logs, structured logs consumed by monitoring)

## When the right answer is "this needs integration testing"

Some code can't be meaningfully unit-tested. Examples:
- A function whose entire job is composing 4 other functions — testing it in isolation just tests the composition mock
- ORM-heavy code where the mock would have to reimplement the ORM
- HTTP handlers where the meaningful behavior is the request/response shape, not the in-memory logic

For these, suggest an *integration* or *contract* test instead of fighting to make a unit test work. See `test-types.md`.

## When to acknowledge there's nothing worth testing

Some files genuinely don't need tests:
- Pure re-exports
- Type definitions
- Static config with no logic
- Trivial mappers (one-line `{ ...obj, x: 1 }`)

If you're suggesting tests for a target and the honest answer is "this file doesn't need tests," say so. The user will trust the rest of the suggestions more.

## Calibration check

Before finalizing a case list, ask yourself:

1. **If a developer wrote only the must-haves, would the next bug in this module be caught?** If no, the must-haves aren't sharp enough.
2. **If a reviewer saw the suggestions, would they say "yes, those would have caught the last 3 bugs we shipped"?** That's the right level.
3. **Could you write each case in 30 minutes from the suggestion alone?** If a case takes hours to figure out from your description, you under-specified.
