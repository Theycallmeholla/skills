#!/usr/bin/env python3
"""Mechanical AI-tells metrics.

Measures only what is countable: lexicon hits, construction tics, rhythm
uniformity, formatting density. The judgment layer (stance, texture,
audience fit, the 500-companies test) is scored by Claude reading the text
-- this script deliberately does not attempt it and produces no overall
score on its own.

Usage: python3 tells_metrics.py <file.md|file.txt>
       cat text | python3 tells_metrics.py -
Output: JSON to stdout.
"""
import json
import re
import statistics
import sys

LEXICON = [
    "delve", "tapestry", "robust", "leverage", "foster", "underscore",
    "pivotal", "seamless", "seamlessly", "nuanced", "testament to",
    "beacon", "realm", "plethora", "multifaceted", "game-changer",
    "game-changing", "revolutionize", "unlock", "unleash", "empower",
    "elevate", "crucial", "synergy", "ever-evolving", "fast-paced",
    "digital landscape", "digital age", "in today's", "dive into",
    "dive in", "navigate the", "navigating the", "the ultimate guide",
    "whether you're a", "whether you are a", "unlock the power",
    "harness the power", "in the world of", "when it comes to",
    "at the end of the day", "look no further",
]

SIGNPOSTS = [
    "moreover", "furthermore", "additionally", "in conclusion",
    "ultimately", "to sum up", "in essence", "in summary",
    "let's dive in", "let us dive in", "but here's the thing",
    "it's important to note", "it is important to note",
    "it's worth noting", "it is worth noting",
    "it's important to remember", "it is important to remember",
    "first and foremost", "that being said", "with that said",
]

HEDGES = [
    "typically", "in most cases", "more often than not",
    "generally speaking", "may potentially", "can potentially",
    "might potentially", "in many cases", "for the most part",
    "it depends on various factors", "a variety of factors",
]

NOT_JUST_FRAMES = [
    r"\bnot just\b[^.\n]{0,80}?\bbut\b",
    r"\bnot just a\b", r"\bnot merely\b", r"\bisn't just\b",
    r"\bis more than just\b", r"\bit's about\b",
]


def _count_phrase(text_lower, phrase):
    if " " in phrase or "'" in phrase or "-" in phrase:
        return text_lower.count(phrase)
    return len(re.findall(r"\b" + re.escape(phrase) + r"\b", text_lower))


def analyze(text):
    text_lower = text.lower()
    words = re.findall(r"[A-Za-z0-9''-]+", text)
    n_words = max(len(words), 1)
    per_k = lambda n: round(n * 1000.0 / n_words, 2)

    lines = text.splitlines()
    heading_lines = [l for l in lines if re.match(r"\s*#{1,6}\s", l)]
    bullet_lines = [l for l in lines if re.match(r"\s*([-*+]|\d+[.)])\s", l)]
    content_lines = [l for l in lines if l.strip()]
    bullet_share = round(len(bullet_lines) / max(len(content_lines), 1), 3)

    # Prose paragraphs: blank-line separated blocks that aren't headings/bullets
    blocks, cur = [], []
    for l in lines:
        if l.strip():
            cur.append(l)
        else:
            if cur:
                blocks.append("\n".join(cur))
                cur = []
    if cur:
        blocks.append("\n".join(cur))
    prose_paras = [
        b for b in blocks
        if not re.match(r"\s*#{1,6}\s", b)
        and not re.match(r"\s*([-*+]|\d+[.)]|\||>)", b)
        and len(b.split()) > 3
    ]

    def sent_count(p):
        return max(len(re.findall(r"[.!?](?:\s|$)", p)), 1)

    para_word_lens = [len(p.split()) for p in prose_paras]
    para_sent_lens = [sent_count(p) for p in prose_paras]

    def cv(vals):
        if len(vals) < 3 or statistics.mean(vals) == 0:
            return None
        return round(statistics.pstdev(vals) / statistics.mean(vals), 3)

    sentences = [s.strip() for s in re.split(r"[.!?](?:\s+|$)", text) if len(s.split()) >= 3]
    sent_word_lens = [len(s.split()) for s in sentences]

    lexicon_hits = {p: c for p in LEXICON if (c := _count_phrase(text_lower, p)) > 0}
    signpost_hits = {p: c for p in SIGNPOSTS if (c := _count_phrase(text_lower, p)) > 0}
    hedge_hits = {p: c for p in HEDGES if (c := _count_phrase(text_lower, p)) > 0}

    signpost_openers = sum(
        1 for p in prose_paras
        if any(p.lower().lstrip().startswith(s) for s in SIGNPOSTS)
    )

    em_dashes = text.count("\u2014") + text.count(" -- ")
    bold_segments = len(re.findall(r"\*\*[^*\n]+\*\*", text))
    colons_in_prose = sum(p.count(":") for p in prose_paras)
    triads = len(re.findall(r",\s+[^,.\n;]{2,40},?\s+and\s+\w", text))
    not_just = sum(len(re.findall(rx, text_lower)) for rx in NOT_JUST_FRAMES)
    question_headings = sum(1 for h in heading_lines if h.rstrip().endswith("?"))
    rhetorical_openers = sum(
        1 for p in prose_paras[:3]
        if re.match(r"^[^.!?]{0,120}\?", p.replace("\n", " "))
    )

    result = {
        "counts": {
            "words": n_words,
            "sentences": len(sentences),
            "prose_paragraphs": len(prose_paras),
            "headings": len(heading_lines),
            "bullet_lines": len(bullet_lines),
        },
        "lexicon": {
            "hits": lexicon_hits,
            "total": sum(lexicon_hits.values()),
            "per_1000_words": per_k(sum(lexicon_hits.values())),
        },
        "signposts": {
            "hits": signpost_hits,
            "total": sum(signpost_hits.values()),
            "paragraph_openers": signpost_openers,
        },
        "hedges": {
            "hits": hedge_hits,
            "total": sum(hedge_hits.values()),
            "per_1000_words": per_k(sum(hedge_hits.values())),
        },
        "constructions": {
            "em_dashes": em_dashes,
            "em_dashes_per_1000_words": per_k(em_dashes),
            "triad_patterns": triads,
            "triads_per_1000_words": per_k(triads),
            "not_just_but_frames": not_just,
            "question_headings": question_headings,
            "rhetorical_openers_first3_paras": rhetorical_openers,
            "bold_segments": bold_segments,
            "bold_per_1000_words": per_k(bold_segments),
            "colons_in_prose": colons_in_prose,
        },
        "rhythm": {
            "paragraph_word_cv": cv(para_word_lens),
            "paragraph_sentence_cv": cv(para_sent_lens),
            "sentence_word_cv": cv(sent_word_lens),
            "mean_paragraph_words": round(statistics.mean(para_word_lens), 1) if para_word_lens else None,
            "mean_sentence_words": round(statistics.mean(sent_word_lens), 1) if sent_word_lens else None,
            "bullet_share_of_lines": bullet_share,
        },
        "reference_thresholds": {
            "note": "Rules of thumb, not verdicts. CV = coefficient of variation; LOWER CV = MORE uniform = more tell-like.",
            "paragraph_sentence_cv_uniform_below": 0.35,
            "sentence_word_cv_uniform_below": 0.40,
            "em_dashes_per_1000_flag_above": 3.5,
            "triads_per_1000_flag_above": 2.5,
            "lexicon_per_1000_flag_above": 3.0,
            "bullet_share_flag_above": 0.33,
            "bold_per_1000_flag_above": 8.0,
        },
    }
    return result


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    if sys.argv[1] == "-":
        text = sys.stdin.read()
    else:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    print(json.dumps(analyze(text), indent=2))


if __name__ == "__main__":
    main()
