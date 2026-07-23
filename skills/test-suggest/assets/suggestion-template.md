# Test Suggestions — [Target]

**Target file(s):** `[path/to/source.ts]` ([N] lines, [framework])
**Test framework:** [detected: Jest / Vitest / node:test / Pytest / etc.]
**Test file location:** [where new tests should live in this repo]
**Existing coverage:** [N existing cases, see below / no existing tests]

---

## Already Covered

[Brief list of what existing tests handle, so the user knows you read them.]

- `path/to/existing.test.ts:42` — happy-path login with valid credentials
- `path/to/existing.test.ts:67` — wrong password returns 401

[If no existing tests: "None — this is a clean slate."]

---

## Must-have

The cases that protect against real failure modes. If these aren't written, the next bug here probably ships.

### 1. [behavior statement, e.g., "Returns 404 when NODE_ENV is 'production'"]

- **Type:** [Unit / Contract / Integration / E2E]
- **Test file:** `[path/to/new-or-existing.test.ts]`
- **Setup:** [concrete preconditions — "set process.env.NODE_ENV = 'production'", "stub authService.verify to return null", "seed a user with id=1"]
- **Action:** [what to invoke — "call POST handler with { user: 'x', code: '123' }"]
- **Assert:** [what to check — "response.status === 404 AND response body contains { error: 'not_found' } AND no Set-Cookie header"]
- **Why:** [the failure mode this catches — "this gate is the only thing preventing MFA bypass in prod; if it regresses, MFA is bypassable"]
- **Watch out for:** [optional — tricky bits, e.g., "remember to restore NODE_ENV after the test"]

### 2. [next must-have]

[same fields]

---

## Should-have

Common error paths and the main happy path. Write these soon after the must-haves.

### 3. [behavior statement]

[same fields]

---

## Nice-to-have

Edge cases that would be unusual in practice but increase confidence.

### 4. [behavior statement]

[same fields]

---

## Untestable As-Written

[Only include this section if applicable. See references/untestable-code.md for criteria.]

**`[file]`** — [what makes it hard]
- **Recommended:** [refactor suggestion, briefly]
- **Or:** [alternative test strategy at higher level]

---

## Test File Layout

[If new test files are needed:]

```
tests/
├── existing-test.test.ts  (already exists)
└── new-test.test.ts       ← put cases 1, 2, 3 here

tests/integration/
└── new-integration.test.ts ← put case 4 here
```

---

## Next Step

I can generate the actual test code for any of these. Say:
- "Write case N" — produce code for one case
- "Write all must-haves" — produce code for the must-have group
- "Write all" — produce code for everything

Test code is written as a normal follow-up task that takes this output as its input — say "write case N" or "write all must-haves".
