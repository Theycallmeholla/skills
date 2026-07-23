#!/usr/bin/env python3
"""Capture a web page for UI oddity scanning.

Produces in --outdir:
  page.png   - full-page screenshot
  page.json  - structured data:
      title, url, viewport, page_size
      text_blocks:  [{text, tag, bbox[x,y,w,h], font_size, is_heading, is_cta, href}]
      ctas:         subset of text_blocks that are buttons / prominent links
      headings:     ordered heading outline
      duplicates:   exact-duplicate text pairs with pixel distance
      repeated_facts:  phone numbers appearing more than once, with all bboxes
      broken_images:   imgs with naturalWidth == 0
      overflow_elements: elements extending past the page width

Usage:
  python3 capture_page.py URL [--outdir DIR] [--width 1280] [--wait 2000]

URL may be http(s):// or file://
Requires: pip install playwright && playwright install chromium
"""
import argparse, json, math, os, re, sys
from collections import defaultdict

EXTRACT_JS = r"""
() => {
  const vw = document.documentElement.clientWidth;
  const blocks = [];
  const walk = (el) => {
    for (const child of el.children) walk(child);
    // direct text content of this element (not from children)
    let direct = '';
    for (const n of el.childNodes) {
      if (n.nodeType === Node.TEXT_NODE) direct += n.textContent;
    }
    direct = direct.replace(/\s+/g, ' ').trim();
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) return;
    const r = el.getBoundingClientRect();
    const tag = el.tagName.toLowerCase();
    const isCta = tag === 'button' || (tag === 'a' && el.href !== undefined) ||
                  el.getAttribute('role') === 'button' ||
                  /\bbtn|button|cta\b/i.test(el.className || '');
    // for CTAs use full innerText so "Get <b>Started</b>" reads whole
    let text = direct;
    if (isCta && el.innerText) text = el.innerText.replace(/\s+/g, ' ').trim();
    if (!text || r.width === 0 || r.height === 0) return;
    if (isCta && el.querySelector('a,button')) return; // container, children will report
    blocks.push({
      text: text.slice(0, 500),
      tag,
      bbox: [Math.round(r.left + window.scrollX), Math.round(r.top + window.scrollY),
             Math.round(r.width), Math.round(r.height)],
      font_size: parseFloat(style.fontSize) || null,
      is_heading: /^h[1-6]$/.test(tag),
      is_cta: isCta,
      href: tag === 'a' ? (el.getAttribute('href') || '') : null,
    });
  };
  walk(document.body);

  const brokenImages = [...document.images]
    .filter(im => im.naturalWidth === 0 && im.src)
    .map(im => {
      const r = im.getBoundingClientRect();
      return { src: im.src.slice(0, 300), alt: im.alt || '',
               bbox: [Math.round(r.left + window.scrollX), Math.round(r.top + window.scrollY),
                      Math.round(r.width), Math.round(r.height)] };
    });

  const pageW = document.documentElement.scrollWidth;
  const overflow = [];
  document.querySelectorAll('body *').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width > 0 && (r.right + window.scrollX) > vw + 8 && r.width < pageW * 2) {
      const s = window.getComputedStyle(el);
      if (s.display !== 'none' && s.visibility !== 'hidden')
        overflow.push({ tag: el.tagName.toLowerCase(),
                        text: (el.innerText || '').replace(/\s+/g,' ').trim().slice(0, 80),
                        bbox: [Math.round(r.left + window.scrollX), Math.round(r.top + window.scrollY),
                               Math.round(r.width), Math.round(r.height)] });
    }
  });

  return {
    title: document.title,
    viewport: { width: vw, height: document.documentElement.clientHeight },
    page_size: { width: pageW, height: document.documentElement.scrollHeight },
    blocks, brokenImages, overflow: overflow.slice(0, 40),
  };
}
"""

PHONE_RE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]?\d{4}")


def center_dist(b1, b2):
    x1, y1 = b1[0] + b1[2] / 2, b1[1] + b1[3] / 2
    x2, y2 = b2[0] + b2[2] / 2, b2[1] + b2[3] / 2
    return math.hypot(x2 - x1, y2 - y1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--outdir", default="capture")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--wait", type=int, default=2000, help="extra ms to wait after load")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": args.width, "height": 900})
        page.goto(args.url, wait_until="load", timeout=45000)
        page.wait_for_timeout(args.wait)
        data = page.evaluate(EXTRACT_JS)
        page.screenshot(path=os.path.join(args.outdir, "page.png"), full_page=True)
        browser.close()

    blocks = data["blocks"]

    # exact-duplicate detection (normalized), ignoring very short strings
    groups = defaultdict(list)
    for b in blocks:
        norm = re.sub(r"\W+", " ", b["text"].lower()).strip()
        if len(norm) >= 12:  # skip tiny labels; CTA dupes handled separately
            groups[norm].append(b)
    duplicates = []
    for norm, bs in groups.items():
        if len(bs) > 1:
            # drop nested parent/child reporting the same text
            pairs = []
            for i in range(len(bs)):
                for j in range(i + 1, len(bs)):
                    d = center_dist(bs[i]["bbox"], bs[j]["bbox"])
                    if d > 4:  # identical position => same element seen twice, skip
                        pairs.append({"text": bs[i]["text"], "bboxes": [bs[i]["bbox"], bs[j]["bbox"]],
                                      "pixel_distance": round(d)})
            duplicates.extend(pairs)
    duplicates.sort(key=lambda d: d["pixel_distance"])

    ctas = [b for b in blocks if b["is_cta"]]

    # repeated facts: phone numbers appearing in more than one block
    phone_groups = defaultdict(list)
    for b in blocks:
        for m in PHONE_RE.findall(b["text"]):
            digits = re.sub(r"\D", "", m)[-10:]
            if len(digits) == 10:
                phone_groups[digits].append(b)
    repeated_facts = []
    for digits, bs in phone_groups.items():
        # dedupe nested parent/child at ~same position
        uniq = []
        for b in bs:
            if not any(center_dist(b["bbox"], u["bbox"]) <= 4 for u in uniq):
                uniq.append(b)
        if len(uniq) > 1:
            repeated_facts.append({
                "fact_type": "phone",
                "value": digits,
                "count": len(uniq),
                "occurrences": [{"text": b["text"], "bbox": b["bbox"]} for b in uniq],
            })

    out = {
        "url": args.url,
        "title": data["title"],
        "viewport": data["viewport"],
        "page_size": data["page_size"],
        "text_blocks": blocks,
        "headings": [b for b in blocks if b["is_heading"]],
        "ctas": ctas,
        "duplicates": duplicates[:60],
        "repeated_facts": repeated_facts,
        "broken_images": data["brokenImages"],
        "overflow_elements": data["overflow"],
    }
    path = os.path.join(args.outdir, "page.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"Captured {args.url}")
    print(f"  screenshot: {os.path.join(args.outdir, 'page.png')} ({data['page_size']['width']}x{data['page_size']['height']})")
    print(f"  data:       {path}")
    print(f"  blocks={len(blocks)} ctas={len(ctas)} duplicates={len(duplicates)} "
          f"repeated_facts={len(repeated_facts)} broken_images={len(data['brokenImages'])} "
          f"overflow={len(data['overflow'])}")


if __name__ == "__main__":
    main()
