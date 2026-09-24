# AI Visibility Packet

Emit this portable JSON object for every full or platform audit so other website/SEO/content agents can consume the result without reparsing prose.

Use `null` for unknown scalar values and `[]` for no observed items. Never convert an unverified state into `false`.

```json
{
  "ai_visibility_packet": {
    "schema_version": "1.0",
    "generated_at": "ISO-8601",
    "target": {
      "domain": "example.com",
      "audited_urls": [],
      "scope": ["chatgpt", "claude", "google_ai", "copilot", "perplexity"]
    },
    "executive_finding": "",
    "platforms": [
      {
        "product": "ChatGPT",
        "retrieval_source": "",
        "search_crawler": "",
        "user_fetcher": "",
        "training_crawler": "",
        "robots_result": "accessible|blocked|partial|unknown",
        "http_result": "reachable|blocked_or_limited|blocked_or_challenged|error_response|unknown",
        "status_code": null,
        "index_or_citation_state": "verified|not_verified|unknown",
        "official_source": "",
        "verified_date": "YYYY-MM-DD",
        "notes": []
      }
    ],
    "technical": {
      "robots_url": "",
      "robots_status": null,
      "sitemaps": [],
      "meta_robots": [],
      "x_robots_tag": null,
      "canonical": [],
      "waf_or_challenge_evidence": [],
      "rendering_issues": [],
      "indexability_issues": []
    },
    "retrieval": {
      "strong_source_pages": [],
      "weak_source_pages": [],
      "passage_issues": [],
      "information_gain_assets": [],
      "entity_gaps": [],
      "freshness_gaps": []
    },
    "findings": [
      {
        "id": "F-001",
        "priority": "P0|P1|P2|Experimental",
        "category": "access|indexability|retrieval|authority|content|freshness|measurement|agent_usability",
        "title": "",
        "evidence": [],
        "consequence": "",
        "fix": "",
        "affected_urls": [],
        "affected_platforms": []
      }
    ],
    "opportunities": [
      {
        "title": "",
        "type": "original_data|tool|definition|comparison|documentation|benchmark|edge_case|other",
        "why_citable": "",
        "source_advantage": "",
        "suggested_asset": ""
      }
    ],
    "prompt_tests": {
      "executed": false,
      "connector": null,
      "results": [
        {
          "product": "",
          "tested_at": "ISO-8601",
          "prompt": "",
          "entity_mentioned": null,
          "domain_cited": null,
          "cited_urls": [],
          "competing_sources": [],
          "notes": []
        }
      ]
    },
    "measurement": {
      "available_sources": [],
      "recommended_metrics": [
        "index coverage",
        "citation share",
        "mention share",
        "prompt coverage",
        "AI referral conversions"
      ]
    },
    "unknowns": []
  }
}
```

## Packet rules

- Keep platform roles separate even when one vendor owns several bots.
- Preserve HTTP status codes and robots evidence separately.
- `robots_result` means policy permission; `http_result` means what the probe actually received. They can disagree.
- Do not mark a page indexed/cited merely because it returned HTTP 200.
- If the probe reports a `spoofed_ua_caveat` for an agent, add it to that platform's `notes` and to `unknowns`; do not raise a P0 finding on it alone.
- Include only findings supported by observed or documented evidence.
- Give stable finding IDs so another agent can refer to a specific fix.
