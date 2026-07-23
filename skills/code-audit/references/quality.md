# Code Quality & Maintainability Checklist

Quality issues are the slow leak. They don't break things today, but they make the codebase progressively more expensive to change. Catch them early or pay forever.

## 1. Complexity heuristics

These are heuristics, not laws. A 200-line function might be fine; a 50-line function might be tangled. Use the numbers as triage signals, then read.

| Signal | Threshold | What it usually means |
|---|---|---|
| File length | >500 lines | Probably mixing responsibilities |
| Function length | >50 lines | Probably doing too many things |
| Function arguments | >5 | API design issue, often a "bag of args" |
| Nesting depth | >4 levels | Hard to follow, often reducible with early returns |
| Cyclomatic complexity | >15 | Too many branches; refactor candidate |
| Inheritance depth | >3 | Coupling chain that's hard to reason about |

To find them quickly: see `scripts/find_smells.sh`.

## 2. Duplication

DRY violations come in flavors:

- **Copy-paste with one variable changed** — extract a function or component
- **Same logic implemented differently in three places** — pick the best, kill the others
- **Parallel hierarchies** — two enums that always change together, two switch statements over the same cases

Tools: `jscpd`, `pmd-cpd`, `simian` (run if available; otherwise visual inspection on suspicious files).

Watch for the over-correction too: premature abstraction creating "DRY" code that's worse than the duplication. If two pieces of code look the same but represent different concepts, leaving them separate is correct. The test: do they need to change for the same reasons?

## 3. Naming

Bad names are bugs in slow motion. Look for:

- **Single letters** outside small loops (`u`, `o`, `s` as parameters)
- **Hungarian notation** in modern code (`strName`, `arrItems`)
- **Misleading names**: `getX` that mutates, `validate` that throws vs returns, `is*` that returns a non-boolean
- **Generic names**: `data`, `info`, `manager`, `helper`, `util`, `process` — these say nothing
- **Inconsistent terminology**: `user`, `account`, `customer` used interchangeably for the same concept
- **Negations**: `isNotEmpty` → `isPopulated`; double-negation in conditions (`!isNotReady`) is a finding

## 4. Error handling

Run this scan and read every hit critically:

```bash
# Empty catches
grep -rEn 'catch\s*\([^)]*\)\s*\{\s*\}' --include='*.{js,ts,java,cs}' .

# Bare except in Python
grep -rEn '^\s*except\s*:' --include='*.py' .

# Unwrap proliferation in Rust
grep -rEn '\.unwrap\(\)' --include='*.rs' . | wc -l

# Errors logged then ignored
grep -rEn 'console\.error.*\n.*return' --include='*.{js,ts}' .
```

What to flag:
- **Empty catches** — silently swallowing errors is almost always wrong
- **Catch-and-log without rethrow** on errors that should fail loudly
- **Generic catches** that swallow `KeyboardInterrupt` / `SystemExit` (Python `except Exception` is OK; bare `except:` is not)
- **No error handling at all** on async operations — unhandled rejections crash modern Node, get silently dropped on browsers
- **Wrong layer handling**: low-level functions catching errors that the caller should decide about

What good error handling looks like:
- Explicit choice at every layer: handle, transform, or propagate
- Errors carry enough context to debug from logs alone
- User-facing error messages don't leak internals (stack traces in production responses are a finding)

## 5. Comments

Three categories:

**Useful** — the *why*: business rules, non-obvious constraints, links to issues, warnings about gotchas.

**Useless** — the *what*: `// increment i by 1` over `i++`. Noise. Often outdated and lying.

**Harmful** — comments that disagree with the code. The code is true; the comment is a trap. When you find these, it's usually a sign of "code rotted, comments didn't follow."

**Commented-out code** — flag every block. Either the code is in version control (so deletion is safe) or the project doesn't use version control (which is the bigger finding). Exception: temporary debug toggles clearly labeled.

## 6. Dead code

- Unreferenced exports / functions / classes
- "v2" implementations alongside "v1" with no migration plan
- Feature flags for features that shipped years ago
- Test fixtures for tests that were deleted
- Endpoints not called by the current frontend

Tools: `ts-prune`, `unimport`, `vulture` (Python), `npm-check`, IDE "find usages."

Caveat: in libraries / public APIs, "unused" code may be public API consumers depend on. Confirm before recommending removal.

## 7. Type safety (in typed languages)

- `any` / `Any` proliferation in TypeScript / Python — these are escape hatches that nullify the type system
- Type assertions (`as`) used to silence errors instead of fixing them
- `@ts-ignore` / `# type: ignore` without explanation
- `eval`-like dynamic dispatch that defeats type checking
- Discriminated unions used as plain unions (missing the discriminant in pattern matches → runtime errors)

## 8. Modularity & coupling

- **God modules**: a `utils.js` with 80 unrelated exports. Break it up.
- **Circular imports**: usually a layering violation. Find with `madge` (JS), `pylint` (Python).
- **Implicit dependencies**: modules that only work if some other module was imported first (initialization order coupling).
- **Test coupling to implementation**: tests that mock everything inside a function are testing the mock.

## 9. Configuration & magic values

- **Magic numbers**: `if x > 86400` should be `if x > SECONDS_PER_DAY`.
- **Magic strings**: status values, role names, URL paths repeated as string literals throughout the code.
- **Configuration in source**: production URLs, feature flag values, thresholds hardcoded where they should be config.
- **Environment leakage**: `if (process.env.NODE_ENV === 'production')` scattered widely. Centralize.

## 10. API design

For internal APIs (functions, classes, modules):

- **Bag-of-args parameters**: `createUser(opts: { name, email, role, ... })` is fine. `createUser(name, email, role, dept, manager, startDate, ...)` is not.
- **Boolean parameters**: `render(data, true, false, true)` — call sites are unreadable. Prefer enums or named options.
- **Output parameters / mutation**: passing a list and mutating it is surprising in most languages. Return new values.
- **Returning multiple types**: `getUser` returning `User | null | undefined | string` (error message) — pick a contract.

## 11. Concurrency

- **Shared mutable state without synchronization** — race conditions
- **Locks held across I/O calls** — deadlock risk, latency disaster
- **Async/await missed**: a forgotten `await` returns a Promise where the caller expects the resolved value. Search for `.then` chained off the result of an `async` function call.
- **Fire-and-forget promises**: `someAsyncOp()` with no `await` and no `.catch` — unhandled rejection waiting to happen.
- **Goroutine leaks**: goroutines started without a clear termination path.

## 12. Logging

Quality (security-relevant logging is in `security.md`):

- **Logs without context**: `log.error("failed")` — failed *what* on *which* request?
- **Inconsistent log levels**: `log.info` for errors, `log.error` for routine events.
- **Log spam**: logging every database query at INFO will overwhelm storage and obscure real signals.
- **No structured logging**: free-text logs are hard to query; structured (JSON) logs let you filter by request ID, user ID, endpoint.

## 13. Tests as code quality signal

You audit tests separately for coverage, but tests also reveal source quality:

- Code that's hard to test is usually code with hidden dependencies / side effects
- Tests that need 50 lines of mocks indicate over-coupled production code
- "Testing through the UI" because units can't be tested in isolation = layering problem
- Lots of `// eslint-disable` in tests = tests fighting the production code's contracts

## 14. Performance smells (light pass — see performance.md for depth)

- O(n²) loops where O(n) is straightforward
- Repeated computation that should be memoized (same call with same args inside a loop)
- String concatenation in loops in languages where it matters (Java, older JS engines)
- Repeated database / API calls inside loops (N+1)

## 15. Quick wins to recommend

These are universally applicable and easy to suggest:

- **Linter + formatter** (ESLint+Prettier, Black, gofmt, rubocop). If absent, recommend.
- **Pre-commit hooks** to enforce lint/format/typecheck before commit.
- **Editor config** so contributors don't fight indent/EOL conventions.
- **CI lint job** so violations fail the build, not just local tooling.
- **Type checker in CI** if the project uses TypeScript or Python with type hints.

These don't fix existing issues but prevent regression — and the audit is incomplete without recommending them when missing.

---

## What NOT to flag

- Style preferences with no functional impact (unless the project has a documented style guide that's being violated)
- "I'd write this differently" without a concrete reason
- Patterns that are idiomatic in the language/framework but non-idiomatic elsewhere
- Internal naming you'd change but isn't actively misleading
- Test code held to the same complexity standards as production (tests are intentionally explicit and repetitive)
