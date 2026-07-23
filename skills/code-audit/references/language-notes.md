# Language-Specific Notes

Patterns and pitfalls that are specific to common languages. When auditing a codebase, load the relevant section based on the inventory.

## JavaScript / TypeScript

### Common security pitfalls
- `eval`, `new Function`, `setTimeout(string)`, `setInterval(string)` — all are eval
- `innerHTML`, `outerHTML`, `document.write` with user input
- React `dangerouslySetInnerHTML`, Vue `v-html`, Angular `bypassSecurityTrust*`
- `window.postMessage` handlers without origin validation
- `JSON.parse` is safe; `JSON.parse` of code-shaped strings is not (but rare)
- `child_process.exec` with user input → command injection. Use `execFile` with arg array.
- `fs.readFile` / `path.join` with user input → path traversal. Validate against canonical path.
- Prototype pollution in `Object.assign` / spread / merge libraries when the source is user-controlled

### Quality / correctness pitfalls
- `==` vs `===` — `==` does coercion (`0 == ''`, `null == undefined`)
- Floating-point arithmetic surprises (`0.1 + 0.2 !== 0.3`)
- `for...in` iterating prototype properties, mostly wrong; use `for...of` or `Object.keys`
- `this` rebinding when methods are passed as callbacks (arrow functions or `.bind` solve it)
- Implicit `undefined` propagation (`obj.x.y` throws when `obj.x` is undefined)
- `Array.sort` with no comparator does string sort (`[10, 2, 1].sort()` → `[1, 10, 2]`)
- `Number.parseInt(s)` without radix (also `parseInt`)
- Mutating function args that are objects or arrays (silent action at a distance)

### Async pitfalls
- Forgotten `await` returns a Promise to a caller expecting a value
- `Promise.all` short-circuits on first rejection — use `Promise.allSettled` if you want all results
- Errors in async functions thrown outside try/catch become unhandled rejections
- `forEach` doesn't await — use `for...of` for sequential async, `Promise.all(map(...))` for parallel
- Top-level `await` only works in modules

### TypeScript specific
- `any` is escape valve; count usages and look at why
- Type assertions (`as`) often hide bugs that real types would catch
- `// @ts-ignore` / `// @ts-expect-error` without comments explaining why
- `strict: false` in tsconfig leaves a lot on the table
- Discriminated union exhaustiveness: missing cases silently passing
- `Object.keys(obj)` typed as `string[]`, not `(keyof typeof obj)[]` — surprising

### Node.js specific
- Synchronous I/O on hot paths: `readFileSync`, `execSync` — block the event loop
- Streams not properly handled: missing `on('error', ...)`, missing backpressure
- Child processes leaked (no exit listener)
- Memory: long-lived caches without eviction
- `process.env` accessed everywhere instead of read once and validated
- `npm install` in CI vs `npm ci`

### React specific
- `useEffect` dependency lint disabled or ignored
- State updates after unmount (modern React warns; older code silently leaks)
- Inline objects/functions as props breaking memoization
- Lists rendered without stable `key`
- Contexts that change often causing all consumers to re-render
- `useState` updater function vs value — race conditions with stale closures

## Python

### Common security pitfalls
- `pickle.loads`, `marshal.loads`, `yaml.load` (without `SafeLoader`) on untrusted data → RCE
- `eval`, `exec` on user input
- `subprocess.run(..., shell=True)` with user input → command injection. Use list args without `shell=True`.
- `os.system` with user input → same
- SQL via string formatting: `cursor.execute(f"SELECT ... {x}")`. Use parameterized queries.
- Django `extra()`, `raw()` with user input
- Flask `render_template_string` with user input → SSTI
- `requests.get(url, verify=False)` disables TLS verification

### Quality / correctness pitfalls
- Mutable default arguments: `def f(x=[])` — the list persists across calls
- Late binding in closures (loop variable captured by reference): `[lambda: i for i in range(3)]` all return 2
- `is` vs `==`: `is` is identity, `==` is equality. `x is None` is correct; `x is 5` is wrong (CPython caches small ints, so it sometimes works).
- Bare `except:` swallows `KeyboardInterrupt` and `SystemExit`. Use `except Exception:`.
- Modifying a list while iterating it
- Generators consumed once (and silently empty thereafter)
- `os.path` vs `pathlib.Path` mixed inconsistently
- Wide imports (`from foo import *`) hiding name origins

### Performance pitfalls
- String concatenation in loops (use `"".join(parts)`)
- `list` accumulation when a generator would do
- Repeated DB queries (Django N+1, fix with `select_related`/`prefetch_related`)
- Loading whole files into memory when streaming would work

### Type / API pitfalls
- Type hints present but not checked in CI (mypy/pyright not run)
- `Any` proliferation
- `Optional[X]` not propagated through call chains, leading to `None` access errors
- Implicit `None` returns from functions that "always return" something

### Django specific
- `DEBUG=True` reachable in production paths
- `ALLOWED_HOSTS` permissive
- CSRF token absence on state-changing endpoints (Django provides it; verify it's not disabled)
- `SECRET_KEY` hardcoded
- `MEDIA_ROOT` served by Django in production (should be by web server / CDN)
- `Http404` carrying message that leaks information

### Flask specific
- `app.run(debug=True)` reachable in production
- No CSRF protection (Flask doesn't include it; verify Flask-WTF or similar)
- `g.user` set by some routes but not others
- Blueprint registration order issues

## PHP

### Common security pitfalls
- `eval`, `assert` (with string arg), `create_function` — all are eval
- `unserialize` on user input → RCE / object injection
- `include` / `require` with user input → LFI / RFI (especially if `allow_url_include` is on)
- `system`, `exec`, `passthru`, `shell_exec`, `popen` with user input → command injection
- SQL via string concatenation; use prepared statements (`PDO`, `mysqli_prepare`)
- Direct echo of `$_GET`/`$_POST` without `htmlspecialchars` → XSS
- `$_REQUEST` (combines GET, POST, COOKIE) — order-dependent surprises
- `move_uploaded_file` to web-accessible directory without restricting type/extension

### Quality / correctness pitfalls
- Loose comparison (`==`) with surprising coercion: `"0" == false`, `"abc" == 0` (in PHP <8)
- `null` propagation: `array_map`, etc. behavior on `null` arguments differs between versions
- Globals usage (`global $foo`) — usually a smell
- `register_globals` (deprecated, but old code may rely)
- Type juggling around equality

### Modern PHP
- Strict types declared? `declare(strict_types=1)` at file top
- Type hints used? Return types?
- Composer autoloader instead of manual requires
- Up-to-date PHP version (8.x); 7.x is end-of-life

### WordPress specific (since you may audit WP-based sites)
- Hardcoded credentials in `wp-config.php` checked into git
- `WP_DEBUG=true` in production
- File permissions (`wp-config.php` shouldn't be world-readable)
- Outdated plugins / themes (the #1 WP security issue)
- `eval` / `base64_decode` blobs in plugins (often malware)
- Direct DB queries instead of `$wpdb->prepare`
- Nonce verification missing on form handlers

## Go

### Common security pitfalls
- `os/exec` with `sh -c` and user input → command injection. Use exec with arg slice.
- SQL via `fmt.Sprintf` — use parameterized queries (`db.Query(query, args...)`)
- `html/template` (safe) vs `text/template` (no escaping) — confirm correct one used for HTML
- `tls.Config{InsecureSkipVerify: true}` — disables TLS verification
- `io/ioutil.ReadAll` on untrusted-size input — DoS risk

### Quality / correctness pitfalls
- Ignored errors: `_, _ = doThing()`. Audit each — sometimes intentional, often not
- Goroutine leaks: started without termination path
- Race conditions: `go run -race` should be in CI
- Mutex held across long operations
- Channel sends/receives that can block indefinitely
- `defer` in loops — defers stack until function return, can leak resources
- Slices: aliasing surprises (`b := a[2:5]` shares underlying array)
- `nil` interface vs `nil` pointer wrapped in interface — different things

### Modules
- `go.sum` committed?
- Replace directives that point to local paths (development leftover)
- Major version pinning (`/v2`)

## Ruby

### Common security pitfalls
- `eval`, `instance_eval`, `class_eval` with user input
- `Kernel.system` with user input
- `Marshal.load` on untrusted data
- `YAML.load` (use `YAML.safe_load`)
- `send` / `public_send` with user-controlled method name → arbitrary method invocation
- ActiveRecord `where` with string + interpolation: `User.where("name = '#{name}'")` — vulnerable. Use placeholders or hash form.
- `Object#tap` / metaprogramming on user input

### Rails specific
- `params.permit` / strong parameters used? Or mass assignment vulnerable?
- `link_to` / `redirect_to` to user-controlled URL → open redirect
- `html_safe` on user input → XSS
- `ActionController::Parameters` permitted properly
- CSRF token check enabled (`protect_from_forgery`)
- Secret key in `secrets.yml` / env var, not in source
- N+1 queries — Bullet gem helps
- Asset pipeline / source maps in production

### Quality
- Monkey-patching of standard library / gems — locate, evaluate
- Method missing / dynamic dispatch making code hard to grep
- Long-lived class variables (`@@foo`) — concurrency hazards in threaded servers

## Java

### Common security pitfalls
- `Runtime.exec` with user input
- `ObjectInputStream.readObject` on untrusted data → RCE
- XML parsers with XXE (`DocumentBuilderFactory.setFeature` for FEATURE_SECURE_PROCESSING)
- SQL via string concatenation; use `PreparedStatement`
- LDAP injection in user-controllable filters
- SSRF via URL / HttpClient with user URLs
- TLS: `HostnameVerifier` that returns true unconditionally; `TrustManager` that trusts everything
- Spring: `@RequestBody` mass assignment if not careful with `@JsonIgnore` / DTOs

### Quality / correctness
- `Optional<T>` returned but caller calls `.get()` without checking — NPE-equivalent
- Equals/hashCode mismatches in domain objects
- `synchronized` on local objects (no-op)
- Mutable singletons accessed across threads
- Logging frameworks: log4j (Log4Shell anyone?) versions
- `instanceof` cascades that should be polymorphism
- Reflection used to bypass access control

### Spring Boot
- Actuator endpoints exposed in production (`/actuator/env`, `/actuator/heapdump` are leaky)
- `@PreAuthorize` / `@Secured` applied where needed
- Default H2 console disabled in production
- DEBUG / TRACE logging in production

## Rust

Rust prevents many classes of bugs but not all. Watch for:

- `unsafe` blocks: count, classify, justify
- `unwrap()` / `expect()` proliferation in library code (panic = crash)
- Send/Sync incorrectly implemented for types
- Integer overflow in release mode (silent wrap)
- `mem::transmute` (almost always wrong)
- `Box::leak` for "lifetime hack"
- Error handling: `Result` returned but caller doesn't check (linter warns; verify it's enabled)
- Cargo features that change behavior in surprising ways
- `tokio::spawn` for tasks that should be `spawn_blocking`

## Shell scripts

The bug-per-line ratio in shell is among the worst. Common findings:

- Unquoted variables (`rm -rf $FOO` when `FOO=""` deletes /)
- Glob expansion in unexpected contexts
- `set -e` not present (errors don't halt the script)
- `set -u` not present (typo'd variable expands to empty)
- `set -o pipefail` not present (failures in pipelines hidden)
- `[ ... ]` with `==` (POSIX is `=`); `[[ ]]` is bash-only
- Word splitting in `for x in $list`
- Using `cd` without checking exit
- Race conditions in temp file handling (`mktemp` not used)

ShellCheck (`shellcheck script.sh`) catches almost all of these. Recommend it.

## SQL

- `SELECT *` in queries that ship over the wire (drift hazard, perf)
- Migrations not in source control
- No transactions around multi-statement updates
- `UPDATE`/`DELETE` without `WHERE` — flag the practice; review individually
- Indexes missing on FK columns
- TEXT/JSON columns growing unboundedly with no archival

## Dockerfile / containers

- Running as root (`USER` not set)
- `apt-get install` without `--no-install-recommends` and without lockfile equivalent
- Latest tags as base images (mutable, breaks reproducibility)
- Secrets in build args or environment (visible in image history)
- Multi-stage build not used → final image bloated with build tools
- `COPY . .` copying `.git`, `.env`, `node_modules`, etc. (use `.dockerignore`)
- `EXPOSE` ports without justification

## Infrastructure-as-code

- Terraform/Pulumi state committed to git (state files contain secrets)
- IAM policies overly permissive (`*` resource, `*` action)
- Public S3 buckets / open security groups
- Hardcoded ARNs / project IDs in cross-environment shared modules
- No `.tfvars` separation between environments

---

## Cross-language quick scans

```bash
# Eval-likes (most languages)
grep -rEn '\beval\s*\(|new Function\s*\(|exec\s*\(' --include='*.{js,ts,py,php,rb}' .

# Disabled TLS
grep -rEn 'verify\s*=\s*False|InsecureSkipVerify|rejectUnauthorized\s*:\s*false|VERIFY_NONE' .

# Hardcoded credentials patterns (broader scan in scripts/scan_secrets.sh)
grep -rEn '(password|passwd|secret|api_key|apikey|token)\s*[:=]\s*["'"'"'][^"'"'"']{6,}["'"'"']' --include='*.{js,ts,py,php,rb,go,yml,yaml,json,env,conf}' .
```
