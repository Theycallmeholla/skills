# Code Audit Report — {PROJECT_NAME}

**Auditor:** {AUDITOR}
**Date:** {DATE}
**Commit / version audited:** {COMMIT}
**Scope:** {SCOPE_DESCRIPTION — paths covered, paths excluded, sampling approach if used}

---

## Executive summary

_Five to eight sentences. Cover: what the project is (stack and purpose), what was reviewed, the top 2–3 issues by impact, and an overall health verdict. The reader should be able to make a triage decision from this section alone._

**Overall health:** {Healthy / Needs attention / Concerning / Critical}

**Top concerns:**

1. {Title of finding #1} — {one-line impact}
2. {Title of finding #2} — {one-line impact}
3. {Title of finding #3} — {one-line impact}

---

## Findings summary

| ID | Severity | Category | Title | Location |
|----|----------|----------|-------|----------|
| F-01 | Critical | Security | _Hardcoded production database credentials in source_ | `config/db.js:14` |
| F-02 | High     | Security | _SQL injection via unparameterized query in admin search_ | `routes/admin.js:88` |
| F-03 | High     | Performance | _N+1 query in order list endpoint_ | `routes/orders.js:41` |
| F-04 | Medium   | Quality  | _12 empty catch blocks silently swallow errors_ | _various_ |
| F-05 | Medium   | Dependencies | _3 dependencies with known high-severity CVEs_ | `package-lock.json` |
| F-06 | Low      | Quality  | _Inconsistent error handling style across modules_ | _codebase-wide_ |
| F-07 | Info     | Architecture | _SQL queries inline in HTTP handlers (no data layer)_ | `routes/*.js` |

_Sort by severity descending. Aim for 5–25 findings on a typical audit; more than that and the report becomes hard to act on — group similar issues._

---

## Severity guide

- **Critical** — Active or imminent harm. Data loss, exposed credentials, exploitable RCE, production outage that the owner doesn't know about. Fix today.
- **High** — Significant risk under realistic conditions. Real bugs likely to fire. Schedule this sprint.
- **Medium** — Will cause incidents or maintenance pain over time. Plan for the quarter.
- **Low** — Quality / smell / future cost. Address in normal course of work.
- **Info** — Observation, not a defect. Context for the rest of the report.

---

## Detailed findings

### F-01 — Hardcoded production database credentials in source

**Severity:** Critical
**Category:** Security
**Location:** `config/db.js:14`

**What it is**
{One paragraph describing the exact issue, including the relevant code excerpt.}

```js
// config/db.js:14
const db = mysql.createConnection({
  host: 'prod-db.example.com',
  user: 'app_user',
  password: 'P@ssw0rd-2023!',  // ← hardcoded
  database: 'app_prod'
});
```

**Why it matters**
{Concrete consequences. For a Critical: what could happen, who could exploit it, what's the blast radius. Avoid hand-waving.}

This credential gives access to the production database. Because the file is committed to the repository, anyone with read access to the repo (current or former employees, anyone on a stolen laptop, anyone who has cloned a fork) has the credential. Git history makes removal incomplete — the value remains accessible via `git log -p`.

**Evidence**

- `config/db.js:14` — credential in current HEAD
- `git log --all -- config/db.js` shows the credential has been present since 2022-03
- No `.gitignore` entry for `config/db.js`

**Recommendation**

1. **Rotate the credential immediately.** Treat this as a leaked-credential incident. Generate a new password, update the production database, deploy the new credential via environment variable / secret manager.
2. **Move credentials out of source.** Read from `process.env.DB_PASSWORD` at startup. Validate presence at boot — fail fast if unset.
3. **Add a pre-commit hook** to prevent recurrence. `gitleaks` or `trufflehog` integrate via [pre-commit](https://pre-commit.com/).
4. **Audit git history** for other credentials. Run a full secret scan against history, not just HEAD.

**Effort to fix:** S (rotate + env var migration in <1 day; history audit a few hours)

---

### F-02 — SQL injection via unparameterized query in admin search

**Severity:** High
**Category:** Security
**Location:** `routes/admin.js:88`

{... follow the same structure for each finding ...}

---

_(Continue for each finding. Keep individual findings focused — a finding is one issue, not a category. If you have 12 instances of the same problem, they're one finding with multiple locations listed in Evidence.)_

---

## What's good

_A list of genuine strengths in the codebase. Five to ten items. Audits that only criticize get tuned out — this section calibrates the negative findings and signals to the reader that you actually read the code._

- {Specific positive observation with location/example}
- {...}

Examples (replace with project specifics):
- Consistent use of parameterized queries throughout the public API surface
- Comprehensive test coverage on payment-related modules (~85% line coverage in `services/billing/`)
- Well-structured domain layer cleanly separated from HTTP transport
- Up-to-date dependencies with active automated update tooling (Dependabot enabled)
- Clear, correct README that gets a developer running locally in under 10 minutes

---

## Coverage & methodology

**What was reviewed**

- {Top-level modules / paths reviewed in detail}
- {Inventory and metrics: `scripts/inventory.sh` output highlights}
- {Tools run: `npm audit`, `pip-audit`, `scripts/scan_secrets.sh`, ...}

**What was sampled**

_If sampling was used:_

- {Strategy: largest 10 files per top-level dir, plus 5 random; plus all auth-related modules}
- {Specifically did NOT review: list paths skipped and why}

**What was NOT reviewed**

- {Anything explicitly out of scope}
- {Tooling not available in the environment}
- {Areas requiring runtime context (e.g., production logs, query plans)}

---

## Recommended next steps

A 30-60-90 day plan ordered by impact. The owner should not have to re-prioritize; that's the auditor's job.

### Within 7 days (Critical + active risk)
1. Rotate any leaked credentials and remove them from source (F-01)
2. Patch the SQL injection in `routes/admin.js` (F-02)

### Within 30 days (High-severity)
1. Upgrade dependencies with known CVEs (F-05)
2. Fix the N+1 in the orders endpoint (F-03)
3. Add CI step to fail builds on new high-severity CVEs

### Within 90 days (Medium and process improvements)
1. Address empty catch blocks (F-04) and standardize error handling (F-06)
2. Introduce a data-access layer to remove inline SQL from handlers (F-07)
3. Add pre-commit secret scanning
4. Establish a quarterly dependency-review cadence

### Continuous (process)
- Treat new findings of equivalent severity to the above with the same urgency in future reviews
- Bring this codebase into a regular review cadence (annual at minimum, semi-annual recommended given the rate of change)

---

## Appendix A — Tool output

_Raw output from automated checks. Trim noise; preserve enough for the owner to verify findings._

### `scripts/inventory.sh`
```
{paste relevant excerpt}
```

### `scripts/scan_secrets.sh`
```
{paste relevant excerpt — scrubbed of actual credential values}
```

### `npm audit` (or equivalent)
```
{paste summary, not the full report}
```

---

## Appendix B — Threat model assumptions

_If applicable, state the threat model used to evaluate severity. Findings can shift in severity depending on this._

Examples:

- **Public-facing web app** — anyone on the internet can reach the public endpoints
- **Authenticated users are mostly trusted** — but assume some are malicious (insider threat is in scope)
- **Admin role is highly trusted** — but admin compromise is the worst-case
- **Out of scope:** physical access to production servers, supply-chain compromise of major upstreams (npm registry, OS packages)

---

_End of report._
