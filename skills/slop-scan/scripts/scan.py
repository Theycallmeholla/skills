#!/usr/bin/env python3
"""Slop Scan: find visual AI tells in a repo, file or URL.

Usage:
  python3 scan.py <path-or-url> [more paths/urls] [--json out.json]

Source locator for fixes. The rendered scan (render.sh) is the primary evidence.
"""
import json, os, re, sys, urllib.request
from collections import Counter
from urllib.parse import urljoin, urlparse

EXTS = {".tsx", ".jsx", ".ts", ".js", ".html", ".htm", ".css", ".scss", ".vue",
        ".svelte", ".astro", ".mdx", ".php", ".liquid"}
SKIP = {"node_modules", ".next", "dist", "build", ".git", "out", ".vercel",
        ".turbo", "coverage", "vendor", ".cache"}
CLS = r"[^\"'`]*"  # stays inside one class string
SCRIPT_FONTS = r"Caveat|Dancing[ _+]Script|Pacifico|Great[ _+]Vibes|Kalam|Sacramento|Satisfy|Parisienne|Allura|Homemade[ _+]Apple|Shadows[ _+]Into[ _+]Light|Permanent[ _+]Marker|Indie[ _+]Flower|Yellowtail|Kaushan[ _+]Script|Lobster|Courgette|Alex[ _+]Brush|Nothing[ _+]You[ _+]Could[ _+]Do|Reenie[ _+]Beanie|Gochi[ _+]Hand|Patrick[ _+]Hand"

# id, big_six, group, label, patterns, partial_at, present_at
CHECKS = [
    ("gradient", True, "Color", "Gradients (purple/blue washes, gradient buttons/backgrounds)",
     [r"\bbg-gradient-to-\w+(?!" + CLS + r"from-(?:black|transparent))", r"\bbg-linear-to-\w+", r"linear-gradient\((?![^;\"']*(?:transparent|rgba?\([^)]*,\s*0\)))", r"radial-gradient\((?![^;\"']*transparent)",
      r"\b(?:from|via|to)-(?:indigo|violet|purple|fuchsia|blue|pink)-\d{2,3}\b"], 1, 3),
    ("gradient-text", True, "Color", "Gradient text", [r"bg-clip-text", r"background-clip:\s*text"], 1, 1),
    ("glow", True, "Color", "Blurred glow orbs", [r"blur-(?:2xl|3xl|\[\d{2,3}px\])" , r"filter:\s*blur\((?:[4-9]\d|\d{3})px\)"], 1, 2),
    ("purple", False, "Color", "Indigo/violet/purple accent",
     [r"\b(?:bg|text|border|ring)-(?:indigo|violet|purple)-\d{2,3}\b", r"#(?:6366f1|4f46e5|4338ca|7c3aed|8b5cf6|a855f7|6d28d9|9333ea)\b"], 1, 3),

    ("highlight-word", True, "Type", "Highlighted word in heading (script/italic/colored/gradient span)",
     [r"<h[1-3]\b[^>]*>(?:(?!</h[1-3]>)[\s\S]){0,300}?<(?:span|em|i|mark|strong)\b[^>]*\b(?:class|className|style)=[^>]*>\s*[A-Za-z]",
      r"<h[1-3]\b[^>]*>(?:(?!</h[1-3]>)[\s\S]){0,300}?<(?:em|i)>",
      r"(?:font-family:\s*[\"']?(?:" + SCRIPT_FONTS + r"))", r"(?:" + SCRIPT_FONTS + r")\s*\(", r"family=(?:" + SCRIPT_FONTS + r")"], 1, 2),
    ("em-dash", True, "Type", "Em dashes as decoration", [r"\u2014", r"&mdash;", r"&#8212;"], 2, 4),
    ("inter", False, "Type", "Inter/Geist default font", [r"\bInter\s*\(|['\"]Inter['\"]|font-family:[^;]*\bInter\b|family=Inter\b", r"\bGeist(?:_Sans|Sans)?\b"], 1, 1),
    ("tight-headline", False, "Type", "Huge tight-tracked headline", [r"text-(?:5|6|7|8)xl" + CLS + r"tracking-tight|tracking-tight" + CLS + r"text-(?:5|6|7|8)xl", r"letter-spacing:\s*-0?\.0[2-6]em"], 1, 2),
    ("caps-label", True, "Type", "ALL-CAPS tracked eyebrow labels", [r"uppercase" + CLS + r"tracking-(?:wide|wider|widest|\[)|tracking-(?:wide|wider|widest|\[)" + CLS + r"uppercase", r"text-transform:\s*uppercase"], 2, 4),
    ("dots-arrows", False, "Type", "Middle-dot strings / arrow on every link", [r"\s\u00b7\s", r"\u2192", r"\bArrowRight\b", r"&rarr;"], 3, 6),
    ("emoji", False, "Type", "Emoji decoration", [r"[\U0001F680\u2728\u26A1\U0001F3AF\U0001F4A1\U0001F525\U0001F31F\U0001F4C8\U0001F4AA\U0001F389]"], 1, 3),

    ("pill", True, "Components", "Eyebrow pill / badge", [r"rounded-full" + CLS + r"px-[2-4]" + CLS + r"py-(?:0\.5|1|1\.5)" + CLS + r"text-(?:xs|sm)", r"<Badge\b", r"<(?:span|div|p|small|a)\b[^>]*class=[\"'][^\"']*\b(?:eyebrow|kicker|pill|badge|chip)\b"], 1, 2),
    ("ghost-pair", False, "Components", "Solid + ghost/outline button pair", [r"variant=[\"'](?:outline|ghost)[\"']", r"\bbtn-(?:outline|ghost|secondary)\b"], 1, 2),
    ("stat-row", False, "Components", "Big-number stat row", [r">\s*\d{1,3}(?:,\d{3})*(?:\+|k\+|K\+)\s*<", r">\s*\d{2}(?:\.\d)?%\s*<", r">\s*24/7\s*<"], 2, 3),
    ("icon-tile", True, "Components", "Icon tiles (line icon in tinted rounded square)",
     [r"(?:h|size)-(?:8|9|10|11|12|14)\b" + CLS + r"rounded-(?:md|lg|xl|2xl|full)" + CLS + r"bg-[a-z]+-(?:50|100|500/10|500/20)\b", r"bg-primary/10",
      r"from\s+['\"]lucide-react['\"]", r"@heroicons/", r"class=[\"'][^\"']*\b(?:icon-wrap|icon-box|icon-tile|icon-circle|feature-icon|card-icon)\b"], 2, 4),
    ("cards", True, "Components", "Identical card recipe (radius + border + shadow)", [r"rounded-(?:lg|xl|2xl|3xl)\b(?=" + CLS + r"\bborder\b)(?=" + CLS + r"shadow-(?:sm|md|lg))", r"<Card\b"], 3, 6),
    ("three-up", True, "Components", "Rows of three equal cards", [r"\b(?:sm:|md:|lg:)?grid-cols-3\b", r"grid-template-columns:\s*repeat\(3,\s*(?:1fr|minmax)"], 1, 3),
    ("accent-bar", False, "Components", "Left accent bar on cards", [r"\bborder-l-(?:2|4|\[\dpx\])\b", r"border-left:\s*[3-6]px\s+solid"], 1, 1),
    ("bento", False, "Components", "Bento tiles", [r"\b(?:md:|lg:)?(?:col|row)-span-2\b", r"grid-(?:column|row):\s*span\s*2"], 2, 3),
    ("popular", False, "Components", "'Most popular' pricing card", [r"most\s+popular"], 1, 1),
    ("accordion", False, "Components", "FAQ accordion", [r"<Accordion\b", r"<details\b"], 1, 2),
    ("avatars", False, "Components", "Round-avatar testimonials", [r"<Avatar\b", r"class=[\"'][^\"']*\bavatar\b"], 1, 3),
    ("checkrows", False, "Components", "Checkmark rows", [r"<(?:Check|CheckCircle2?|CircleCheck|BadgeCheck|CheckIcon)\b", r"[\u2713\u2714\u2705]"], 3, 4),
    ("marquee", False, "Components", "Logo marquee", [r"animate-(?:marquee|scroll|infinite-scroll)", r"grayscale" + CLS + r"opacity-\d{2}", r"@keyframes\s+(?:marquee|scroll)"], 1, 1),
    ("monogram", False, "Components", "Monogram letter logo in rounded tile", [r"rounded-(?:md|lg|xl|2xl|full)" + CLS + r"[\"'`][^>]*>\s*[A-Z]{1,2}\s*<"], 1, 1),

    ("one-column", True, "Mechanical", "Everything in one centered max-width column", [r"max-w-(?:5xl|6xl|7xl|screen-xl)\s+mx-auto|mx-auto\s+max-w-(?:5xl|6xl|7xl|screen-xl)", r"margin:\s*0 auto"], 3, 6),
    ("gray-bands", False, "Mechanical", "Alternating light-gray sections", [r"\bbg-(?:gray|slate|zinc|neutral|stone)-50\b", r"\bbg-muted(?:/\d+)?\b"], 2, 4),
    ("dark-overlay", False, "Mechanical", "Full-bleed photo with dark overlay", [r"bg-gradient-to-[tb]\s+from-(?:black|slate-900|gray-900|zinc-900)", r"\bbg-black/(?:30|40|50|60|70)\b", r"rgba\(0,\s*0,\s*0,\s*0?\.[3-7]\)"], 1, 2),

    ("fade-up", False, "Motion", "Fade-up on scroll", [r"whileInView", r"data-aos", r"animate-fade(?:-in)?-up", r"fade-?up", r"initial=\{\{\s*opacity:\s*0", r"IntersectionObserver"], 2, 4),
    ("glass", False, "Motion", "Glassmorphism / blurred nav", [r"backdrop-blur", r"backdrop-filter:\s*blur"], 1, 3),
    ("hover-lift", False, "Motion", "Hover lift on every card", [r"hover:-translate-y-\d", r"hover:shadow-(?:lg|xl|2xl)", r"translateY\(-[2-8]px\)"], 2, 4),
]

BANNED = [
    ("Outlined/ghost word behind headline", [r"text-stroke"]),
    ("Watermark numbers", [r"text-(?:\[\d{3}px\]|9xl|\[\d{1,2}rem\])" + CLS + r"opacity-(?:5|10)", r"opacity-(?:5|10)" + CLS + r"text-(?:\[\d{3}px\]|9xl)"]),
    ("Grain/noise overlay", [r"feTurbulence", r"(?:noise|grain)\.(?:svg|png)"]),
    ("Rotated sticker badge", [r"-?rotate-(?:2|3|6|12|\[-?\d+deg\])" + CLS + r"(?:badge|sticker|rounded-full)"]),
    ("Diagonal/wavy dividers", [r"clip-path:\s*polygon", r"\[clip-path:polygon", r"-?skew-y-\d", r"wave\.svg"]),
    ("Duotone/tint photo overlay", [r"mix-blend-(?:multiply|color|overlay|screen)"]),
    ("Safe grotesk swap", [r"\b(?:Manrope|Plus[ _+]Jakarta[ _+]Sans|DM[ _+]Sans|Satoshi|General[ _+]Sans|Outfit|Poppins)\b"]),
    ("Cream + terracotta", [r"#(?:f4f1ea|f5f0e8|faf7f2)\b", r"#(?:d97757|c96442|cc785c)\b"]),
    ("Acid accent", [r"#(?:c6ff00|d4ff00|ccff00|bef264)\b", r"\b(?:bg|text)-lime-(?:300|400)\b"]),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 slop-scan"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


def gather(target):
    if re.match(r"https?://", target):
        html = fetch(target)
        docs = [(target, html)]
        host = urlparse(target).netloc
        hrefs = re.findall(r"<link[^>]+href=[\"']([^\"']+\.css[^\"']*)[\"']", html, re.I)
        for h in list(dict.fromkeys(hrefs))[:6]:
            full = urljoin(target, h)
            if urlparse(full).netloc in (host, ""):
                try:
                    docs.append((full, fetch(full)))
                except Exception:  # noqa: BLE001
                    pass
        return docs
    if os.path.isfile(target):
        with open(target, encoding="utf-8", errors="replace") as f:
            return [(os.path.basename(target), f.read())]
    docs = []
    for dp, dns, fns in os.walk(target):
        dns[:] = [d for d in dns if d not in SKIP and not d.startswith(".")]
        for fn in sorted(fns):
            if os.path.splitext(fn)[1].lower() in EXTS:
                p = os.path.join(dp, fn)
                if os.path.getsize(p) < 1_500_000:
                    with open(p, encoding="utf-8", errors="replace") as f:
                        docs.append((os.path.relpath(p, target), f.read()))
    return docs


def find(docs, pats):
    hits = []
    for src, text in docs:
        for pat in pats:
            for m in re.finditer(pat, text, re.I):
                line = text.count("\n", 0, m.start()) + 1
                snip = text[max(0, m.start() - 25): m.end() + 25].replace("\n", " ").strip()
                hits.append(f"{src}:{line}  {snip[:110]}")
    return hits


def same_gap(docs):
    pads = Counter()
    for _, t in docs:
        pads.update(re.findall(r"\b(?:md:|lg:)?py-(\d{2})\b", t))
        pads.update(re.findall(r"padding(?:-block)?:\s*(\d+(?:px|rem))\s+(?:0|\d)", t))
    total = sum(pads.values())
    if total >= 4:
        v, n = pads.most_common(1)[0]
        if n / total >= 0.6:
            return (2 if n / total >= 0.75 else 1), [f"'{v}' is the section padding {n}/{total} times"]
    return 0, []


def scan(target):
    docs = gather(target)
    results = []
    for cid, big, group, label, pats, part, pres in CHECKS:
        hits = find(docs, pats)
        n = len(hits)
        state = "Present" if n >= pres else "Partial" if n >= part else "Absent"
        results.append({"id": cid, "big_six": big, "group": group, "label": label, "hits": n, "state": state, "evidence": hits[:3]})
    s, ev = same_gap(docs)
    results.append({"id": "same-gap", "big_six": True, "group": "Mechanical", "label": "Same gap between every section",
                    "hits": None, "state": ["Absent", "Partial", "Present"][s], "evidence": ev})
    banned = [{"label": lab, "evidence": find(docs, pats)[:2]} for lab, pats in BANNED if find(docs, pats)]
    present = [r for r in results if r["state"] == "Present"]
    # map to the Big Six buckets
    buckets = set()
    for r in present:
        if not r["big_six"]:
            continue
        b = {"gradient": "Gradients", "gradient-text": "Gradients", "glow": "Gradients",
             "highlight-word": "Highlighted heading word", "em-dash": "Em dashes",
             "pill": "Eyebrow pills/labels", "caps-label": "Eyebrow pills/labels",
             "icon-tile": "Icon tiles"}.get(r["id"], "Mechanical look")
        buckets.add(b)
    n = len(present)
    verdict = ("Looks AI-generated" if n >= 6 or len(buckets) >= 3 else
               "Some AI tells" if n >= 3 or len(buckets) >= 2 else "Doesn't look AI-generated")
    return {"target": target, "files": len(docs), "verdict": verdict, "present": n,
            "big_six_hit": sorted(buckets), "checks": results, "banned_replacements": banned}


def show(rep):
    print(f"\n=== {rep['target']} ({rep['files']} files)")
    print(f"CODE VERDICT: {rep['verdict']}  ({rep['present']} present; Big Six: {', '.join(rep['big_six_hit']) or 'none'})")
    print("First pass only. Confirm with screenshots.\n")
    for state in ("Present", "Partial"):
        rows = [r for r in rep["checks"] if r["state"] == state]
        if rows:
            print(state.upper())
            for r in rows:
                star = "*" if r["big_six"] else " "
                cnt = f" ({r['hits']})" if r["hits"] is not None else ""
                print(f" {star} {r['label']}{cnt}")
                for e in r["evidence"][:2]:
                    print(f"      {e}")
            print()
    if rep["banned_replacements"]:
        print("BANNED REPLACEMENT MOVES FOUND")
        for b in rep["banned_replacements"]:
            print(f"   {b['label']}: {b['evidence'][0]}")
        print()
    print("* = Big Six tell")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    out = None
    if "--json" in args:
        i = args.index("--json"); out = args[i + 1]; args = args[:i] + args[i + 2:]
    reps = []
    for t in args:
        try:
            reps.append(scan(t))
        except Exception as e:  # noqa: BLE001
            print(f"Failed on {t}: {e}", file=sys.stderr)
    for r in reps:
        show(r)
    if out:
        with open(out, "w") as f:
            json.dump(reps if len(reps) > 1 else reps[0], f, indent=2)
        print(f"JSON written to {out}")


if __name__ == "__main__":
    main()
