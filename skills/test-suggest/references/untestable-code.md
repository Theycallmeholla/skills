# Untestable Code

Some code can't be unit-tested without refactoring. Recognize it. Don't suggest workarounds that mock everything in sight — that produces tests that pass while the code breaks. Be honest with the user.

## Signals that code is untestable as-written

### Heavy module-level side effects on import

```ts
// Top of file — runs on import
const db = new DatabaseClient(process.env.DATABASE_URL);
const stripe = new Stripe(process.env.STRIPE_KEY!);
console.log('Module loaded');

export function chargeUser(userId, amount) {
  return stripe.charges.create({ ... });
}
```

The exported function can't be tested in isolation because *importing the file* tries to connect to a database and Stripe. Testing requires mocking before import (Jest auto-mocks, `vi.mock`), and even then the test is fragile.

**Honest answer:** This needs DI. Don't suggest a unit test; suggest the case as an integration test or recommend extraction:
> "lib/charges.ts initializes Stripe at module scope, which makes unit testing brittle. Either:
> - Refactor to inject the Stripe client (e.g., `chargeUser(stripeClient, userId, amount)`)
> - Test this via an integration test with a real Stripe test-mode key"

### Hardcoded singletons

```ts
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

export async function getUser(id) {
  return prisma.user.findUnique({ where: { id } });
}
```

Same problem — the dependency is hardcoded. Tests have to either mock `@prisma/client` (testing the mock, not the code) or use a real test DB (integration).

**Honest answer:** Suggest the integration test, OR recommend a one-line refactor (factory function that takes the client). Don't pretend it's a clean unit test.

### Direct `Date.now()` / `new Date()` / `Math.random()` calls

```ts
export function generateToken() {
  return `${Date.now()}-${Math.random()}`;
}
```

You can mock `Date.now` and `Math.random`, but it's clunky and language-dependent.

**Honest answer:** Suggest the test with a note: "Will need to fake the clock and RNG (`vi.useFakeTimers()`, `vi.spyOn(Math, 'random')`) — consider whether injecting a clock/random source would be cleaner long-term."

### File system reads/writes inline

```ts
export function loadConfig() {
  return JSON.parse(fs.readFileSync('./config.json', 'utf-8'));
}
```

Either mock `fs` (fragile and depends on test framework) or write a real fixture file (now your test depends on the working directory).

**Honest answer:** Suggest one of:
- Refactor to take the config path as a parameter (1-line change, makes it trivially testable)
- Use a tmp dir fixture and accept this as integration-level

### Network calls without injection

```ts
export async function fetchWeather(city) {
  const res = await fetch(`https://api.weather.com/?q=${city}`);
  return res.json();
}
```

Mocking `fetch` globally is a common pattern but easy to leak between tests.

**Honest answer:** Suggest a contract test with `nock` or `msw` rather than a unit test, OR recommend injecting a fetcher.

### "God classes" with too many responsibilities

```ts
class UserService {
  // 40 methods covering auth, billing, notifications, profile,
  // permissions, and email sending
}
```

You *can* test each method, but each test has to set up the entire class's dependency chain. The test setup is bigger than the test itself.

**Honest answer:** Suggest a few tests for the highest-value methods, but flag in the output: "UserService has too many responsibilities — most useful next step is splitting it before adding more tests."

### Side effects that can't be observed

```ts
export function doImportantWork(data) {
  // 100 lines of logic
  return; // returns void, no observable output
}
```

If you can't observe the output, you can't assert on it. The function is testable only via its side effects, which need to be observable somehow.

**Honest answer:** Either the function actually does have observable effects (DB writes, log output, downstream calls) — which the suggestion should target — or it really is unobservable, in which case the right answer is "this function shouldn't exist as written; it can't fail in any way the test can detect."

### Functions that swallow all errors

```ts
export async function syncData() {
  try {
    // 100 lines
  } catch (e) {
    // do nothing
  }
}
```

The test can't distinguish "ran successfully" from "failed silently." Even if you stub the dependencies to throw, the function still resolves to `undefined`.

**Honest answer:** "syncData swallows errors, so failures can't be detected by tests. Recommend changing the catch to log and rethrow (or to return an error result) before adding tests."

## How to write the "untestable" finding

In the suggestion output, dedicate a section labeled "Untestable as-written" if any apply. For each:

- **The pattern** — what makes it hard to test
- **The honest options** — refactor (and how, briefly), test at a higher level (integration/contract), or accept and skip
- **Don't pretend** — never suggest a unit test that requires mocking 5+ dependencies. That's the failure mode of generated tests.

Example output section:

```
## Untestable as-written

**lib/charges.ts** initializes Stripe at module scope. Options:
- (Recommended) Refactor: pass the Stripe client as the first argument, then unit-test with a fake.
- Or: skip unit tests, write an integration test with Stripe in test mode.

**lib/sync-job.ts** swallows errors silently. Add tests only after changing the catch block to surface failures, otherwise the tests can't tell pass from fail.
```

## When the user pushes back

If the user says "just give me a test, I don't care about refactoring":

You can still suggest the case, but be explicit: "This will test that the function runs without throwing on the happy path. It will not catch most realistic bugs because everything material is mocked."

That's an honest answer. The user can decide whether the test is worth writing anyway. Don't pretend a heavily-mocked test is a real test — they read the same to a future maintainer, but they don't catch the same bugs.

## What's the threshold for "untestable"?

Rough rule: **if the test setup is longer than the function being tested, the code probably needs DI before tests are worth writing.**

This isn't always true, but it's a useful prompt to slow down and look for the real issue.
