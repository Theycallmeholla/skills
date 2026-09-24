#!/usr/bin/env python3
"""Deterministic first-pass probe for Open SaysAI audits.

Checks one page, robots.txt, common/declared sitemaps, and per-agent HTTP access.
Robots matching implements the core Google/RFC-style behavior needed for audits:
most-specific user-agent group, longest matching Allow/Disallow rule, `*` wildcard,
`$` end anchor, and Allow winning equal-specificity ties.

This is evidence gathering, not a search-index checker, full browser, or WAF bypass.
"""

from __future__ import annotations

import argparse
import codecs
import json
import re
import sys
from html.parser import HTMLParser
from urllib import error, parse, request
from xml.etree import ElementTree as ET

MAX_BODY_BYTES = 2_000_000

AGENTS = {
    "Googlebot": {
        "purpose": "search",
        "ua": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    },
    "Bingbot": {
        "purpose": "search",
        "ua": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    },
    "OAI-SearchBot": {
        "purpose": "search/retrieval",
        "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot",
    },
    "ChatGPT-User": {
        "purpose": "user fetch",
        "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
    },
    "GPTBot": {
        "purpose": "training",
        "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.4; +https://openai.com/gptbot",
    },
    "Claude-SearchBot": {
        "purpose": "search/retrieval",
        "ua": "Claude-SearchBot",
    },
    "Claude-User": {
        "purpose": "user fetch",
        "ua": "Claude-User",
    },
    "ClaudeBot": {
        "purpose": "training",
        "ua": "ClaudeBot",
    },
    "PerplexityBot": {
        "purpose": "search/retrieval",
        "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
    },
    "Perplexity-User": {
        "purpose": "user fetch",
        "ua": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)",
    },
}

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta = []
        self.links = []
        self.headings = []
        self._heading_tag = None
        self._heading_parts = []
        self.jsonld_count = 0
        self._in_jsonld = False
        self._visible_parts = []
        self._ignore_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_d = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        if tag in {"script", "style", "noscript"}:
            self._ignore_depth += 1
        if tag == "script" and attrs_d.get("type", "").lower() == "application/ld+json":
            self.jsonld_count += 1
            self._in_jsonld = True
        if tag == "meta":
            self.meta.append(attrs_d)
        if tag == "link":
            self.links.append(attrs_d)
        if re.fullmatch(r"h[1-6]", tag):
            self._heading_tag = tag
            self._heading_parts = []

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag in {"script", "style", "noscript"} and self._ignore_depth:
            self._ignore_depth -= 1
        if tag == "script":
            self._in_jsonld = False
        if self._heading_tag == tag:
            text = normalize_ws(" ".join(self._heading_parts))
            if text:
                self.headings.append({"tag": tag, "text": text})
            self._heading_tag = None
            self._heading_parts = []

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._heading_tag:
            self._heading_parts.append(data)
        if not self._ignore_depth and not self._in_jsonld:
            text = normalize_ws(data)
            if text:
                self._visible_parts.append(text)

    @property
    def visible_text(self):
        return " ".join(self._visible_parts)


def normalize_ws(value: str) -> str:
    return " ".join(value.split())


def safe_decode(body: bytes, charset: str | None) -> tuple[str, str]:
    candidates = [charset, "utf-8", "windows-1252"]
    tried = set()
    for enc in candidates:
        if not enc or enc.lower() in tried:
            continue
        tried.add(enc.lower())
        try:
            codecs.lookup(enc)
            return body.decode(enc), enc
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", errors="replace"), "utf-8-replace"


def selected_headers(headers: dict[str, str]) -> dict[str, str]:
    wanted = {
        "content-type",
        "content-encoding",
        "server",
        "x-robots-tag",
        "location",
        "retry-after",
        "cf-ray",
        "cf-mitigated",
        "cf-cache-status",
        "x-sucuri-id",
        "x-sucuri-block",
    }
    return {k: v for k, v in headers.items() if k.lower() in wanted}


def fetch(url: str, timeout: int, user_agent: str = BROWSER_UA) -> dict:
    req = request.Request(url, headers={"User-Agent": user_agent, "Accept": "text/html,application/xml,text/xml,*/*;q=0.8"})
    try:
        resp = request.urlopen(req, timeout=timeout)
        try:
            body = resp.read(MAX_BODY_BYTES)
            headers = dict(resp.headers.items())
            charset = resp.headers.get_content_charset()
            text, used_charset = safe_decode(body, charset)
            return {
                "url": resp.geturl(),
                "status": resp.status,
                "headers": headers,
                "text": text,
                "charset": used_charset,
            }
        finally:
            resp.close()
    except error.HTTPError as exc:
        body = exc.read(MAX_BODY_BYTES)
        headers = dict(exc.headers.items()) if exc.headers else {}
        charset = exc.headers.get_content_charset() if exc.headers else None
        text, used_charset = safe_decode(body, charset)
        return {
            "url": exc.geturl() or url,
            "status": exc.code,
            "headers": headers,
            "text": text,
            "charset": used_charset,
            "http_error": str(exc),
        }
    except Exception as exc:
        return {"url": url, "error": f"{type(exc).__name__}: {exc}"}


def meta_content(meta, *, name=None, prop=None):
    out = []
    for m in meta:
        if name and m.get("name", "").lower() == name.lower():
            out.append(m.get("content", ""))
        if prop and m.get("property", "").lower() == prop.lower():
            out.append(m.get("content", ""))
    return out


def parse_robots(robots_text: str) -> dict:
    """Parse user-agent groups and Allow/Disallow rules without robotparser shortcuts."""
    groups = []
    sitemaps = []
    agents: list[str] = []
    rules: list[dict] = []
    have_rules = False

    def flush():
        nonlocal agents, rules, have_rules
        if agents:
            groups.append({"agents": agents, "rules": rules})
        agents = []
        rules = []
        have_rules = False

    for raw in robots_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        field, value = line.split(":", 1)
        field = field.strip().lower()
        value = value.strip()

        if field == "sitemap":
            if value:
                sitemaps.append(value)
            continue

        if field == "user-agent":
            if have_rules:
                flush()
            if value:
                agents.append(value.lower())
            continue

        if field in {"allow", "disallow"} and agents:
            have_rules = True
            # Empty Disallow means no restriction; empty Allow has no useful match.
            if value:
                rules.append({"directive": field, "pattern": value})

    flush()
    return {"groups": groups, "sitemaps": list(dict.fromkeys(sitemaps))}


def user_agent_specificity(group: dict, user_agent: str) -> int | None:
    ua = user_agent.lower()
    best = None
    for token in group["agents"]:
        if token == "*":
            score = 0
        elif token in ua:
            score = len(token)
        else:
            continue
        if best is None or score > best:
            best = score
    return best


def compile_robot_pattern(pattern: str) -> re.Pattern:
    end_anchor = pattern.endswith("$")
    core = pattern[:-1] if end_anchor else pattern
    regex = "".join(".*" if ch == "*" else re.escape(ch) for ch in core)
    return re.compile("^" + regex + ("$" if end_anchor else ""))


def rule_specificity(pattern: str) -> int:
    # Google describes specificity by the length of the matching rule path.
    return len(pattern.replace("*", "").rstrip("$"))


def robots_decision(parsed_robots: dict, user_agent: str, url: str) -> dict:
    candidates = []
    for group in parsed_robots["groups"]:
        spec = user_agent_specificity(group, user_agent)
        if spec is not None:
            candidates.append((spec, group))

    if not candidates:
        return {"allowed": True, "reason": "no matching user-agent group", "matched_rule": None}

    max_agent_spec = max(spec for spec, _ in candidates)
    chosen = [g for spec, g in candidates if spec == max_agent_spec]

    parts = parse.urlsplit(url)
    target = parts.path or "/"
    if parts.query:
        target += "?" + parts.query

    matches = []
    for group in chosen:
        for rule in group["rules"]:
            if compile_robot_pattern(rule["pattern"]).search(target):
                matches.append({
                    **rule,
                    "specificity": rule_specificity(rule["pattern"]),
                })

    if not matches:
        return {"allowed": True, "reason": "no matching rule", "matched_rule": None}

    longest = max(r["specificity"] for r in matches)
    tied = [r for r in matches if r["specificity"] == longest]
    # Allow wins an equal-length conflict.
    winner = next((r for r in tied if r["directive"] == "allow"), tied[0])
    allowed = winner["directive"] == "allow"
    return {
        "allowed": allowed,
        "reason": f"longest matching {winner['directive']} rule",
        "matched_rule": winner,
        "target": target,
        "user_agent_group_specificity": max_agent_spec,
    }


def classify_access(fetch_result: dict) -> dict:
    if "error" in fetch_result:
        return {"state": "unknown", "reason": fetch_result["error"]}
    status = fetch_result.get("status")
    text = fetch_result.get("text", "").lower()
    headers = fetch_result.get("headers", {})
    # cf-mitigated is only sent when Cloudflare actually served a challenge.
    if any(k.lower() == "cf-mitigated" for k in headers):
        return {"state": "blocked_or_challenged", "reason": "cf-mitigated header present"}
    # Body markers only count on non-success responses. Normal pages often embed
    # reCAPTCHA or contain phrases like "just a moment", which caused false positives.
    challenge_markers = [
        "cf-chl-",
        "challenge-platform",
        "just a moment",
        "attention required",
        "cloudflare ray id",
        "captcha",
        "verify you are human",
    ]
    if status in {403, 429, 503} and any(marker in text for marker in challenge_markers):
        return {"state": "blocked_or_challenged", "reason": f"HTTP {status} with challenge/WAF markers"}
    if status in {401, 403, 407, 429}:
        return {"state": "blocked_or_limited", "reason": f"HTTP {status}"}
    if status is not None and 200 <= status < 400:
        return {"state": "reachable", "reason": f"HTTP {status}"}
    if status is not None:
        return {"state": "error_response", "reason": f"HTTP {status}"}
    return {"state": "unknown", "reason": "no status"}


SPOOFED_UA_CAVEAT = (
    "Blocked for this crawler's user-agent string while the generic browser request was reachable. "
    "This probe does not come from the crawler's verified IP ranges, so the block may be fake-bot "
    "protection that still admits the real crawler. Confirm with server/CDN logs or the platform's "
    "webmaster tools before treating it as a blocker."
)


def parse_sitemap_xml(text: str) -> dict:
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"xml_valid": False, "error": str(exc)}

    def local(tag: str) -> str:
        return tag.rsplit("}", 1)[-1].lower()

    root_name = local(root.tag)
    locs = []
    lastmods = 0
    for elem in root.iter():
        name = local(elem.tag)
        if name == "loc" and elem.text:
            locs.append(elem.text.strip())
        elif name == "lastmod" and elem.text and elem.text.strip():
            lastmods += 1

    if root_name == "sitemapindex":
        kind = "sitemap_index"
        child_count = len([c for c in list(root) if local(c.tag) == "sitemap"])
        return {
            "xml_valid": True,
            "kind": kind,
            "child_sitemap_count": child_count,
            "lastmod_count": lastmods,
            "sample_locations": locs[:20],
        }
    if root_name == "urlset":
        url_count = len([c for c in list(root) if local(c.tag) == "url"])
        return {
            "xml_valid": True,
            "kind": "urlset",
            "url_count": url_count,
            "lastmod_count": lastmods,
            "sample_locations": locs[:20],
        }
    return {
        "xml_valid": True,
        "kind": root_name or "unknown",
        "lastmod_count": lastmods,
        "sample_locations": locs[:20],
    }


def custom_agents(values: list[str] | None) -> dict:
    out = {}
    for raw in values or []:
        if "=" in raw:
            name, ua = raw.split("=", 1)
            name, ua = name.strip(), ua.strip()
        else:
            name = ua = raw.strip()
        if name and ua:
            out[name] = {"purpose": "custom", "ua": ua}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe a page for AI/search crawl and retrieval signals")
    ap.add_argument("url", help="Page URL or domain")
    ap.add_argument("--timeout", type=int, default=12)
    ap.add_argument(
        "--agent",
        action="append",
        dest="agents",
        help="Additional agent as TOKEN or NAME=full-user-agent; repeatable",
    )
    ap.add_argument("--skip-agent-fetch", action="store_true", help="Skip per-agent HTTP/WAF requests")
    ap.add_argument("--max-sitemaps", type=int, default=5, help="Maximum sitemap URLs to fetch")
    args = ap.parse_args()

    url = args.url
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url

    parsed = parse.urlsplit(url)
    robots_url = parse.urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))

    result = {
        "requested_url": url,
        "page": {},
        "agent_access": {},
        "robots": {"url": robots_url},
        "sitemaps": [],
        "notes": [
            "This probe does not prove search-engine index status or citation eligibility.",
            "Per-agent fetches can reveal user-agent-based blocking, but they do not verify crawler IP ranges and cannot bypass a WAF/CAPTCHA.",
            "Robots decisions are computed from observed robots.txt using longest-rule matching with * and $ support; platform-specific exceptions still require current primary documentation.",
        ],
    }

    page = fetch(url, args.timeout)
    if "error" not in page:
        parser = PageParser()
        parser.feed(page.get("text", ""))
        canonical = [
            l.get("href", "")
            for l in parser.links
            if "canonical" in l.get("rel", "").lower().split()
        ]
        robots_meta = meta_content(parser.meta, name="robots")
        description = meta_content(parser.meta, name="description")
        words = re.findall(r"\b[\w'-]+\b", parser.visible_text)
        result["page"] = {
            "final_url": page["url"],
            "status": page["status"],
            "title": normalize_ws(parser.title),
            "meta_description": description[:3],
            "meta_robots": robots_meta,
            "x_robots_tag": next((v for k, v in page["headers"].items() if k.lower() == "x-robots-tag"), None),
            "canonical": canonical[:5],
            "jsonld_blocks": parser.jsonld_count,
            "headings": parser.headings[:50],
            "visible_word_count_estimate": len(words),
            "content_type": next((v for k, v in page["headers"].items() if k.lower() == "content-type"), None),
            "decoded_charset": page.get("charset"),
            "selected_headers": selected_headers(page["headers"]),
        }
    else:
        result["page"] = {"error": page["error"]}

    agents = dict(AGENTS)
    agents.update(custom_agents(args.agents))

    baseline = classify_access(page)
    result["baseline_access"] = {"user_agent": BROWSER_UA, **baseline}

    if not args.skip_agent_fetch:
        for name, info in agents.items():
            probe = fetch(url, args.timeout, info["ua"])
            entry = {
                "purpose": info["purpose"],
                "user_agent": info["ua"],
                **classify_access(probe),
            }
            if "error" in probe:
                entry["error"] = probe["error"]
            else:
                entry.update({
                    "status": probe.get("status"),
                    "final_url": probe.get("url"),
                    "headers": selected_headers(probe.get("headers", {})),
                })
            if baseline["state"] == "reachable" and entry["state"] in {"blocked_or_challenged", "blocked_or_limited"}:
                entry["spoofed_ua_caveat"] = SPOOFED_UA_CAVEAT
            result["agent_access"][name] = entry

    rob = fetch(robots_url, args.timeout)
    robots_parsed = None
    if "error" in rob:
        result["robots"].update({"error": rob["error"]})
    else:
        result["robots"].update({
            "status": rob.get("status"),
            "headers": selected_headers(rob.get("headers", {})),
            "body_preview": rob.get("text", "")[:12000],
        })
        if rob.get("status") == 200:
            robots_parsed = parse_robots(rob.get("text", ""))
            result["robots"]["sitemaps"] = robots_parsed["sitemaps"]
            test_url = result.get("page", {}).get("final_url") or url
            result["robots"]["can_fetch"] = {
                name: robots_decision(robots_parsed, info["ua"], test_url)
                for name, info in agents.items()
            }
        elif rob.get("status") == 404:
            result["robots"]["note"] = "robots.txt returned 404; no robots rules were observed."
        else:
            result["robots"]["note"] = "robots.txt did not return 200; crawler handling of this response can vary by platform and failure duration."

    sitemap_urls = []
    if robots_parsed:
        sitemap_urls.extend(robots_parsed["sitemaps"])
    origin = parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
    sitemap_urls.extend([origin + "/sitemap.xml", origin + "/sitemap_index.xml"])
    sitemap_urls = list(dict.fromkeys(sitemap_urls))[: max(0, args.max_sitemaps)]

    for sitemap_url in sitemap_urls:
        sm = fetch(sitemap_url, args.timeout)
        entry = {"url": sitemap_url}
        if "error" in sm:
            entry["error"] = sm["error"]
        else:
            entry.update({
                "status": sm.get("status"),
                "final_url": sm.get("url"),
                "headers": selected_headers(sm.get("headers", {})),
            })
            if sm.get("status") == 200:
                entry.update(parse_sitemap_xml(sm.get("text", "")))
        result["sitemaps"].append(entry)

    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
