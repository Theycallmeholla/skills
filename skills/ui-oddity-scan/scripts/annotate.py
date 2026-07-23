#!/usr/bin/env python3
"""Draw numbered finding boxes on a page screenshot.

Usage:
  python3 annotate.py page.png findings.json --out annotated.png

findings.json: [{"label": "1", "bbox": [x, y, w, h], "severity": "high|medium|low"}]
Colors: high=red, medium=orange, low=gold.
Requires: pip install pillow
"""
import argparse, json
from PIL import Image, ImageDraw, ImageFont

COLORS = {"high": "#D93025", "medium": "#E8710A", "low": "#C9A400"}

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font():
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, 22)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("screenshot")
    ap.add_argument("findings")
    ap.add_argument("--out", default="annotated.png")
    args = ap.parse_args()

    img = Image.open(args.screenshot).convert("RGB")
    draw = ImageDraw.Draw(img)
    with open(args.findings) as f:
        findings = json.load(f)

    font = load_font()

    for f_ in findings:
        x, y, w, h = f_["bbox"]
        pad = 6
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(img.width - 1, x + w + pad), min(img.height - 1, y + h + pad)
        color = COLORS.get(str(f_.get("severity", "medium")).lower(), COLORS["medium"])
        draw.rectangle([x0, y0, x1, y1], outline=color, width=4)
        # numbered badge, top-left of the box (inside image bounds)
        label = str(f_.get("label", "?"))
        bw = 18 + 13 * len(label)
        bx, by = x0, max(0, y0 - 30)
        draw.rectangle([bx, by, bx + bw, by + 30], fill=color)
        draw.text((bx + 8, by + 3), label, fill="white", font=font)

    img.save(args.out)
    print(f"Annotated {len(findings)} finding(s) -> {args.out}")


if __name__ == "__main__":
    main()
