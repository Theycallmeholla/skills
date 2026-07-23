# Risk Mapping Rubric

The risk map is the centerpiece of the assessment. This doc gives you the rubric for assigning a risk level to each module and a coverage level alongside it.

## Risk levels

### Critical
A bug here causes immediate, visible damage: lost money, breached data, broken auth, deleted user content. Examples:
- Payment processing, refund logic, billing calculations
- Authentication: login, session creation/validation, password reset, OAuth callbacks
- Authorization: permission checks, role assignments, ACL evaluation
- Data deletion: account closure, GDPR endpoints, hard-delete operations
- Cryptography: signing, verification, encryption, key derivation
- Anything that talks to a payment processor (Stripe, Plaid, etc.)

A Critical module with no tests is the top finding of the report. Always.

### High
Core business logic. A bug causes wrong behavior, bad data, or degraded UX, but isn't immediately catastrophic. Examples:
- The main domain model (Orders, Reservations, Posts — whatever the product *is*)
- API endpoints that mutate state
- Background job processors, queue consumers
- Webhook handlers
- Database migration runners
- Input validation and sanitization for non-trivial inputs
- Rate limiting, throttling, quota enforcement

### Medium
Supporting logic. A bug is annoying but recoverable. Examples:
- Email/notification formatting (the *content*, not the *delivery*)
- Reporting, analytics aggregation
- Search ranking, sorting, filtering
- UI state management for non-critical flows
- Caching layers (the cache itself, not the data it caches)

### Low
Glue, utilities, presentation. Bugs are obvious and quickly noticed. Examples:
- String formatting helpers
- Date display utilities
- Logging wrappers
- Static config parsers
- Trivial CRUD with no business rules

## Coverage levels

Determined per-module from static analysis if no coverage data exists.

### None
- No corresponding test file
- Or: a test file exists but contains no test cases (only setup/teardown, or an empty `describe` block)
- Or: tests exist but never import the module under test

### Sparse
- A test file exists with 1-3 test cases for a module that has 5+ exported functions
- Tests cover only the happy path; no error cases
- Tests exist but rely entirely on mocked versions of the module under test (testing the mock, not the code)

### Partial
- Test file covers most exported functions but skips edge cases
- Happy path well-covered, error paths partially covered
- Some integration points tested, others not

### Solid
- Tests for all exported functions/methods
- Both happy path and error path covered
- Edge cases tested (nulls, empty inputs, boundary values)
- Tests that would actually catch a regression

## How to map a module

For each module that matters (use the sampling approach from SKILL.md if the repo is huge):

1. Determine risk by reading the module name, location, and the first 50-100 lines. Most modules announce what they do clearly. If unclear, look at imports — a module that imports a payment SDK is Critical regardless of name.

2. Determine coverage:
   - Find the corresponding test file (try `<name>.test.<ext>`, `tests/<name>.<ext>`, `__tests__/<name>.<ext>`, `spec/<name>_spec.<ext>`)
   - Count test cases: `it(`, `test(`, `def test_`, `it '`, `func Test`
   - Count exported things in the source: `export function/const`, `def ` (Python public), `func` (Go public), `public function` (PHP)
   - Skim test names: do they include error/failure/invalid/edge keywords?

3. Place in the matrix.

## The matrix

Plot every module assessed. The interesting cells:

|             | None         | Sparse       | Partial      | Solid        |
|-------------|--------------|--------------|--------------|--------------|
| **Critical**| **TOP FINDING** | **TOP FINDING** | High        | OK           |
| **High**    | High         | High         | Medium       | OK           |
| **Medium**  | Medium       | Low          | Low          | OK           |
| **Low**     | Info         | Info         | OK           | OK           |

Cells marked TOP FINDING become the primary findings of the report. Cells marked OK don't need to appear individually — just note the count.

## What to put in each finding

For every Critical+None or Critical+Sparse cell, write a finding that includes:

1. **What** — the module name and what it does
2. **Why it matters** — the failure mode if a bug ships unnoticed
3. **What to test** — 2-4 specific cases that should be covered (happy path, the most likely error case, an edge case, a security-relevant case if applicable)
4. **What kind of test** — unit, integration, contract, end-to-end?

Don't write the actual tests. Describe what should be tested.

## Anti-patterns to avoid in the rubric

- **Don't grade on volume.** A test file with 50 trivial assertions is not better than 5 meaningful ones.
- **Don't reward mocking everything.** Heavy mocking around a unit under test means the test isn't actually testing the unit's behavior.
- **Don't penalize the absence of tests for obviously trivial code.** A one-line getter doesn't need a test. Use judgment.
- **Don't score generated code (proto, OpenAPI clients, ORM models without custom logic) as needing tests.** Note them as "out of scope" rather than "uncovered."
