# Dependencies & Supply Chain Checklist

Modern apps are mostly other people's code. Auditing dependencies is auditing the bulk of your attack surface.

## 1. Detect the package manager

A repo can have multiple. Check for the manifest files:

| Ecosystem | Manifest | Lockfile | Audit command |
|---|---|---|---|
| Node.js (npm) | `package.json` | `package-lock.json` | `npm audit --json` |
| Node.js (yarn) | `package.json` | `yarn.lock` | `yarn npm audit --json` (Berry) / `yarn audit --json` (Classic) |
| Node.js (pnpm) | `package.json` | `pnpm-lock.yaml` | `pnpm audit --json` |
| Python (pip) | `requirements*.txt`, `pyproject.toml` | `requirements*.txt` (pinned), `uv.lock`, `poetry.lock` | `pip-audit -r requirements.txt` |
| Python (poetry) | `pyproject.toml` | `poetry.lock` | `poetry export | pip-audit -r /dev/stdin` |
| Ruby | `Gemfile` | `Gemfile.lock` | `bundle audit check --update` |
| Go | `go.mod` | `go.sum` | `govulncheck ./...` |
| Rust | `Cargo.toml` | `Cargo.lock` | `cargo audit` |
| PHP | `composer.json` | `composer.lock` | `composer audit` |
| Java (Maven) | `pom.xml` | (no built-in lock) | `mvn dependency-check:check` (OWASP plugin) |
| Java (Gradle) | `build.gradle` | (no built-in lock) | OWASP dependency-check Gradle plugin |
| .NET | `*.csproj`, `packages.config` | `packages.lock.json` (opt-in) | `dotnet list package --vulnerable` |

`scripts/deps_check.sh` auto-detects and runs the appropriate command. If it doesn't recognize the project, fall back to manual.

## 2. CVE scan

Run the audit. Triage by severity:

- **Critical / High** with a runtime path that reaches user input → top of the report
- **Critical / High** in a build-only or dev-only dependency → still flag, but lower priority
- **Medium / Low** → batch-mention, don't prioritize each individually

For each high-severity finding, verify:
1. Is the affected version actually in the dependency tree? (`npm ls <package>`, `pip show <package>`)
2. Is the vulnerable code path reachable from this app's usage?
3. Is a fix available? (Patched version, replacement package, mitigation)

A CVE that doesn't apply to this app's usage is a low priority. Don't inflate.

## 3. Lockfile hygiene

The lockfile is what actually gets installed. Without it, `latest minor` semantics mean different machines get different code.

Check:
- **Lockfile present and committed?** No lockfile = nondeterministic builds.
- **Manifest and lockfile consistent?** If `package.json` says `^1.0.0` but `package-lock.json` was generated against `^2.0.0`, somebody's running on stale lock. Run a dry install and check.
- **CI installs from lockfile?** `npm ci` (not `npm install`), `yarn install --frozen-lockfile`, `pip install -r requirements.txt` with pinned versions, `bundle install --frozen`, `go mod download`. `npm install` in CI is a finding.
- **Lockfile diff hygiene.** A lockfile with hundreds of unrelated changes in every PR points to a broken setup or to people regenerating it unnecessarily.

## 4. Stale & unmaintained

For each direct dependency, check:

- **Last release date.** A package with last release 3+ years ago is a yellow flag. For security-relevant packages (auth, crypto, parsers), it's red.
- **Last commit date.** Sometimes packages release infrequently but stay maintained — check the repo activity.
- **Major versions behind.** If we're on v2 and current is v6, you're missing 4 years of fixes.
- **Open issue count vs response time.** A repo with 500 open issues and last maintainer response 2 years ago is dead.
- **Number of maintainers.** Single-maintainer packages are bus-factor risks.

Tools:
- `npm outdated` shows current vs wanted vs latest
- `pip list --outdated`
- `bundle outdated`
- `composer outdated`

## 5. Dependency sprawl

Some signals that the dep tree is out of hand:

- **800 dependencies for a simple CRUD app.** Each is a supply-chain risk.
- **Multiple packages doing the same thing.** Three date libraries, two HTTP clients, two test frameworks. Pick one.
- **Tiny utility packages** for things the standard library does (`is-odd`, `left-pad`-class). Each is an attack surface for marginal value.
- **Forked / private packages** without clear ownership inside the org.

Pull `du -sh node_modules` or equivalent — the size alone is informative.

## 6. License compatibility

Often skipped, sometimes critical. For commercial / closed-source projects:

- **AGPL** in the dependency tree of a closed-source product is usually a problem (depending on use)
- **GPL** static linking in commercial products
- **"WTFPL"**, "Beerware", or unlicensed code in commercial products
- **License changes mid-version** (e.g., Elastic, Redis, MongoDB BSL transitions) — version pin may have been on a permissively-licensed version that's no longer available going forward

Tools:
- `license-checker` (Node)
- `pip-licenses` (Python)
- `licensee` (general)

## 7. Typo-squatting & malicious packages

- Recently-added dependencies with very similar names to popular ones — `requst` vs `request`, `lodahs` vs `lodash`. Spot-check the package source.
- Packages added in commits that don't otherwise mention them
- Packages with very few weekly downloads but pulled into critical paths
- Recent supply-chain incidents to be aware of: `event-stream`, `ua-parser-js`, `coa`, `rc`, the various PyPI typo-squat campaigns, `colors.js`/`faker.js` self-sabotage

For each direct dependency in security-critical paths, confirm the publisher and look at the diff vs. the known-good source.

## 8. Transitive dependencies

Most CVEs come through transitive deps. Verify:

- Lockfile records integrity hashes (subresource integrity for packages)
- `npm ls <package>` to find what pulls in a vulnerable transitive
- Override mechanisms used appropriately when direct dep can't be upgraded:
  - `npm overrides` / `pnpm overrides`
  - `yarn resolutions`
  - `pip-tools` constraints
  - Bundler `gem 'foo', '>= 1.2.3'` to pull transitive

## 9. Native / binary dependencies

- Compiled binaries (`*-linux-x64.node`, `*.so`) committed to the repo
- Binaries downloaded from arbitrary URLs in install scripts
- Postinstall scripts (`scripts.postinstall` in package.json) — these run on every `npm install`. Audit them. This is a major supply-chain attack vector.

```bash
grep -rE '"postinstall"|"preinstall"' --include='package.json' .
```

## 10. CI/CD supply chain

Slightly outside dependency-of-package scope but related:

- **GitHub Actions / CI actions pinned by SHA** (not by tag). A tag can be rewritten; a SHA can't.
- **Third-party Docker base images pinned by digest**, not just tag. `node:18` is mutable; `node:18@sha256:...` is not.
- **Secrets exposed to PR builds** from forks — major risk
- **Build artifacts signed** if distributed externally

## 11. SBOM (Software Bill of Materials)

For projects under regulatory or supply-chain compliance pressure (executive order 14028, NTIA guidance):

- Is an SBOM produced as part of the build?
- Is it in a standard format (SPDX, CycloneDX)?
- Is it updated automatically?

Not every project needs this; flag only if the project's domain (gov, healthcare, finance) suggests it's expected.

---

## Quick scan commands

```bash
# Node: full audit + outdated
npm audit --json && npm outdated

# Python: pip-audit (install with pipx if not present)
pip-audit -r requirements.txt --format=json

# Find postinstall scripts (supply-chain risk)
find . -name package.json -not -path '*/node_modules/*' -exec grep -l 'postinstall\|preinstall' {} \;

# Show direct dependency count
jq '.dependencies | length' package.json
jq '.devDependencies | length' package.json

# Is the lockfile in git?
git ls-files | grep -E '(package-lock|yarn|pnpm-lock|poetry|Cargo)\.(json|lock|yaml)'

# Last modified manifest vs lockfile (drift signal)
ls -la package.json package-lock.json 2>/dev/null
```

## Recommended in the report

Most projects benefit from these recommendations even if no specific CVE is found:

1. **Automated dependency updates** (Dependabot, Renovate) configured for security and routine updates
2. **CI dependency audit step** that fails the build on new high-severity CVEs
3. **Lockfile required in CI** (`npm ci`, etc.)
4. **Pinned base images** in Dockerfiles by digest
5. **Dependency review process** for new direct dependencies (code review checks the addition)
