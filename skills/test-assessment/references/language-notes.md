# Language and Framework Notes

Per-language conventions for finding tests, recognizing frameworks, and spotting language-specific smells.

## JavaScript / TypeScript

**Test file conventions:**
- `*.test.{js,jsx,ts,tsx,mjs}` (Jest, Vitest)
- `*.spec.{js,jsx,ts,tsx}` (Jasmine, Mocha, Vitest)
- `__tests__/**` directory (Jest convention)
- `tests/`, `test/` directories (varies)

**Frameworks (in rough order of prevalence):**
- **Jest** — `jest.config.{js,ts,json}`, `package.json` `jest` key
- **Vitest** — `vitest.config.{js,ts}`, `vite.config.{js,ts}` with test block
- **Mocha** — `.mocharc.{js,json,yml}`, often paired with Chai
- **Jasmine** — older, less common in new projects
- **Tap / AVA / Tape** — niche but exist
- **Playwright Test** — `playwright.config.ts`, increasingly common
- **Cypress** — `cypress.config.{js,ts}`, `cypress/`
- **node:test** — built-in Node test runner, growing in usage

**Coverage:**
- Istanbul/nyc: `coverage/`, `.nycrc`
- Jest built-in: `--coverage` flag, output to `coverage/`
- v8 native: `--experimental-test-coverage` (node:test)

**Smells specific to JS/TS:**
- `expect(x).toBeTruthy()` overused instead of specific assertions
- `expect(fn).toHaveBeenCalled()` without checking *what* it was called with
- Snapshot tests with no review process
- `// @ts-ignore` to make tests compile (often masks broken tests)
- Tests inside the source tree mixed with production code (harder to exclude from builds)

## Python

**Test file conventions:**
- `test_*.py` (Pytest default)
- `*_test.py` (some projects)
- `tests/` directory at project root

**Frameworks:**
- **Pytest** — most common. `pytest.ini`, `pyproject.toml` with `[tool.pytest.ini_options]`, `conftest.py`
- **unittest** — stdlib, used by older projects. `class TestFoo(unittest.TestCase)`
- **nose / nose2** — legacy, deprecated
- **doctest** — inline tests in docstrings, often forgotten

**Coverage:**
- `coverage.py`: `.coverage`, `.coveragerc`, `coverage.xml`, `htmlcov/`
- Often invoked via `pytest --cov`

**Smells specific to Python:**
- `assert True` or `assert 1 == 1`
- Bare `pytest.skip` without reason
- `mock.patch` chains 4-5 deep (over-mocking)
- Tests that import from production code with side effects at import time
- Missing `__init__.py` causing test discovery to silently miss files

## PHP

**Test file conventions:**
- `*Test.php` (PHPUnit convention)
- `tests/` directory

**Frameworks:**
- **PHPUnit** — dominant. `phpunit.xml`, `phpunit.xml.dist`
- **Pest** — newer, growing. Built on PHPUnit. `Pest.php`, `tests/Pest.php`
- **Codeception** — full-stack testing framework, less common now

**Coverage:**
- PHPUnit + Xdebug or pcov: `coverage.xml`, `coverage-html/`

**Smells specific to PHP:**
- `markTestSkipped` accumulating
- Tests that touch the global state (`$_SESSION`, `$_GET`, etc.) without proper isolation
- Database tests without transaction rollback (leaves test data behind)
- WordPress/Laravel codebases with no tests for custom logic (common pattern)

## Go

**Test file conventions:**
- `*_test.go` (mandatory, enforced by `go test`)
- Tests live alongside source in the same package (or `_test` package suffix for external tests)

**Frameworks:**
- **Standard `testing` package** — almost universal
- **Testify** (`github.com/stretchr/testify`) — adds `assert`, `require`, `suite`, `mock`. Very common.
- **Ginkgo + Gomega** — BDD style, less common
- **Go fuzz** — built into `go test` since 1.18

**Coverage:**
- Built-in: `go test -cover`, `-coverprofile=coverage.out`

**Smells specific to Go:**
- Tests that don't use `t.Helper()` in test helpers (worse error messages)
- `t.Fatal` vs `t.Error` confusion (should pick deliberately)
- Table-driven tests with hundreds of cases and no subtest naming (hard to debug)
- `go test ./...` excluded from CI (rarer but happens)
- Race detection (`-race`) not enabled in CI

## Ruby

**Test file conventions:**
- `*_spec.rb` (RSpec)
- `*_test.rb` (Minitest)
- `spec/` or `test/` directories

**Frameworks:**
- **RSpec** — dominant in app code. `.rspec`, `spec/spec_helper.rb`, `spec/rails_helper.rb`
- **Minitest** — Rails default for new apps, growing again. `test/test_helper.rb`
- **Cucumber** — BDD, used in some shops

**Coverage:**
- SimpleCov: `coverage/`, `.simplecov`

**Smells specific to Ruby:**
- `let!` blocks creating data that no test uses (slow setup)
- `before(:all)` shared state (test pollution)
- VCR cassettes that are stale or untracked
- Stubbing `Time.now` everywhere (use `Timecop` or `ActiveSupport::Testing::TimeHelpers`)

## Java / Kotlin

**Test file conventions:**
- `src/test/java/**/*Test.java`
- `src/test/kotlin/**/*Test.kt`
- Build tool decides: Maven, Gradle

**Frameworks:**
- **JUnit 5** (Jupiter) — current standard. `@Test`, `@ParameterizedTest`
- **JUnit 4** — still common in legacy codebases
- **TestNG** — alternative, less common now
- **Spock** (Groovy/Kotlin) — BDD style
- **Mockito** — mocking, ubiquitous
- **AssertJ / Hamcrest / Truth** — assertion libraries

**Coverage:**
- JaCoCo: `target/site/jacoco/`, `build/reports/jacoco/`
- Cobertura (older)

**Smells specific to Java:**
- `@Disabled` / `@Ignore` accumulating
- `@SuppressWarnings("unchecked")` in tests (often hiding broken type assumptions)
- Spring tests with `@SpringBootTest` everywhere (slow, indicates lack of unit testability)
- Heavy mocking with PowerMock (sign of untestable production code)

## Rust

**Test file conventions:**
- `#[test]` functions inline in source files
- `tests/` directory at crate root for integration tests

**Frameworks:**
- Built-in test harness, `cargo test`
- **`proptest`**, **`quickcheck`** for property tests
- **`mockall`**, **`mockito`** for mocks

**Coverage:**
- `cargo-tarpaulin`, `cargo-llvm-cov`

**Smells specific to Rust:**
- `#[ignore]` accumulating
- Tests that only use `unwrap()` and don't check error variants
- Integration tests that don't actually integrate (only use public API of one module)

## C# / .NET

**Test file conventions:**
- `*Tests.cs`, `*.Tests.csproj`
- `tests/` or `test/` directory

**Frameworks:**
- **xUnit** — most common in modern .NET
- **NUnit** — also common
- **MSTest** — Microsoft's, less popular
- **Moq**, **NSubstitute** for mocking

**Coverage:**
- Coverlet, dotCover, Visual Studio Code Coverage

**Smells specific to .NET:**
- `[Fact]` without `[Theory]` for parameterized tests
- Tests that call `.Result` or `.Wait()` on async (deadlock risk)
- Heavy reliance on `Moq.It.IsAny<>` (assertion-free mocking)

## Shell scripts

**Test file conventions:**
- Rare. Look for `tests/`, `test/`, `*.bats`, `*_test.sh`

**Frameworks:**
- **Bats** — Bash Automated Testing System
- **shUnit2** — older, still used

**Smells:**
- Untested shell scripts that do destructive things (rm, find -delete) → flag even if not testable, recommend extracting logic to a testable language

## SQL / Stored procedures

**Test conventions:** Often untested. If a project has significant SQL logic (stored procs, complex views), flag the absence of tests as a finding regardless of language.

**Frameworks:**
- **pgTAP** for PostgreSQL
- **tSQLt** for SQL Server
- **utPLSQL** for Oracle

## Infrastructure as code

**Terraform:** Look for `*_test.go` (Terratest), `*.tftest.hcl` (built-in test framework, recent), Kitchen-Terraform.

**Ansible:** Molecule for role testing.

**Kubernetes manifests:** Conftest, kubeval, kube-score for static checks.

**Smell:** IaC with no validation pipeline beyond `terraform plan` is normal but worth flagging if the infrastructure is critical.
