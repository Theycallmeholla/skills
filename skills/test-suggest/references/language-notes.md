# Language and Framework Notes

Per-language idioms for designing test suggestions that match what a writer would actually produce.

## JavaScript / TypeScript

### Frameworks

**Jest:**
- Test names: `describe('module', () => { it('does X', () => { ... }) })` or `test('does X', () => {})`
- Assertions: `expect(actual).toBe(expected)`, `.toEqual`, `.toMatchObject`, `.toThrow`, `.rejects.toThrow`
- Mocks: `jest.mock('./path')`, `jest.fn()`, `jest.spyOn`
- Setup: `beforeEach`, `beforeAll`, `afterEach`, `afterAll`

**Vitest:**
- Same shape as Jest, but `vi.mock`, `vi.fn`, `vi.spyOn`
- Imports: `import { describe, it, expect, vi } from 'vitest'`

**node:test (built-in):**
- `import { describe, it, before, beforeEach } from 'node:test'`
- Assertions from `node:assert/strict`: `assert.strictEqual`, `assert.deepStrictEqual`, `assert.throws`, `assert.rejects`
- No built-in mock/spy library; common to use manual stubs or `mock` from `node:test` (Node 20+)
- Tests usually compiled from TS via `tsc -p tests/tsconfig.json` then run as `node --test`

**Playwright (E2E):**
- `import { test, expect } from '@playwright/test'`
- Assertions: `await expect(page.getByRole('button')).toBeVisible()`
- Setup: `test.beforeAll`, `test.beforeEach`, fixtures via `test.extend`

### TypeScript-specific

- Don't suggest cases that just check return types — TS already does that
- DO suggest cases for runtime validation that TS can't catch (e.g., Zod schemas rejecting bad shapes at runtime)
- DO suggest cases for `as` casts and `any` boundaries — those are where TS's protection ends

### React-specific

- Component tests: prefer `@testing-library/react`. Test from the user's perspective (what's visible, clickable) not the implementation
- Don't suggest tests for "renders without crashing" — useless
- DO suggest tests for: form validation, conditional rendering based on props/state, accessibility (label associations), event handler behavior
- Avoid snapshot tests unless there's a review process; otherwise they become rubber-stamps

### Common JS/TS patterns to test

- Async/promise rejection paths (often forgotten — `await expect(fn()).rejects.toThrow(SpecificError)`)
- Optional chaining edge cases (`obj?.prop?.method?.()` returning undefined when chain breaks)
- Array methods on edge cases (`.reduce` on empty array, `.find` returning undefined)
- Date math (timezone-dependent, often broken)
- JSON parse/stringify roundtrips for non-trivial shapes (Date objects, undefined fields, etc.)

## Python

### Frameworks

**Pytest (most common):**
- Test names: `def test_does_x():`
- Assertions: plain `assert x == y` (Pytest rewrites for readable failure output)
- Fixtures: `@pytest.fixture` decorator, then function arg
- Parameterize: `@pytest.mark.parametrize('input,expected', [...])`
- Mocks: `unittest.mock.patch` / `monkeypatch` fixture
- Imports: `import pytest`

**unittest (stdlib):**
- `class TestFoo(unittest.TestCase): def test_x(self): ...`
- Assertions: `self.assertEqual`, `self.assertRaises`, `self.assertTrue`
- Setup: `setUp`, `setUpClass`, `tearDown`
- Less ergonomic than pytest but still common in older codebases

### Python-specific patterns

- Generator/iterator behavior: `next(gen)` exhausting, `StopIteration`, `yield` in finally
- Exception chaining: `raise X from Y` — test that the cause is preserved
- Context manager protocol: `__enter__` / `__exit__` ordering, exception suppression
- Async: `pytest-asyncio` for `async def test_`, `await` in test body
- Type hints don't catch runtime — DO suggest tests for `isinstance` boundaries

### Common Python smells in suggested tests

- Don't suggest `assert True` placeholders — use `pytest.skip("not implemented")` if needed
- Don't suggest tests that depend on dict ordering (use sets for unordered comparison)
- Floating-point comparisons: use `pytest.approx`, not `==`

## PHP

### Frameworks

**PHPUnit:**
- Test names: `public function testDoesX(): void`
- Assertions: `$this->assertEquals`, `$this->assertSame`, `$this->expectException`
- Setup: `setUp(): void`
- Mocks: `$this->createMock(SomeClass::class)`
- Annotations: `@dataProvider`, `@depends` (legacy), `#[DataProvider]` (PHP 8 attributes)

**Pest:**
- Test names: `test('does X', function () { ... })` or `it('does X', function () { ... })`
- Assertions: `expect($x)->toBe($y)`, `->toEqual`, `->toThrow`
- Built on PHPUnit, share infrastructure

### Laravel-specific

- Use `RefreshDatabase` trait for tests that touch DB
- HTTP tests: `$response = $this->postJson('/api/x', [...])` then `$response->assertStatus(201)`
- Mock service container bindings, not direct instantiation
- Eloquent factories: `User::factory()->create([...])`

### WordPress-specific

- Use WP_UnitTestCase as base
- Reset state between tests via `setUp` (often just `parent::setUp()`)
- Custom plugins often have zero tests — finding *anything* worth testing is the suggestion

## Go

### Conventions

- Test files: `xyz_test.go` alongside `xyz.go`, same package or `xyz_test` package
- Test names: `func TestXyz(t *testing.T)`, sub-tests via `t.Run("case", func(t *testing.T) {...})`
- Assertions: built-in `t.Errorf`, `t.Fatalf`, or `testify/assert`/`testify/require`
- Table-driven tests are idiomatic — suggest them with named cases:
  ```go
  cases := []struct{ name string; input X; want Y }{ ... }
  for _, c := range cases {
    t.Run(c.name, func(t *testing.T) { ... })
  }
  ```

### Go-specific patterns to test

- Error wrapping: `errors.Is(err, target)`, `errors.As(err, &target)` — test that wrapping preserves the chain
- Goroutine leaks: tests that spawn goroutines should verify they exit (`runtime.NumGoroutine` before/after, or use `goleak`)
- Context cancellation: `ctx, cancel := context.WithCancel(...)` — test that work stops when cancelled
- Race conditions: suggest tests run with `-race` flag if there's any concurrency
- Interface implementation tests: `var _ Iface = (*Impl)(nil)` is a compile-time check, not a runtime test

### Avoid in Go suggestions

- Don't suggest mocking interfaces unless the interface has multiple implementations in production
- Don't suggest tests for getters/setters on structs

## Ruby

### Frameworks

**RSpec:**
- Test names: `describe SomeClass do; it 'does X' do; ... end; end`
- Matchers: `expect(actual).to eq(expected)`, `.to raise_error`, `.to change`
- Setup: `before(:each)`, `let(:x) { ... }`, `let!` (eager evaluation)
- Mocks: `allow(obj).to receive(:method).and_return(...)`, `expect(obj).to have_received(:method)`

**Minitest:**
- `class FooTest < Minitest::Test; def test_does_x; assert_equal expected, actual; end; end`
- Or spec-style: `describe 'Foo' do; it 'does x' do; ... end; end`

### Rails-specific

- Use `ActiveRecord::Base.transaction` rollback in tests (`use_transactional_fixtures`)
- HTTP tests via `ActionDispatch::IntegrationTest` or RSpec `request` specs
- Suggest factory patterns (FactoryBot) over fixtures for new test code
- VCR cassettes for HTTP — suggest re-recording with `:new_episodes` if stale

### Ruby-specific patterns

- Method missing / `respond_to?` boundaries
- Module mixin behavior (test classes that include the module)
- Block-based APIs: `expect { ... }.to change(SomeClass, :count).by(1)`

## Java / Kotlin

### Frameworks

**JUnit 5:**
- `@Test public void doesX() { ... }`
- Assertions: `assertEquals(expected, actual)`, `assertThrows`, AssertJ's `assertThat`
- Parameterized: `@ParameterizedTest @ValueSource(strings = {...})`
- Setup: `@BeforeEach`, `@BeforeAll`

**Spring Boot:**
- `@SpringBootTest` for integration, `@WebMvcTest` for controller layer, `@DataJpaTest` for repository layer
- Test slices are *contract*-level tests, not unit tests
- `@MockBean` for replacing beans in the context

### Kotlin-specific

- Coroutine tests: `runTest { ... }` (kotlinx-coroutines-test)
- `expect`/`actual` in multiplatform code

## Rust

### Conventions

- Inline `#[cfg(test)] mod tests { ... }` for unit tests in source files
- `tests/` directory at crate root for integration tests
- `#[test] fn does_x() { ... }`
- Assertions: `assert_eq!`, `assert_ne!`, `assert!`
- `#[should_panic(expected = "...")]` for panic cases

### Rust-specific patterns

- `Result` variants — test both `Ok` and `Err`
- `Option` variants — test `Some` and `None`
- Lifetimes — usually compile-time, don't suggest runtime tests for them
- `unsafe` blocks deserve careful tests — invariants the compiler can't check

## C# / .NET

### Frameworks

**xUnit (most common in modern .NET):**
- `[Fact] public void DoesX() { ... }`
- `[Theory] [InlineData(...)] public void DoesX(int input) { ... }` for parameterized
- Assertions: `Assert.Equal`, `Assert.Throws<T>`

**NUnit:** `[Test]`, `[TestCase]`, similar shape

**Moq for mocks:** `var mock = new Mock<IService>(); mock.Setup(s => s.M(...)).Returns(...)`

### .NET-specific patterns

- Async: `[Fact] public async Task DoesXAsync() { await ... }`
- Don't suggest `.Result` or `.Wait()` in tests (deadlock risk)
- Disposable resources: test that `Dispose()` runs even on exceptions (`using` block)

## Shell / Bash

### Conventions

- **Bats** (Bash Automated Testing System): `@test "does X" { run cmd; [ "$status" -eq 0 ] }`
- **shUnit2**: older, function-based

### Shell-specific patterns

- Exit codes: assert specific codes, not just zero
- stdout vs stderr: capture both separately
- Argument parsing: edge cases with quoting, special characters
- Trap handlers: signals, cleanup on exit
- File globbing: empty match behavior

If shell scripts are doing destructive operations and have no tests, the suggestion is often "extract logic to a testable language" rather than "write Bats tests for shell."

## SQL / Stored procedures

### Frameworks

- pgTAP, tSQLt, utPLSQL

### SQL-specific patterns

- NULL handling — most common bug source
- Constraint behavior under transactions
- Index usage (use EXPLAIN in tests for performance contracts)
- Trigger ordering and cascading effects

For projects that have significant SQL logic, the absence of SQL tests is itself worth flagging — but suggesting them requires knowing the testing framework is set up.

## Cross-language reminders

When suggesting cases, always:

- Use the framework's idiomatic test name pattern (`it('does X')` vs `def test_does_x` vs `func TestDoesX(t *testing.T)`)
- Use the assertion style the repo already uses
- Match the test file location convention the repo already uses
- Don't introduce new dependencies (no "use this fancy library") unless there's no alternative
- If you can't tell what the convention is from the repo, default to the language's most common idiom and flag the assumption
