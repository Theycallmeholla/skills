# AI Visibility Packet

Emit this portable JSON object for every full or platform audit so other website/SEO/content agents can consume the result without reparsing prose.

Use `null` for unknown scalar values and `[]` for no observed items. Never convert an unverified state into `false`.

```json
{
  "ai_visibility_packet": {
    "schema_version": "2.0",
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
        "access_evidence_tier": "synthetic_ua|ua_attributed_logs|verified_crawler|webmaster_tool|none",
        "search_index_state": "indexed|partially_indexed|not_indexed|unknown",
        "ai_citation_state": "cited|not_cited_in_tests|not_tested|unknown",
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
      "indexability_issues": [],
      "dataset_reconciliation": [
        {
          "sources": ["sitemap", "search_console"],
          "counts": {},
          "explanation": null,
          "resolved": false
        }
      ]
    },
    "retrieval": {
      "page_reviews": [
        {
          "url": "",
          "page_type": "",
          "information_gain_class": "primary_source|useful_synthesis|commodity|thin",
          "passage_lift": "pass|fail|mixed",
          "quoted_passage": "",
          "target_question": "",
          "competing_sources": [],
          "fix": ""
        }
      ],
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
    "first_action": {
      "finding_id": "",
      "why_first": "",
      "quick_wins": []
    },
    "opportunities": [
      {
        "title": "",
        "type": "original_data|tool|definition|comparison|documentation|benchmark|edge_case|other",
        "target_question": "",
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
      "gaps": [],
      "recommended_metrics": [
        "index coverage",
        "citation share",
        "mention share",
        "prompt coverage",
        "AI referral conversions"
      ]
    },
    "coverage": {
      "access": "evaluated|unknown|out_of_scope",
      "indexability": "evaluated|unknown|out_of_scope",
      "renderability": "evaluated|unknown|out_of_scope",
      "retrieval_fitness": "evaluated|unknown|out_of_scope",
      "trust_evidence": "evaluated|unknown|out_of_scope",
      "information_gain": "evaluated|unknown|out_of_scope",
      "entity_clarity": "evaluated|unknown|out_of_scope",
      "topic_graph": "evaluated|unknown|out_of_scope",
      "freshness": "evaluated|unknown|out_of_scope",
      "agent_usability": "evaluated|unknown|out_of_scope",
      "measurement": "evaluated|unknown|out_of_scope",
      "prompt_visibility": "evaluated|unknown|out_of_scope"
    },
    "incidental_issues": [],
    "unknowns": []
  }
}
```

## Packet rules

- Keep platform roles separate even when one vendor owns several bots.
- Preserve HTTP status codes and robots evidence separately.
- `robots_result` means policy permission; `http_result` means what the synthetic-UA probe actually received. They can disagree.
- `access_evidence_tier` is the strongest access evidence you actually have. The probe alone never goes above `synthetic_ua`; log counts without IP/DNS verification are `ua_attributed_logs`.
- `search_index_state` and `ai_citation_state` are independent. Being indexed never implies being cited. Use `not_cited_in_tests` only when prompt tests actually ran.
- Do not mark a page indexed/cited merely because it returned HTTP 200.
- If the probe reports a `spoofed_ua_caveat` for an agent, add it to that platform's `notes` and to `unknowns`; do not raise a P0 finding on it alone.
- Add a `dataset_reconciliation` entry whenever counts from overlapping sources disagree materially. Leave `resolved: false` and add the gap to `unknowns` if it can't be explained.
- `first_action.finding_id` must be the top finding by the audit-framework priority order, not the easiest one.
- Every `coverage` key must be set for a full audit; `unknown` is allowed, a missing key is not.
- `incidental_issues` holds site bugs that don't affect AI discovery, retrieval, or source selection; keep them out of `findings`.
- Include only findings supported by observed or documented evidence.
- Give stable finding IDs so another agent can refer to a specific fix.

## Version history

- **2.0** -- replaced `index_or_citation_state` with `search_index_state` and `ai_citation_state`; added `access_evidence_tier`, `dataset_reconciliation`, `page_reviews`, `first_action`, `measurement.gaps`, `coverage`, `incidental_issues`, and `opportunities[].target_question`.
