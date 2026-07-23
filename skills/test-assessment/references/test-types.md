# Test Types and Pyramid Health

A healthy test suite has multiple types of tests in roughly the right proportions. This doc helps you identify which types exist and which are missing.

## The types

### Unit tests
**What:** Test a single function, method, or class in isolation. No I/O, no network, no real database. Dependencies are stubbed or use simple in-memory implementations.

**How to identify them:**
- Filenames: `*.test.*`, `*.spec.*`, `*_test.py`, `_spec.rb`
- Test framework imports: Jest, Mocha, Pytest, RSpec, JUnit, xUnit
- Test bodies that import the module under test directly and call its functions
- Fast: usually milliseconds per test
- No setup/teardown of external services

**Healthy ratio:** ~70% of tests in most codebases. Less if the codebase is very glue-heavy (mostly orchestration of other services).

### Integration tests
**What:** Test multiple modules working together, or a module against a real (test) database / file system / message queue. They exercise the seams between components.

**How to identify them:**
- Often in a separate directory: `tests/integration/`, `__tests__/integration/`, `spec/integration/`
- Filenames sometimes: `*.integration.test.*`, `*_integration_test.go`
- Setup/teardown of test databases, fixtures, transaction rollback
- Test framework + DB driver + ORM imports

**Healthy ratio:** ~20-25% of tests. Often the highest-value tests because they catch what unit tests miss (wrong SQL, wrong contract assumptions, real timing).

**Common gap:** Codebases that have lots of unit tests but no integration tests. The unit tests pass; the deployed app breaks at the seams.

### API / Contract tests
**What:** Test the HTTP/gRPC/etc. surface that other systems consume. Verify request/response shapes, status codes, error formats, idempotency.

**How to identify them:**
- Use HTTP clients (`supertest`, `requests`, `httpx`, `axios` in tests)
- Test against the running app (in-process or via test server)
- Check status codes, headers, response bodies
- Sometimes: contract testing tools (Pact, Spring Cloud Contract)

**Healthy ratio:** Should exist for every public API endpoint. If absent, every breaking change to the API ships unnoticed.

### End-to-end tests
**What:** Drive the running application like a user would — through the UI for web apps, through the CLI for tools, through the full request path for services.

**How to identify them:**
- Tools: Playwright, Cypress, Selenium, Puppeteer, TestCafe, Detox, Espresso, XCTest
- Often in `e2e/`, `cypress/`, `tests/e2e/`
- Slow: seconds to minutes per test
- Test the deployed/built artifact, not source code

**Healthy ratio:** ~5-10%. Few but high-value. Cover the most critical user journeys (signup, checkout, login).

**Anti-pattern:** Codebases with *only* E2E tests ("the inverted pyramid"). Slow, flaky, expensive to maintain, and they still miss unit-level bugs.

### Property-based / fuzz tests
**What:** Generate many random inputs and check invariants hold. Useful for parsers, validators, serializers, math.

**How to identify them:**
- Libraries: `fast-check` (JS), `Hypothesis` (Python), `QuickCheck` (Haskell), `proptest` (Rust)
- Usually small in number but high-leverage

**Healthy ratio:** Rare in most codebases. Their absence is only a finding if the codebase has obvious property-test territory: input parsers, encoders/decoders, validation logic, math libraries.

### Regression tests
**What:** Test cases tied to a specific bug that was fixed. Often documented with the bug number or PR link in a comment.

**How to identify them:**
- Comments referencing issue numbers: `// regression: fixes #1234`, `# bug from PR-567`
- Test names: `test_regression_*`, `it('does not regress when...')`

**Healthy signal:** Their existence indicates a culture of writing tests when bugs are fixed. Their absence in a mature codebase suggests bugs are being fixed without tests.

## Identifying the suite's shape

After Phase 1 inventory, classify the tests by type. Look at:

1. **Directory structure** — separate `unit/`, `integration/`, `e2e/` directories tell you immediately
2. **Imports** — what does each test file import? HTTP clients = API/E2E, DB drivers = integration, just the source = unit
3. **Speed indicators** — `jest.config` timeout settings, `pytest.ini` markers, CI parallelization
4. **CI structure** — multiple test jobs (`test:unit`, `test:integration`, `test:e2e`) is a strong signal

## Common shapes and what they mean

### Pyramid (healthy)
Many unit, fewer integration, few E2E. Standard advice. Fast feedback at unit level, confidence at higher levels.

### Inverted pyramid (problematic)
Few unit, some integration, many E2E. Slow CI, flaky suite, hard to localize failures. Common in codebases that started with E2E "to get coverage" and never built up the unit layer.

### Hourglass (questionable)
Many unit, no integration, some E2E. Misses everything in between — wrong SQL, wrong contracts, wrong service interactions. Often the result of unit tests being easy and E2E being mandated, with no one owning the integration layer.

### Trophy (modern variant, often healthy)
Many integration tests, fewer unit, few E2E, plus static analysis (TS, type checking) doing the work that brittle unit tests used to. Increasingly common in TypeScript/Python codebases.

### Missing layers
- No unit tests → developers can't iterate fast, every change runs the slow suite
- No integration tests → the most likely place for real bugs
- No E2E tests → critical user journeys can break without anyone noticing
- No API tests → consumers break on every release

## What to put in the report

After identifying the suite shape:

1. **State the shape** in plain English: "This codebase has a pyramid-shaped suite with strong unit coverage and minimal integration tests."

2. **Call out missing layers** as findings with severity:
   - Missing unit tests in a complex codebase: High
   - Missing integration tests: High (this is the most common, most painful gap)
   - Missing API tests for a service with public consumers: High
   - Missing E2E tests for critical user journeys: Medium to High depending on stakes
   - Missing property tests where they'd help: Low to Medium

3. **Don't recommend test types that don't fit.** A library doesn't need E2E tests. A pure-data service doesn't need UI tests. Match recommendations to what the codebase actually is.
