# Security Checklist

Organized by attack class. For each, the questions to ask, what to grep for, and how to verify.

## 1. Secrets in source

**Why it matters**: A leaked production credential in git history is essentially permanent — even if removed, it's been cloned, forked, scraped. Rotation is the only fix, and that's a real incident.

**What to look for**:
- API keys, tokens, secrets in source files, config files, `.env`-shaped files committed to the repo
- Credentials in URLs (`postgres://user:password@host/db`)
- Private keys (`-----BEGIN ... PRIVATE KEY-----`)
- High-entropy strings in comments or test fixtures
- `.env.example` files with real values instead of placeholders
- Credentials in CI configs or Dockerfiles

**Patterns to grep**:
```
AKIA[0-9A-Z]{16}                    # AWS access key
sk_live_[0-9a-zA-Z]{24,}            # Stripe live key
ghp_[A-Za-z0-9]{36}                 # GitHub personal access token
xox[baprs]-[A-Za-z0-9-]+            # Slack token
-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----
password\s*[:=]\s*["'][^"']+["']
secret\s*[:=]\s*["'][^"']{8,}["']
api[_-]?key\s*[:=]\s*["'][^"']+["']
```

**Verify**: `git log -p --all -S '<the-secret>'` shows when it entered. Even if removed in HEAD, history exposure means rotation is required.

**Recommend**: rotate every leaked credential, add `.env*` to `.gitignore` (verify with `git ls-files | grep -E '\.env'`), introduce a pre-commit secret scanner (gitleaks, trufflehog), document credential rotation procedure.

## 2. Injection: SQL, NoSQL, command, LDAP, XPath

**SQL injection** — the original. Look for string concatenation or interpolation building queries:
```js
// Vulnerable
db.query(`SELECT * FROM users WHERE id = ${req.params.id}`)
db.query("SELECT * FROM users WHERE name = '" + name + "'")

// Safe
db.query('SELECT * FROM users WHERE id = ?', [req.params.id])
db.query('SELECT * FROM users WHERE id = $1', [req.params.id])
```

ORMs are usually safe but have escape hatches: `raw()`, `$queryRaw`, `db.execute()` with strings. Audit every raw-query call.

**Command injection** — anywhere user input reaches a shell:
```js
exec(`convert ${userFile} out.png`)              // Vulnerable
execFile('convert', [userFile, 'out.png'])       // Safer (no shell)
```

```python
os.system(f"ls {user_path}")                     # Vulnerable
subprocess.run(["ls", user_path], shell=False)   # Safe
```

```php
shell_exec("ping " . $_GET['host']);             # Vulnerable
```

**NoSQL injection** — MongoDB queries that accept whole objects from request bodies:
```js
db.users.findOne({ username: req.body.username, password: req.body.password })
// If req.body.password is { $ne: null }, this matches any user
```

Always coerce to string before querying.

**Template injection** — server-side template engines (Jinja, Twig, ERB) rendered with user input:
```python
template = Template("Hello " + user_input)  # Server-side template injection
```

## 3. Cross-site scripting (XSS)

**Stored XSS**: user content rendered as HTML on someone else's session.
**Reflected XSS**: user input echoed back in the response.
**DOM XSS**: client-side JS writing user input into the DOM.

**What to look for**:
- React: `dangerouslySetInnerHTML` with non-sanitized input
- Vue: `v-html` with user content
- Angular: `bypassSecurityTrust*` calls
- Plain JS: `el.innerHTML = userInput`, `document.write(userInput)`
- Templating: unescaped output (`{{{ }}}` in Handlebars, `{!!  !!}` in Blade, `<%- %>` in EJS)
- PHP: `echo $_GET['x']` without `htmlspecialchars`

**Verify**: render a payload like `<img src=x onerror=alert(1)>` mentally — does it reach the DOM unescaped?

**Defense in depth**: Content-Security-Policy header, especially `script-src` excluding `'unsafe-inline'` and `'unsafe-eval'`. Note absence as a finding.

## 4. Authentication

- **Password storage**: must be bcrypt, scrypt, argon2id, or PBKDF2 with appropriate work factor. MD5/SHA1/SHA256 of passwords is a finding. Salts must be per-user random.
- **Session tokens**: must be cryptographically random, sufficient length (≥128 bits), and stored as `HttpOnly; Secure; SameSite=Lax` (or Strict) cookies.
- **JWT pitfalls**: `alg: none` accepted? Algorithm confusion (HS256 vs RS256) by treating public key as secret? Tokens signed with hardcoded weak secrets? Long expiry without revocation mechanism?
- **Login throttling**: any rate limit on login attempts? Lockout after N failures? Otherwise credential stuffing is trivial.
- **MFA**: present for admin accounts at minimum?
- **Password reset**: token expiry (≤1 hour), single-use, sent over email with no other auth — this is a privilege escalation surface. Reset tokens must not be predictable (`uuid v4` ok, `Math.random()` not ok).
- **Account enumeration**: does login differentiate "wrong password" vs "no such user"? That's a finding.
- **OAuth/SSO**: state parameter validated? Redirect URIs whitelisted? PKCE for public clients?

## 5. Authorization

The most common security bug class today. Look for:

- **Missing checks** on endpoints. `GET /api/orders/:id` — does it verify the order belongs to the requester?
- **IDOR** (Insecure Direct Object Reference). Sequential IDs (`/users/123`) make this trivial to test.
- **Mass assignment**. `User.update(req.body)` lets an attacker set `role: 'admin'` if not whitelisted.
- **Role checks on the client only**. If the UI hides the admin button but the API doesn't check, that's a critical finding.
- **Decorators/middleware applied inconsistently**. `@requires_auth` on most endpoints but not all — find the gaps.

For every public endpoint, ask: "What if I'm authenticated as user A and pass user B's resource ID?"

## 6. CSRF (Cross-Site Request Forgery)

- Cookie-based sessions on state-changing endpoints without CSRF tokens or SameSite cookies = vulnerable
- `SameSite=Lax` is sufficient for most cases on modern browsers
- API-only services using `Authorization: Bearer` headers are not CSRF-vulnerable (the header doesn't auto-attach)
- GET requests that mutate state (`/delete?id=1`) are CSRF-vulnerable even with tokens

## 7. SSRF (Server-Side Request Forgery)

Anywhere the server fetches a URL the user controls:
- Webhook URLs
- Image proxies / URL preview unfurlers
- "Import from URL" features
- PDF generators with user-supplied URLs

**Defenses to verify**:
- Reject private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16, ::1, fc00::/7)
- Reject `file://`, `gopher://`, `dict://` schemes
- Resolve DNS once and connect to the resolved IP (DNS rebinding defense)
- Cloud metadata endpoint (`169.254.169.254`) explicitly blocked

## 8. Insecure deserialization

- Python `pickle.loads(user_input)` → RCE
- PHP `unserialize($user_input)` → RCE
- Java `ObjectInputStream` on untrusted data → RCE
- Ruby `Marshal.load(user_input)` → RCE
- YAML loaders that accept tags (`!!python/object`) → RCE

JSON is generally safe (no code execution). Use JSON unless there's a strong reason not to.

## 9. Path traversal

User input building a file path:
```python
open(f"./uploads/{request.GET['file']}")          # ../../etc/passwd
send_file(f"images/{filename}")                    # Same problem
```

Defenses to verify: canonicalize the path (`os.path.realpath`), check it starts with the intended directory after canonicalization. Allowlist filenames where possible.

## 10. File upload

- File type validated by content (magic bytes), not just extension or `Content-Type` header (both forgeable)
- Uploaded files stored outside webroot, or served with `Content-Disposition: attachment` to prevent execution
- For images: check actual image dimensions before processing; ImageMagick/other parsers have a long history of CVEs (ImageTragick)
- Size limits enforced before reading the whole file into memory
- Virus scanning where the threat model warrants it

## 11. Cryptography

- **Hash for passwords ≠ hash for integrity**. SHA256 is fine for the second, terrible for the first.
- **AES-ECB** is a finding; the famous penguin demonstrates why. Use AES-GCM or ChaCha20-Poly1305 (authenticated encryption).
- **Hardcoded IV** with CBC = effectively no encryption.
- **`Math.random()`** for security purposes. Use `crypto.randomBytes` / `secrets.token_bytes` / `os.urandom`.
- **Custom crypto**. Anyone implementing AES from scratch in production code is a finding by definition.
- **TLS verification disabled**. `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true` — search for these explicitly.

## 12. Configuration & headers

For web apps, verify presence (or document absence) of:
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy`
- `X-Frame-Options` or CSP `frame-ancestors`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy`

CORS:
- `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true` — invalid combination, often misimplemented
- Reflecting the request's `Origin` header without validation
- Trusting subdomains too broadly

Cookies:
- `Secure` flag set for cookies on HTTPS sites
- `HttpOnly` for session cookies
- `SameSite` set explicitly

## 13. Logging & monitoring

- **Sensitive data in logs**: passwords, tokens, full credit card numbers, full SSNs, request bodies of auth endpoints. Search `log.*req.body`, `console.log(.*password)`, etc.
- **No security-relevant logging**: failed logins, permission denials, admin actions — these should be logged for incident response.
- **Logs sent to external services** (Sentry, Datadog, LogRocket) might include PII / secrets — verify scrubbing config exists.

## 14. Rate limiting & DoS

- Public endpoints should have rate limits (especially auth endpoints).
- Endpoints that trigger expensive work (PDF generation, image processing, external API calls) need extra protection.
- Recursive / pathological inputs (regex with catastrophic backtracking, deeply nested JSON, zip bombs).
- Pagination defaults: an endpoint with no `limit` parameter that returns "all rows" is a DoS waiting to happen.

## 15. Third-party integrations

- Webhook signature verification — if the service sends signed webhooks (Stripe, GitHub, etc.), is the signature verified before processing? Constant-time comparison?
- Third-party redirects — open redirect surface (`/login?redirect=` accepting full URLs).
- Dependency on external services without circuit breakers or timeouts (cascading failures).

---

## Quick reference: commands to run

```bash
# Secret scan (also see scripts/scan_secrets.sh)
git log -p --all | grep -E 'AKIA|password|secret|api[_-]?key' | head

# Find raw query patterns
grep -rEn 'query\s*\(\s*[`"][^`"]*\$\{|query\s*\(\s*"[^"]*"\s*\+' --include='*.{js,ts,py,php,rb}' .

# innerHTML / dangerouslySetInnerHTML
grep -rEn 'dangerouslySetInnerHTML|innerHTML\s*=' --include='*.{js,jsx,ts,tsx,html,vue}' .

# Disabled TLS verification
grep -rEn 'verify\s*=\s*False|rejectUnauthorized\s*:\s*false|InsecureSkipVerify' .

# eval and friends
grep -rEn '\beval\s*\(|new Function\s*\(|setTimeout\s*\(\s*["`]' --include='*.{js,ts,py,php,rb}' .

# Weak hashing of passwords
grep -rEn 'md5|sha1' --include='*.{js,ts,py,php,rb,go}' . | grep -i pass
```

## What NOT to flag

To stay credible, avoid:
- Test fixture credentials clearly marked as test (`test_password`, `dummy-token-for-tests`).
- `eval` in build tooling or REPL utilities (not in request paths).
- Disabled TLS verification in scripts that explicitly target localhost dev environments — note it, don't escalate.
- Theoretical issues with no realistic exploit path. "If an attacker compromised the build server, they could..." is not a finding; it's the threat model.
