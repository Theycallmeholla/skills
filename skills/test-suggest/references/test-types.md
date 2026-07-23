# Choosing the Right Test Type per Case

Not every case is a unit test. Match the type to what the case actually exercises.

## The four types in scope

### Unit test
- Single function, method, or class in isolation
- Dependencies stubbed/mocked
- No I/O, no real DB, no real network
- Fast (milliseconds)
- Can run thousands of these in a CI pass

**Suggest a unit test when:** the case is about pure logic — input → output, branch coverage, error paths in code that doesn't actually touch external systems.

**Don't suggest a unit test when:** making the case work requires mocking 5+ dependencies. That's a sign the test is fighting the design and won't catch real bugs.

### Integration test
- Multiple modules together
- Real test database, real file system, real local services
- May use Docker containers, in-memory DBs, or real Postgres on a CI port
- Slower (hundreds of milliseconds to seconds per test)

**Suggest an integration test when:**
- The case exercises real SQL behavior (constraints, joins, transactions)
- The case crosses a real module boundary (repository → DB, queue producer → consumer)
- The case verifies behavior that depends on the *actual* dependency, not a mock of it

**Examples:**
- "Concurrent inserts on the same unique key produce exactly one row, second errors with constraint violation"
- "Transaction rollback after partial commit leaves DB in pre-transaction state"

### Contract test (HTTP/RPC contract)
- Invokes a real handler with a real request shape
- Verifies the response shape, status code, headers, error format
- Internal dependencies often stubbed (DB layer mocked, business logic real)
- Sits between unit and integration

**Suggest a contract test when:**
- The case is about an API endpoint's request/response surface
- The thing being tested is "this handler emits the right JSON"
- The case targets auth gates, permission checks at the edge, response shaping

**Examples:**
- "GET /api/users/:id returns 404 with `{ error: 'not found' }` body when user doesn't exist"
- "POST /api/posts strips the `internalNotes` field before saving"
- "GET /api/admin/* returns 403 for non-admin actors"

### End-to-end test
- Full app running (or as close as practical)
- Real browser (Playwright, Cypress) for web UIs
- Real network requests, real user flows
- Slowest (seconds to minutes per test)
- Most fragile to maintain

**Suggest an E2E test when:**
- The case is about a user journey across multiple pages
- The case verifies behavior that depends on browser/JS specifics (cookies, redirects, focus management)
- The case targets a critical revenue flow that must not break (signup, checkout, login)

**Don't suggest E2E when:** any other type would catch the same bug. E2E is expensive — reserve it for cases that genuinely need the full stack.

## How to pick

Walk this decision tree:

1. **Can this be exercised purely in-memory with no real dependencies?** → Unit
2. **Does the case depend on the actual database/queue/external system behavior?** → Integration
3. **Is the case about an HTTP/RPC handler's request-response contract?** → Contract
4. **Does the case require a real browser or full request lifecycle?** → E2E

When in doubt, **prefer the cheapest type that catches the bug**. A unit test that catches the bug is better than an E2E test that catches the same bug, because the unit test runs in milliseconds.

## The "mocking everything" anti-pattern

If a case requires mocking the database, the auth system, the email sender, and the external HTTP client just to run, **stop**. You're not testing the code; you're testing your assumptions about what the dependencies do. The test will pass and the code will break in production.

Two real options:
1. Suggest a contract or integration test instead, where the boundaries are real
2. Note in the output that "this code is hard to test in isolation — consider refactoring to extract the pure logic"

See `untestable-code.md` for the second option in detail.

## The "E2E for everything" anti-pattern

Some teams reach for E2E because "it tests the real thing." This produces slow, flaky CI and tests that are hard to localize when they fail. If you find yourself suggesting E2E for the 5th case in a row, push back: probably most of those should be contract or integration tests.

A healthy ratio per target file:
- Lots of unit cases (10s)
- A few integration/contract cases (3-7)
- Maybe one E2E case (or zero)

If your suggestions invert this, re-examine.

## Mapping common code patterns to test types

| Code pattern | Default test type | Notes |
|---|---|---|
| Pure function (input → output) | Unit | |
| Class with internal state, no I/O | Unit | |
| Function that calls 1 dependency | Unit (with stub) or Integration | If stubbing is one line, unit. If three lines of mock setup, integration. |
| Repository / DAO | Integration | Mocking the ORM defeats the purpose |
| HTTP route handler | Contract | Real handler, stubbed business deps |
| Validator/parser | Unit | Often a great target for property-based tests |
| Auth middleware | Contract | Test against the real handler chain it wraps |
| Background job / queue consumer | Integration | Real queue, real handler |
| React/Vue component | Unit (with testing-library) or E2E | Component tests for logic, E2E for journeys |
| CLI command | Integration | Spawn the binary or invoke the entry point |
| Database migration | Integration | Run the migration on a fresh DB, assert schema |
| Crypto primitive | Unit | Round-trip, tamper, wrong-key cases |
| Rate limiter | Unit (if pure logic) or Integration (if uses Redis) | |
| Webhook handler | Contract | Test the request → response, mock outbound effects |

## Per-test-type setup tips

When suggesting cases, include any non-obvious setup notes:

**Unit:**
- Specify what to stub and the stub's behavior
- If using fake time (clock control), say so
- If the function reads env vars, mention which need to be set

**Integration:**
- Mention if the test needs a fresh DB or shared one
- Note any seed data or factories needed
- If the test runs against a real port, mention what process needs to be running

**Contract:**
- Specify how the handler is invoked (in-process import vs HTTP via supertest)
- Note any auth setup (signed cookie, JWT, session)
- Mention which deps are stubbed vs real

**E2E:**
- Specify the user role / state at start
- Mention whether the test needs to seed data first
- Note any external services that need to be mocked at the network layer (e.g., MSW)
