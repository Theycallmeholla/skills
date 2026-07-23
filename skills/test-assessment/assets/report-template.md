# Test Assessment Report — [Project Name]

**Assessed:** [Date]
**Scope:** [What was assessed — full repo, specific module, etc.]
**Method:** [Static analysis / coverage data / both. Note any sampling.]

---

## Executive Summary

[3-5 sentences. Answer these in plain English:]

- **What's the overall state of the test suite?** (Healthy / Adequate / Struggling / Effectively absent)
- **What's the single biggest gap?**
- **Is this a "ship more tests" problem or a "fix the existing suite" problem?**

[Example: "The codebase has 240 test files covering ~60% of source files by count, but coverage is heavily skewed: utility code is well-tested while the payment processing and authentication modules have minimal coverage. The suite has structural problems — 14 skipped tests, no integration tests, and CI does not enforce test passage. Priority is fixing the test/code risk mismatch before adding more tests."]

---

## The Numbers

[Two paragraphs max. Drop in the inventory output.]

- **Test framework(s):** [Jest, Pytest, etc.]
- **Test files:** [count]
- **Source files:** [count]
- **Ratio:** [tests per source file]
- **Test cases (approximate):** [count]
- **Coverage data available:** [Yes — N% line / No — assessment based on static analysis only]
- **CI runs tests on PRs:** [Yes / No / Advisory only]

---

## Risk Map

The centerpiece of the assessment. Modules placed by risk × coverage.

|             | None         | Sparse       | Partial      | Solid        |
|-------------|--------------|--------------|--------------|--------------|
| **Critical**| [list]       | [list]       | [list]       | [count]      |
| **High**    | [list]       | [list]       | [count]      | [count]      |
| **Medium**  | [count]      | [count]      | [count]      | [count]      |
| **Low**     | [count]      | [count]      | [count]      | [count]      |

[Note: cells with high counts can be summarized; cells with critical entries should list specific files/modules.]

---

## Top Gaps

The Critical+None and High+Sparse cells, expanded into actionable findings.

### Finding 1: [Module/Area Name] — Severity: [Critical/High]

- **What:** [Module name and what it does]
- **Why it matters:** [Failure mode if a bug ships]
- **Current state:** [No tests / N test cases covering only happy path / etc.]
- **What to test:**
  - [Specific scenario 1, e.g., "Payment with insufficient funds returns proper error code, no charge made"]
  - [Specific scenario 2]
  - [Specific scenario 3]
- **Test type recommended:** [Unit / Integration / Contract / E2E]

### Finding 2: [...]

[Repeat for each top gap. Aim for 3-8 findings here. More than 10 means you should consolidate.]

---

## Quality Findings

Issues with tests that exist. Severity-ranked.

### Critical-severity quality issues

- [e.g., ".only() left in 2 test files — these silently disable the rest of their test files in CI"]

### High-severity quality issues

- [e.g., "No integration tests — every test runs against mocked dependencies, leaving the seams between modules untested"]
- [e.g., "CI workflow does not block merges on test failure — tests are advisory only"]

### Medium-severity quality issues

- [e.g., "14 skipped tests across the suite, with no tracking of why or when they'll be re-enabled"]
- [e.g., "Heavy mocking in the user-service tests (avg 8 mock calls per test); tests likely don't catch real integration issues"]

### Low-severity quality issues

- [e.g., "Vague test names in 12 files (`it('works')`, `test('test1')`); test failures will be hard to diagnose"]

---

## What's Working Well

[Earn credibility for the negatives. Be specific. Don't fabricate.]

- [e.g., "The auth-token-validation module has thorough unit tests including edge cases for expired, malformed, and tampered tokens"]
- [e.g., "Test files are co-located with source, making the ownership model clear"]
- [e.g., "CI runs tests on multiple Node versions, catching version-specific bugs"]

[If genuinely nothing is working well: "The suite has structural issues that should be addressed before attempting to evaluate quality. The recommendations below assume a near-complete rebuild of the testing approach."]

---

## Recommended Next Steps

A prioritized plan, not a backlog.

### First (this week)

[1-3 items. Actions that take hours and have outsized impact.]

- [e.g., "Remove `.only()` from PaymentService.test.ts and BillingFlow.test.ts — these are masking failures in CI"]
- [e.g., "Make CI block merges on test failure (set `required: true` on the test workflow)"]

### Soon (this month)

[3-7 items. Medium-effort changes that close the most dangerous gaps.]

- [e.g., "Add integration tests for the payment processing flow: charge creation, refund, failure handling"]
- [e.g., "Add unit tests for permission-check.ts — currently 0 tests for code that gates 14 API endpoints"]

### Eventually (this quarter)

[Larger structural improvements.]

- [e.g., "Establish E2E test for the signup → first-payment user journey"]
- [e.g., "Replace heavy mocking in user-service tests with a real test database to verify SQL behavior"]
- [e.g., "Audit and re-enable or delete the 14 skipped tests"]

---

## Methodology Notes

[Brief notes on how the assessment was performed. Include caveats.]

- Inventory and smell scans run via `test-assessment` skill scripts on [date]
- Risk classification based on static analysis (file/directory naming, imports, manifest inspection)
- [Did or did not have access to] coverage data
- [Note any sampling or scope limitations]

---

*Generated using the test-assessment skill. Findings reflect the state of the codebase at the time of assessment and may be affected by sampling, naming conventions that don't match common patterns, or generated code that wasn't excluded.*
