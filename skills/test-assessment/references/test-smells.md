# Test Smells

Patterns that indicate a test suite has problems even when tests exist. Each smell includes how to detect it, why it matters, and what severity to assign.

## Tests with no assertions

**Detection:** Test bodies that contain calls but no assertion calls. Patterns:
- JS/TS: `it()` body with no `expect`, `assert`, `should`
- Python: `def test_` body with no `assert` keyword
- Ruby: `it` block with no `expect`, `assert`, `should`
- Java: `@Test` method with no `Assert.*`, `assertThat`, `assertEquals`

**Why it matters:** A test with no assertion is checking that the code *runs* but not that it *works*. It catches crashes, nothing else. Often a sign of a test that was started and never finished.

**Severity:** Medium. Higher if found in Critical modules.

## Tautological assertions

**Detection:** Assertions where both sides are the same expression or literal. Examples:
- `expect(user.id).toBe(user.id)`
- `assertEquals(5, 5)`
- `assert x == x`
- `expect(true).toBe(true)`

**Why it matters:** These always pass. They're cargo-culted assertions that look like tests but check nothing. Frequently the result of a half-written test or a copy-paste error.

**Severity:** Medium.

## Skipped or focused tests

**Detection:**
- `.skip`, `.only`, `xit`, `xdescribe`, `fit`, `fdescribe` (JS/TS)
- `@pytest.mark.skip`, `@pytest.mark.skipif`, `@unittest.skip` (Python)
- `xit`, `xdescribe`, `pending` (RSpec)
- `@Disabled`, `@Ignore` (Java)
- `t.Skip()` (Go)
- `markTestSkipped` (PHPUnit)

**Why it matters:**
- `.only` / `fit` / `fdescribe` left in CI means **only that test runs and the rest are silently skipped**. This is a Critical CI hazard.
- `.skip` accumulating over time is a sign of test rot — tests that broke and were disabled instead of fixed.

**Severity:** Critical for `.only`/`fit` in committed code. High for >5 skipped tests. Medium otherwise.

## Excessive mocking

**Detection:** Test files where the import of mocking utilities (`jest.mock`, `unittest.mock.patch`, `Mockito.mock`) appears more than test assertions. Or where every dependency of the unit under test is mocked.

**Why it matters:** When you mock everything, you're testing your assumptions about how the dependencies work, not how they actually work. The tests pass, the code breaks in production. Especially bad when mocking the unit under test itself.

**Severity:** Medium. High if the module is Critical.

## Tests hitting real services

**Detection:** Test code that contains:
- Real hostnames (`api.stripe.com`, production URLs)
- Database connection strings to non-test databases
- API keys or tokens (even in env-var lookups for production)
- File paths to non-test directories

**Why it matters:** Tests that hit real services are flaky (network), slow (latency), and dangerous (might mutate prod data). They also fail in CI environments without network access.

**Severity:** High. Critical if hitting prod credentials.

## Hardcoded sleeps

**Detection:**
- `setTimeout(..., N)` in tests where N > 100
- `time.sleep(N)` in tests
- `Thread.sleep(N)` in tests
- `await new Promise(r => setTimeout(r, N))`

**Why it matters:** Sleeps in tests indicate timing-dependent tests, which are flaky by nature. They also slow the suite down. Better solutions exist for almost all cases (proper async waiting, deterministic clocks).

**Severity:** Medium. Higher if many present (suite-wide flakiness).

## Snapshot-test overuse

**Detection:** A test suite with more `toMatchSnapshot()` / `assertSnapshot` calls than explicit assertions. Snapshot files larger than the source they test.

**Why it matters:** Snapshot tests catch *change* but don't catch *correctness*. Developers update snapshots without reviewing them, then ship bugs. Useful in moderation; toxic when overused.

**Severity:** Low to Medium depending on ratio.

## Hidden assertions in setup

**Detection:** `beforeEach`, `setUp`, fixture functions that contain assertions or that throw on bad state.

**Why it matters:** When setup throws, the failure message is "setup failed" not "the actual condition was wrong." Worse, the test that "would have run" is unclear. Assertions belong in test bodies.

**Severity:** Low.

## One giant test per file

**Detection:** Test files with a single test case that does dozens of things (registers a user, logs in, places an order, cancels it, etc.).

**Why it matters:** When the test fails, you don't know which step broke. Hard to debug, slow to run individually, encourages skipping.

**Severity:** Low to Medium.

## Tests that always pass / never fail

**Detection:** Hard to find statically, but check git log: `git log --all --diff-filter=M -- <test-file>` for files modified rarely or never since creation. Combined with a high-churn source file, suggests the tests don't catch the changes being made.

**Why it matters:** Tests that don't fail aren't doing their job.

**Severity:** Info — flag but don't over-claim.

## Test names that don't describe behavior

**Detection:** Test names like `test1`, `test_user`, `it('works')`, `it('returns true')` without context.

**Why it matters:** Test names are documentation. When a test fails in CI, the name should tell you what regressed. Vague names make debugging slower and indicate the test author didn't think clearly about what they were testing.

**Severity:** Low.

## How to triage smell findings

In the report:
- Combine related smells into one finding ("Test quality issues: 14 skipped tests, 6 tests with no assertions, 3 tautological assertions")
- Don't list every individual occurrence — list a count with 2-3 examples and a path to the worst offenders
- Severity comes from *what's affected*, not *how many*. 1 skipped test in the auth module is worse than 20 in the logging module.
- If the same file shows multiple smells, mention the file once with all its issues, not once per smell.
